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
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


class GraphTests(ArchesTestCase):

    @classmethod
    def setUpClass(cls):
        resource_graphs.load_graphs(os.path.join(test_settings.RESOURCE_GRAPH_LOCATIONS))

        cls.NODE_NODETYPE_GRAPHID = '22000000-0000-0000-0000-000000000001'
        cls.SINGLE_NODE_GRAPHID = '22000000-0000-0000-0000-000000000000'
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
        metadata = models.Graph.objects.create(
            name="TEST GRAPH",
            subtitle="ARCHES TEST GRAPH",
            author="Arches",
            description="ARCHES TEST GRAPH",
            ontology_id="e6e8db47-2ccf-11e6-927e-b8f6b115d7dd",
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
            ontologyclass='E1_CRM_Entity',
            datatype='semantic',
            nodegroup=newgroup,
            graph=metadata
        )

    def tearDown(self):
        self.deleteGraph(self.rootNode)

    def test_new_graph(self):
        name = "TEST NEW GRAPH"
        author = "ARCHES TEST"
        graph = Graph.new(name=name,is_resource=True,author=author)
        self.assertEqual(graph.metadata.name, name)
        self.assertEqual(graph.metadata.author, author)
        self.assertTrue(graph.metadata.isresource)
        self.assertFalse(graph.root.is_collector())
        self.assertEqual(len(graph.nodes), 1)

        graph = Graph.new(name=name,is_resource=False,author=author)
        self.assertEqual(graph.metadata.name, name)
        self.assertEqual(graph.metadata.author, author)
        self.assertFalse(graph.metadata.isresource)
        self.assertTrue(graph.root.is_collector())
        self.assertEqual(len(graph.nodes), 1)

    def test_graph_doesnt_polute_db(self):
        """
        test that the mere act of creating a Graph instance doesn't save anything to the database

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
                "nodegroup_id": "55555555-343e-4af3-8857-f7322dc9eb4b",
                "datatype": "semantic",
                "cardinality": "1"
            },{
                "status": None,
                "description": "",
                "name": "NODE_NAME",
                "istopnode": False,
                "ontologyclass": "",
                "nodeid": "66666666-24c9-4226-bde2-2c40ee60a26c",
                "nodegroup_id": "55555555-343e-4af3-8857-f7322dc9eb4b",
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
        root = models.Node.objects.get(pk=self.HERITAGE_RESOURCE_FIXTURE)
        graph = Graph(root)

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
        root = models.Node.objects.get(pk=self.HERITAGE_RESOURCE_FIXTURE)
        graph = Graph(root)
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

    def test_branch_append_with_ontology(self):
        """
        test if a branch is properly appended to a graph that defines an ontology

        """

        nodes_count_before = models.Node.objects.count()
        edges_count_before = models.Edge.objects.count()
        nodegroups_count_before = models.NodeGroup.objects.count()

        graph = Graph(self.rootNode)
        graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
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
            self.assertIsNotNone(edge.ontologyproperty)

        for key, node in graph.nodes.iteritems():
            self.assertIsNotNone(node.ontologyclass)
            if node.istopnode:
                self.assertEqual(node, self.rootNode)


        appended_branch = graph.append_branch('P1_is_identified_by', graphid=self.SINGLE_NODE_GRAPHID)
        graph.save()
        self.assertEqual(len(graph.nodes), 4)
        self.assertEqual(len(graph.edges), 3)
        self.assertEqual(len(graph.nodegroups), 2)

        self.assertEqual(models.Node.objects.count()-nodes_count_before, 3)
        self.assertEqual(models.Edge.objects.count()-edges_count_before, 3)
        self.assertEqual(models.NodeGroup.objects.count()-nodegroups_count_before, 1)

        self.assertEqual(appended_branch.root.nodegroup,self.rootNode.nodegroup)

    def test_manage_nodegroups_during_node_update(self):
        """
        test to make sure that node groups are properly managed when changing a nodegroup value on a node being updated 
        
        """

        # create a graph, append the node/node type graph and confirm is has the correct 
        # number of nodegroups then remove the appended branches group and reconfirm that 
        # the proper number of groups are properly relfected in the graph

        graph = Graph(self.rootNode)
        graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        self.assertEqual(len(graph.nodegroups), 2)

        node_to_update = None
        for node_id, node in graph.nodes.iteritems():
            if node.name == 'Node':
                node_to_update = JSONDeserializer().deserialize(JSONSerializer().serialize(node))
            if node.name == 'Node Type':
                node_type_node = JSONDeserializer().deserialize(JSONSerializer().serialize(node))

        node_to_update['nodegroup_id'] = None
        graph.update_node(node_to_update)
        self.assertEqual(len(graph.nodegroups), 1)
        for node_id, node in graph.nodes.iteritems():
            self.assertEqual(graph.root.nodegroup, node.nodegroup)

        graph.append_branch('P1_is_identified_by', nodeid=node_type_node['nodeid'], graphid=self.NODE_NODETYPE_GRAPHID)
        self.assertEqual(len(graph.nodegroups), 2)

        for edge_id, edge in graph.edges.iteritems():
            if str(edge.domainnode_id) == str(node_type_node['nodeid']):
                child_nodegroup_node = JSONDeserializer().deserialize(JSONSerializer().serialize(edge.rangenode))

        child_nodegroup_node['nodegroup_id'] = None
        graph.update_node(child_nodegroup_node)
        self.assertEqual(len(graph.nodegroups), 1)
        for node_id, node in graph.nodes.iteritems():
            self.assertEqual(graph.root.nodegroup, node.nodegroup)

        node_to_update['nodegroup_id'] = node_to_update['nodeid']
        graph.update_node(node_to_update)
        self.assertEqual(len(graph.nodegroups), 2)
        children = graph.get_child_nodes(node_to_update['nodeid'])
        for child in children:
            self.assertEqual(child.nodegroup_id, node_to_update['nodegroup_id'])

        child_nodegroup_node['nodegroup_id'] = child_nodegroup_node['nodeid']
        graph.update_node(child_nodegroup_node)
        self.assertEqual(len(graph.nodegroups), 3)
        children = graph.get_child_nodes(child_nodegroup_node['nodeid'])
        for child in children:
            self.assertEqual(child.nodegroup_id, child_nodegroup_node['nodegroup_id'])

    def test_move_node(self):
        """
        test if a node can be successfully moved to another node in the graph

        """

        # test moving a single node to another branch
        # this node should be grouped with it's new parent nodegroup
        graph = Graph(self.rootNode)
        branch_one = graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        branch_two = graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        branch_three = graph.append_branch('P1_is_identified_by', graphid=self.SINGLE_NODE_GRAPHID)

        branch_three_nodeid = branch_three.nodes.iterkeys().next()
        branch_one_rootnodeid = branch_one.root.nodeid
        graph.move_node(branch_three_nodeid, 'P1_is_identified_by', branch_one_rootnodeid)

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
        graph.move_node(branch_one_rootnodeid, 'P1_is_identified_by', branch_two_rootnodeid)

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

    def test_get_valid_ontology_classes(self):
        """
        test to see if we return the proper ontology classes for a graph that uses an ontology system

        """

        graph = Graph(self.rootNode)
        ret = graph.get_valid_ontology_classes(nodeid=self.rootNode.nodeid)
        self.assertTrue(len(ret) == 1)

        self.assertEqual(ret[0]['ontology_property'], '')
        self.assertEqual(len(ret[0]['ontology_classes']), models.OntologyClass.objects.filter(ontology_id=graph.metadata.ontology_id).count())

    def test_get_valid_ontology_classes_on_resource_with_no_ontology_set(self):
        """
        test to see if we return the proper ontology classes for a graph that doesn't use an ontology system

        """

        self.rootNode.graph.ontology_id = None
        graph = Graph(self.rootNode)
        ret = graph.get_valid_ontology_classes(nodeid=self.rootNode.nodeid)
        self.assertTrue(len(ret) == 0)

    def test_append_branch_to_resource_with_no_ontology_system(self):
        """
        test to see that we remove all ontologyclass and ontologyproperty references when appending a
        graph that uses an ontolgoy system to a graph that doesn't

        """

        graph = Graph(self.rootNode)
        graph.clear_ontology_references()
        graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        for node_id, node in graph.nodes.iteritems():
            self.assertTrue(node.ontologyclass is None)
        for edge_id, edge in graph.edges.iteritems():
            self.assertTrue(edge.ontologyproperty is None)

    def test_delete_graph(self):
        """
        test the graph delete method

        """
        graph = Graph(self.NODE_NODETYPE_GRAPHID)
        self.assertEqual(len(graph.nodes),2)
        self.assertEqual(len(graph.edges),1)
        graph.delete()

        node_count = models.Node.objects.filter(graph_id=self.NODE_NODETYPE_GRAPHID).count()
        edge_count = models.Edge.objects.filter(graph_id=self.NODE_NODETYPE_GRAPHID).count()
        self.assertEqual(node_count,0)
        self.assertEqual(edge_count,0)
