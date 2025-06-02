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

import uuid
from unittest import mock

from django.contrib.auth.models import User
from guardian.models import GroupObjectPermission, UserObjectPermission

from arches.app.const import IntegrityCheck
from arches.app.models import models
from arches.app.models.graph import Graph, GraphValidationError
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.models.graph_tests --settings="tests.test_settings"


class GraphTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.SINGLE_NODE_GRAPHID = "22000000-0000-0000-0000-000000000000"
        cls.NODE_NODETYPE_GRAPHID = "22000000-0000-0000-0000-000000000001"
        cls.single_node_graph = cls.create_single_node_graph()
        cls.node_node_type_graph = cls.create_node_node_type_graph()
        cls.test_graph = cls.create_test_graph()

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
        return graph

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

        # default_widgets_by_datatype = {
        #     datatype.pk: datatype.defaultwidget
        #     for datatype in models.DDataType.objects.select_related("defaultwidget")
        # }
        for node_data in nodes_data:
            node = models.Node.objects.create(**node_data)
            # This should be uncommented when it will no longer cause failures.
            # models.CardXNodeXWidget.objects.create(
            #     card=node.nodegroup.cardmodel_set.all()[0],
            #     node=node,
            #     widget=default_widgets_by_datatype[node.datatype],
            # )

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

        cls.rootNode = test_graph.root
        return test_graph

    def test_new_graph(self):
        name = "TEST NEW GRAPH"

        user = User.objects.create(
            username="arches_test_user",
            first_name="TEST",
            last_name="USER",
        )

        graph = Graph.objects.create_graph(name=name, is_resource=True, user=user)
        self.assertEqual(graph.name, name)
        self.assertEqual(graph.author, "TEST USER")
        self.assertTrue(graph.isresource)
        self.assertFalse(graph.root.is_collector)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(len(graph.cards), 0)
        self.assertEqual(len(graph.get_nodegroups()), 0)

        graph = Graph.objects.create_graph(name=name, is_resource=False, user=user)
        self.assertEqual(graph.name, name)
        self.assertEqual(graph.author, "TEST USER")
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
            "slug": "test_graph",
            "subtitle": "ARCHES TEST GRAPH",
            "author": "Arches",
            "description": "ARCHES TEST GRAPH",
            "version": "v1.0.0",
            "isresource": True,
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
        self.assertEqual(graph_obj["iconclass"], graph.iconclass)

    def test_nodes_are_byref(self):
        """
        test that the nodes referred to in the Graph.edges are exact references to
        the nodes as opposed to a node with the same attribute values

        """

        graph = self.test_graph
        graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
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

        graph = Graph.objects.create_graph(name="TEST RESOURCE")
        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        graph.save()
        graph.publish()

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
        self.assertEqual(
            childnodegroup_copy.parentnodegroup_id, parentnodegroup_copy.pk
        )

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
        self.assertEqual(
            parentcard_copy.nodegroup, childcard_copy.nodegroup.parentnodegroup
        )

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
            self.assertEqual(
                newedge.domainnode, graph_copy.nodes[newedge.domainnode.pk]
            )
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

        graph = Graph.objects.get(pk=self.test_graph.pk)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(len(graph.edges), 0)
        self.assertEqual(len(graph.cards), 1)
        self.assertEqual(len(graph.get_nodegroups()), 1)

        graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
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
        appended_branch = graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            graphid=self.SINGLE_NODE_GRAPHID,
        )
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
        self.assertIsNotNone(
            graph.append_branch(
                "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
                graphid=self.NODE_NODETYPE_GRAPHID,
            )
        )

        graph = Graph.objects.create_graph()
        graph.root.datatype = "string"
        graph.update_node(JSONSerializer().serializeToPython(graph.root))

        # create card collector graph to use for appending on to other graphs
        collector_graph = Graph.objects.create_graph()
        collector_graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        collector_graph.save()

    def test_node_creation_sets_grouping_node(self):
        self.assertEqual(self.rootNode.nodegroup.grouping_node, self.rootNode)

    def test_node_update(self):
        """
        test to make sure that node groups and card are properly managed
        when changing a nodegroup value on a node being updated

        """

        # create a graph, append the node/node type graph and confirm is has the correct
        # number of nodegroups then remove the appended branches group and reconfirm that
        # the proper number of groups are properly relfected in the graph

        graph = self.test_graph
        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )

        node_to_update = None
        for node_id, node in list(graph.nodes.items()):
            if node.name == "Node":
                node_to_update = JSONDeserializer().deserialize(
                    JSONSerializer().serialize(node)
                )
            if node.name == "Node Type":
                node_type_node = JSONDeserializer().deserialize(
                    JSONSerializer().serialize(node)
                )

        # confirm that nulling out a child group will then make that group a part of the parent group
        node_to_update["nodegroup_id"] = None
        graph.update_node(node_to_update)
        self.assertEqual(len(graph.get_nodegroups()), 1)
        self.assertEqual(len(graph.cards), 1)
        for node in list(graph.nodes.values()):
            self.assertEqual(graph.root.nodegroup, node.nodegroup)

        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            nodeid=node_type_node["nodeid"],
            graphid=self.SINGLE_NODE_GRAPHID,
        )
        for edge in list(graph.edges.values()):
            if str(edge.domainnode_id) == str(node_type_node["nodeid"]):
                child_nodegroup_node = JSONDeserializer().deserialize(
                    JSONSerializer().serialize(edge.rangenode)
                )

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
        graph = self.test_graph
        branch_one = graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        for node in list(branch_one.nodes.values()):
            if node is branch_one.root:
                node.name = "branch_one_root"
            else:
                node.name = "branch_one_child"
        branch_two = graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        for node in list(branch_two.nodes.values()):
            if node is branch_two.root:
                node.name = "branch_two_root"
            else:
                node.name = "branch_two_child"
        branch_three = graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            graphid=self.SINGLE_NODE_GRAPHID,
        )
        branch_three.root.name = "branch_three_root"
        self.assertEqual(len(graph.edges), 5)
        self.assertEqual(len(graph.nodes), 6)

        branch_three_nodeid = next(iter(list(branch_three.nodes.keys())))
        branch_one_rootnodeid = branch_one.root.nodeid
        graph.move_node(
            branch_three_nodeid,
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            branch_one_rootnodeid,
        )
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
            branch_one_rootnodeid,
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            branch_two_rootnodeid,
            skip_validation=True,
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
            if (
                edge.domainnode_id == branch_two_rootnodeid
                and edge.rangenode_id == branch_one_rootnodeid
            ):
                updated_edge = edge

        self.assertIsNotNone(updated_edge)

        # save and retrieve the graph from the database and confirm that
        # the graph shape has been saved properly
        graph.save()
        for node in list(branch_two.nodes.values()):
            node.datatype = "semantic"
        graph.save()
        graph.refresh_from_database()
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

        graph = self.test_graph
        ret = graph.get_valid_ontology_classes(nodeid=self.rootNode.nodeid)
        self.assertTrue(len(ret) == 1)

        self.assertEqual(ret[0]["ontology_property"], "")
        self.assertEqual(
            len(ret[0]["ontology_classes"]),
            models.OntologyClass.objects.filter(ontology_id=graph.ontology_id).count(),
        )

    def test_get_valid_ontology_classes_on_resource_with_no_ontology_set(self):
        """
        test to see if we return the proper ontology classes for a graph that doesn't use an ontology system

        """

        self.rootNode.graph.ontology_id = None
        graph = self.test_graph

        graph.ontology_id = None
        ret = graph.get_valid_ontology_classes(nodeid=self.rootNode.nodeid)
        self.assertTrue(len(ret) == 0)

    def test_append_branch_to_resource_with_no_ontology_system(self):
        """
        test to see that we remove all ontologyclass and ontologyproperty references when appending a
        graph that uses an ontology system to a graph that doesn't

        """

        graph = self.test_graph
        graph.clear_ontology_references()
        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
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

        # test that data is persisted properly when creating a new graph
        graph = Graph.objects.create_graph(is_resource=False)

        nodes_count_after = models.Node.objects.count()
        edges_count_after = models.Edge.objects.count()
        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()

        self.assertEqual(
            nodes_count_after - nodes_count_before, 2
        )  # one for new graph, one for draft_graph
        self.assertEqual(edges_count_after - edges_count_before, 0)
        self.assertEqual(
            nodegroups_count_after - nodegroups_count_before, 2
        )  # one for new graph, one for draft_graph
        self.assertEqual(
            card_count_after - card_count_before, 2
        )  # one for new graph, one for draft_graph

        # test that data is persisted properly during an append opertation
        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        graph.save()

        nodes_count_after = models.Node.objects.count()
        edges_count_after = models.Edge.objects.count()
        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()

        self.assertEqual(nodes_count_after - nodes_count_before, 4)
        self.assertEqual(edges_count_after - edges_count_before, 2)
        self.assertEqual(nodegroups_count_after - nodegroups_count_before, 3)
        self.assertEqual(card_count_after - card_count_before, 3)

        # test that removing a node group by setting it to None, removes it from the db
        node_to_update = None
        for node_id, node in list(graph.nodes.items()):
            if node.name == "Node":
                self.assertTrue(node.is_collector)
                node_to_update = JSONDeserializer().deserialize(
                    JSONSerializer().serialize(node)
                )

        node_to_update["nodegroup_id"] = None
        graph.update_node(node_to_update.copy())
        graph.save()

        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()

        self.assertEqual(nodegroups_count_after - nodegroups_count_before, 2)
        self.assertEqual(card_count_after - card_count_before, 2)

        # test that adding back a node group adds it back to the db
        node_to_update["nodegroup_id"] = node_to_update["nodeid"]
        graph.update_node(node_to_update)
        graph.save()

        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()

        self.assertEqual(nodegroups_count_after - nodegroups_count_before, 3)
        self.assertEqual(card_count_after - card_count_before, 3)

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

        node_count = models.Node.objects.filter(
            graph_id=self.NODE_NODETYPE_GRAPHID
        ).count()
        edge_count = models.Edge.objects.filter(
            graph_id=self.NODE_NODETYPE_GRAPHID
        ).count()
        self.assertEqual(node_count, 0)
        self.assertEqual(edge_count, 0)

    def test_delete_branch(self):
        """
        tests that deleting the top node of a branch deletes the entire branch

        """
        graph = Graph.objects.create_graph(
            name="TEST",
            is_resource=False,
        )

        initial_node_count = models.Node.objects.count()
        initial_edge_count = models.Edge.objects.count()
        initial_nodegroup_count = models.NodeGroup.objects.count()
        initial_card_count = models.CardModel.objects.count()
        initial_widget_count = models.CardXNodeXWidget.objects.count()

        initial_graph_nodes_count = len(graph.nodes)
        initial_graph_edges_count = len(graph.edges)
        initial_graph_cards_count = len(graph.cards)
        initial_graph_nodegroups_count = len(graph.get_nodegroups())

        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        graph.save()
        graph.publish()

        node_count_after_append = models.Node.objects.count()
        edge_count_after_append = models.Edge.objects.count()
        nodegroup_count_after_append = models.NodeGroup.objects.count()
        card_count_after_append = models.CardModel.objects.count()
        widget_count_after_append = models.CardXNodeXWidget.objects.count()

        node_for_branch = models.Node.objects.get(graph=graph, name="Node")
        graph = graph.delete_node(node_for_branch)
        graph.publish()

        node_count_after_deletion = models.Node.objects.count()
        edge_count_after_deletion = models.Edge.objects.count()
        nodegroup_count_after_deletion = models.NodeGroup.objects.count()
        card_count_after_deletion = models.CardModel.objects.count()
        widget_count_after_deletion = models.CardXNodeXWidget.objects.count()

        # assert database does not contain orphans
        nodes_added = node_count_after_append - initial_node_count
        nodes_removed = node_count_after_append - node_count_after_deletion
        expected_node_count_after_deletion = (
            initial_node_count + nodes_added - nodes_removed
        )
        self.assertEqual(node_count_after_deletion, expected_node_count_after_deletion)

        edges_added = edge_count_after_append - initial_edge_count
        edges_removed = edge_count_after_append - edge_count_after_deletion
        expected_edge_count_after_deletion = (
            initial_edge_count + edges_added - edges_removed
        )
        self.assertEqual(edge_count_after_deletion, expected_edge_count_after_deletion)

        nodegroups_added = nodegroup_count_after_append - initial_nodegroup_count
        nodegroups_removed = (
            nodegroup_count_after_append - nodegroup_count_after_deletion
        )
        expected_nodegroup_count_after_deletion = (
            initial_nodegroup_count + nodegroups_added - nodegroups_removed
        )
        self.assertEqual(
            nodegroup_count_after_deletion, expected_nodegroup_count_after_deletion
        )

        cards_added = card_count_after_append - initial_card_count
        cards_removed = card_count_after_append - card_count_after_deletion
        expected_card_count_after_deletion = (
            initial_card_count + cards_added - cards_removed
        )
        self.assertEqual(card_count_after_deletion, expected_card_count_after_deletion)

        widgets_added = widget_count_after_append - initial_widget_count
        widgets_removed = widget_count_after_append - widget_count_after_deletion
        expected_widget_count_after_deletion = (
            initial_widget_count + widgets_added - widgets_removed
        )
        self.assertEqual(
            widget_count_after_deletion, expected_widget_count_after_deletion
        )

        # assert graph has correct represntation of database
        self.assertEqual(len(graph.nodes), initial_graph_nodes_count)
        self.assertEqual(len(graph.edges), initial_graph_edges_count)
        self.assertEqual(len(graph.cards), initial_graph_cards_count)
        self.assertEqual(len(graph.get_nodegroups()), initial_graph_nodegroups_count)

    def test_delete_node(self):
        """
        tests deleting a single node
        """
        graph = Graph.objects.create_graph(
            name="TEST",
            is_resource=False,
        )

        initial_graph_nodes_count = len(graph.nodes)
        initial_graph_edges_count = len(graph.edges)
        initial_graph_cards_count = len(graph.cards)
        initial_graph_nodegroups_count = len(graph.get_nodegroups())

        initial_node_count = models.Node.objects.count()
        initial_edge_count = models.Edge.objects.count()
        initial_nodegroup_count = models.NodeGroup.objects.count()
        initial_card_count = models.CardModel.objects.count()
        initial_widget_count = models.CardXNodeXWidget.objects.count()

        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        graph.save()
        graph.publish()

        node_count_after_append = models.Node.objects.count()
        edge_count_after_append = models.Edge.objects.count()
        nodegroup_count_after_append = models.NodeGroup.objects.count()
        card_count_after_append = models.CardModel.objects.count()
        widget_count_after_append = models.CardXNodeXWidget.objects.count()

        node_to_delete = models.Node.objects.get(graph=graph, name="Node Type")
        graph = graph.delete_node(node_to_delete)
        graph.publish()

        node_count_after_deletion = models.Node.objects.count()
        edge_count_after_deletion = models.Edge.objects.count()
        nodegroup_count_after_deletion = models.NodeGroup.objects.count()
        card_count_after_deletion = models.CardModel.objects.count()
        widget_count_after_deletion = models.CardXNodeXWidget.objects.count()

        # assert database does not contain orphans
        nodes_added = node_count_after_append - initial_node_count
        nodes_removed = node_count_after_append - node_count_after_deletion
        expected_node_count_after_deletion = (
            initial_node_count + nodes_added - nodes_removed
        )
        self.assertEqual(node_count_after_deletion, expected_node_count_after_deletion)

        edges_added = edge_count_after_append - initial_edge_count
        edges_removed = edge_count_after_append - edge_count_after_deletion
        expected_edge_count_after_deletion = (
            initial_edge_count + edges_added - edges_removed
        )
        self.assertEqual(edge_count_after_deletion, expected_edge_count_after_deletion)

        nodegroups_added = nodegroup_count_after_append - initial_nodegroup_count
        nodegroups_removed = (
            nodegroup_count_after_append - nodegroup_count_after_deletion
        )
        expected_nodegroup_count_after_deletion = (
            initial_nodegroup_count + nodegroups_added - nodegroups_removed
        )
        self.assertEqual(
            nodegroup_count_after_deletion, expected_nodegroup_count_after_deletion
        )

        cards_added = card_count_after_append - initial_card_count
        cards_removed = card_count_after_append - card_count_after_deletion
        expected_card_count_after_deletion = (
            initial_card_count + cards_added - cards_removed
        )
        self.assertEqual(card_count_after_deletion, expected_card_count_after_deletion)

        widgets_added = widget_count_after_append - initial_widget_count
        widgets_removed = widget_count_after_append - widget_count_after_deletion
        expected_widget_count_after_deletion = (
            initial_widget_count + widgets_added - widgets_removed
        )
        self.assertEqual(
            widget_count_after_deletion, expected_widget_count_after_deletion
        )

        # assert graph has correct represntation of database
        expected_graph_nodes_count = initial_graph_nodes_count + (
            nodes_added - nodes_removed
        )
        self.assertEqual(len(graph.nodes), expected_graph_nodes_count)

        expected_graph_edges_count = initial_graph_edges_count + (
            edges_added - edges_removed
        )
        self.assertEqual(len(graph.edges), expected_graph_edges_count)

        expected_graph_cards_count = initial_graph_cards_count + (
            cards_added - cards_removed
        )
        self.assertEqual(len(graph.cards), expected_graph_cards_count)

        expected_graph_nodegroups_count = initial_graph_nodegroups_count + (
            nodegroups_added - nodegroups_removed
        )
        self.assertEqual(len(graph.get_nodegroups()), expected_graph_nodegroups_count)

    def test_derives_initial_card_values(self):
        """
        Tests that cards generated with Graph intially start with values described in Graph

        """
        graph = Graph.objects.create_graph(
            name="TEST",
            is_resource=False,
        )
        graph.description = "A test description"

        for card in graph.get_cards(force_recalculation=True):
            self.assertEqual(card["name"], graph.name)
            self.assertEqual(card["description"], graph.description)

    def test_derives_card_values(self):
        """
        Tests that cards in a branch have correctly derived values

        """
        graph = Graph.objects.create_graph(
            name="TEST",
            is_resource=False,
        )
        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.SINGLE_NODE_GRAPHID,
            return_appended_graph=True,
        )
        graph.description = "A test description"

        graph.save()

        for card in graph.get_cards(force_recalculation=True):
            if str(card["nodegroup_id"]) == str(graph.root.nodegroup_id):
                self.assertEqual(card["name"], graph.name)
                self.assertEqual(card["description"], graph.description)
            else:
                self.assertTrue(len(graph.nodes[card["nodegroup_id"]].name) > 0)
                self.assertTrue(len(graph.nodes[card["nodegroup_id"]].description) > 0)
                self.assertEqual(card["name"], graph.nodes[card["nodegroup_id"]].name)
                self.assertEqual(
                    card["description"], graph.nodes[card["nodegroup_id"]].description
                )

    def test_derives_card_values_from_node(self):
        """
        Tests that cards in a resource have correctly derived values

        """
        graph = Graph.objects.create_graph(
            name="TEST",
            is_resource=True,
        )
        graph.description = "A test description"
        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
            return_appended_graph=True,
        )
        graph.save()

        top_card = next(iter(graph.cards.values()))
        for card in graph.get_cards():
            self.assertEqual(card["name"], top_card.name)
            self.assertEqual(card["description"], top_card.description)

        # after removing the card name and description, the cards should take on the node name and description
        top_card.name = ""
        top_card.description = ""
        for card in graph.get_cards():
            self.assertEqual(card["name"], graph.nodes[card["nodegroup_id"]].name)
            self.assertEqual(
                card["description"],
                graph.nodes[card["nodegroup_id"]].description,
            )

    def test_get_root_nodegroup(self):
        """
        test we can get the right parent NodeGroup

        """

        graph = Graph.objects.create_graph(
            name="TEST",
            is_resource=False,
        )
        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )

        for node in list(graph.nodes.values()):
            if node.is_collector:
                if node.nodegroup.parentnodegroup is None:
                    self.assertEqual(graph.get_root_nodegroup(), node.nodegroup)

    def test_get_root_card(self):
        """
        test we can get the right parent card

        """

        graph = Graph.objects.create_graph(
            name="TEST",
            is_resource=False,
        )
        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        graph.publish()

        for card in list(graph.cards.values()):
            if card.nodegroup.parentnodegroup is None:
                self.assertEqual(graph.get_root_card(), card)

    def test_graph_validation_of_null_ontology_class(self):
        """
        test to make sure null ontology classes aren't allowed

        """

        graph = self.test_graph
        new_node = graph.add_node(
            {"nodeid": uuid.uuid4(), "datatype": "semantic"}
        )  # A blank node with no ontology class is specified
        graph.add_edge(
            {
                "domainnode_id": self.rootNode.pk,
                "rangenode_id": new_node.pk,
                "ontologyproperty": None,
            }
        )

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1000)

    def test_graph_validation_of_invalid_ontology_class(self):
        """
        test to make sure invalid ontology classes aren't allowed

        """

        graph = self.test_graph
        new_node = graph.add_node(
            {
                "nodeid": uuid.uuid4(),
                "datatype": "semantic",
                "ontologyclass": "InvalidOntologyClass",
            }
        )  # A blank node with an invalid ontology class specified
        graph.add_edge(
            {
                "domainnode_id": self.rootNode.pk,
                "rangenode_id": new_node.pk,
                "ontologyproperty": None,
            }
        )

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1001)

    def test_graph_validation_of_null_ontology_property(self):
        """
        test to make sure null ontology properties aren't allowed

        """

        graph = self.test_graph
        graph.append_branch(None, graphid=self.NODE_NODETYPE_GRAPHID)

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1002)

    def test_graph_validation_of_incorrect_ontology_property(self):
        """
        test to make sure a valid ontology property but incorrect use of the property fails

        """

        graph = self.test_graph
        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1003)

    def test_graph_validation_of_invalid_ontology_property(self):
        """
        test to make sure we use a valid ontology property value

        """

        graph = self.test_graph
        graph.append_branch("some invalid property", graphid=self.NODE_NODETYPE_GRAPHID)

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.code, 1003)

    def test_graph_validation_of_branch_with_ontology_appended_to_graph_with_no_ontology(
        self,
    ):
        """
        test to make sure we can't append a branch with ontology defined to a graph with no ontology defined

        """

        graph = Graph.objects.create_graph()
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
        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P43_has_dimension",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()

    def test_appending_a_branch_with_an_invalid_ontology_class(self):
        graph = Graph.objects.create_graph()
        graph.name = "TEST GRAPH"
        graph.subtitle = "ARCHES TEST GRAPH"
        graph.author = "Arches"
        graph.description = "ARCHES TEST GRAPH"
        graph.ontology = models.Ontology.objects.get(
            pk="e6e8db47-2ccf-11e6-927e-b8f6b115d7dd"
        )
        graph.version = "v1.0.0"
        graph.iconclass = "fa fa-building"
        graph.nodegroups = []

        graph.root.name = "ROOT NODE"
        graph.root.description = "Test Root Node"
        graph.root.ontologyclass = "http://www.cidoc-crm.org/cidoc-crm/E21_Person"
        graph.root.datatype = "semantic"

        graph.save()

        graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P43_has_dimension",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )

        with self.assertRaises(GraphValidationError) as cm:
            graph.save()

    def test_graph_validation_of_widget_count(self):
        # Add missing CardXNodeXWidget instances to the graph
        # See commented out code in setUpTestData() where this should be done.
        default_widgets_by_datatype = {
            datatype.pk: datatype.defaultwidget
            for datatype in models.DDataType.objects.select_related("defaultwidget")
        }
        for node in self.node_node_type_graph.nodes.values():
            models.CardXNodeXWidget.objects.create(
                card=node.nodegroup.cardmodel_set.first(),
                node=node,
                widget=default_widgets_by_datatype[node.datatype],
            )

        self.node_node_type_graph.refresh_from_database()
        self.node_node_type_graph.has_unpublished_changes = True
        superfluous_widgets = {
            uid: models.CardXNodeXWidget(node=node)
            for uid, node in [
                (uuid.uuid4(), widget.node)
                for widget in self.node_node_type_graph.widgets.values()
            ]
        }
        self.node_node_type_graph.widgets |= superfluous_widgets
        self.node_node_type_graph.has_unpublished_changes = True

        with self.assertRaises(GraphValidationError) as cm:
            self.node_node_type_graph.validate()
        self.assertEqual(cm.exception.code, IntegrityCheck.TOO_MANY_WIDGETS.value)

    def test_add_resource_instance_lifecycle(self):
        resource_instance_lifecycle = {
            "id": "f7a0fd46-4c71-49cb-ae1e-778c96763440",
            "name": "Test Lifecycle",
            "resource_instance_lifecycle_states": [
                {
                    "id": "e2ac2a61-c140-43f5-bf65-3fe8ce47a594",
                    "name": "State 1",
                    "next_resource_instance_lifecycle_states": [
                        "0b52dbac-405a-49e0-9151-43ebf2100e6c"
                    ],
                    "previous_resource_instance_lifecycle_states": [],
                },
                {
                    "id": "0b52dbac-405a-49e0-9151-43ebf2100e6c",
                    "name": "State 2",
                    "next_resource_instance_lifecycle_states": [],
                    "previous_resource_instance_lifecycle_states": [
                        "e2ac2a61-c140-43f5-bf65-3fe8ce47a594"
                    ],
                },
            ],
        }

        graph = Graph.objects.create_graph(
            name="RESOURCE_INSTANCE_LIFECYCLE_TEST_GRAPH",
            is_resource=True,
        )
        graph.add_resource_instance_lifecycle(resource_instance_lifecycle)
        graph.save()

        lifecycle = models.ResourceInstanceLifecycle.objects.get(
            id="f7a0fd46-4c71-49cb-ae1e-778c96763440"
        )

        self.assertEqual(lifecycle.name, "Test Lifecycle")

        # Verify the states were created correctly
        state1 = models.ResourceInstanceLifecycleState.objects.get(
            id="e2ac2a61-c140-43f5-bf65-3fe8ce47a594"
        )
        state2 = models.ResourceInstanceLifecycleState.objects.get(
            id="0b52dbac-405a-49e0-9151-43ebf2100e6c"
        )
        self.assertEqual(state1.name, "State 1")
        self.assertEqual(state2.name, "State 2")

        # Verify the relationships between states
        self.assertEqual(
            list(state1.next_resource_instance_lifecycle_states.all()), [state2]
        )
        self.assertEqual(
            list(state2.previous_resource_instance_lifecycle_states.all()), [state1]
        )

        resource_instance_lifecycle_states = (
            lifecycle.resource_instance_lifecycle_states.all()
        )
        # Verify the lifecycle contains the states
        self.assertIn(state1, resource_instance_lifecycle_states)
        self.assertIn(state2, resource_instance_lifecycle_states)

    def test_geometry_config_persists_after_unpublishing_graph(self):

        models.GraphModel.objects.create(
            **{
                "name": "Test Graph",
                "graphid": "49a7eea8-2e2b-48e3-8b6e-650f25ec2954",
                "isresource": True,
                "slug": "test-graph",
            }
        )

        models.NodeGroup.objects.create(pk="88677159-dccf-4629-9210-f6a2a7463552")

        models.Node.objects.create(
            **{
                "name": "Top Node",
                "graph_id": "49a7eea8-2e2b-48e3-8b6e-650f25ec2954",
                "datatype": "semantic",
                "istopnode": True,
                "nodeid": "c1257d42-9275-40df-835e-5b99eee818fa",
            }
        )

        models.Node.objects.create(
            **{
                "name": "GeoJSON Node",
                "graph_id": "49a7eea8-2e2b-48e3-8b6e-650f25ec2954",
                "datatype": "geojson-feature-collection",
                "istopnode": False,
                "config": {
                    "fillColor": "rgba(130, 130, 130, 0.7)",
                },
                "nodeid": "88677159-dccf-4629-9210-f6a2a7463552",
                "nodegroup_id": "88677159-dccf-4629-9210-f6a2a7463552",
            }
        )

        models.Edge.objects.create(
            **{
                "domainnode_id": "c1257d42-9275-40df-835e-5b99eee818fa",
                "edgeid": "16a8ec0d-7d8c-422a-aa33-fac1ac3a07b0",
                "graph_id": "49a7eea8-2e2b-48e3-8b6e-650f25ec2954",
                "rangenode_id": "88677159-dccf-4629-9210-f6a2a7463552",
            }
        )

        graph = Graph.objects.get(pk="49a7eea8-2e2b-48e3-8b6e-650f25ec2954")
        admin = User.objects.get(username="admin")
        graph.create_draft_graph()
        graph.publish(user=admin)

        draft_graph = Graph.objects.get(slug="test-graph", source_identifier=graph.pk)
        draft_node = draft_graph.node_set.get(name="GeoJSON Node")
        draft_node.config["fillColor"] = "rgba(200, 130, 130, 0.7)"
        draft_node.save()
        draft_graph.refresh_from_database()

        graph = Graph.objects.get(slug="test-graph", source_identifier=None)
        graph.update_from_draft_graph(draft_graph)

        graph_from_db = Graph.objects.get(pk="49a7eea8-2e2b-48e3-8b6e-650f25ec2954")
        self.assertEqual(
            graph_from_db.nodes[
                uuid.UUID("88677159-dccf-4629-9210-f6a2a7463552")
            ].config["fillColor"],
            "rgba(200, 130, 130, 0.7)",
        )


class DraftGraphTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.SINGLE_NODE_GRAPHID = "22000000-0000-0000-0000-000000000000"
        cls.NODE_NODETYPE_GRAPHID = "22000000-0000-0000-0000-000000000001"
        cls.single_node_graph = cls.create_single_node_graph()
        cls.node_node_type_graph = cls.create_node_node_type_graph()
        cls.test_graph = cls.create_test_graph()

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
        return graph

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

        default_widgets_by_datatype = {
            datatype.pk: datatype.defaultwidget
            for datatype in models.DDataType.objects.select_related("defaultwidget")
        }
        for node_data in nodes_data:
            node = models.Node.objects.create(**node_data)
            models.CardXNodeXWidget.objects.create(
                card=card,
                node=node,
                widget=default_widgets_by_datatype[node.datatype],
            )

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

        cls.rootNode = test_graph.root
        return test_graph

    def _compare_serialized_updated_source_graph_and_serialized_draft_graph(
        self, serialized_updated_source_graph, serialized_draft_graph
    ):
        def filter_and_sort(entity, ignore_keys):
            if isinstance(entity, dict):
                return {
                    key: filter_and_sort(value, ignore_keys)
                    for key, value in entity.items()
                    if key not in ignore_keys
                }
            elif isinstance(entity, list):
                return [filter_and_sort(item, ignore_keys) for item in entity]
            else:
                return entity

        serialized_updated_source_nodes = {
            (
                node["source_identifier_id"]
                if node.get("source_identifier_id") not in [None, "None"]
                else node["nodeid"]
            ): node
            for node in serialized_updated_source_graph["nodes"]
        }
        serialized_editable_future_nodes = {
            (
                node["source_identifier_id"]
                if node.get("source_identifier_id") not in [None, "None"]
                else node["nodeid"]
            ): node
            for node in serialized_draft_graph["nodes"]
        }
        with self.subTest("nodes"):
            self.assertEqual(
                filter_and_sort(
                    serialized_updated_source_nodes,
                    ["graph_id", "nodeid", "nodegroup_id", "source_identifier_id"],
                ),
                filter_and_sort(
                    serialized_editable_future_nodes,
                    ["graph_id", "nodeid", "nodegroup_id", "source_identifier_id"],
                ),
            )

        serialized_updated_source_edges = {
            (
                edge["source_identifier_id"]
                if edge.get("source_identifier_id") not in [None, "None"]
                else edge["edgeid"]
            ): edge
            for edge in serialized_updated_source_graph["edges"]
        }
        serialized_editable_future_edges = {
            (
                edge["source_identifier_id"]
                if edge.get("source_identifier_id") not in [None, "None"]
                else edge["edgeid"]
            ): edge
            for edge in serialized_draft_graph["edges"]
        }
        with self.subTest("edges"):
            self.assertEqual(
                filter_and_sort(
                    serialized_updated_source_edges,
                    [
                        "graph_id",
                        "edgeid",
                        "domainnode_id",
                        "rangenode_id",
                        "source_identifier_id",
                    ],
                ),
                filter_and_sort(
                    serialized_editable_future_edges,
                    [
                        "graph_id",
                        "edgeid",
                        "domainnode_id",
                        "rangenode_id",
                        "source_identifier_id",
                    ],
                ),
            )

        serialized_updated_source_cards = {
            (
                card["source_identifier_id"]
                if card.get("source_identifier_id") not in [None, "None"]
                else card["cardid"]
            ): card
            for card in serialized_updated_source_graph["cards"]
        }
        serialized_editable_future_cards = {
            (
                card["source_identifier_id"]
                if card.get("source_identifier_id") not in [None, "None"]
                else card["cardid"]
            ): card
            for card in serialized_draft_graph["cards"]
        }
        with self.subTest("cards"):
            self.assertEqual(
                filter_and_sort(
                    serialized_updated_source_cards,
                    ["graph_id", "cardid", "nodegroup_id", "source_identifier_id"],
                ),
                filter_and_sort(
                    serialized_editable_future_cards,
                    ["graph_id", "cardid", "nodegroup_id", "source_identifier_id"],
                ),
            )

        serialized_updated_source_cards_x_nodes_x_widgets = {
            (
                card_x_node_x_widget["source_identifier_id"]
                if card_x_node_x_widget.get("source_identifier_id")
                not in [None, "None"]
                else card_x_node_x_widget["id"]
            ): card_x_node_x_widget
            for card_x_node_x_widget in serialized_updated_source_graph[
                "cards_x_nodes_x_widgets"
            ]
        }
        serialized_editable_future_cards_x_nodes_x_widgets = {
            (
                card_x_node_x_widget["source_identifier_id"]
                if card_x_node_x_widget.get("source_identifier_id")
                not in [None, "None"]
                else card_x_node_x_widget["id"]
            ): card_x_node_x_widget
            for card_x_node_x_widget in serialized_draft_graph[
                "cards_x_nodes_x_widgets"
            ]
        }
        with self.subTest("cards_x_nodes_x_widgets"):
            self.assertEqual(
                filter_and_sort(
                    serialized_updated_source_cards_x_nodes_x_widgets,
                    ["graph_id", "id", "card_id", "node_id", "source_identifier_id"],
                ),
                filter_and_sort(
                    serialized_editable_future_cards_x_nodes_x_widgets,
                    ["graph_id", "id", "card_id", "node_id", "source_identifier_id"],
                ),
            )

        with self.subTest("graph"):
            self.assertEqual(
                filter_and_sort(
                    serialized_updated_source_graph,
                    [
                        "graphid",
                        "cards",
                        "nodes",
                        "edges",
                        "nodegroups",
                        "functions",
                        "root",
                        "widgets",
                        "cards_x_nodes_x_widgets",
                        "resource_instance_lifecycle",
                        "resource_instance_lifecycle_id",
                        "source_identifier",
                        "source_identifier_id",
                        "publication_id",
                        "has_unpublished_changes",
                    ],
                ),
                filter_and_sort(
                    serialized_draft_graph,
                    [
                        "graphid",
                        "cards",
                        "nodes",
                        "edges",
                        "nodegroups",
                        "functions",
                        "root",
                        "widgets",
                        "cards_x_nodes_x_widgets",
                        "resource_instance_lifecycle",
                        "resource_instance_lifecycle_id",
                        "source_identifier",
                        "source_identifier_id",
                        "publication_id",
                        "has_unpublished_changes",
                    ],
                ),
            )

    def test_publish_sets_correct_has_unpublished_changes_value(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )

        source_graph.name = "TEST NAME"
        source_graph.save()
        source_graph.refresh_from_database()

        self.assertEqual(source_graph.name, "TEST NAME")
        self.assertTrue(source_graph.has_unpublished_changes)

        source_graph.publish()
        self.assertFalse(source_graph.has_unpublished_changes)

        draft_graph = Graph.objects.get(source_identifier=source_graph)
        self.assertFalse(draft_graph.has_unpublished_changes)

    def test_create_draft_graph_sets_correct_has_unpublished_changes_value(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )

        self.assertFalse(source_graph.has_unpublished_changes)

        source_graph.create_draft_graph()
        self.assertFalse(source_graph.has_unpublished_changes)

        draft_graph = Graph.objects.get(source_identifier=source_graph)
        self.assertFalse(draft_graph.has_unpublished_changes)

    def test_restore_state_from_serialized_graph(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )

        source_graph.name = "TEST NAME"
        source_graph.save()
        source_graph.refresh_from_database()

        self.assertEqual(source_graph.name, "TEST NAME")
        self.assertTrue(source_graph.has_unpublished_changes)

        published_graph = models.PublishedGraph.objects.get(
            publication=source_graph.publication,
            language="en",
        )

        source_graph = source_graph.restore_state_from_serialized_graph(
            published_graph.serialized_graph
        )

        self.assertFalse(source_graph.has_unpublished_changes)
        self.assertEqual(source_graph.name, "TEST RESOURCE")

    @mock.patch("arches.app.search.search.SearchEngine.create_mapping")
    def test_saving_draft_graph_does_not_create_es_mapping(self, mocked_create_mapping):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        result = source_graph.append_node()
        result["node"].datatype = "string"
        source_graph.save()
        mocked_create_mapping.assert_called_once()

        draft_graph = source_graph.create_draft_graph()
        draft_graph.save()

        mocked_create_mapping.assert_called_once()

    def test_update_empty_graph_from_draft_graph(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = Graph.objects.get(source_identifier=source_graph)

        draft_graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        draft_graph.save()
        self.assertTrue(draft_graph.has_unpublished_changes)

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        self.assertFalse(updated_source_graph.has_unpublished_changes)

        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(updated_source_graph)
        )

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_draft_graph
        )

    def test_update_graph_with_multiple_nodes_and_edges(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = Graph.objects.get(source_identifier=source_graph)

        draft_graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        draft_graph.save()

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        # update_from_draft_graph() leaves the prior draft graph in an unusable
        # state. So we fetch it again before working with it.
        draft_graph = Graph.objects.get(source_identifier=source_graph)

        for node in list(draft_graph.nodes.values()):
            if node.name == "Node Type":
                node_type_node = JSONDeserializer().deserialize(
                    JSONSerializer().serialize(node)
                )

        draft_graph.append_branch(
            "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as",
            graphid=self.SINGLE_NODE_GRAPHID,
            nodeid=node_type_node["nodeid"],
        )
        draft_graph.save()

        updated_source_graph = updated_source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = Graph.objects.get(source_identifier=updated_source_graph)

        serialized_updated_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(updated_source_graph)
        )

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_updated_draft_graph
        )

    def test_update_graph_with_permissions(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = Graph.objects.get(source_identifier=source_graph)

        draft_graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        draft_graph.save()

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )

        nodegroup = updated_source_graph.get_nodegroups()[:1][0]

        GroupObjectPermission.objects.create(
            group_id=1, content_object=nodegroup, permission_id=93
        )
        UserObjectPermission.objects.create(
            user_id=2, content_object=nodegroup, permission_id=94
        )
        # calling `*.objects.create()` does not set dirty flag
        updated_source_graph.has_unpublished_changes = True

        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(updated_source_graph)
        )

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_draft_graph
        )

    def test_update_graph_with_relatable_resources(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = source_graph.create_draft_graph()

        draft_graph.root.set_relatable_resources([source_graph.root.pk])
        draft_graph.root.save()
        draft_graph.save()

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        self.assertTrue(len(updated_source_graph.root.get_relatable_resources()))

        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(updated_source_graph)
        )

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_draft_graph
        )

    def test_create_draft_graphs_does_not_pollute_database(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = source_graph.create_draft_graph()

        draft_graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        draft_graph.save()

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )

        nodegroup_count_before = models.NodeGroup.objects.count()
        node_count_before = models.Node.objects.count()
        edge_count_before = models.Edge.objects.count()
        card_count_before = models.CardModel.objects.count()
        card_x_node_x_widget_count_before = models.CardXNodeXWidget.objects.count()

        updated_source_graph.create_draft_graph()

        nodegroup_count_after = models.NodeGroup.objects.count()
        node_count_after = models.Node.objects.count()
        edge_count_after = models.Edge.objects.count()
        card_count_after = models.CardModel.objects.count()
        card_x_node_x_widget_count_after = models.CardXNodeXWidget.objects.count()

        self.assertEqual(nodegroup_count_before, nodegroup_count_after)
        self.assertEqual(node_count_before, node_count_after)
        self.assertEqual(edge_count_before, edge_count_after)
        self.assertEqual(card_count_before, card_count_after)
        self.assertEqual(
            card_x_node_x_widget_count_before, card_x_node_x_widget_count_after
        )

    def test_deleting_source_graph_deletes_draft_graph_and_all_related_models(
        self,
    ):
        nodegroup_count_before = models.NodeGroup.objects.count()
        node_count_before = models.Node.objects.count()
        edge_count_before = models.Edge.objects.count()
        card_count_before = models.CardModel.objects.count()
        card_x_node_x_widget_count_before = models.CardXNodeXWidget.objects.count()
        resource_2_resource_constraints_count_before = (
            models.Resource2ResourceConstraint.objects.count()
        )

        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = source_graph.create_draft_graph()

        draft_graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        draft_graph.save()
        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )

        updated_source_graph.delete()

        nodegroup_count_after = models.NodeGroup.objects.count()
        node_count_after = models.Node.objects.count()
        edge_count_after = models.Edge.objects.count()
        card_count_after = models.CardModel.objects.count()
        card_x_node_x_widget_count_after = models.CardXNodeXWidget.objects.count()
        resource_2_resource_constraints_count_after = (
            models.Resource2ResourceConstraint.objects.count()
        )

        self.assertEqual(nodegroup_count_before, nodegroup_count_after)
        self.assertEqual(node_count_before, node_count_after)
        self.assertEqual(edge_count_before, edge_count_after)
        self.assertEqual(card_count_before, card_count_after)
        self.assertEqual(
            card_x_node_x_widget_count_before, card_x_node_x_widget_count_after
        )
        self.assertEqual(
            resource_2_resource_constraints_count_before,
            resource_2_resource_constraints_count_after,
        )

    def test_revert_draft_graph(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )

        draft_graph = source_graph.create_draft_graph()

        nodegroup_count_before = models.NodeGroup.objects.count()
        node_count_before = models.Node.objects.count()
        edge_count_before = models.Edge.objects.count()
        card_count_before = models.CardModel.objects.count()
        card_x_node_x_widget_count_before = models.CardXNodeXWidget.objects.count()

        draft_graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        draft_graph.save()

        source_graph.create_draft_graph()

        draft_graph = models.Graph.objects.get(source_identifier_id=source_graph.pk)

        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(source_graph)
        )

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_draft_graph
        )

        nodegroup_count_after = models.NodeGroup.objects.count()
        node_count_after = models.Node.objects.count()
        edge_count_after = models.Edge.objects.count()
        card_count_after = models.CardModel.objects.count()
        card_x_node_x_widget_count_after = models.CardXNodeXWidget.objects.count()

        self.assertEqual(nodegroup_count_before, nodegroup_count_after)
        self.assertEqual(node_count_before, node_count_after)
        self.assertEqual(edge_count_before, edge_count_after)
        self.assertEqual(card_count_before, card_count_after)
        self.assertEqual(
            card_x_node_x_widget_count_before, card_x_node_x_widget_count_after
        )

    def test_update_nodegroup(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = source_graph.create_draft_graph()

        draft_graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        draft_graph.save()

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        nodegroup_count_before = models.NodeGroup.objects.count()
        node_count_before = models.Node.objects.count()
        edge_count_before = models.Edge.objects.count()
        card_count_before = models.CardModel.objects.count()
        card_x_node_x_widget_count_before = models.CardXNodeXWidget.objects.count()

        nodegroup = draft_graph.get_nodegroups()[:1][0]
        nodegroup.cardinality = "1"
        nodegroup.save()

        updated_source_graph = updated_source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(updated_source_graph)
        )

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_draft_graph
        )

        nodegroup = updated_source_graph.get_nodegroups()[:1][0]
        self.assertEqual(nodegroup.cardinality, "1")

        nodegroup_count_after = models.NodeGroup.objects.count()
        node_count_after = models.Node.objects.count()
        edge_count_after = models.Edge.objects.count()
        card_count_after = models.CardModel.objects.count()
        card_x_node_x_widget_count_after = models.CardXNodeXWidget.objects.count()

        self.assertEqual(nodegroup_count_before, nodegroup_count_after)
        self.assertEqual(node_count_before, node_count_after)
        self.assertEqual(edge_count_before, edge_count_after)
        self.assertEqual(card_count_before, card_count_after)
        self.assertEqual(
            card_x_node_x_widget_count_before, card_x_node_x_widget_count_after
        )

    def test_update_node(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = source_graph.create_draft_graph()

        draft_graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        draft_graph.save()

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        nodegroup_count_before = models.NodeGroup.objects.count()
        node_count_before = models.Node.objects.count()
        edge_count_before = models.Edge.objects.count()
        card_count_before = models.CardModel.objects.count()
        card_x_node_x_widget_count_before = models.CardXNodeXWidget.objects.count()

        draft_graph.root.name = "UPDATED_NODE_NAME"

        updated_source_graph = updated_source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(updated_source_graph)
        )

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_draft_graph
        )

        self.assertEqual(updated_source_graph.root.name, "UPDATED_NODE_NAME")

        nodegroup_count_after = models.NodeGroup.objects.count()
        node_count_after = models.Node.objects.count()
        edge_count_after = models.Edge.objects.count()
        card_count_after = models.CardModel.objects.count()
        card_x_node_x_widget_count_after = models.CardXNodeXWidget.objects.count()

        self.assertEqual(nodegroup_count_before, nodegroup_count_after)
        self.assertEqual(node_count_before, node_count_after)
        self.assertEqual(edge_count_before, edge_count_after)
        self.assertEqual(card_count_before, card_count_after)
        self.assertEqual(
            card_x_node_x_widget_count_before, card_x_node_x_widget_count_after
        )

    def test_update_card(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = source_graph.create_draft_graph()

        draft_graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        draft_graph.save()

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        nodegroup_count_before = models.NodeGroup.objects.count()
        node_count_before = models.Node.objects.count()
        edge_count_before = models.Edge.objects.count()
        card_count_before = models.CardModel.objects.count()
        card_x_node_x_widget_count_before = models.CardXNodeXWidget.objects.count()

        original_card = [card for card in draft_graph.cards.values()][0]
        original_card.description = "UPDATED_CARD_DESCRIPTION"
        original_card.save()

        updated_source_graph = updated_source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(updated_source_graph)
        )

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_draft_graph
        )

        updated_card = [
            card
            for card in updated_source_graph.cards.values()
            if card.pk == original_card.source_identifier_id
        ][0]
        self.assertEqual(
            updated_card.description.value, '{"en": "UPDATED_CARD_DESCRIPTION"}'
        )

        nodegroup_count_after = models.NodeGroup.objects.count()
        node_count_after = models.Node.objects.count()
        edge_count_after = models.Edge.objects.count()
        card_count_after = models.CardModel.objects.count()
        card_x_node_x_widget_count_after = models.CardXNodeXWidget.objects.count()

        self.assertEqual(nodegroup_count_before, nodegroup_count_after)
        self.assertEqual(node_count_before, node_count_after)
        self.assertEqual(edge_count_before, edge_count_after)
        self.assertEqual(card_count_before, card_count_after)
        self.assertEqual(
            card_x_node_x_widget_count_before, card_x_node_x_widget_count_after
        )

    def test_update_widget(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = source_graph.create_draft_graph()

        draft_graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        draft_graph.save()

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        card = [card for card in draft_graph.cards.values()][0]
        old_draft_widget = (
            card.cardxnodexwidget_set.filter(
                node_id=card.nodegroup_id, source_identifier__isnull=False
            )
            .get()
            .source_identifier
        )
        new_draft_widget = models.CardXNodeXWidget.objects.create(
            card=card,
            node_id=card.nodegroup_id,
            widget=models.Widget.objects.first(),
            label="Widget name",
        )
        draft_graph.widgets.pop(old_draft_widget.pk)
        draft_graph.widgets[new_draft_widget.pk] = new_draft_widget

        draft_graph.save()

        updated_source_graph = updated_source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        nodegroup_count_before = models.NodeGroup.objects.count()
        node_count_before = models.Node.objects.count()
        edge_count_before = models.Edge.objects.count()
        card_count_before = models.CardModel.objects.count()
        card_x_node_x_widget_count_before = models.CardXNodeXWidget.objects.count()

        updated_widget = [
            widget
            for widget in draft_graph.widgets.values()
            if widget.source_identifier_id == new_draft_widget.pk
        ][0]
        updated_widget.label = "UPDATED_WIDGET_NAME"
        updated_widget.save()

        updated_source_graph = updated_source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(updated_source_graph)
        )

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_draft_graph
        )

        re_updated_widget = [
            widget
            for widget in draft_graph.widgets.values()
            if widget.source_identifier_id == updated_widget.source_identifier_id
        ][0]
        self.assertEqual(re_updated_widget.label.value, '{"en": "UPDATED_WIDGET_NAME"}')

        nodegroup_count_after = models.NodeGroup.objects.count()
        node_count_after = models.Node.objects.count()
        edge_count_after = models.Edge.objects.count()
        card_count_after = models.CardModel.objects.count()
        card_x_node_x_widget_count_after = models.CardXNodeXWidget.objects.count()

        self.assertEqual(nodegroup_count_before, nodegroup_count_after)
        self.assertEqual(node_count_before, node_count_after)
        self.assertEqual(edge_count_before, edge_count_after)
        self.assertEqual(card_count_before, card_count_after)
        self.assertEqual(
            card_x_node_x_widget_count_before, card_x_node_x_widget_count_after
        )

    def test_update_from_draft_graph_does_not_affect_resources(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = source_graph.create_draft_graph()

        nodegroup = models.NodeGroup.objects.create()
        string_node = models.Node.objects.create(
            pk=nodegroup.pk,
            graph=source_graph,
            name="String Node",
            datatype="string",
            istopnode=False,
            nodegroup=nodegroup,
        )
        resource_instance_node = models.Node.objects.create(
            graph=source_graph,
            name="Resource Node",
            datatype="resource-instance",
            istopnode=True,
        )

        resource = models.ResourceInstance.objects.create(graph=source_graph)
        tile = models.TileModel.objects.create(
            nodegroup_id=nodegroup.pk,
            resourceinstance=resource,
            data={
                str(string_node.pk): {
                    "en": {"value": "test value", "direction": "ltr"},
                },
                str(resource_instance_node.pk): {
                    "resourceId": str(resource.pk),
                    "ontologyProperty": "",
                    "inverseOntologyProperty": "",
                },
            },
            sortorder=0,
        )

        serialized_resource = JSONDeserializer().deserialize(
            JSONSerializer().serialize(resource)
        )
        serialized_tile = JSONDeserializer().deserialize(
            JSONSerializer().serialize(tile)
        )

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        resource_from_database = models.ResourceInstance.objects.get(pk=resource.pk)
        tile_from_database = models.TileModel.objects.get(pk=tile.pk)

        serialized_resource_from_database = JSONDeserializer().deserialize(
            JSONSerializer().serialize(resource_from_database)
        )
        serialized_tile_from_database = JSONDeserializer().deserialize(
            JSONSerializer().serialize(tile_from_database)
        )

        self.assertEqual(serialized_resource, serialized_resource_from_database)
        self.assertEqual(serialized_tile, serialized_tile_from_database)

    def test_placing_node_in_separate_card_does_not_pollute_database(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = source_graph.create_draft_graph()

        draft_graph.append_branch(
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            graphid=self.NODE_NODETYPE_GRAPHID,
        )
        draft_graph.save()

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        node = [
            node for node in draft_graph.nodes.values() if node.alias == "node_type"
        ][0]

        nodegroup_count_before = models.NodeGroup.objects.count()

        source_identifier_id = node.source_identifier_id
        original_nodegroup_id = node.nodegroup_id
        updated_nodegroup_id = node.pk

        models.NodeGroup.objects.create(
            **{
                "cardinality": "n",
                "legacygroupid": "",
                "nodegroupid": str(updated_nodegroup_id),
                "parentnodegroup_id": None,
            }
        ).save()

        node.nodegroup_id = updated_nodegroup_id
        node.save()

        updated_source_graph = updated_source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        # a source_graph nodegroup and an draft_graph nodegroup have been created
        self.assertEqual(nodegroup_count_before, models.NodeGroup.objects.count() - 2)

        node = [
            node
            for node in draft_graph.nodes.values()
            if node.source_identifier_id == source_identifier_id
        ][0]
        node.nodegroup_id = original_nodegroup_id
        node.save()

        updated_source_graph = updated_source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(updated_source_graph)
        )

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_draft_graph
        )

        # the source_graph nodegroup and the draft_graph nodegroup have been deleted
        self.assertEqual(nodegroup_count_before, models.NodeGroup.objects.count())

    def test_can_update_graph_slug(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = source_graph.create_draft_graph()

        # test adding slug
        draft_graph.slug = "test-resource"
        draft_graph.save()

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(updated_source_graph)
        )

        self.assertEqual(serialized_updated_source_graph["slug"], "test-resource")

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_draft_graph
        )

        # test updating slug
        draft_graph.slug = "test-resource-two"
        draft_graph.save()

        updated_source_graph = updated_source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(updated_source_graph)
        )

        self.assertEqual(serialized_updated_source_graph["slug"], "test-resource-two")

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_draft_graph
        )

    def test_can_update_other_data_in_graph_with_slug(self):
        source_graph = Graph.objects.create_graph(
            name="TEST RESOURCE",
            is_resource=True,
        )
        draft_graph = source_graph.create_draft_graph()

        draft_graph.slug = "test-resource"
        draft_graph.save()

        updated_source_graph = source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        draft_graph.name = "TEST RESOURCE TWO"
        draft_graph.save()

        updated_source_graph = updated_source_graph.update_from_draft_graph(
            draft_graph=draft_graph
        )
        draft_graph = updated_source_graph.create_draft_graph()

        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )
        serialized_updated_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(updated_source_graph)
        )

        self.assertEqual(serialized_updated_source_graph["name"], "TEST RESOURCE TWO")

        self._compare_serialized_updated_source_graph_and_serialized_draft_graph(
            serialized_updated_source_graph, serialized_draft_graph
        )
