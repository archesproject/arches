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
from django.core import management
from django.core.urlresolvers import reverse
from arches.management.commands.package_utils import resource_graphs
from arches.app.models.models import Node, NodeGroup, GraphModel, Edge
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


class GraphManagerViewTests(ArchesTestCase):

    @classmethod
    def setUpClass(cls):
        management.call_command('packages', operation='import_json', source=os.path.join(test_settings.RESOURCE_GRAPH_LOCATIONS))

        cls.HERITAGE_RESOURCE_FIXTURE_GRAPH_ID = "11111111-0000-0000-0000-191919191919"
        cls.ROOT_ID = 'd8f4db21-343e-4af3-8857-f7322dc9eb4b'
        cls.HERITAGE_RESOURCE_PLACE_ID = '9b35fd39-6668-4b44-80fb-d50d0e5211a2'
        cls.ARCHES_CONFIG_ID = '20000000-0000-0000-0000-000000000000'
        cls.NODE_COUNT = 111
        cls.PLACE_NODE_COUNT = 1
        cls.PLACE_BRANCH_COUNT = 17
        cls.client = Client()

    @classmethod
    def tearDownClass(cls):
        cls.deleteGraph("2f7f8e40-adbc-11e6-ac7f-14109fd34195")
        cls.deleteGraph(cls.HERITAGE_RESOURCE_FIXTURE_GRAPH_ID)

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
        self.client.login(username='admin', password='admin')
        url = reverse('graph', kwargs={'graphid':''})
        response = self.client.get(url)
        graphs = json.loads(response.context['graphs'])
        self.assertEqual(len(graphs), GraphModel.objects.count())

        graphid = Node.objects.get(nodeid=self.ROOT_ID).graph.pk
        url = reverse('graph', kwargs={'graphid':graphid})
        response = self.client.get(url)
        graph = json.loads(response.context['graph_json'])

        node_count = len(graph['nodes'])
        self.assertEqual(node_count, self.NODE_COUNT+1)

        edge_count = len(graph['edges'])
        self.assertEqual(edge_count, self.NODE_COUNT)

    def test_graph_settings(self):
        """
        Test the graph settings view

        """
        self.client.login(username='admin', password='admin')
        graphid = Node.objects.get(nodeid=self.ROOT_ID).graph.pk
        url = reverse('graph_settings', kwargs={'graphid':graphid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        graph = json.loads(response.context['graph_json'])

        graph['name'] = 'new graph name'
        post_data = {'graph':graph, 'relatable_resource_ids': [self.ARCHES_CONFIG_ID]}
        post_data = JSONSerializer().serialize(post_data)
        content_type = 'application/x-www-form-urlencoded'
        response = self.client.post(url, post_data, content_type)
        response_json = json.loads(response.content)

        self.assertTrue(response_json['success'])
        self.assertEqual(response_json['graph']['name'], 'new graph name')
        self.assertTrue(self.ARCHES_CONFIG_ID in response_json['relatable_resource_ids'])

    def test_node_update(self):
        """
        Test updating a node (HERITAGE_RESOURCE_PLACE) via node view

        """
        self.client.login(username='admin', password='admin')
        graphid = Node.objects.get(nodeid=self.ROOT_ID).graph.pk
        url = reverse('node', kwargs={'graphid':graphid})
        node = Node.objects.get(nodeid=self.HERITAGE_RESOURCE_PLACE_ID)
        node.name = "new node name"
        nodegroup, created = NodeGroup.objects.get_or_create(pk=self.HERITAGE_RESOURCE_PLACE_ID)
        node.nodegroup = nodegroup
        post_data = JSONSerializer().serialize(node)
        content_type = 'application/x-www-form-urlencoded'
        response = self.client.post(url, post_data, content_type)
        response_json = json.loads(response.content)

        node_count = 0
        for node in response_json['nodes']:
            if node['nodeid'] == self.HERITAGE_RESOURCE_PLACE_ID:
                self.assertEqual(node['name'], 'new node name')
            if node['nodegroup_id'] == self.HERITAGE_RESOURCE_PLACE_ID:
                node_count =  node_count + 1
        self.assertEqual(node_count, self.PLACE_NODE_COUNT)

        node_ = Node.objects.get(nodeid=self.HERITAGE_RESOURCE_PLACE_ID)

        self.assertEqual(node_.name, 'new node name')
        self.assertTrue(node_.is_collector)

    def test_node_delete(self):
        """
        Test delete a node (HERITAGE_RESOURCE_PLACE) via node view

        """
        self.client.login(username='admin', password='admin')
        graphid = Node.objects.get(nodeid=self.ROOT_ID).graph.pk
        node = Node.objects.get(nodeid=self.HERITAGE_RESOURCE_PLACE_ID)
        url = reverse('delete_node', kwargs={'graphid':graphid})
        post_data = JSONSerializer().serialize({'nodeid':node.nodeid})
        response = self.client.delete(url, post_data)
        self.assertEqual(response.status_code, 200)
        new_count = self.NODE_COUNT-self.PLACE_BRANCH_COUNT

        root = Node.objects.get(nodeid=self.ROOT_ID)

        nodes, edges = root.get_child_nodes_and_edges()
        self.assertEqual(len(nodes), new_count)
        self.assertEqual(len(edges), new_count)

    def test_graph_clone(self):
        """
        Test clone a graph (HERITAGE_RESOURCE) via view

        """
        self.client.login(username='admin', password='admin')
        graphid = Node.objects.get(nodeid=self.ROOT_ID).graph.pk
        url = reverse('clone_graph', kwargs={'graphid':graphid})
        post_data = {}
        content_type = 'application/x-www-form-urlencoded'
        response = self.client.post(url, post_data, content_type)
        response_json = json.loads(response.content)
        self.assertEqual(len(response_json['nodes']), self.NODE_COUNT+1)

    def test_new_graph(self):
        """
        Test creating a new graph via the view

        """
        self.client.login(username='admin', password='admin')
        url = reverse('new_graph')
        post_data = JSONSerializer().serialize({'isresource': False})
        content_type = 'application/x-www-form-urlencoded'
        response = self.client.post(url, post_data, content_type)
        response_json = json.loads(response.content)
        self.assertEqual(len(response_json['nodes']), 1)
        self.assertFalse(response_json['isresource'])

    def test_delete_graph(self):
        """
        test the graph delete method

        """
        self.client.login(username='admin', password='admin')
        graphid = Node.objects.get(nodeid=self.ROOT_ID).graph.pk
        url = reverse('graph', kwargs={'graphid':graphid})
        response = self.client.delete(url)

        node_count = Node.objects.filter(graph_id=graphid).count()
        edge_count = Edge.objects.filter(graph_id=graphid).count()
        self.assertEqual(node_count,0)
        self.assertEqual(edge_count,0)

    def test_graph_export(self):
        """
        test graph export method

        """

        self.client.login(username='admin', password='admin')
        graphid = Node.objects.get(nodeid=self.ROOT_ID).graph.pk
        url = reverse('export_graph', kwargs={'graphid':graphid})
        response = self.client.get(url)
        graph_json = json.loads(response._container[0])
        node_count = len(graph_json['graph'][0]['nodes'])
        self.assertTrue(response._container[0])
        self.assertEqual(node_count, self.NODE_COUNT+1)
        self.assertEqual(list(response._headers['content-type'])[1], 'json/plain')

    def test_graph_import(self):
        """
        test graph import method

        """

        self.client.login(username='admin', password='admin')
        url = reverse('import_graph')
        with open(os.path.join(list(test_settings.RESOURCE_GRAPH_LOCATIONS)[0], 'archesv4_resource.json')) as f:
            response = self.client.post(url, {'importedGraph': f})
        self.assertIsNotNone(response.content)

        imported_json = JSONDeserializer().deserialize(response.content)
        self.assertEqual(imported_json, [])
