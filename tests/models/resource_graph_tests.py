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
from django.test import Client
from django.core.urlresolvers import reverse
from arches.management.commands.package_utils import resource_graphs
from arches.app.models import models
from arches.app.models.resource_graphs import ResourceGraph
from arches.app.utils.betterJSONSerializer import JSONSerializer


class ResourceGraphTests(ArchesTestCase):

    @classmethod
    def setUpClass(cls):
        resource_graphs.load_graphs(os.path.join(test_settings.RESOURCE_GRAPH_LOCATIONS))
        
        cls.NODE_NODETYPE_ROOTNODE_ID = '20000000-0000-0000-0000-100000000001'
        cls.ARCHES_CONFIG_GRAPH = '20000000-0000-0000-0000-000000000000'
        cls.HERITAGE_RESOURCE_FIXTURE = 'd8f4db21-343e-4af3-8857-f7322dc9eb4b'
        # cls.NODE_COUNT = 111
        # cls.PLACE_NODE_COUNT = 17
        # cls.client = Client()

    def setUp(self):
        self.rootNode = models.Node.objects.create(
            name='ROOT NODE',
            description='Test Root Node',
            istopnode=True,
            ontologyclass='E1',
            datatype='semantic'
        )

    def tearDown(self):
        def delete_children(node):
            for edge in models.Edge.objects.filter(rangenode=node):
                edge.delete()
                delete_children(edge.rangenode)
         
        delete_children(self.rootNode)   
        self.rootNode.delete()

    def test_nodes_are_byref(self):
        """
        test that the nodes referred to in the ResourceGraph.edges are exact references to 
        the nodes as opposed to a node with the same attribute values

        """

        graph = ResourceGraph(self.HERITAGE_RESOURCE_FIXTURE)

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

        graph = ResourceGraph(self.HERITAGE_RESOURCE_FIXTURE)
        new_graph = graph.copy()

        self.assertEqual(len(graph.nodes), len(new_graph.nodes))
        self.assertEqual(len(graph.edges), len(new_graph.edges))

        def findNodeByName(graph, name):
            for key, node in graph.nodes.iteritems():
                if node.name == name:
                    return node
            return None

        for key, node in graph.nodes.iteritems():
            newNode = findNodeByName(new_graph, node.name)
            self.assertIsNotNone(newNode)
            self.assertNotEqual(node.pk, newNode.pk)
            self.assertNotEqual(id(node), id(newNode))

        for key, newedge in new_graph.edges.iteritems():
            with self.assertRaises(KeyError):
                graph.edges[newedge.pk]

    # def test_branch_append(self):
    #     graph = ResourceGraph(self.rootNode)
    #     graph.append_branch('P1', branchmetadataid=self.NODE_NODETYPE_ROOTNODE_ID) 

    #     pass
