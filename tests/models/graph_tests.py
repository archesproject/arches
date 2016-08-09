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
from arches.app.models.graph import Graph, ValidationError
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
        graph = Graph.new()
        graph.name = "TEST GRAPH"
        graph.subtitle = "ARCHES TEST GRAPH"
        graph.author = "Arches"
        graph.description = "ARCHES TEST GRAPH"
        graph.ontology_id = "e6e8db47-2ccf-11e6-927e-b8f6b115d7dd"
        graph.version = "v1.0.0"
        graph.isactive = False
        graph.iconclass = "fa fa-building"
        graph.save()

        graph.root.name = 'ROOT NODE'
        graph.root.description = 'Test Root Node'
        graph.root.ontologyclass = 'E1_CRM_Entity'
        graph.root.datatype = 'semantic'
        graph.root.save()

        self.rootNode = graph.root

    def tearDown(self):
        self.deleteGraph(self.rootNode)

    def test_new_graph(self):
        name = "TEST NEW GRAPH"
        author = "ARCHES TEST"
        graph = Graph.new(name=name,is_resource=True,author=author)
        self.assertEqual(graph.name, name)
        self.assertEqual(graph.author, author)
        self.assertTrue(graph.isresource)
        self.assertFalse(graph.root.is_collector)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(len(graph.cards), 0)
        self.assertEqual(len(graph.get_nodegroups()), 0)

        graph = Graph.new(name=name,is_resource=False,author=author)
        self.assertEqual(graph.name, name)
        self.assertEqual(graph.author, author)
        self.assertFalse(graph.isresource)
        self.assertTrue(graph.root.is_collector)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(len(graph.cards), 1)
        self.assertEqual(len(graph.get_nodegroups()), 1)

    def test_graph_doesnt_polute_db(self):
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
            'nodes':[{
                "status": None,
                "description": "",
                "name": "ROOT_NODE",
                "istopnode": True,
                "ontologyclass": "",
                "nodeid": "55555555-343e-4af3-8857-f7322dc9eb4b",
                "nodegroup_id": "",
                "datatype": "semantic"
            },{
                "status": None,
                "description": "",
                "name": "NODE_NAME",
                "istopnode": False,
                "ontologyclass": "",
                "nodeid": "66666666-24c9-4226-bde2-2c40ee60a26c",
                "nodegroup_id": "66666666-24c9-4226-bde2-2c40ee60a26c",
                "datatype": "string"
            }],
            'edges':[{
                "rangenode_id": "66666666-24c9-4226-bde2-2c40ee60a26c",
                "name": "",
                "edgeid": "11111111-d50f-11e5-8754-80e6500ee4e4",
                "domainnode_id": "55555555-343e-4af3-8857-f7322dc9eb4b",
                "ontologyproperty": "P2",
                "description": ""
            }],
            'cards':[{
                "name": "NODE_NAME",
                "description": "",
                "instructions": "",
                "helptext": "",
                "cardinality": "n",
                "nodegroup_id": "66666666-24c9-4226-bde2-2c40ee60a26c"
            }]
        }

        nodes_count_before = models.Node.objects.count()
        edges_count_before = models.Edge.objects.count()
        cards_count_before = models.CardModel.objects.count()
        nodegroups_count_before = models.NodeGroup.objects.count()

        graph = Graph(graph_obj)

        self.assertEqual(models.Node.objects.count()-nodes_count_before, 0)
        self.assertEqual(models.Edge.objects.count()-edges_count_before, 0)
        self.assertEqual(models.CardModel.objects.count()-cards_count_before, 0)
        self.assertEqual(models.NodeGroup.objects.count()-nodegroups_count_before, 0)
        self.assertEqual(graph_obj['name'], graph.name)
        self.assertEqual(graph_obj['subtitle'], graph.subtitle)
        self.assertEqual(graph_obj['author'], graph.author)
        self.assertEqual(graph_obj['description'], graph.description)
        self.assertEqual(graph_obj['version'], graph.version)
        self.assertEqual(graph_obj['isresource'], graph.isresource)
        self.assertEqual(graph_obj['isactive'], graph.isactive)
        self.assertEqual(graph_obj['iconclass'], graph.iconclass)

    def test_nodes_are_byref(self):
        """
        test that the nodes referred to in the Graph.edges are exact references to
        the nodes as opposed to a node with the same attribute values

        """
        root = models.Node.objects.get(pk=self.HERITAGE_RESOURCE_FIXTURE)
        graph = Graph.objects.get(graphid=root.graph.graphid)

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

        graph = Graph.new(name='TEST RESOURCE')
        graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        graph_copy = graph.copy()

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
                parentnodegroup_copy = nodegroup;
            else:
                childnodegroup_copy = nodegroup
        self.assertTrue(parentnodegroup_copy.parentnodegroup is None)
        self.assertEqual(childnodegroup_copy.parentnodegroup, parentnodegroup_copy)
        self.assertFalse(parentnodegroup_copy.parentnodegroup_id)
        self.assertEqual(childnodegroup_copy.parentnodegroup_id, parentnodegroup_copy.pk)

        # assert the copied node groups are not equal to the originals
        for nodegroup in graph.get_nodegroups():
            if graph.nodes[nodegroup.pk] is graph.root:
                parentnodegroup = nodegroup;
            else:
                childnodegroup = nodegroup

        self.assertNotEqual(parentnodegroup, parentnodegroup_copy)
        self.assertNotEqual(parentnodegroup.pk, parentnodegroup_copy.pk)
        self.assertNotEqual(childnodegroup, childnodegroup_copy)
        self.assertNotEqual(childnodegroup.pk, childnodegroup_copy.pk)

        # assert the nodegroups attached to the cards are heirarchically correct
        for card in graph_copy.cards.itervalues():
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
            for node in graph.nodes.itervalues():
                if node.name == name:
                    return node
            return None

        def findCardByName(graph, name):
            for card in graph.cards.itervalues():
                if card.name == name:
                    return card
            return None

        for node in graph.nodes.itervalues():
            node_copy = findNodeByName(graph_copy, node.name)
            self.assertIsNotNone(node_copy)
            self.assertNotEqual(node.pk, node_copy.pk)
            self.assertNotEqual(id(node), id(node_copy))
            self.assertEqual(node.is_collector, node_copy.is_collector)
            if node.nodegroup != None:
                self.assertNotEqual(node.nodegroup, node_copy.nodegroup)

        for card in graph.cards.itervalues():
            card_copy = findCardByName(graph_copy, card.name)
            self.assertIsNotNone(card_copy)
            self.assertNotEqual(card.pk, card_copy.pk)
            self.assertNotEqual(id(card), id(card_copy))
            self.assertNotEqual(card.nodegroup, card_copy.nodegroup)

        for newedge in graph_copy.edges.itervalues():
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

        appended_graph = graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        graph.save()

        self.assertEqual(len(graph.nodes), 3)
        self.assertEqual(len(graph.edges), 2)
        self.assertEqual(len(graph.cards), 2)
        self.assertEqual(len(graph.get_nodegroups()), 2)

        self.assertEqual(models.Node.objects.count()-nodes_count_before, 2)
        self.assertEqual(models.Edge.objects.count()-edges_count_before, 2)
        self.assertEqual(models.CardModel.objects.count()-cards_count_before, 1)
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


        # confirm that a non-grouped node takes on the parent group when appended
        appended_branch = graph.append_branch('P1_is_identified_by', graphid=self.SINGLE_NODE_GRAPHID)
        self.assertEqual(len(graph.nodes), 4)
        self.assertEqual(len(graph.edges), 3)
        self.assertEqual(len(graph.cards), 2)
        self.assertEqual(len(graph.get_nodegroups()), 2)
        self.assertEqual(appended_branch.root.nodegroup, self.rootNode.nodegroup)

        graph.save()
        self.assertEqual(models.Node.objects.count()-nodes_count_before, 3)
        self.assertEqual(models.Edge.objects.count()-edges_count_before, 3)
        self.assertEqual(models.CardModel.objects.count()-cards_count_before, 1)
        self.assertEqual(models.NodeGroup.objects.count()-nodegroups_count_before, 1)

    def test_rules_for_appending(self):
        """
        test the rules that control the appending of branches to graphs

        """

        graph = Graph.objects.get(node=self.rootNode)
        graph.isresource = True
        self.assertIsNotNone(graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID))

        # try to append to any other node that is not the root
        for node in graph.nodes.itervalues():
            if node is not graph.root:
                with self.assertRaises(ValidationError):
                    graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID, nodeid=node.nodeid)

        # try to append a non-grouped graph
        with self.assertRaises(ValidationError):
            graph.append_branch('P1_is_identified_by', graphid=self.SINGLE_NODE_GRAPHID)


        graph = Graph.objects.get(graphid=self.SINGLE_NODE_GRAPHID)
        # test that we can't append a single non-grouped node to a graph that is a single non grouped node
        with self.assertRaises(ValidationError):
            graph.append_branch('P1_is_identified_by', graphid=self.SINGLE_NODE_GRAPHID)

        graph = Graph.new()
        graph.root.datatype = 'string'
        graph.update_node(JSONSerializer().serializeToPython(graph.root))

        # test that we can't append a card to a graph that is a card that at it's root is not semantic
        with self.assertRaises(ValidationError):
            graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)

        # test that we can't append a card as a child to another card
        graph.append_branch('P1_is_identified_by', graphid=self.SINGLE_NODE_GRAPHID)
        for node in graph.nodes.itervalues():
            if node != graph.root:
                with self.assertRaises(ValidationError):
                    graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID, nodeid=node.nodeid)


        # create card collector graph to use for appending on to other graphs
        collector_graph = Graph.new()
        collector_graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        collector_graph.save()

        # test that we can't append a card collector on to a graph that is a card
        graph = Graph.new()
        with self.assertRaises(ValidationError):
            graph.append_branch('P1_is_identified_by', graphid=collector_graph.graphid)

        # test that we can't append a card collector to another card collector
        collector_copy = collector_graph.copy()
        with self.assertRaises(ValidationError):
            collector_copy.append_branch('P1_is_identified_by', graphid=collector_graph.graphid)

        # test that we can't append a card to a node in a child card within a card collector
        for node in collector_graph.nodes.itervalues():
            if node != collector_graph.root:
                with self.assertRaises(ValidationError):
                    collector_graph.append_branch('P1_is_identified_by', graphid=graph.graphid, nodeid=node.nodeid)

    def test_node_update(self):
        """
        test to make sure that node groups and card are properly managed 
        when changing a nodegroup value on a node being updated

        """

        # create a graph, append the node/node type graph and confirm is has the correct
        # number of nodegroups then remove the appended branches group and reconfirm that
        # the proper number of groups are properly relfected in the graph

        graph = Graph.objects.get(pk=self.rootNode.graph.graphid)
        graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)

        node_to_update = None
        for node_id, node in graph.nodes.iteritems():
            if node.name == 'Node':
                node_to_update = JSONDeserializer().deserialize(JSONSerializer().serialize(node))
            if node.name == 'Node Type':
                node_type_node = JSONDeserializer().deserialize(JSONSerializer().serialize(node))

        # confirm that nulling out a child group will then make that group a part of the parent group
        node_to_update['nodegroup_id'] = None
        graph.update_node(node_to_update)
        self.assertEqual(len(graph.get_nodegroups()), 1)
        self.assertEqual(len(graph.cards), 1)
        for node in graph.nodes.itervalues():
            self.assertEqual(graph.root.nodegroup, node.nodegroup)

        graph.append_branch('P1_is_identified_by', nodeid=node_type_node['nodeid'], graphid=self.SINGLE_NODE_GRAPHID)
        for edge in graph.edges.itervalues():
            if str(edge.domainnode_id) == str(node_type_node['nodeid']):
                child_nodegroup_node = JSONDeserializer().deserialize(JSONSerializer().serialize(edge.rangenode))

        # make a node group with a single node and confirm that that node is now not part of it's parent node group
        child_nodegroup_node['nodegroup_id'] = child_nodegroup_node['nodeid']
        graph.update_node(child_nodegroup_node)
        self.assertEqual(len(graph.get_nodegroups()), 2)
        for node_id, node in graph.nodes.iteritems():
            if node_id == child_nodegroup_node['nodeid']:
                self.assertNotEqual(graph.root.nodegroup, node.nodegroup)
            else:
                self.assertEqual(graph.root.nodegroup, node.nodegroup)

        # make another node group with a node (that has a child) and confirm that that node and
        # it's child are now not part of it's parent node group and that both nodes are grouped together
        node_to_update['nodegroup_id'] = node_to_update['nodeid']
        graph.update_node(node_to_update)
        self.assertEqual(len(graph.get_nodegroups()), 3)
        children = graph.get_child_nodes(node_to_update['nodeid'])
        for child in children:
            if child.nodeid == child_nodegroup_node['nodeid']:
                self.assertEqual(child.nodeid, child.nodegroup_id)
            else:
                self.assertEqual(child.nodegroup_id, node_to_update['nodegroup_id'])

        # remove a node's node group and confirm that that node takes the node group of it's parent
        child_nodegroup_node['nodegroup_id'] = None
        graph.update_node(child_nodegroup_node)
        self.assertEqual(len(graph.get_nodegroups()), 2)
        children = graph.get_child_nodes(node_to_update['nodeid'])
        for child in children:
            self.assertEqual(child.nodegroup_id, node_to_update['nodegroup_id'])

    def test_move_node(self):
        """
        test if a node can be successfully moved to another node in the graph

        """

        # test moving a single node to another branch
        # this node should be grouped with it's new parent nodegroup
        graph = Graph.objects.get(pk=self.rootNode.graph.graphid)
        branch_one = graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        for node in branch_one.nodes.itervalues():
            if node is branch_one.root:
                node.name = 'branch_one_root'
            else:
                node.name = 'branch_one_child'
        branch_two = graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        for node in branch_two.nodes.itervalues():
            if node is branch_two.root:
                node.name = 'branch_two_root'
            else:
                node.name = 'branch_two_child'
        branch_three = graph.append_branch('P1_is_identified_by', graphid=self.SINGLE_NODE_GRAPHID)
        branch_three.root.name = 'branch_three_root'
        self.assertEqual(len(graph.edges), 5)
        self.assertEqual(len(graph.nodes), 6)

        branch_three_nodeid = branch_three.nodes.iterkeys().next()
        branch_one_rootnodeid = branch_one.root.nodeid
        graph.move_node(branch_three_nodeid, 'P1_is_identified_by', branch_one_rootnodeid)
        self.assertEqual(len(graph.edges), 5)
        self.assertEqual(len(graph.nodes), 6)

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
        with self.assertRaises(ValidationError):
            graph.move_node(branch_one_rootnodeid, 'P1_is_identified_by', branch_two_rootnodeid)
        graph.move_node(branch_one_rootnodeid, 'P1_is_identified_by', branch_two_rootnodeid, skip_validation=True)
        self.assertEqual(len(graph.edges), 5)
        self.assertEqual(len(graph.nodes), 6)

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
        # have to set the parentnodegroup nodes to semantic datatype to pass validation
        with self.assertRaises(ValidationError):
            graph.save()
        for node in branch_two.nodes.itervalues():
            node.datatype = 'semantic'
        graph.save()
        graph = Graph.objects.get(pk=self.rootNode.graph.graphid)
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

        graph = Graph.objects.get(pk=self.rootNode.graph.graphid)
        ret = graph.get_valid_ontology_classes(nodeid=self.rootNode.nodeid)
        self.assertTrue(len(ret) == 1)

        self.assertEqual(ret[0]['ontology_property'], '')
        self.assertEqual(len(ret[0]['ontology_classes']), models.OntologyClass.objects.filter(ontology_id=graph.ontology_id).count())

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
        graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        for node_id, node in graph.nodes.iteritems():
            self.assertTrue(node.ontologyclass is None)
        for edge_id, edge in graph.edges.iteritems():
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

        self.assertEqual(nodes_count_after-nodes_count_before, 1)
        self.assertEqual(edges_count_after-edges_count_before, 0)
        self.assertEqual(nodegroups_count_after-nodegroups_count_before, 1)
        self.assertEqual(card_count_after-card_count_before, 1)

        # test that data is persisited propertly during an append opertation
        graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        graph.save()

        nodes_count_after = models.Node.objects.count()
        edges_count_after = models.Edge.objects.count()
        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()

        self.assertEqual(nodes_count_after-nodes_count_before, 3)
        self.assertEqual(edges_count_after-edges_count_before, 2)
        self.assertEqual(nodegroups_count_after-nodegroups_count_before, 2)
        self.assertEqual(card_count_after-card_count_before, 2)

        # test that removing a node group by setting it to None, removes it from the db
        node_to_update = None
        for node_id, node in graph.nodes.iteritems():
            if node.name == 'Node':
                self.assertTrue(node.is_collector)
                node_to_update = JSONDeserializer().deserialize(JSONSerializer().serialize(node))

        node_to_update['nodegroup_id'] = None
        graph.update_node(node_to_update.copy())
        graph.save()

        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()
        
        self.assertEqual(nodegroups_count_after-nodegroups_count_before, 1)
        self.assertEqual(card_count_after-card_count_before, 1)

        # test that adding back a node group adds it back to the db
        node_to_update['nodegroup_id'] = node_to_update['nodeid']
        graph.update_node(node_to_update)
        graph.save()

        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()
        
        self.assertEqual(nodegroups_count_after-nodegroups_count_before, 2)
        self.assertEqual(card_count_after-card_count_before, 2)

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

        self.assertEqual(nodes_count_before-nodes_count_after, 2)
        self.assertEqual(edges_count_before-edges_count_after, 1)
        self.assertEqual(nodegroups_count_before-nodegroups_count_after, 1)
        self.assertEqual(card_count_before-card_count_after, 1)

        node_count = models.Node.objects.filter(graph_id=self.NODE_NODETYPE_GRAPHID).count()
        edge_count = models.Edge.objects.filter(graph_id=self.NODE_NODETYPE_GRAPHID).count()
        self.assertEqual(node_count, 0)
        self.assertEqual(edge_count, 0)

    def test_delete_node(self):
        """
        test the node delete method

        """
        graph = Graph.new(name='TEST',is_resource=False,author='TEST')
        graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        graph.save()
        node = models.Node.objects.get(graph=graph,name="Node")

        nodes_count_before = models.Node.objects.count()
        edges_count_before = models.Edge.objects.count()
        nodegroups_count_before = models.NodeGroup.objects.count()
        card_count_before = models.CardModel.objects.count()
        
        graph.delete_node(node)

        nodes_count_after = models.Node.objects.count()
        edges_count_after = models.Edge.objects.count()
        nodegroups_count_after = models.NodeGroup.objects.count()
        card_count_after = models.CardModel.objects.count()

        self.assertEqual(nodes_count_before-nodes_count_after, 2)
        self.assertEqual(edges_count_before-edges_count_after, 2)
        self.assertEqual(nodegroups_count_before-nodegroups_count_after, 1)
        self.assertEqual(card_count_before-card_count_after, 1)

        graph = Graph.objects.get(graphid=graph.pk)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(len(graph.edges), 0)
        self.assertEqual(len(graph.cards), 1)
        self.assertEqual(len(graph.get_nodegroups()), 1)

        graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        graph.save()
        node = models.Node.objects.get(graph=graph,name="Node Type")
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
        graph = Graph.new(name='TEST',is_resource=False,author='TEST')
        graph.description = 'A test description'

        self.assertEqual(len(graph.cards), 1)
        for card in graph.get_cards():
            self.assertEqual(card.name, graph.name)
            self.assertEqual(card.description, graph.description)
            card.name = 'TEST card name'
            card.description = 'TEST card description'
            card.save()

        for card in graph.get_cards():
            self.assertEqual(card.name, 'TEST')
            self.assertEqual(card.description, 'A test description')

        graph.append_branch('P1_is_identified_by', graphid=self.SINGLE_NODE_GRAPHID)
        graph.save()

        for node in graph.nodes.itervalues():
            if node is not graph.root:
                nodeJson = JSONSerializer().serializeToPython(node)
                nodeJson['nodegroup_id'] = nodeJson['nodeid']
                graph.update_node(nodeJson)   
                             
        graph.save()

        self.assertEqual(len(graph.get_cards()), 2)
        for card in graph.get_cards():
            if str(card.nodegroup_id) == str(graph.root.nodegroup_id):
                self.assertEqual(card.name, graph.name)
                self.assertEqual(card.description, graph.description)
            else:
                self.assertTrue(len(graph.nodes[card.nodegroup.pk].name) > 0)
                self.assertTrue(len(graph.nodes[card.nodegroup.pk].description) > 0)
                self.assertEqual(card.name, graph.nodes[card.nodegroup.pk].name)
                self.assertEqual(card.description, graph.nodes[card.nodegroup.pk].description)


        # TESTING A RESOURCE
        resource_graph = Graph.new(name='TEST RESOURCE',is_resource=True,author='TEST')
        resource_graph.description = 'A test resource description'
        resource_graph.append_branch('P1_is_identified_by', graphid=graph.graphid)
        resource_graph.save()

        self.assertEqual(len(resource_graph.get_cards()), 2)
        for card in resource_graph.get_cards():
            if card.nodegroup.parentnodegroup is None:
                self.assertEqual(card.name, graph.name)
                self.assertEqual(card.description, graph.description)
                card.name = 'altered root card name'
                card.description = 'altered root card description'
            else:
                self.assertTrue(len(resource_graph.nodes[card.nodegroup.pk].name) > 0)
                self.assertTrue(len(resource_graph.nodes[card.nodegroup.pk].description) > 0)
                self.assertEqual(card.name, resource_graph.nodes[card.nodegroup.pk].name)
                self.assertEqual(card.description, resource_graph.nodes[card.nodegroup.pk].description)
                card.name = 'altered child card name'
                card.description = 'altered child card description'

        # loop through the cards again now looking for the updated desctiptions
        for card in resource_graph.get_cards():
            if card.nodegroup.parentnodegroup is None:
                self.assertEqual(card.name, 'altered root card name')
                self.assertEqual(card.description, 'altered root card description')
            else:
                self.assertEqual(card.name, 'altered child card name')
                self.assertEqual(card.description, 'altered child card description')

        resource_graph.delete()


        # TESTING A RESOURCE
        resource_graph = Graph.new(name='TEST',is_resource=True,author='TEST')
        resource_graph.description = 'A test description'
        resource_graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)
        resource_graph.save()

        self.assertEqual(len(resource_graph.cards), 1)
        the_card = resource_graph.cards.itervalues().next()
        for card in resource_graph.get_cards():
            self.assertEqual(card.name, the_card.name)
            self.assertEqual(card.description, the_card.description)
        
        # after removing the card name and description, the cards should take on the node name and description
        the_card.name = ''
        the_card.description = ''
        for card in resource_graph.get_cards():
            self.assertEqual(card.name, resource_graph.nodes[card.nodegroup.pk].name)
            self.assertEqual(card.description, resource_graph.nodes[card.nodegroup.pk].description)

    def test_get_root_nodegroup(self):
        """
        test we can get the right parent NodeGroup

        """

        graph = Graph.new(name='TEST',is_resource=False,author='TEST')
        graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)

        for node in graph.nodes.itervalues():
            if node.is_collector:
                if node.nodegroup.parentnodegroup is None:
                    self.assertEqual(graph.get_root_nodegroup(), node.nodegroup)

    def test_get_root_card(self):
        """
        test we can get the right parent card

        """

        graph = Graph.new(name='TEST',is_resource=False,author='TEST')
        graph.append_branch('P1_is_identified_by', graphid=self.NODE_NODETYPE_GRAPHID)

        for card in graph.cards.itervalues():
            if card.nodegroup.parentnodegroup is None:
                self.assertEqual(graph.get_root_card(), card)