from arches.app.models import models
from arches.app.models.graph import Graph

from tests.base_test import ArchesTestCase


class GraphHasUnpublishedChangesSignalTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.SINGLE_NODE_GRAPHID = "22000000-0000-0000-0000-000000000000"
        cls.NODE_NODETYPE_GRAPHID = "22000000-0000-0000-0000-000000000001"
        cls.create_single_node_graph()
        cls.create_node_node_type_graph()
        cls.create_test_graph()

    @classmethod
    def create_single_node_graph(cls):
        graph_data = {
            "author": "Arches",
            "color": None,
            "deploymentdate": None,
            "deploymentfile": None,
            "description": "Represents a single node in a graph",
            "graphid": cls.SINGLE_NODE_GRAPHID,
            "iconclass": "fa fa-circle",
            "isresource": False,
            "name": "Node",
            "slug": "node",
            "ontology_id": "e6e8db47-2ccf-11e6-927e-b8f6b115d7dd",
            "subtitle": "Represents a single node in a graph.",
            "version": "v1",
        }
        graph_model = models.GraphModel.objects.create(**graph_data)

        node_data = {
            "config": None,
            "datatype": "semantic",
            "description": "Represents a single node in a graph",
            "graph_id": cls.SINGLE_NODE_GRAPHID,
            "isrequired": False,
            "issearchable": True,
            "istopnode": True,
            "name": "Single Node",
            "nodegroup_id": None,
            "nodeid": "20000000-0000-0000-0000-100000000000",
            "ontologyclass": "http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity",
        }
        models.Node.objects.create(**node_data).save()

        graph = Graph.objects.get(pk=graph_model.pk)
        graph.save()
        graph.publish()

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
            "slug": "node_type",
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

        models.CardModel.objects.create(**card_data).save()
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

        for node in nodes_data:
            models.Node.objects.create(**node).save()

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

    @classmethod
    def create_test_graph(cls):
        test_graph = Graph.objects.create_graph()
        draft_graph = test_graph.get_draft_graph()

        draft_graph.name = "TEST GRAPH"
        draft_graph.subtitle = "ARCHES TEST GRAPH"
        draft_graph.author = "Arches"
        draft_graph.description = "ARCHES TEST GRAPH"
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

        draft_graph.save()

        test_graph.promote_draft_graph_to_active_graph()
        test_graph.publish()

        cls.test_graph = test_graph
        cls.rootNode = test_graph.root

    def test_card_save_signal(self):
        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_card = [card for card in self.test_graph.cards.values()][0]
        test_card.save()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_card_delete_signal(self):
        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_card = [card for card in self.test_graph.cards.values()][0]
        test_card.delete()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_card_model_save_signal(self):
        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_card = [card for card in self.test_graph.cards.values()][0]

        test_card_model = models.CardModel.objects.get(pk=test_card.pk)
        test_card_model.save()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_card_model_delete_signal(self):
        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_card = [card for card in self.test_graph.cards.values()][0]

        test_card_model = models.CardModel.objects.get(pk=test_card.pk)
        test_card_model.delete()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_node_save_signal(self):
        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_node = [node for node in self.test_graph.nodes.values()][0]
        test_node.save()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_node_delete_signal(self):
        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_node = [node for node in self.test_graph.nodes.values()][0]
        test_node.delete()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_edge_save_signal(self):
        self.test_graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        self.test_graph.save()
        self.test_graph.publish()

        self.test_graph.refresh_from_db()
        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_edge = [edge for edge in self.test_graph.edges.values()][0]
        test_edge.save()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_edge_delete_signal(self):
        self.test_graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        self.test_graph.save()
        self.test_graph.publish()

        self.test_graph.refresh_from_db()
        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_edge = [edge for edge in self.test_graph.edges.values()][0]
        test_edge.delete()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_function_x_graph_save_signal(self):
        models.FunctionXGraph.objects.create(
            graph=self.test_graph,
            function_id="60000000-0000-0000-0000-000000000001",
            config={
                "descriptor_types": {
                    "name": {
                        "nodegroup_id": None,
                        "string_template": "<String Node> <Resource Node>",
                    },
                    "map_popup": {
                        "nodegroup_id": None,
                        "string_template": "",
                    },
                    "description": {
                        "nodegroup_id": None,
                        "string_template": "",
                    },
                },
            },
        )

        self.assertFalse(self.test_graph.has_unpublished_changes)

        function_x_graph = models.FunctionXGraph.objects.get(
            function_id="60000000-0000-0000-0000-000000000001"
        )
        function_x_graph.save()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_function_x_graph_delete_signal(self):
        models.FunctionXGraph.objects.create(
            graph=self.test_graph,
            function_id="60000000-0000-0000-0000-000000000001",
            config={
                "descriptor_types": {
                    "name": {
                        "nodegroup_id": None,
                        "string_template": "<String Node> <Resource Node>",
                    },
                    "map_popup": {
                        "nodegroup_id": None,
                        "string_template": "",
                    },
                    "description": {
                        "nodegroup_id": None,
                        "string_template": "",
                    },
                },
            },
        )

        self.assertFalse(self.test_graph.has_unpublished_changes)

        function_x_graph = models.FunctionXGraph.objects.get(
            function_id="60000000-0000-0000-0000-000000000001"
        )
        function_x_graph.delete()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_graph_x_published_graph_save_signal(self):
        self.assertFalse(self.test_graph.has_unpublished_changes)

        self.test_graph.publication.save()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_graph_x_published_graph_delete_signal(self):
        self.assertFalse(self.test_graph.has_unpublished_changes)

        self.test_graph.publication.delete()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_nodegroup_save_signal(self):
        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_node = [node for node in self.test_graph.nodes.values()][0]

        test_node.nodegroup.save()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_nodegroup_delete_signal(self):
        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_node = [node for node in self.test_graph.nodes.values()][0]

        test_node.nodegroup.delete()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_card_x_node_x_widget_save_signal(self):
        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_card = [card for card in self.test_graph.cards.values()][0]

        models.CardXNodeXWidget.objects.create(
            card=test_card,
            node_id=test_card.nodegroup_id,
            widget=models.Widget.objects.first(),
            label="Widget name",
        )

        self.test_graph.publish()
        self.test_graph.refresh_from_db()

        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_card_x_node_x_widget = [
            card_x_node_x_widget
            for card_x_node_x_widget in self.test_graph.widgets.values()
        ][0]
        test_card_x_node_x_widget.save()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)

    def test_card_x_node_x_widget_delete_signal(self):
        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_card = [card for card in self.test_graph.cards.values()][0]

        models.CardXNodeXWidget.objects.create(
            card=test_card,
            node_id=test_card.nodegroup_id,
            widget=models.Widget.objects.first(),
            label="Widget name",
        )

        self.test_graph.publish()
        self.test_graph.refresh_from_db()

        self.assertFalse(self.test_graph.has_unpublished_changes)

        test_card_x_node_x_widget = [
            card_x_node_x_widget
            for card_x_node_x_widget in self.test_graph.widgets.values()
        ][0]
        test_card_x_node_x_widget.delete()

        self.test_graph.refresh_from_db()
        self.assertTrue(self.test_graph.has_unpublished_changes)
