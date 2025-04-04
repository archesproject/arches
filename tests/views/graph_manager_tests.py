"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import json
from http import HTTPStatus

from tests import test_settings
from arches.app.models.system_settings import settings
from tests.base_test import ArchesTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from urllib.parse import urlencode
from arches.app.models.graph import Graph
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

# these tests can be run from the command line via
# python manage.py test tests.views.graph_manager_tests --settings="tests.test_settings"


class GraphManagerViewTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.NODE_NODETYPE_GRAPHID = "22000000-0000-0000-0000-000000000001"

        cls.create_node_node_type_graph()
        cls.create_test_graph()

        cls.appended_branch_1 = cls.test_graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            graphid=cls.NODE_NODETYPE_GRAPHID,
        )
        cls.appended_branch_2 = cls.test_graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            graphid=cls.NODE_NODETYPE_GRAPHID,
        )

        cls.test_graph.save()
        cls.test_graph.publish()
        cls.test_graph.create_draft_graph()

        cls.ROOT_ID = cls.test_graph.root.nodeid
        cls.GRAPH_ID = str(cls.test_graph.pk)
        cls.NODE_COUNT = 5

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
            "ontology_id": "e6e8db47-2ccf-11e6-927e-b8f6b115d7dd",
            "subtitle": "Represents a node and node type pairing",
            "version": "v1",
        }
        graph_model = models.models.GraphModel.objects.create(**graph_data)

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
        models.models.Edge.objects.create(**edge_data).save()

        graph = Graph.objects.get(pk=graph_model.pk)
        graph.save()
        graph.publish()

    @classmethod
    def create_test_graph(cls):
        test_graph = Graph.objects.create_graph()
        test_graph.name = "TEST GRAPH"
        test_graph.subtitle = "ARCHES TEST GRAPH"
        test_graph.author = "Arches"
        test_graph.description = "ARCHES TEST GRAPH"
        test_graph.ontology_id = "e6e8db47-2ccf-11e6-927e-b8f6b115d7dd"
        test_graph.version = "v1.0.0"
        test_graph.iconclass = "fa fa-building"
        test_graph.nodegroups = []
        test_graph.root.ontologyclass = (
            "http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity"
        )
        test_graph.root.name = "ROOT NODE"
        test_graph.root.description = "Test Root Node"
        test_graph.root.datatype = "semantic"
        test_graph.root.save()

        test_graph.save()
        test_graph.publish()

        cls.test_graph = test_graph
        cls.rootNode = test_graph.root

    def test_graph_manager(self):
        """
        Test the graph manager view

        """
        self.client.login(username="admin", password="admin")
        url = reverse("graph", kwargs={"graphid": ""})
        response = self.client.get(url)
        graphs = json.loads(response.context["graphs"])
        self.assertEqual(
            len(graphs),
            models.GraphModel.objects.all()
            .exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .count(),
        )

        url = reverse("graph_designer", kwargs={"graphid": self.GRAPH_ID})
        response = self.client.get(url)
        graph = json.loads(response.context["graph_json"])

        node_count = len(graph["nodes"])
        self.assertEqual(node_count, self.NODE_COUNT)

        edge_count = len(graph["edges"])
        self.assertEqual(edge_count, self.NODE_COUNT - 1)

    def test_graph_manager_redirects_future_graph(self):
        self.client.login(username="admin", password="admin")

        draft_graph = Graph.objects.get(source_identifier_id=self.GRAPH_ID)
        url = reverse("graph_designer", kwargs={"graphid": draft_graph.graphid})
        response = self.client.get(url)

        redirect_url = reverse("graph_designer", kwargs={"graphid": self.GRAPH_ID})
        query_string = urlencode({"has_been_redirected_from_draft_graph": True})

        self.assertRedirects(response, "{}?{}".format(redirect_url, query_string))

    def test_graph_settings(self):
        """
        Test the graph settings view
        """
        self.client.login(username="admin", password="admin")
        url = reverse("graph_settings", kwargs={"graphid": self.GRAPH_ID})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        graph = json.loads(response.content)

        graph["name"] = "new graph name"
        graph["root"] = {"datatype": "semantic", "config": None}
        graph["nodegroups"] = []
        post_data = {"graph": graph, "relatable_resource_ids": [str(self.ROOT_ID)]}
        post_data = JSONSerializer().serialize(post_data)
        content_type = "application/x-www-form-urlencoded"
        response = self.client.post(url, post_data, content_type)
        response_json = json.loads(response.content)

        self.assertTrue(response_json["success"])
        self.assertEqual(response_json["graph"]["name"], "new graph name")
        self.assertTrue(str(self.ROOT_ID) in response_json["relatable_resource_ids"])

    def test_node_update(self):
        """
        Test updating a node (HERITAGE_RESOURCE_PLACE) via node view

        """
        self.client.login(username="admin", password="admin")
        url = reverse("update_node", kwargs={"graphid": self.GRAPH_ID})
        node = models.Node.objects.get(nodeid=str(self.appended_branch_1.root.pk))
        node.name = "new node name"
        nodegroup, created = models.NodeGroup.objects.get_or_create(
            pk=str(self.appended_branch_1.root.pk)
        )
        node.nodegroup = nodegroup
        post_data = JSONSerializer().serializeToPython(node)
        post_data["parentproperty"] = (
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as"
        )
        content_type = "application/x-www-form-urlencoded"
        response = self.client.post(
            url, JSONSerializer().serialize(post_data), content_type
        )
        response_json = json.loads(response.content)

        node_count = 0
        for node in response_json["nodes"]:
            if node["nodeid"] == str(self.appended_branch_1.root.pk):
                self.assertEqual(node["name"], "new node name")
            if node["nodegroup_id"] == str(self.appended_branch_1.root.pk):
                node_count = node_count + 1
        self.assertEqual(node_count, 2)

        node_ = models.Node.objects.get(nodeid=str(self.appended_branch_1.root.pk))

        self.assertEqual(node_.name, "new node name")
        self.assertTrue(node_.is_collector)

    def test_node_delete(self):
        """
        Test delete a node (HERITAGE_RESOURCE_PLACE) via node view

        """
        self.client.login(username="admin", password="admin")
        node = models.Node.objects.get(nodeid=str(self.appended_branch_1.root.pk))
        url = reverse("delete_node", kwargs={"graphid": self.GRAPH_ID})
        post_data = JSONSerializer().serialize({"nodeid": node.nodeid})
        response = self.client.delete(url, post_data)
        self.assertEqual(response.status_code, 200)

        graph = Graph.objects.get(graphid=self.GRAPH_ID).serialize()
        self.assertEqual(len(graph["nodes"]), 3)
        self.assertEqual(len(graph["edges"]), 2)

    def test_update_node_malicious_config_key(self):
        self.client.login(username="admin", password="admin")
        url = reverse("update_node", kwargs={"graphid": self.GRAPH_ID})
        node = models.Node.objects.get(nodeid=self.appended_branch_1.root.pk)
        nodegroup, _created = models.NodeGroup.objects.get_or_create(
            pk=self.appended_branch_1.root.pk
        )
        node.nodegroup = nodegroup
        node.config = {
            "placeholder": {"en": "Enter text"},
            "i18n_properties": ["placeholder"],
            "malicious'": None,
        }
        data = JSONSerializer().serializeToPython(node)
        data["parentproperty"] = "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as"

        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(url, data, content_type="application/json")
        self.assertContains(
            response,
            "aliases cannot contain",
            # TODO: should become BAD_REQUEST eventually
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    def test_graph_clone_on_unpublished_graph(self):
        """
        Test clone a graph (HERITAGE_RESOURCE) via view

        """
        self.client.login(username="admin", password="admin")
        url = reverse("clone_graph", kwargs={"graphid": self.GRAPH_ID})
        post_data = {}
        content_type = "application/x-www-form-urlencoded"
        response = self.client.post(url, post_data, content_type)
        response_json = json.loads(response.content)

        self.assertEqual(len(response_json["nodes"]), self.NODE_COUNT)

        cloned_graph = Graph.objects.get(pk=response_json["graphid"])

        original_graph_node_ids = [
            str(node.pk) for node in self.test_graph.nodes.values()
        ]
        cloned_graph_node_ids = [str(node.pk) for node in cloned_graph.nodes.values()]

        self.assertFalse(set(original_graph_node_ids) & set(cloned_graph_node_ids))

    def test_graph_clone_on_published_graph(self):
        """
        Test clone a graph (HERITAGE_RESOURCE) via view

        """
        self.client.login(username="admin", password="admin")

        user_id = self.client.session["_auth_user_id"]
        logged_in_user = get_user_model().objects.get(pk=user_id)
        self.test_graph.publish(user=logged_in_user)

        url = reverse("clone_graph", kwargs={"graphid": self.GRAPH_ID})
        post_data = {}
        content_type = "application/x-www-form-urlencoded"
        response = self.client.post(url, post_data, content_type)
        response_json = json.loads(response.content)

        self.assertEqual(len(response_json["nodes"]), self.NODE_COUNT)

        cloned_graph = Graph.objects.get(pk=response_json["graphid"])

        original_graph_node_ids = [
            str(node.pk) for node in self.test_graph.nodes.values()
        ]
        cloned_graph_node_ids = [str(node.pk) for node in cloned_graph.nodes.values()]

        self.assertFalse(set(original_graph_node_ids) & set(cloned_graph_node_ids))

    def test_new_graph(self):
        """
        Test creating a new graph via the view

        """
        self.client.login(username="admin", password="admin")
        url = reverse("new_graph")
        post_data = JSONSerializer().serialize({"isresource": False})
        content_type = "application/x-www-form-urlencoded"
        response = self.client.post(url, post_data, content_type)
        response_json = json.loads(response.content)
        self.assertEqual(len(response_json["nodes"]), 1)
        self.assertFalse(response_json["isresource"])

    def test_delete_graph(self):
        """
        test the graph delete method

        """
        self.client.login(username="admin", password="admin")
        url = reverse("delete_graph", kwargs={"graphid": self.GRAPH_ID})
        response = self.client.delete(url)

        node_count = models.Node.objects.filter(graph_id=self.GRAPH_ID).count()
        edge_count = models.Edge.objects.filter(graph_id=self.GRAPH_ID).count()
        self.assertEqual(node_count, 0)
        self.assertEqual(edge_count, 0)

    def test_branch_export_on_unpublished_graph(self):
        self.client.login(username="admin", password="admin")
        url = reverse("export_branch", kwargs={"graphid": self.GRAPH_ID})
        node = [value for value in self.test_graph.nodes.values()][1]
        post_data = JSONSerializer().serialize(node)
        content_type = "application/x-www-form-urlencoded"

        response = self.client.post(url, post_data, content_type)

        exported_branch = Graph.objects.get(pk=response.json()["graphid"])

        original_graph_node_ids = [
            str(node.pk) for node in self.test_graph.nodes.values()
        ]
        export_branch_node_ids = [
            str(node.pk) for node in exported_branch.nodes.values()
        ]

        self.assertFalse(set(original_graph_node_ids) & set(export_branch_node_ids))

    def test_branch_export_on_published_graph(self):
        self.client.login(username="admin", password="admin")

        user_id = self.client.session["_auth_user_id"]
        logged_in_user = get_user_model().objects.get(pk=user_id)
        self.test_graph.publish(user=logged_in_user)

        url = reverse("export_branch", kwargs={"graphid": self.GRAPH_ID})
        node = [value for value in self.test_graph.nodes.values()][1]
        post_data = JSONSerializer().serialize(node)
        content_type = "application/x-www-form-urlencoded"

        response = self.client.post(url, post_data, content_type)

        exported_branch = Graph.objects.get(pk=response.json()["graphid"])

        original_graph_node_ids = [
            str(node.pk) for node in self.test_graph.nodes.values()
        ]
        export_branch_node_ids = [
            str(node.pk) for node in exported_branch.nodes.values()
        ]

        self.assertFalse(set(original_graph_node_ids) & set(export_branch_node_ids))

    def test_graph_export(self):
        """
        test graph export method

        """

        self.client.login(username="admin", password="admin")
        url = reverse("export_graph", kwargs={"graphid": self.GRAPH_ID})
        response = self.client.get(url)
        graph_json = json.loads(response._container[0])
        node_count = len(graph_json["graph"][0]["nodes"])
        self.assertTrue(response._container[0])
        self.assertEqual(node_count, self.NODE_COUNT)
        self.assertEqual(response.headers["content-type"], "json/plain")

    def test_graph_import(self):
        """
        test graph import method

        """

        self.client.login(username="admin", password="admin")
        url = reverse("import_graph")
        with open(
            os.path.join(
                list(test_settings.RESOURCE_GRAPH_LOCATIONS)[0],
                "Cardinality Test Model.json",
            )
        ) as f:
            response = self.client.post(url, {"importedGraph": f})
        self.assertIsNotNone(response.content)

        # Note: If you change the imported_json array to make this test work you should also change the expected
        # response in the import_graph method in arches.app.media.js.views.graph.js
        imported_json = JSONDeserializer().deserialize(response.content)
        self.assertEqual(imported_json[0], [])
        self.assertEqual(imported_json[1]["graphs_saved"], 1)
        self.assertEqual(imported_json[1]["name"], "Cardinality Test Model")
