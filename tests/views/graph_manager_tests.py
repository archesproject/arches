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
from tests import test_settings
from arches.app.models.system_settings import settings
from tests.base_test import ArchesTestCase
from django.test import Client
from django.core import management
from django.urls import reverse
from arches.app.models.graph import Graph
from arches.app.models.models import Node, NodeGroup, GraphModel, CardModel, Edge
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

# these tests can be run from the command line via
# python manage.py test tests/views/graph_manager_tests.py --pattern="*.py" --settings="tests.test_settings"


class GraphManagerViewTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        cls.loadOntology()

    def setUp(self):
        self.NODE_NODETYPE_GRAPHID = "22000000-0000-0000-0000-000000000001"

        if len(Graph.objects.filter(graphid=self.NODE_NODETYPE_GRAPHID)) == 0:
            # Node Branch
            graph_dict = {
                "author": "Arches",
                "color": None,
                "deploymentdate": None,
                "deploymentfile": None,
                "description": "Represents a single node in a graph",
                "graphid": "22000000-0000-0000-0000-000000000000",
                "iconclass": "fa fa-circle",
                "isactive": True,
                "isresource": False,
                "name": "Node",
                "ontology_id": "e6e8db47-2ccf-11e6-927e-b8f6b115d7dd",
                "subtitle": "Represents a single node in a graph.",
                "version": "v1",
            }
            GraphModel.objects.create(**graph_dict).save()

            node_dict = {
                "config": None,
                "datatype": "semantic",
                "description": "Represents a single node in a graph",
                "graph_id": "22000000-0000-0000-0000-000000000000",
                "isrequired": False,
                "issearchable": True,
                "istopnode": True,
                "name": "Node",
                "nodegroup_id": None,
                "nodeid": "20000000-0000-0000-0000-100000000000",
                "ontologyclass": "http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity",
            }
            Node.objects.create(**node_dict).save()

            # Node/Node Type Branch
            graph_dict = {
                "author": "Arches",
                "color": None,
                "deploymentdate": None,
                "deploymentfile": None,
                "description": "Represents a node and node type pairing",
                "graphid": "22000000-0000-0000-0000-000000000001",
                "iconclass": "fa fa-angle-double-down",
                "isactive": True,
                "isresource": False,
                "name": "Node/Node Type",
                "ontology_id": "e6e8db47-2ccf-11e6-927e-b8f6b115d7dd",
                "subtitle": "Represents a node and node type pairing",
                "version": "v1",
            }
            GraphModel.objects.create(**graph_dict).save()

            nodegroup_dict = {
                "cardinality": "n",
                "legacygroupid": "",
                "nodegroupid": "20000000-0000-0000-0000-100000000001",
                "parentnodegroup_id": None,
            }
            NodeGroup.objects.create(**nodegroup_dict).save()

            card_dict = {
                "active": True,
                "cardid": "bf9ea150-3eaa-11e8-8b2b-c3a348661f61",
                "description": "Represents a node and node type pairing",
                "graph_id": "22000000-0000-0000-0000-000000000001",
                "helpenabled": False,
                "helptext": None,
                "helptitle": None,
                "instructions": "",
                "name": "Node/Node Type",
                "nodegroup_id": "20000000-0000-0000-0000-100000000001",
                "sortorder": None,
                "visible": True,
            }
            CardModel.objects.create(**card_dict).save()

            nodes = [
                {
                    "config": None,
                    "datatype": "string",
                    "description": "",
                    "graph_id": "22000000-0000-0000-0000-000000000001",
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
                    "graph_id": "22000000-0000-0000-0000-000000000001",
                    "isrequired": False,
                    "issearchable": True,
                    "istopnode": False,
                    "name": "Node Type",
                    "nodegroup_id": "20000000-0000-0000-0000-100000000001",
                    "nodeid": "20000000-0000-0000-0000-100000000002",
                    "ontologyclass": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                },
            ]

            for node in nodes:
                Node.objects.create(**node).save()

            edges_dict = {
                "description": None,
                "domainnode_id": "20000000-0000-0000-0000-100000000001",
                "edgeid": "22200000-0000-0000-0000-000000000001",
                "graph_id": "22000000-0000-0000-0000-000000000001",
                "name": None,
                "ontologyproperty": "http://www.cidoc-crm.org/cidoc-crm/P2_has_type",
                "rangenode_id": "20000000-0000-0000-0000-100000000002",
            }
            Edge.objects.create(**edges_dict).save()

        graph = Graph.new()
        graph.name = "TEST GRAPH"
        graph.subtitle = "ARCHES TEST GRAPH"
        graph.author = "Arches"
        graph.description = "ARCHES TEST GRAPH"
        graph.ontology_id = "e6e8db47-2ccf-11e6-927e-b8f6b115d7dd"
        graph.version = "v1.0.0"
        graph.isactive = False
        graph.iconclass = "fa fa-building"
        graph.nodegroups = []
        graph.save()

        graph.root.name = "ROOT NODE"
        graph.root.description = "Test Root Node"
        graph.root.ontologyclass = "http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity"
        graph.root.datatype = "semantic"
        graph.root.save()
        graph = Graph.objects.get(graphid=graph.pk)
        self.appended_branch_1 = graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as", graphid=self.NODE_NODETYPE_GRAPHID
        )
        self.appended_branch_2 = graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as", graphid=self.NODE_NODETYPE_GRAPHID
        )
        graph.save()

        self.ROOT_ID = graph.root.nodeid
        self.GRAPH_ID = str(graph.pk)
        self.NODE_COUNT = 5

        self.client = Client()

    def tearDown(self):
        try:
            self.deleteGraph(self.GRAPH_ID)
        except:
            pass

    def test_graph_manager(self):
        """
        Test the graph manager view

        """
        self.client.login(username="admin", password="admin")
        url = reverse("graph", kwargs={"graphid": ""})
        response = self.client.get(url)
        graphs = json.loads(response.context["graphs"])
        self.assertEqual(len(graphs), GraphModel.objects.all().exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).count())

        url = reverse("graph_designer", kwargs={"graphid": self.GRAPH_ID})
        response = self.client.get(url)
        graph = json.loads(response.context["graph_json"])

        node_count = len(graph["nodes"])
        self.assertEqual(node_count, self.NODE_COUNT)

        edge_count = len(graph["edges"])
        self.assertEqual(edge_count, self.NODE_COUNT - 1)

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
        node = Node.objects.get(nodeid=str(self.appended_branch_1.root.pk))
        node.name = "new node name"
        nodegroup, created = NodeGroup.objects.get_or_create(pk=str(self.appended_branch_1.root.pk))
        node.nodegroup = nodegroup
        post_data = JSONSerializer().serializeToPython(node)
        post_data["parentproperty"] = "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as"
        content_type = "application/x-www-form-urlencoded"
        response = self.client.post(url, JSONSerializer().serialize(post_data), content_type)
        response_json = json.loads(response.content)

        node_count = 0
        for node in response_json["nodes"]:
            if node["nodeid"] == str(self.appended_branch_1.root.pk):
                self.assertEqual(node["name"], "new node name")
            if node["nodegroup_id"] == str(self.appended_branch_1.root.pk):
                node_count = node_count + 1
        self.assertEqual(node_count, 2)

        node_ = Node.objects.get(nodeid=str(self.appended_branch_1.root.pk))

        self.assertEqual(node_.name, "new node name")
        self.assertTrue(node_.is_collector)

    def test_node_delete(self):
        """
        Test delete a node (HERITAGE_RESOURCE_PLACE) via node view

        """
        self.client.login(username="admin", password="admin")
        node = Node.objects.get(nodeid=str(self.appended_branch_1.root.pk))
        url = reverse("delete_node", kwargs={"graphid": self.GRAPH_ID})
        post_data = JSONSerializer().serialize({"nodeid": node.nodeid})
        response = self.client.delete(url, post_data)
        self.assertEqual(response.status_code, 200)

        graph = Graph.objects.get(graphid=self.GRAPH_ID).serialize()
        self.assertEqual(len(graph["nodes"]), 3)
        self.assertEqual(len(graph["edges"]), 2)

    def test_graph_clone(self):
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

        node_count = Node.objects.filter(graph_id=self.GRAPH_ID).count()
        edge_count = Edge.objects.filter(graph_id=self.GRAPH_ID).count()
        self.assertEqual(node_count, 0)
        self.assertEqual(edge_count, 0)

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
        self.assertEqual(list(response._headers["content-type"])[1], "json/plain")

    def test_graph_import(self):
        """
        test graph import method

        """

        self.client.login(username="admin", password="admin")
        url = reverse("import_graph")
        with open(os.path.join(list(test_settings.RESOURCE_GRAPH_LOCATIONS)[0], "Cardinality Test Model.json")) as f:
            response = self.client.post(url, {"importedGraph": f})
        self.assertIsNotNone(response.content)

        # Note: If you change the imported_json array to make this test work you should also change the expected
        # response in the import_graph method in arches.app.media.js.views.graph.js
        imported_json = JSONDeserializer().deserialize(response.content)
        self.assertEqual(imported_json[0], [])
        self.assertEqual(imported_json[1]["graphs_saved"], 1)
        self.assertEqual(imported_json[1]["name"], "Cardinality Test Model")
