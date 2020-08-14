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

import os, json, uuid
from django.core import management
from tests import test_settings
from tests.base_test import ArchesTestCase
from arches.app.models import models
from arches.app.models.graph import Graph, GraphValidationError
from arches.app.models.card import Card
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

# these tests can be run from the command line via
# python manage.py test tests/models/graph_tests.py --pattern="*.py" --settings="tests.test_settings"


class GraphTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        cls.loadOntology()

        for path in test_settings.RESOURCE_GRAPH_LOCATIONS:
            management.call_command("packages", operation="import_graphs", source=path)

        cls.NODE_NODETYPE_GRAPHID = "22000000-0000-0000-0000-000000000001"
        cls.SINGLE_NODE_GRAPHID = "22000000-0000-0000-0000-000000000000"

        # Node Branch
        graph_dict = {
            "author": "Arches",
            "color": None,
            "deploymentdate": None,
            "deploymentfile": None,
            "description": "Represents a single node in a graph",
            "graphid": cls.SINGLE_NODE_GRAPHID,
            "iconclass": "fa fa-circle",
            "isactive": True,
            "isresource": False,
            "name": "Node",
            "ontology_id": "e6e8db47-2ccf-11e6-927e-b8f6b115d7dd",
            "subtitle": "Represents a single node in a graph.",
            "version": "v1",
        }
        models.GraphModel.objects.create(**graph_dict).save()

        node_dict = {
            "config": None,
            "datatype": "semantic",
            "description": "Represents a single node in a graph",
            "graph_id": cls.SINGLE_NODE_GRAPHID,
            "isrequired": False,
            "issearchable": True,
            "istopnode": True,
            "name": "Node",
            "nodegroup_id": None,
            "nodeid": "20000000-0000-0000-0000-100000000000",
            "ontologyclass": "http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity",
        }
        models.Node.objects.create(**node_dict).save()

        # Node/Node Type Branch
        graph_dict = {
            "author": "Arches",
            "color": None,
            "deploymentdate": None,
            "deploymentfile": None,
            "description": "Represents a node and node type pairing",
            "graphid": cls.NODE_NODETYPE_GRAPHID,
            "iconclass": "fa fa-angle-double-down",
            "isactive": True,
            "isresource": False,
            "name": "Node/Node Type",
            "ontology_id": "e6e8db47-2ccf-11e6-927e-b8f6b115d7dd",
            "subtitle": "Represents a node and node type pairing",
            "version": "v1",
        }
        models.GraphModel.objects.create(**graph_dict).save()

        nodegroup_dict = {
            "cardinality": "n",
            "legacygroupid": "",
            "nodegroupid": "20000000-0000-0000-0000-100000000001",
            "parentnodegroup_id": None,
        }
        models.NodeGroup.objects.create(**nodegroup_dict).save()

        card_dict = {
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
        models.CardModel.objects.create(**card_dict).save()

        nodes = [
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

        for node in nodes:
            models.Node.objects.create(**node).save()

        edges_dict = {
            "description": None,
            "domainnode_id": "20000000-0000-0000-0000-100000000001",
            "edgeid": "22200000-0000-0000-0000-000000000001",
            "graph_id": cls.NODE_NODETYPE_GRAPHID,
            "name": None,
            "ontologyproperty": "http://www.cidoc-crm.org/cidoc-crm/P2_has_type",
            "rangenode_id": "20000000-0000-0000-0000-100000000002",
        }
        models.Edge.objects.create(**edges_dict).save()

    @classmethod
    def tearDownClass(cls):
        cls.deleteGraph("2f7f8e40-adbc-11e6-ac7f-14109fd34195")

    def setUp(self):
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

        self.rootNode = graph.root

    def tearDown(self):
        self.deleteGraph(self.rootNode.graph_id)

    def test_new_graph(self):
        name = "TEST NEW GRAPH"
        author = "ARCHES TEST"
        graph = Graph.new(name=name, is_resource=True, author=author)
        self.assertEqual(graph.name, name)
        self.assertEqual(graph.author, author)
        self.assertTrue(graph.isresource)
        self.assertFalse(graph.root.is_collector)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(len(graph.cards), 0)
        self.assertEqual(len(graph.get_nodegroups()), 0)

        graph = Graph.new(name=name, is_resource=False, author=author)
        self.assertEqual(graph.name, name)
        self.assertEqual(graph.author, author)
        self.assertFalse(graph.isresource)
        self.assertTrue(graph.root.is_collector)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(len(graph.cards), 1)
        self.assertEqual(len(graph.get_nodegroups()), 1)

    def test_graph_doesnt_pollute_db(self):
        """
        test that the mere act of creating a Graph instance doesn't save anything to the database

        """

        graph_obj = {
            "name": "TEST GRAPH",
            "subtitle": "ARCHES TEST GRAPH",
            "author": "Arches",
            "description": "ARCHES TEST GRAPH",
            "version": "v1.0.0",
            "isresource": True,
            "isactive": False,
            "iconclass": "fa fa-building",
            "nodegroups": [],
            "nodes": [
                {
                    "status": None,
                    "description": "",
                    "name": "ROOT_NODE",
                    "istopnode": True,
                    "ontologyclass": "",
                    "nodeid": "55555555-343e-4af3-8857-f7322dc9eb4b",
                    "nodegroup_id": "",
                    "datatype": "semantic",
                },
                {
                    "status": None,
                    "description": "",
                    "name": "NODE_NAME",
                    "istopnode": False,
                    "ontologyclass": "",
                    "nodeid": "66666666-24c9-4226-bde2-2c40ee60a26c",
                    "nodegroup_id": "66666666-24c9-4226-bde2-2c40ee60a26c",
                    "datatype": "string",
                },
            ],
            "edges": [
                {
                    "rangenode_id": "66666666-24c9-4226-bde2-2c40ee60a26c",
                    "name": "",
                    "edgeid": "11111111-d50f-11e5-8754-80e6500ee4e4",
                    "domainnode_id": "55555555-343e-4af3-8857-f7322dc9eb4b",
                    "ontologyproperty": "P2",
                    "description": "",
                }
            ],
            "cards": [
                {
                    "name": "NODE_NAME",
                    "description": "",
                    "instructions": "",
                    "helptext": "",
                    "cardinality": "n",
                    "nodegroup_id": "66666666-24c9-4226-bde2-2c40ee60a26c",
                }
            ],
            "functions": [],
        }

        nodes_count_before = models.Node.objects.count()
        edges_count_before = models.Edge.objects.count()
        cards_count_before = models.CardModel.objects.count()
        nodegroups_count_before = models.NodeGroup.objects.count()

        graph = Graph(graph_obj)

        self.assertEqual(models.Node.objects.count() - nodes_count_before, 0)
        self.assertEqual(models.Edge.objects.count() - edges_count_before, 0)
        self.assertEqual(models.CardModel.objects.count() - cards_count_before, 0)
        self.assertEqual(models.NodeGroup.objects.count() - nodegroups_count_before, 0)
        self.assertEqual(graph_obj["name"], graph.name)
        self.assertEqual(graph_obj["subtitle"], graph.subtitle)
        self.assertEqual(graph_obj["author"], graph.author)
        self.assertEqual(graph_obj["description"], graph.description)
        self.assertEqual(graph_obj["version"], graph.version)
        self.assertEqual(graph_obj["isresource"], graph.isresource)
        self.assertEqual(graph_obj["isactive"], graph.isactive)
        self.assertEqual(graph_obj["iconclass"], graph.iconclass)

    def test_nodes_are_byref(self):
        """
        test that the nodes referred to in the Graph.edges are exact references to
        the nodes as opposed to a node with the same attribute values

        """

        graph = Graph.objects.get(graphid=self.rootNode.graph_id)
        graph.append_branch("http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as", graphid=self.NODE_NODETYPE_GRAPHID)
        graph.save()

        node_mapping = {nodeid: id(node) for nodeid, node in list(graph.nodes.items())}

        for key, edge in list(graph.edges.items()):
            self.assertEqual(node_mapping[edge.domainnode.pk], id(edge.domainnode))
            self.assertEqual(node_mapping[edge.rangenode.pk], id(edge.rangenode))

        for key, node in list(graph.nodes.items()):
            for key, edge in list(graph.edges.items()):
                newid = uuid.uuid4()
                if edge.domainnode.pk == node.pk:
                    node.pk = newid
                    self.assertEqual(edge.domainnode.pk, newid)
                elif edge.rangenode.pk == node.pk:
                    node.pk = newid
                    self.assertEqual(edge.rangenode.pk, newid)

    def test_copy_graph(self):
        """
        test that a copy of a graph has the same number of nodes and edges and that the primary keys have been changed
        and that the actual node references are different

        """

        graph = Graph.new(name="TEST RESOURCE")
        graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", graphid=self.NODE_NODETYPE_GRAPHID)
        graph_copy = graph.copy()["copy"]

        self.assertEqual(len(graph_copy.nodes), 3)
        self.assertEqual(len(graph_copy.edges), 2)
        self.assertEqual(len(graph_copy.cards), 2)
        self.assertEqual(len(graph_copy.get_nodegroups()), 2)
        self.assertEqual(len(graph.nodes), len(graph_copy.nodes))
        self.assertEqual(len(graph.edges), len(graph_copy.edges))
        self.assertEqual(len(graph.cards), len(graph_copy.cards))
        self.assertEqual(len(graph.get_nodegroups()), len(graph_copy.get_nodegroups()))

        # assert the copied nodegroup heirarchy is maintained
        for nodegroup in graph_copy.get_nodegroups():
            if graph_copy.nodes[nodegroup.pk] is graph_copy.root:
                parentnodegroup_copy = nodegroup
            else:
                childnodegroup_copy = nodegroup
        self.assertTrue(parentnodegroup_copy.parentnodegroup is None)
        self.assertEqual(childnodegroup_copy.parentnodegroup, parentnodegroup_copy)
        self.assertFalse(parentnodegroup_copy.parentnodegroup_id)
        self.assertEqual(childnodegroup_copy.parentnodegroup_id, parentnodegroup_copy.pk)

        # assert the copied node groups are not equal to the originals
        for nodegroup in graph.get_nodegroups():
            if graph.nodes[nodegroup.pk] is graph.root:
                parentnodegroup = nodegroup
            else:
                childnodegroup = nodegroup

        self.assertNotEqual(parentnodegroup, parentnodegroup_copy)
        self.assertNotEqual(parentnodegroup.pk, parentnodegroup_copy.pk)
        self.assertNotEqual(childnodegroup, childnodegroup_copy)
        self.assertNotEqual(childnodegroup.pk, childnodegroup_copy.pk)

        # assert the nodegroups attached to the cards are heirarchically correct
        for card in list(graph_copy.cards.values()):
            if str(card.nodegroup_id) == str(graph_copy.root.nodeid):
                parentcard_copy = card
            else:
                childcard_copy = card

        self.assertTrue(parentcard_copy.nodegroup is not None)
        self.assertTrue(childcard_copy.nodegroup is not None)
        self.assertTrue(parentcard_copy.nodegroup.parentnodegroup is None)
        self.assertTrue(childcard_copy.nodegroup.parentnodegroup is not None)
        self.assertEqual(parentcard_copy.nodegroup, childcard_copy.nodegroup.parentnodegroup)

        def findNodeByName(graph, name):
            for node in list(graph.nodes.values()):
                if node.name == name:
                    return node
            return None

        def findCardByName(graph, name):
            for card in list(graph.cards.values()):
                if card.name == name:
                    return card
            return None

        for node in list(graph.nodes.values()):
            node_copy = findNodeByName(graph_copy, node.name)
            self.assertIsNotNone(node_copy)
            self.assertNotEqual(node.pk, node_copy.pk)
            self.assertNotEqual(id(node), id(node_copy))
            self.assertEqual(node.is_collector, node_copy.is_collector)
            if node.nodegroup is not None:
                self.assertNotEqual(node.nodegroup, node_copy.nodegroup)

        for card in list(graph.cards.values()):
            card_copy = findCardByName(graph_copy, card.name)
            self.assertIsNotNone(card_copy)
            self.assertNotEqual(card.pk, card_copy.pk)
            self.assertNotEqual(id(card), id(card_copy))
            self.assertNotEqual(card.nodegroup, card_copy.nodegroup)

        for newedge in list(graph_copy.edges.values()):
            self.assertIsNotNone(graph_copy.nodes[newedge.domainnode_id])
            self.assertIsNotNone(graph_copy.nodes[newedge.rangenode_id])
            self.assertEqual(newedge.domainnode, graph_copy.nodes[newedge.domainnode.pk])
            self.assertEqual(newedge.rangenode, graph_copy.nodes[newedge.rangenode.pk])
            with self.assertRaises(KeyError):
                graph.edges[newedge.pk]

    def test_branch_append_with_ontology(self):
        """
        test if a branch is properly appended to a graph that defines an ontology

        """

        nodes_count_before = models.Node.objects.count()
        edges_count_before = models.Edge.objects.count()
        cards_count_before = models.CardModel.objects.count()
        nodegroups_count_before = models.NodeGroup.objects.count()

        graph = Graph.objects.get(pk=self.rootNode.graph.graphid)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(len(graph.edges), 0)
        self.assertEqual(len(graph.cards), 1)
        self.assertEqual(len(graph.get_nodegroups()), 1)

        appended_graph = graph.append_branch("http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as", graphid=self.NODE_NODETYPE_GRAPHID)
        graph.save()

        self.assertEqual(len(graph.nodes), 3)
        self.assertEqual(len(graph.edges), 2)
        self.assertEqual(len(graph.cards), 2)
        self.assertEqual(len(graph.get_nodegroups()), 2)

        self.assertEqual(models.Node.objects.count() - nodes_count_before, 2)
        self.assertEqual(models.Edge.objects.count() - edges_count_before, 2)
        self.assertEqual(models.CardModel.objects.count() - cards_count_before, 1)
        self.assertEqual(models.NodeGroup.objects.count() - nodegroups_count_before, 1)

        for key, edge in list(graph.edges.items()):
            self.assertIsNotNone(graph.nodes[edge.domainnode_id])
            self.assertIsNotNone(graph.nodes[edge.rangenode_id])
            self.assertEqual(edge.domainnode, graph.nodes[edge.domainnode.pk])
            self.assertEqual(edge.rangenode, graph.nodes[edge.rangenode.pk])
            self.assertIsNotNone(edge.ontologyproperty)

        for key, node in list(graph.nodes.items()):
            self.assertIsNotNone(node.ontologyclass)
            if node.istopnode:
                self.assertEqual(node, self.rootNode)

        # confirm that a non-grouped node takes on the parent group when appended
        appended_branch = graph.append_branch("http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as", graphid=self.SINGLE_NODE_GRAPHID)
        self.assertEqual(len(graph.nodes), 4)
        self.assertEqual(len(graph.edges), 3)
        self.assertEqual(len(graph.cards), 2)
        self.assertEqual(len(graph.get_nodegroups()), 2)
        self.assertEqual(appended_branch.root.nodegroup, self.rootNode.nodegroup)

        graph.save()
        self.assertEqual(models.Node.objects.count() - nodes_count_before, 3)
        self.assertEqual(models.Edge.objects.count() - edges_count_before, 3)
        self.assertEqual(models.CardModel.objects.count() - cards_count_before, 1)
        self.assertEqual(models.NodeGroup.objects.count() - nodegroups_count_before, 1)

    def test_rules_for_appending(self):
        """
        test the rules that control the appending of branches to graphs

        """

        graph = Graph.objects.get(node=self.rootNode)
        graph.isresource = True
        self.assertIsNotNone(graph.append_branch("http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as", graphid=self.NODE_NODETYPE_GRAPHID))

        graph = Graph.new()
        graph.root.datatype = "string"
        graph.update_node(JSONSerializer().serializeToPython(graph.root))

        # create card collector graph to use for appending on to other graphs
        collector_graph = Graph.new()
        collector_graph.append_branch("http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as", graphid=self.NODE_NODETYPE_GRAPHID)
        collector_graph.save()

    def test_node_update(self):
        """
        test to make sure that node groups and card are properly managed
        when changing a nodegroup value on a node being updated

        """

        # create a graph, append the node/node type graph and confirm is has the correct
        # number of nodegroups then remove the appended branches group and reconfirm that
        # the proper number of groups are properly relfected in the graph

        graph = Graph.objects.get(pk=self.rootNode.graph.graphid)
        graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", graphid=self.NODE_NODETYPE_GRAPHID)

        node_to_update = None
        for node_id, node in list(graph.nodes.items()):
            if node.name == "Node":
                node_to_update = JSONDeserializer().deserialize(JSONSerializer().serialize(node))
            if node.name == "Node Type":
                node_type_node = JSONDeserializer().deserialize(JSONSerializer().serialize(node))

        # confirm that nulling out a child group will then make that group a part of the parent group
        node_to_update["nodegroup_id"] = None
        graph.update_node(node_to_update)
        self.assertEqual(len(graph.get_nodegroups()), 1)
        self.assertEqual(len(graph.cards), 1)
        for node in list(graph.nodes.values()):
            self.assertEqual(graph.root.nodegroup, node.nodegroup)

        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", nodeid=node_type_node["nodeid"], graphid=self.SINGLE_NODE_GRAPHID
        )
        for edge in list(graph.edges.values()):
            if str(edge.domainnode_id) == str(node_type_node["nodeid"]):
                child_nodegroup_node = JSONDeserializer().deserialize(JSONSerializer().serialize(edge.rangenode))

        # make a node group with a single node and confirm that that node is now not part of it's parent node group
        child_nodegroup_node["nodegroup_id"] = child_nodegroup_node["nodeid"]
        graph.update_node(child_nodegroup_node)
        self.assertEqual(len(graph.get_nodegroups()), 2)
        for node_id, node in list(graph.nodes.items()):
            if node_id == child_nodegroup_node["nodeid"]:
                self.assertNotEqual(graph.root.nodegroup, node.nodegroup)
            else:
                self.assertEqual(graph.root.nodegroup, node.nodegroup)

        # make another node group with a node (that has a child) and confirm that that node and
        # it's child are now not part of it's parent node group and that both nodes are grouped together
        node_to_update["nodegroup_id"] = node_to_update["nodeid"]
        graph.update_node(node_to_update)
        self.assertEqual(len(graph.get_nodegroups()), 3)
        children = graph.get_child_nodes(node_to_update["nodeid"])
        for child in children:
            if child.nodeid == child_nodegroup_node["nodeid"]:
                self.assertEqual(child.nodeid, child.nodegroup_id)
            else:
                self.assertEqual(child.nodegroup_id, node_to_update["nodegroup_id"])

        # remove a node's node group and confirm that that node takes the node group of it's parent
        child_nodegroup_node["nodegroup_id"] = None
        graph.update_node(child_nodegroup_node)
        self.assertEqual(len(graph.get_nodegroups()), 2)
        children = graph.get_child_nodes(node_to_update["nodeid"])
        for child in children:
            self.assertEqual(child.nodegroup_id, node_to_update["nodegroup_id"])

    def test_move_node(self):
        """
        test if a node can be successfully moved to another node in the graph

        """

        # test moving a single node to another branch
        # this node should be grouped with it's new parent nodegroup
        graph = Graph.objects.get(pk=self.rootNode.graph.graphid)
        branch_one = graph.append_branch("http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as", graphid=self.NODE_NODETYPE_GRAPHID)
        for node in list(branch_one.nodes.values()):
            if node is branch_one.root:
                node.name = "branch_one_root"
            else:
                node.name = "branch_one_child"
        branch_two = graph.append_branch("http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as", graphid=self.NODE_NODETYPE_GRAPHID)
        for node in list(branch_two.nodes.values()):
            if node is branch_two.root:
                node.name = "branch_two_root"
            else:
                node.name = "branch_two_child"
        branch_three = graph.append_branch("http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as", graphid=self.SINGLE_NODE_GRAPHID)
        branch_three.root.name = "branch_three_root"
        self.assertEqual(len(graph.edges), 5)
        self.assertEqual(len(graph.nodes), 6)

        branch_three_nodeid = next(iter(list(branch_three.nodes.keys())))
        branch_one_rootnodeid = branch_one.root.nodeid
        graph.move_node(branch_three_nodeid, "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as", branch_one_rootnodeid)
        self.assertEqual(len(graph.edges), 5)
        self.assertEqual(len(graph.nodes), 6)

        new_parent_nodegroup = None
        moved_branch_nodegroup = None
        for node_id, node in list(graph.nodes.items()):
            if node_id == branch_one_rootnodeid:
                new_parent_nodegroup = node.nodegroup
            if node_id == branch_three_nodeid:
                moved_branch_nodegroup = node.nodegroup

        self.assertIsNotNone(new_parent_nodegroup)
        self.assertIsNotNone(moved_branch_nodegroup)
        self.assertEqual(new_parent_nodegroup, moved_branch_nodegroup)

        # test moving a branch to another branch
        # this branch should NOT be grouped with it's new parent nodegroup
        branch_two_rootnodeid = branch_two.root.nodeid
        graph.move_node(
            branch_one_rootnodeid, "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as", branch_two_rootnodeid, skip_validation=True
        )
        self.assertEqual(len(graph.edges), 5)
        self.assertEqual(len(graph.nodes), 6)

        new_parent_nodegroup = None
        moved_branch_nodegroup = None
        for node_id, node in list(graph.nodes.items()):
            if node_id == branch_two_rootnodeid:
                new_parent_nodegroup = node.nodegroup
            if node_id == branch_one_rootnodeid:
                moved_branch_nodegroup = node.nodegroup

        self.assertIsNotNone(new_parent_nodegroup)
        self.assertIsNotNone(moved_branch_nodegroup)
        self.assertNotEqual(new_parent_nodegroup, moved_branch_nodegroup)

        updated_edge = None
        for edge_id, edge in list(graph.edges.items()):
            if edge.domainnode_id == branch_two_rootnodeid and edge.rangenode_id == branch_one_rootnodeid:
                updated_edge = edge

        self.assertIsNotNone(updated_edge)

        # save and retrieve the graph from the database and confirm that
        # the graph shape has been saved properly
        graph.save()
        for node in list(branch_two.nodes.values()):
            node.datatype = "semantic"
        graph.save()
        graph = Graph.objects.get(pk=self.rootNode.graph.graphid)
        tree = graph.get_tree()

        self.assertEqual(len(tree["children"]), 1)
        level_one_node = tree["children"][0]

        self.assertEqual(branch_two_rootnodeid, level_one_node["node"].nodeid)
        self.assertEqual(len(level_one_node["children"]), 2)
        for child in level_one_node["children"]:
            if child["node"].nodeid == branch_one_rootnodeid:
                self.assertEqual(len(child["children"]), 2)
                found_branch_three = False
                for child in child["children"]:
                    if child["node"].nodeid == branch_three_nodeid:
                        found_branch_three = True
                self.assertTrue(found_branch_three)
            else:
                self.assertEqual(len(child["children"]), 0)

        # Pressumed final graph shape
        #
        #                                                self.rootNode
        #                                                      |
        #                                            branch_two_rootnodeid (Node)
        #                                                    /   \
        #                         branch_one_rootnodeid (Node)    branch_two_child (NodeType)
        #                                 /   \
        # branch_one_childnodeid (NodeType)    branch_three_nodeid (Node)

    def test_get_valid_ontology_classes(self):
        """
        test to see if we return the proper ontology classes for a graph that uses an ontology system

        """

        graph = Graph.objects.get(pk=self.rootNode.graph.graphid)
        ret = graph.get_valid_ontology_classes(nodeid=self.rootNode.nodeid)
        self.assertTrue(len(ret) == 1)

        self.assertEqual(ret[0]["ontology_property"], "")
        self.assertEqual(len(ret[0]["ontology_classes"]), models.OntologyClass.objects.filter(ontology_id=graph.ontology_id).count())

    def test_get_valid_ontology_classes_on_resource_with_no_ontology_set(self):
        """
        test to see if we return the proper ontology classes for a graph that doesn't use an ontology system

        """

        self.rootNode.graph.ontology_id = None
        graph = Graph.objects.get(pk=self.rootNode.graph.graphid)

        graph.ontology_id = None
        ret = graph.get_valid_ontology_classes(nodeid=self.rootNode.nodeid)
        self.assertTrue(len(ret) == 0)

    def test_append_branch_to_resource_with_no_ontology_system(self):
        """
        test to see that we remove all ontologyclass and ontologyproperty references when appending a
        graph that uses an ontology system to a graph that doesn't

        """

        graph = Graph.objects.get(pk=self.rootNode.graph.graphid)
        graph.clear_ontology_references()
        graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", graphid=self.NODE_NODETYPE_GRAPHID)
        for node_id, node in list(graph.nodes.items()):
            self.assertTrue(node.ontologyclass is None)
        for edge_id, edge in list(graph.edges.items()):
            self.assertTrue(edge.ontologyproperty is None)

    def test_save_and_update_dont_orphan_records_in_the_db(self):
        """
        test that the proper number of nodes, edges, nodegroups, and cards are persisted
        to the database during save and update opertaions

        """

        nodes_count_before = models.Node.objects.count()
        edges_count_before = models.Edge.objects.count()
        nodegroups_count_before = models.NodeGroup.objects.count()
        card_count_before = models.CardModel.objects.count()

        # test that data is persisited propertly when creating a new graph
        graph = Graph.new(is_resource=False)

        nodes_count_after = models.Node.objects.count()
        edges_count_after = models.Edge.objects.count()
        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()

        self.assertEqual(nodes_count_after - nodes_count_before, 1)
        self.assertEqual(edges_count_after - edges_count_before, 0)
        self.assertEqual(nodegroups_count_after - nodegroups_count_before, 1)
        self.assertEqual(card_count_after - card_count_before, 1)

        # test that data is persisited propertly during an append opertation
        graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", graphid=self.NODE_NODETYPE_GRAPHID)
        graph.save()

        nodes_count_after = models.Node.objects.count()
        edges_count_after = models.Edge.objects.count()
        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()

        self.assertEqual(nodes_count_after - nodes_count_before, 3)
        self.assertEqual(edges_count_after - edges_count_before, 2)
        self.assertEqual(nodegroups_count_after - nodegroups_count_before, 2)
        self.assertEqual(card_count_after - card_count_before, 2)

        # test that removing a node group by setting it to None, removes it from the db
        node_to_update = None
        for node_id, node in list(graph.nodes.items()):
            if node.name == "Node":
                self.assertTrue(node.is_collector)
                node_to_update = JSONDeserializer().deserialize(JSONSerializer().serialize(node))

        node_to_update["nodegroup_id"] = None
        graph.update_node(node_to_update.copy())
        graph.save()

        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()

        self.assertEqual(nodegroups_count_after - nodegroups_count_before, 1)
        self.assertEqual(card_count_after - card_count_before, 1)

        # test that adding back a node group adds it back to the db
        node_to_update["nodegroup_id"] = node_to_update["nodeid"]
        graph.update_node(node_to_update)
        graph.save()

        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()

        self.assertEqual(nodegroups_count_after - nodegroups_count_before, 2)
        self.assertEqual(card_count_after - card_count_before, 2)

    def test_delete_graph(self):
        """
        test the graph delete method

        """

        graph = Graph.objects.get(graphid=self.NODE_NODETYPE_GRAPHID)
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(len(graph.get_nodegroups()), 1)

        nodes_count_before = models.Node.objects.count()
        edges_count_before = models.Edge.objects.count()
        nodegroups_count_before = models.NodeGroup.objects.count()
        card_count_before = models.CardModel.objects.count()

        graph.delete()

        nodes_count_after = models.Node.objects.count()
        edges_count_after = models.Edge.objects.count()
        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()

        self.assertEqual(nodes_count_before - nodes_count_after, 2)
        self.assertEqual(edges_count_before - edges_count_after, 1)
        self.assertEqual(nodegroups_count_before - nodegroups_count_after, 1)
        self.assertEqual(card_count_before - card_count_after, 1)

        node_count = models.Node.objects.filter(graph_id=self.NODE_NODETYPE_GRAPHID).count()
        edge_count = models.Edge.objects.filter(graph_id=self.NODE_NODETYPE_GRAPHID).count()
        self.assertEqual(node_count, 0)
        self.assertEqual(edge_count, 0)

    def test_delete_node(self):
        """
        test the node delete method

        """
        graph = Graph.new(name="TEST", is_resource=False, author="TEST")
        graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", graphid=self.NODE_NODETYPE_GRAPHID)
        graph.save()
        node = models.Node.objects.get(graph=graph, name="Node")

        nodes_count_before = models.Node.objects.count()
        edges_count_before = models.Edge.objects.count()
        nodegroups_count_before = models.NodeGroup.objects.count()
        card_count_before = models.CardModel.objects.count()

        graph.delete_node(node)

        nodes_count_after = models.Node.objects.count()
        edges_count_after = models.Edge.objects.count()
        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()

        self.assertEqual(nodes_count_before - nodes_count_after, 2)
        self.assertEqual(edges_count_before - edges_count_after, 2)
        self.assertEqual(nodegroups_count_before - nodegroups_count_after, 1)
        self.assertEqual(card_count_before - card_count_after, 1)

        graph = Graph.objects.get(graphid=graph.pk)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(len(graph.edges), 0)
        self.assertEqual(len(graph.cards), 1)
        self.assertEqual(len(graph.get_nodegroups()), 1)

        graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", graphid=self.NODE_NODETYPE_GRAPHID)
        graph.save()
        node = models.Node.objects.get(graph=graph, name="Node Type")
        graph.delete_node(node)
        graph = Graph.objects.get(graphid=graph.pk)
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(len(graph.cards), 2)
        self.assertEqual(len(graph.get_nodegroups()), 2)

    def test_derive_card_values(self):
        """
        test to make sure we get the proper name and description for display in the ui

        """

        # TESTING A GRAPH
        graph = Graph.new(name="TEST", is_resource=False, author="TEST")
        graph.description = "A test description"

        self.assertEqual(len(graph.cards), 1)
        for card in graph.get_cards():
            self.assertEqual(card["name"], graph.name)
            self.assertEqual(card["description"], graph.description)
            card = Card.objects.get(pk=card["cardid"])
            card.name = "TEST card name"
            card.description = "TEST card description"
            card.save()

        for card in graph.get_cards():
            self.assertEqual(card["name"], "TEST")
            self.assertEqual(card["description"], "A test description")

        graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", graphid=self.SINGLE_NODE_GRAPHID)
        graph.save()

        for node in list(graph.nodes.values()):
            if node is not graph.root:
                nodeJson = JSONSerializer().serializeToPython(node)
                nodeJson["nodegroup_id"] = nodeJson["nodeid"]
                graph.update_node(nodeJson)

        graph.save()

        self.assertEqual(len(graph.get_cards()), 2)
        for card in graph.get_cards():
            if str(card["nodegroup_id"]) == str(graph.root.nodegroup_id):
                self.assertEqual(card["name"], graph.name)
                self.assertEqual(card["description"], graph.description)
            else:
                self.assertTrue(len(graph.nodes[card["nodegroup_id"]].name) > 0)
                self.assertTrue(len(graph.nodes[card["nodegroup_id"]].description) > 0)
                self.assertEqual(card["name"], graph.nodes[card["nodegroup_id"]].name)
                self.assertEqual(card["description"], graph.nodes[card["nodegroup_id"]].description)

        # TESTING A RESOURCE
        resource_graph = Graph.new(name="TEST RESOURCE", is_resource=True, author="TEST")
        resource_graph.description = "A test resource description"
        resource_graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", graphid=graph.graphid)
        resource_graph.save()

        self.assertEqual(len(resource_graph.get_cards()), 2)

        for card in resource_graph.get_cards():
            cardobj = Card.objects.get(pk=card["cardid"])
            if cardobj.nodegroup.parentnodegroup is None:
                self.assertEqual(card["name"], graph.name)
                self.assertEqual(card["description"], graph.description)
            else:
                self.assertEqual(card["name"], resource_graph.nodes[card["nodegroup_id"]].name)
                self.assertEqual(card["description"], resource_graph.nodes[card["nodegroup_id"]].description)
                self.assertTrue(len(resource_graph.nodes[card["nodegroup_id"]].name) > 0)
                self.assertTrue(len(resource_graph.nodes[card["nodegroup_id"]].description) > 0)

        resource_graph.delete()

        # TESTING A RESOURCE
        resource_graph = Graph.new(name="TEST", is_resource=True, author="TEST")
        resource_graph.description = "A test description"
        resource_graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", graphid=self.NODE_NODETYPE_GRAPHID)
        resource_graph.save()

        self.assertEqual(len(resource_graph.cards), 1)
        the_card = next(iter(list(resource_graph.cards.values())))
        for card in resource_graph.get_cards():
            self.assertEqual(card["name"], the_card.name)
            self.assertEqual(card["description"], the_card.description)

        # after removing the card name and description, the cards should take on the node name and description
        the_card.name = ""
        the_card.description = ""
        for card in resource_graph.get_cards():
            self.assertEqual(card["name"], resource_graph.nodes[card["nodegroup_id"]].name)
            self.assertEqual(card["description"], resource_graph.nodes[card["nodegroup_id"]].description)

    def test_get_root_nodegroup(self):
        """
        test we can get the right parent NodeGroup

        """

        graph = Graph.new(name="TEST", is_resource=False, author="TEST")
        graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", graphid=self.NODE_NODETYPE_GRAPHID)

        for node in list(graph.nodes.values()):
            if node.is_collector:
                if node.nodegroup.parentnodegroup is None:
                    self.assertEqual(graph.get_root_nodegroup(), node.nodegroup)

    def test_get_root_card(self):
        """
        test we can get the right parent card

        """

        graph = Graph.new(name="TEST", is_resource=False, author="TEST")
        graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", graphid=self.NODE_NODETYPE_GRAPHID)

        for card in list(graph.cards.values()):
            if card.nodegroup.parentnodegroup is None:
                self.assertEqual(graph.get_root_card(), card)

    def test_graph_validation_of_null_ontology_class(self):
        """
        test to make sure null ontology classes aren't allowed

        """

        graph = Graph.objects.get(graphid=self.rootNode.graph_id)
        new_node = graph.add_node({"nodeid": uuid.uuid1(), "datatype": "semantic"})  # A blank node with no ontology class is specified
        graph.add_edge({"domainnode_id": self.rootNode.pk, "rangenode_id": new_node.pk, "ontologyproperty": None})

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1000)

    def test_graph_validation_of_invalid_ontology_class(self):
        """
        test to make sure invalid ontology classes aren't allowed

        """

        graph = Graph.objects.get(graphid=self.rootNode.graph_id)
        new_node = graph.add_node(
            {"nodeid": uuid.uuid1(), "datatype": "semantic", "ontologyclass": "InvalidOntologyClass"}
        )  # A blank node with an invalid ontology class specified
        graph.add_edge({"domainnode_id": self.rootNode.pk, "rangenode_id": new_node.pk, "ontologyproperty": None})

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1001)

    def test_graph_validation_of_null_ontology_property(self):
        """
        test to make sure null ontology properties aren't allowed

        """

        graph = Graph.objects.get(graphid=self.rootNode.graph_id)
        graph.append_branch(None, graphid=self.NODE_NODETYPE_GRAPHID)

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1002)

    def test_graph_validation_of_incorrect_ontology_property(self):
        """
        test to make sure a valid ontology property but incorrect use of the property fails

        """

        graph = Graph.objects.get(graphid=self.rootNode.graph_id)
        graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by", graphid=self.NODE_NODETYPE_GRAPHID)

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1003)

    def test_graph_validation_of_invalid_ontology_property(self):
        """
        test to make sure we use a valid ontology property value

        """

        graph = Graph.objects.get(graphid=self.rootNode.graph_id)
        graph.append_branch("some invalid property", graphid=self.NODE_NODETYPE_GRAPHID)

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1003)

    def test_graph_validation_of_branch_with_ontology_appended_to_graph_with_no_ontology(self):
        """
        test to make sure we can't append a branch with ontology defined to a graph with no ontology defined

        """

        graph = Graph.new()
        graph.name = "TEST GRAPH"
        graph.ontology = None
        graph.save()

        graph.root.name = "ROOT NODE"
        graph.root.description = "Test Root Node"
        graph.root.ontologyclass = "http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity"
        graph.root.datatype = "semantic"
        graph.root.save()

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1005)

    def test_appending_a_branch_with_an_invalid_ontology_property(self):
        graph = Graph.objects.get(graphid=self.NODE_NODETYPE_GRAPHID)
        graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P43_has_dimension", graphid=self.NODE_NODETYPE_GRAPHID)

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()

    def test_appending_a_branch_with_an_invalid_ontology_class(self):
        graph = Graph.new()
        graph.name = "TEST GRAPH"
        graph.subtitle = "ARCHES TEST GRAPH"
        graph.author = "Arches"
        graph.description = "ARCHES TEST GRAPH"
        graph.ontology = models.Ontology.objects.get(pk="e6e8db47-2ccf-11e6-927e-b8f6b115d7dd")
        graph.version = "v1.0.0"
        graph.isactive = False
        graph.iconclass = "fa fa-building"
        graph.nodegroups = []

        graph.root.name = "ROOT NODE"
        graph.root.description = "Test Root Node"
        graph.root.ontologyclass = "http://www.cidoc-crm.org/cidoc-crm/E21_Person"
        graph.root.datatype = "semantic"

        graph.save()

        graph.append_branch("http://www.cidoc-crm.org/cidoc-crm/P43_has_dimension", graphid=self.NODE_NODETYPE_GRAPHID)

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()
