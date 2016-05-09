'''
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
'''

import os, json, uuid
from tests import test_settings
from tests.base_test import ArchesTestCase
from arches.management.commands.package_utils import resource_graphs
from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.utils.betterJSONSerializer import JSONSerializer


class GraphTests(ArchesTestCase):

    @classmethod
    def setUpClass(cls):
        resource_graphs.load_graphs(os.path.join(test_settings.RESOURCE_GRAPH_LOCATIONS))

        cls.NODE_NODETYPE_GRAPHMETADATAID = '22000000-0000-0000-0000-000000000001'
        cls.SINGLE_NODE_GRAPHMETADATAID = '22000000-0000-0000-0000-000000000000'
        cls.HERITAGE_RESOURCE_FIXTURE = 'd8f4db21-343e-4af3-8857-f7322dc9eb4b'

    @classmethod
    def tearDownClass(cls):
        root = models.Node.objects.get(pk=cls.HERITAGE_RESOURCE_FIXTURE)
        cls.deleteGraph(root)

    def setUp(self):
        newid = uuid.uuid1()
        newgroup = models.NodeGroup.objects.create(
            pk=newid,
            cardinality='1'
        )
        metadata = models.GraphMetadata.objects.create(
            name="TEST GRAPH",
            subtitle="ARCHES TEST GRAPH",
            author="Arches",
            description="ARCHES TEST GRAPH",
            version="v1.0.0",
            isresource=True,
            isactive=False,
            iconclass="fa fa-building"
        )
        self.rootNode = models.Node.objects.create(
            pk=newid,
            name='ROOT NODE',
            description='Test Root Node',
            istopnode=True,
            ontologyclass_id='c03db431-4564-34eb-ba86-4c8169e4276c',
            datatype='semantic',
            nodegroup=newgroup,
            graphmetadata=metadata
        )

    def tearDown(self):
        self.deleteGraph(self.rootNode)

    def test_graph_doesnt_polute_db(self):
        """
        test that the mere act of creating a Graph instance
        doesn't save anything to the database

        """

        graph_obj = {
            "metadata": {
                "name": "TEST GRAPH",
                "subtitle": "ARCHES TEST GRAPH",
                "author": "Arches",
                "description": "ARCHES TEST GRAPH",
                "version": "v1.0.0",
                "isresource": True,
                "isactive": False,
                "iconclass": "fa fa-building"
            },
            'nodes':[{
                "status": None,
                "description": "",
                "name": "ROOT_NODE",
                "istopnode": True,
                "ontologyclass": "",
                "nodeid": "55555555-343e-4af3-8857-f7322dc9eb4b",
                "nodegroupid": "55555555-343e-4af3-8857-f7322dc9eb4b",
                "datatype": "semantic",
                "cardinality": "1"
            },{
                "status": None,
                "description": "",
                "name": "NODE_NAME",
                "istopnode": False,
                "ontologyclass": "",
                "nodeid": "66666666-24c9-4226-bde2-2c40ee60a26c",
                "nodegroupid": "55555555-343e-4af3-8857-f7322dc9eb4b",
                "datatype": "string",
                "cardinality": "n"
            }],
            'edges':[{
                "rangenodeid": "66666666-24c9-4226-bde2-2c40ee60a26c",
                "name": "",
                "edgeid": "11111111-d50f-11e5-8754-80e6500ee4e4",
                "domainnodeid": "55555555-343e-4af3-8857-f7322dc9eb4b",
                "ontologyproperty": "P2",
                "description": ""
            }]
        }

        nodes_count_before = models.Node.objects.count()
        edges_count_before = models.Edge.objects.count()
        nodegroups_count_before = models.NodeGroup.objects.count()

        graph = Graph(graph_obj)

        self.assertEqual(models.Node.objects.count()-nodes_count_before, 0)
        self.assertEqual(models.Edge.objects.count()-edges_count_before, 0)
        self.assertEqual(models.NodeGroup.objects.count()-nodegroups_count_before, 0)

    def test_nodes_are_byref(self):
        """
        test that the nodes referred to in the Graph.edges are exact references to
        the nodes as opposed to a node with the same attribute values

        """

        graph = Graph(self.HERITAGE_RESOURCE_FIXTURE)

        node_mapping = {nodeid:id(node) for nodeid, node in graph.nodes.iteritems()}

        for key, edge in graph.edges.iteritems():
            self.assertEqual(node_mapping[edge.domainnode.pk], id(edge.domainnode))
            self.assertEqual(node_mapping[edge.rangenode.pk], id(edge.rangenode))

        for key, node in graph.nodes.iteritems():
            for key, edge in graph.edges.iteritems():
                newid = uuid.uuid4()
                if (edge.domainnode.pk == node.pk):
                    node.pk = newid
                    self.assertEqual(edge.domainnode.pk, newid)
                elif (edge.rangenode.pk == node.pk):
                    node.pk = newid
                    self.assertEqual(edge.rangenode.pk, newid)

    def test_copy_graph(self):
        """
        test that a copy of a graph has the same number of nodes and edges and that the primary keys have been changed
        and that the actual node references are different

        """

        graph = Graph(self.HERITAGE_RESOURCE_FIXTURE)
        graph_copy = graph.copy()

        self.assertEqual(len(graph.nodes), len(graph_copy.nodes))
        self.assertEqual(len(graph.edges), len(graph_copy.edges))
        self.assertEqual(len(graph.nodegroups), len(graph_copy.nodegroups))

        def findNodeByName(graph, name):
            for key, node in graph.nodes.iteritems():
                if node.name == name:
                    return node
            return None

        for key, node in graph.nodes.iteritems():
            node_copy = findNodeByName(graph_copy, node.name)
            self.assertIsNotNone(node_copy)
            self.assertNotEqual(node.pk, node_copy.pk)
            self.assertNotEqual(id(node), id(node_copy))
            self.assertEqual(node.is_collector(), node_copy.is_collector())
            if node.nodegroup != None:
                self.assertNotEqual(node.nodegroup, node_copy.nodegroup)

        for key, newedge in graph_copy.edges.iteritems():
            self.assertIsNotNone(graph_copy.nodes[newedge.domainnode_id])
            self.assertIsNotNone(graph_copy.nodes[newedge.rangenode_id])
            self.assertEqual(newedge.domainnode, graph_copy.nodes[newedge.domainnode.pk])
            self.assertEqual(newedge.rangenode, graph_copy.nodes[newedge.rangenode.pk])
            with self.assertRaises(KeyError):
                graph.edges[newedge.pk]

    def test_branch_append(self):
        """
        test if a branch is properly appended to a graph

        """

        nodes_count_before = models.Node.objects.count()
        edges_count_before = models.Edge.objects.count()
        nodegroups_count_before = models.NodeGroup.objects.count()

        graph = Graph(self.rootNode)
        graph.append_branch('P1', graphmetadataid=self.NODE_NODETYPE_GRAPHMETADATAID)
        graph.save()

        self.assertEqual(len(graph.nodes), 3)
        self.assertEqual(len(graph.edges), 2)
        self.assertEqual(len(graph.nodegroups), 2)

        self.assertEqual(models.Node.objects.count()-nodes_count_before, 2)
        self.assertEqual(models.Edge.objects.count()-edges_count_before, 2)
        self.assertEqual(models.NodeGroup.objects.count()-nodegroups_count_before, 1)

        for key, edge in graph.edges.iteritems():
            self.assertIsNotNone(graph.nodes[edge.domainnode_id])
            self.assertIsNotNone(graph.nodes[edge.rangenode_id])
            self.assertEqual(edge.domainnode, graph.nodes[edge.domainnode.pk])
            self.assertEqual(edge.rangenode, graph.nodes[edge.rangenode.pk])

        for key, node in graph.nodes.iteritems():
            if node.istopnode:
                self.assertEqual(node, self.rootNode)


        appended_branch = graph.append_branch('P1', graphmetadataid=self.SINGLE_NODE_GRAPHMETADATAID)
        graph.save()
        self.assertEqual(len(graph.nodes), 4)
        self.assertEqual(len(graph.edges), 3)
        self.assertEqual(len(graph.nodegroups), 2)

        self.assertEqual(models.Node.objects.count()-nodes_count_before, 3)
        self.assertEqual(models.Edge.objects.count()-edges_count_before, 3)
        self.assertEqual(models.NodeGroup.objects.count()-nodegroups_count_before, 1)

        self.assertEqual(appended_branch.root.nodegroup,self.rootNode.nodegroup)

    def test_move_node(self):
        """
        test if a node can be successfully moved to another node in the graph

        """

        # test moving a single node to another branch
        # this node should be grouped with it's new parent nodegroup
        graph = Graph(self.rootNode)
        branch_one = graph.append_branch('P1', graphmetadataid=self.NODE_NODETYPE_GRAPHMETADATAID)
        branch_two = graph.append_branch('P1', graphmetadataid=self.NODE_NODETYPE_GRAPHMETADATAID)
        branch_three = graph.append_branch('P1', graphmetadataid=self.SINGLE_NODE_GRAPHMETADATAID)

        branch_three_nodeid = branch_three.nodes.iterkeys().next()
        branch_one_rootnodeid = branch_one.root.nodeid
        graph.move_node(branch_three_nodeid, 'P1', branch_one_rootnodeid)

        new_parent_nodegroup = None
        moved_branch_nodegroup = None
        for node_id, node in graph.nodes.iteritems():
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
        graph.move_node(branch_one_rootnodeid, 'P1', branch_two_rootnodeid)

        new_parent_nodegroup = None
        moved_branch_nodegroup = None
        for node_id, node in graph.nodes.iteritems():
            if node_id == branch_two_rootnodeid:
                new_parent_nodegroup = node.nodegroup
            if node_id == branch_one_rootnodeid:
                moved_branch_nodegroup = node.nodegroup

        self.assertIsNotNone(new_parent_nodegroup)
        self.assertIsNotNone(moved_branch_nodegroup)
        self.assertNotEqual(new_parent_nodegroup, moved_branch_nodegroup)

        updated_edge = None
        for edge_id, edge in graph.edges.iteritems():
            if (edge.domainnode_id == branch_two_rootnodeid and
                edge.rangenode_id == branch_one_rootnodeid):
                updated_edge = edge

        self.assertIsNotNone(updated_edge)

        # save and retrieve the graph from the database and confirm that
        # the graph shape has been saved properly
        graph.save()
        graph = Graph(self.rootNode)
        tree = graph.get_tree()

        self.assertEqual(len(tree['children']), 1)
        level_one_node = tree['children'][0]

        self.assertEqual(branch_two_rootnodeid, level_one_node['node'].nodeid)
        self.assertEqual(len(level_one_node['children']), 2)
        for child in level_one_node['children']:
            if child['node'].nodeid == branch_one_rootnodeid:
                self.assertEqual(len(child['children']), 2)
                found_branch_three = False
                for child in child['children']:
                    if child['node'].nodeid == branch_three_nodeid:
                        found_branch_three = True
                self.assertTrue(found_branch_three)
            else:
                self.assertEqual(len(child['children']), 0)


# Pressumed final graph shape
#
#                                                self.rootNode
#                                                      |
#                                            branch_two_rootnodeid (Node)
#                                                    /   \
#                         branch_one_rootnodeid (Node)    branch_two_child (NodeType)
#                                 /   \
# branch_one_childnodeid (NodeType)    branch_three_nodeid (Node)
