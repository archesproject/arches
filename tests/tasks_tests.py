import logging

from django.contrib.auth.models import User
from unittest.mock import patch

from arches.app.tasks import update_resource_instance_data_based_on_graph_diff
from arches.app.models import models
from arches.app.models.graph import Graph

from tests.base_test import ArchesTestCase


class UpdateResourceInstanceDataTaskTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        logging.getLogger("arches.app.tasks").setLevel(logging.CRITICAL)

        super().setUpTestData()

        cls.user = User.objects.create(
            username="arches_test_user",
            first_name="TEST",
            last_name="USER",
        )

        cls.NODE_NODETYPE_GRAPHID = "22000000-0000-0000-0000-000000000001"
        cls.node_node_type_graph = cls.create_node_node_type_graph()

        cls.test_graph = cls.create_test_graph()

    @classmethod
    def create_test_graph(cls):
        test_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = test_graph.get_draft_graph()

        draft_graph.subtitle = "ARCHES TEST RESOURCE"
        draft_graph.author = "Arches"
        draft_graph.description = "ARCHES TEST RESOURCE DESCRIPTION"
        draft_graph.ontology_id = "e6e8db47-2ccf-11e6-927e-b8f6b115d7dd"
        draft_graph.version = "v1.0.0"
        draft_graph.iconclass = "fa fa-building"
        draft_graph.nodegroups = []
        draft_graph.root.ontologyclass = (
            "http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity"
        )
        draft_graph.root.name = "ROOT NODE"
        draft_graph.root.description = "Test Root Node"
        draft_graph.root.datatype = "semantic"
        draft_graph.root.save()

        draft_graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=cls.NODE_NODETYPE_GRAPHID,
        )
        draft_graph.save(validate=False)

        updated_test_graph = test_graph.promote_draft_graph_to_active_graph()
        updated_test_graph.publish()

        cls.string_node_id = [
            node
            for node in updated_test_graph.nodes.values()
            if node.datatype == "string"
        ][0].nodeid
        cls.concept_node_id = [
            node
            for node in updated_test_graph.nodes.values()
            if node.datatype == "concept"
        ][0].nodeid

        return updated_test_graph

    @classmethod
    def create_node_node_type_graph(cls):
        graph_data = {
            "author": "Arches",
            "color": None,
            "deploymentdate": None,
            "deploymentfile": None,
            "description": "Represents a node and node type pairing",
            "graphid": cls.NODE_NODETYPE_GRAPHID,
            "iconclass": "fa fa-angle-double-down",
            "isresource": False,
            "name": "Node/Node Type",
            "slug": "node_node_type",
            "ontology_id": "e6e8db47-2ccf-11e6-927e-b8f6b115d7dd",
            "subtitle": "Represents a node and node type pairing",
            "version": "v1",
        }
        graph_model = models.GraphModel.objects.create(**graph_data)

        nodegroup_data = {
            "cardinality": "n",
            "legacygroupid": "",
            "nodegroupid": "20000000-0000-0000-0000-100000000001",
            "parentnodegroup_id": None,
        }
        models.NodeGroup.objects.create(**nodegroup_data).save()

        card_data = {
            "active": True,
            "cardid": "bf9ea150-3eaa-11e8-8b2b-c3a348661f61",
            "description": "Represents a node and node type pairing",
            "graph_id": cls.NODE_NODETYPE_GRAPHID,
            "helpenabled": False,
            "helptext": None,
            "helptitle": None,
            "instructions": "",
            "name": "Node/Node Type",
            "nodegroup_id": "20000000-0000-0000-0000-100000000001",
            "sortorder": None,
            "visible": True,
        }

        card = models.CardModel.objects.create(**card_data)
        nodes_data = [
            {
                "config": None,
                "datatype": "string",
                "description": "",
                "graph_id": cls.NODE_NODETYPE_GRAPHID,
                "isrequired": False,
                "issearchable": True,
                "istopnode": True,
                "name": "Node",
                "nodegroup_id": "20000000-0000-0000-0000-100000000001",
                "nodeid": "20000000-0000-0000-0000-100000000001",
                "ontologyclass": "http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity",
            },
            {
                "config": {"rdmCollection": None},
                "datatype": "concept",
                "description": "",
                "graph_id": cls.NODE_NODETYPE_GRAPHID,
                "isrequired": False,
                "issearchable": True,
                "istopnode": False,
                "name": "Node Type",
                "nodegroup_id": "20000000-0000-0000-0000-100000000001",
                "nodeid": "20000000-0000-0000-0000-100000000002",
                "ontologyclass": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
            },
        ]

        for node_data in nodes_data:
            models.Node.objects.create(**node_data)

        models.NodeGroup.objects.filter(
            pk="20000000-0000-0000-0000-100000000001"
        ).update(grouping_node_id="20000000-0000-0000-0000-100000000001")

        edge_data = {
            "description": None,
            "domainnode_id": "20000000-0000-0000-0000-100000000001",
            "edgeid": "22200000-0000-0000-0000-000000000001",
            "graph_id": cls.NODE_NODETYPE_GRAPHID,
            "name": None,
            "ontologyproperty": "http://www.cidoc-crm.org/cidoc-crm/P2_has_type",
            "rangenode_id": "20000000-0000-0000-0000-100000000002",
        }
        models.Edge.objects.create(**edge_data).save()

        graph = Graph.objects.get(pk=graph_model.pk)
        graph.save()
        graph.publish()
        return graph

    @patch("arches.app.tasks.notify_completion")
    def test_task_runs_and_notifies_success(self, mock_notify):
        published_graph = models.PublishedGraph.objects.get(
            publication=self.test_graph.publication,
            language="en",
        )
        serialized_graph = published_graph.serialized_graph

        update_resource_instance_data_based_on_graph_diff(
            initial_graph=serialized_graph,
            updated_graph=serialized_graph,
            user_id=self.user.pk,
        )

        self.assertEqual(mock_notify.call_count, 2)
        msg, notified_user = mock_notify.call_args[0]
        self.assertEqual(notified_user, self.user)
        self.assertTrue(
            msg.startswith(
                "Business has been updated in concurrence with publishing the latest model."
            ),
        )

    @patch("arches.app.tasks.notify_completion")
    def test_notify_completion_on_exception(self, mock_notify):
        update_resource_instance_data_based_on_graph_diff(
            initial_graph={},
            updated_graph={},
            user_id=self.user.pk,
        )

        self.assertEqual(mock_notify.call_count, 2)
        msg, notified_user = mock_notify.call_args[0]
        self.assertEqual(notified_user, self.user)
        self.assertEqual(
            msg,
            "Business data update failed. Check the error logs for more information.",
        )

    @patch("arches.app.tasks.notify_completion")
    def test_updates_publication_id(self, mock_notify):
        first_resource_instance = models.ResourceInstance.objects.create(
            graph=self.test_graph
        )
        second_resource_instance = models.ResourceInstance.objects.create(
            graph=self.test_graph
        )

        original_published_graph = models.PublishedGraph.objects.get(
            publication=self.test_graph.publication, language="en"
        )

        self.test_graph.publish()

        updated_published_graph = models.PublishedGraph.objects.get(
            publication=self.test_graph.publication, language="en"
        )

        self.assertNotEqual(
            original_published_graph.serialized_graph["publication_id"],
            updated_published_graph.serialized_graph["publication_id"],
        )

        self.assertEqual(
            str(first_resource_instance.graph_publication_id),
            original_published_graph.serialized_graph["publication_id"],
        )
        self.assertEqual(
            str(second_resource_instance.graph_publication_id),
            original_published_graph.serialized_graph["publication_id"],
        )

        update_resource_instance_data_based_on_graph_diff(
            initial_graph=original_published_graph.serialized_graph,
            updated_graph=updated_published_graph.serialized_graph,
            user_id=self.user.pk,
        )

        first_resource_instance.refresh_from_db()
        second_resource_instance.refresh_from_db()

        self.assertEqual(
            str(first_resource_instance.graph_publication_id),
            updated_published_graph.serialized_graph["publication_id"],
        )
        self.assertEqual(
            str(second_resource_instance.graph_publication_id),
            updated_published_graph.serialized_graph["publication_id"],
        )

    @patch("arches.app.tasks.notify_completion")
    def test_prunes_deleted_nodes(self, mock_notify):
        original_published_graph = models.PublishedGraph.objects.get(
            publication=self.test_graph.publication,
            language="en",
        )

        resource_instance = models.ResourceInstance.objects.create(
            graph=self.test_graph
        )

        tile = models.TileModel.objects.create(
            resourceinstance=resource_instance,
            data={
                str(self.concept_node_id): "DUMMY DATA",
            },
            sortorder=0,
        )

        self.assertEqual(
            tile.data,
            {
                str(self.concept_node_id): "DUMMY DATA",
            },
        )

        draft_graph = self.test_graph.create_draft_graph()

        node_to_delete = models.Node.objects.get(
            source_identifier_id=self.concept_node_id
        )
        draft_graph.delete_node(node_to_delete)

        updated_graph = self.test_graph.promote_draft_graph_to_active_graph()
        updated_graph.publish()

        updated_published_graph = models.PublishedGraph.objects.get(
            publication=updated_graph.publication,
            language="en",
        )

        self.assertNotEqual(
            original_published_graph.serialized_graph["publication_id"],
            updated_published_graph.serialized_graph["publication_id"],
        )

        update_resource_instance_data_based_on_graph_diff(
            initial_graph=original_published_graph.serialized_graph,
            updated_graph=updated_published_graph.serialized_graph,
            user_id=self.user.pk,
        )

        tile.refresh_from_db()

        self.assertNotIn(
            str(self.concept_node_id),
            tile.data,
        )

    @patch("arches.app.tasks.notify_completion")
    def test_adds_new_nodes_and_populates_defaults(self, mock_notify):
        original_published_graph = models.PublishedGraph.objects.get(
            publication=self.test_graph.publication,
            language="en",
        )

        resource_instance = models.ResourceInstance.objects.create(
            graph=self.test_graph
        )
        tile = models.TileModel.objects.create(
            resourceinstance=resource_instance,
            nodegroup_id=self.test_graph.get_nodegroups()[0].nodegroupid,
            data={
                str(self.string_node_id): {
                    "en": {"value": "test value", "direction": "ltr"},
                }
            },
            sortorder=0,
        )

        self.assertDictEqual(
            tile.data[str(self.string_node_id)],
            {"en": {"value": "test value", "direction": "ltr"}},
        )

        draft_graph = self.test_graph.create_draft_graph()

        new_node_id = "33333333-3333-3333-3333-333333333333"
        node_to_add = models.Node.objects.create(
            config={
                "defaultValue": {
                    "en": {"value": "Default Value", "direction": "ltr"},
                }
            },
            datatype="string",
            description="Added test node",
            graph_id=draft_graph.graphid,
            isrequired=False,
            issearchable=True,
            istopnode=False,
            name="Added Node",
            nodegroup_id=draft_graph.get_nodegroups()[0].nodegroupid,
            nodeid=new_node_id,
            ontologyclass="http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity",
        )
        draft_graph.add_node(node_to_add)

        card = models.CardModel.objects.get(pk=draft_graph.get_cards()[0]["cardid"])

        models.CardXNodeXWidget.objects.create(
            config={
                "defaultValue": {
                    "en": {"value": "Overridden Default Value", "direction": "ltr"},
                }
            },
            card=card,
            node_id=node_to_add.nodeid,
            widget=models.Widget.objects.first(),
            label="Widget name",
        )

        self.test_graph.promote_draft_graph_to_active_graph()
        self.test_graph.publish()

        updated_published_graph = models.PublishedGraph.objects.get(
            publication=self.test_graph.publication,
            language="en",
        )

        update_resource_instance_data_based_on_graph_diff(
            initial_graph=original_published_graph.serialized_graph,
            updated_graph=updated_published_graph.serialized_graph,
            user_id=self.user.pk,
        )

        tile.refresh_from_db()

        self.assertDictEqual(
            tile.data[str(self.string_node_id)],
            {"en": {"value": "test value", "direction": "ltr"}},
        )

        widget_defaults = {
            widget["node_id"]: widget["config"]["defaultValue"]
            for widget in updated_published_graph.serialized_graph[
                "cards_x_nodes_x_widgets"
            ]
        }

        self.assertEqual(
            tile.data[new_node_id],
            widget_defaults[new_node_id],
        )

    @patch("arches.app.tasks.notify_completion")
    def test_updates_defaults(self, mock_notify):
        models.CardXNodeXWidget.objects.create(
            config={
                "defaultValue": {
                    "en": {"value": "Default Value", "direction": "ltr"},
                },
            },
            card=models.CardModel.objects.get(pk=self.test_graph.get_cards()[0].cardid),
            node_id=self.string_node_id,
            widget=models.Widget.objects.first(),
            label="Widget name",
        )

        self.test_graph.refresh_from_database()
        self.test_graph.save(validate=False)
        self.test_graph.publish()

        original_published_graph = models.PublishedGraph.objects.get(
            publication=self.test_graph.publication,
            language="en",
        )

        resource_instance = models.ResourceInstance.objects.create(
            graph=self.test_graph
        )
        tile = models.TileModel.objects.create(
            resourceinstance=resource_instance,
            nodegroup_id=self.test_graph.get_nodegroups()[0].nodegroupid,
            data={
                str(self.string_node_id): {
                    "en": {"value": "Default Value", "direction": "ltr"},
                },
            },
            sortorder=0,
        )

        self.assertDictEqual(
            tile.data[str(self.string_node_id)],
            {"en": {"value": "Default Value", "direction": "ltr"}},
        )

        draft_graph = self.test_graph.create_draft_graph()

        models.CardXNodeXWidget.objects.filter(
            node_id=models.Node.objects.get(
                source_identifier_id=self.string_node_id
            ).nodeid,
        ).update(
            config={
                "defaultValue": {
                    "en": {"value": "Overridden Default Value", "direction": "ltr"},
                },
            }
        )

        draft_graph.refresh_from_database()

        self.test_graph.promote_draft_graph_to_active_graph()
        self.test_graph.publish()

        updated_published_graph = models.PublishedGraph.objects.get(
            publication=self.test_graph.publication,
            language="en",
        )

        update_resource_instance_data_based_on_graph_diff(
            initial_graph=original_published_graph.serialized_graph,
            updated_graph=updated_published_graph.serialized_graph,
            user_id=self.user.pk,
        )

        tile.refresh_from_db()

        self.assertDictEqual(
            tile.data[str(self.string_node_id)],
            {"en": {"value": "Overridden Default Value", "direction": "ltr"}},
        )

    @patch("arches.app.tasks.notify_completion")
    def test_deletes_tiles_when_nodegroup_is_deleted(self, mock_notify):
        original_published_graph = models.PublishedGraph.objects.get(
            publication=self.test_graph.publication,
            language="en",
        )

        resource_instance = models.ResourceInstance.objects.create(
            graph=self.test_graph
        )

        nodegroup_id = self.test_graph.get_nodegroups()[0].nodegroupid
        tile = models.TileModel.objects.create(
            resourceinstance=resource_instance,
            nodegroup_id=nodegroup_id,
            data={
                str(self.string_node_id): {
                    "en": {"value": "Default Value", "direction": "ltr"},
                }
            },
            sortorder=0,
        )

        self.assertDictEqual(
            tile.data[str(self.string_node_id)],
            {"en": {"value": "Default Value", "direction": "ltr"}},
        )

        draft_graph = self.test_graph.create_draft_graph()

        node_to_delete = models.Node.objects.get(
            source_identifier_id=self.string_node_id
        )
        draft_graph.delete_node(node_to_delete)

        self.test_graph.promote_draft_graph_to_active_graph()
        self.test_graph.publish()

        updated_published_graph = models.PublishedGraph.objects.get(
            publication=self.test_graph.publication,
            language="en",
        )

        update_resource_instance_data_based_on_graph_diff(
            initial_graph=original_published_graph.serialized_graph,
            updated_graph=updated_published_graph.serialized_graph,
            user_id=self.user.pk,
        )

        with self.assertRaises(models.TileModel.DoesNotExist):
            models.TileModel.objects.get(
                resourceinstance=resource_instance,
                nodegroup_id=nodegroup_id,
            )
