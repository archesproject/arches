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

import os, json
from tests import test_settings
from tests.base_test import ArchesTestCase
from django.test import Client
from django.core.urlresolvers import reverse
from arches.management.commands.package_utils import resource_graphs
from arches.app.models.models import Node, NodeGroup
from arches.app.utils.betterJSONSerializer import JSONSerializer


class GraphManagerViewTests(ArchesTestCase):

    @classmethod
    def setUpClass(cls):
        resource_graphs.load_graphs(os.path.join(test_settings.RESOURCE_GRAPH_LOCATIONS))

        cls.ROOT_ID = 'd8f4db21-343e-4af3-8857-f7322dc9eb4b'
        cls.HERITAGE_RESOURCE_PLACE_ID = '9b35fd39-6668-4b44-80fb-d50d0e5211a2'
        cls.NODE_COUNT = 111
        cls.PLACE_NODE_COUNT = 17
        cls.RESOURCE_COUNT = 111
        cls.client = Client()

    @classmethod
    def tearDownClass(cls):
        root = Node.objects.get(pk=cls.ROOT_ID)
        cls.deleteGraph(root)

    def test_graph_import(self):
        """
        Test that correct number of nodes and edges load

        """

        root = Node.objects.get(nodeid=self.ROOT_ID)
        nodes, edges = root.get_child_nodes_and_edges()
        node_count = len(nodes)
        edge_count = len(edges)

        self.assertEqual(node_count, self.NODE_COUNT)
        self.assertEqual(edge_count, self.NODE_COUNT)

    def test_graph_manager(self):
        """
        Test the graph manager view

        """
        url = reverse('graph', kwargs={'nodeid':''})
        response = self.client.get(url)
        graphs = json.loads(response.context['graphs'])
        self.assertEqual(len(graphs), 4)

        url = reverse('graph', kwargs={'nodeid':self.ROOT_ID})
        response = self.client.get(url)
        graph = json.loads(response.context['graph'])

        node_count = len(graph['nodes'])
        self.assertEqual(node_count, self.NODE_COUNT+1)

        edge_count = len(graph['edges'])
        self.assertEqual(edge_count, self.NODE_COUNT)

    def test_node_update(self):
        """
        Test updating a node (HERITAGE_RESOURCE_PLACE) via node view

        """

        url = reverse('node', kwargs={'nodeid':self.HERITAGE_RESOURCE_PLACE_ID})
        node = Node.objects.get(nodeid=self.HERITAGE_RESOURCE_PLACE_ID)
        node.name = "new node name"
        nodegroup, created = NodeGroup.objects.get_or_create(pk=self.HERITAGE_RESOURCE_PLACE_ID)
        node.nodegroup = nodegroup
        post_data = JSONSerializer().serialize(node)
        content_type = 'application/x-www-form-urlencoded'
        response = self.client.post(url, post_data, content_type)
        response_json = json.loads(response.content)

        self.assertEqual(len(response_json['group_nodes']), self.PLACE_NODE_COUNT-1)
        self.assertEqual(response_json['node']['name'], 'new node name')

        node_ = Node.objects.get(nodeid=self.HERITAGE_RESOURCE_PLACE_ID)

        self.assertEqual(node_.name, 'new node name')
        self.assertTrue(node_.is_collector())

    def test_node_delete(self):
        """
        Test delete a node (HERITAGE_RESOURCE_PLACE) via node view

        """

        url = reverse('node', kwargs={'nodeid':self.HERITAGE_RESOURCE_PLACE_ID})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        new_count = self.NODE_COUNT-self.PLACE_NODE_COUNT
        root = Node.objects.get(nodeid=self.ROOT_ID)

        nodes, edges = root.get_child_nodes_and_edges()
        node_count = len(nodes)
        edge_count = len(edges)

        self.assertEqual(node_count, new_count)
        self.assertEqual(edge_count, new_count)
