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
from arches.app.models.models import Node

def setUpModule():
    resource_graphs.load_graphs(os.path.join(test_settings.RESOURCE_GRAPH_LOCATIONS))

ROOT_ID = 'd8f4db21-343e-4af3-8857-f7322dc9eb4b'
HERITAGE_RESOURCE_PLACE_ID = '9b35fd39-6668-4b44-80fb-d50d0e5211a2'

NODE_COUNT = 111
PLACE_NODE_COUNT = 17
client = Client()

class ResourceGraphTests(ArchesTestCase):

    def test_graph_import(self):
        """
        Test that correct number of nodes and edges load

        """
        root = Node.objects.get(nodeid=ROOT_ID)
        node_count = len(root.get_downstream_nodes())
        self.assertEqual(node_count, NODE_COUNT)
        edge_count = len(root.get_downstream_edges())
        self.assertEqual(edge_count, NODE_COUNT)

    def test_graph_manager(self):
        """
        Test the graph manager view

        """
        url = reverse('graph', kwargs={'nodeid':ROOT_ID})
        response = client.get(url)
        graph = json.loads(response.context['graph'])
        node_count = len(graph['nodes'])
        self.assertEqual(node_count, NODE_COUNT+1)
        edge_count = len(graph['edges'])
        self.assertEqual(edge_count, NODE_COUNT)

    def test_node_update(self):
        """
        Test updating a node (HERITAGE_RESOURCE_PLACE) via node view

        """
        url = reverse('node', kwargs={'nodeid':HERITAGE_RESOURCE_PLACE_ID})
        post_data = {
            "description": "",
            "istopnode": False,
            "ontologyclass": "",
            "nodeid": HERITAGE_RESOURCE_PLACE_ID,
            "branchmetadata_id": None,
            "datatype": "",
            "nodegroup_id": HERITAGE_RESOURCE_PLACE_ID,
            "name": "new node name"
        }
        content_type = 'application/x-www-form-urlencoded'
        response = client.post(url, json.dumps(post_data), content_type)
        response_json = json.loads(response.content)
        self.assertEqual(len(response_json['group_nodes']), PLACE_NODE_COUNT-1)
        self.assertEqual(response_json['node']['name'], 'new node name')
        node = Node.objects.get(nodeid=HERITAGE_RESOURCE_PLACE_ID)
        self.assertEqual(node.name, 'new node name')
        self.assertTrue(node.is_collector())

    def test_node_delete(self):
        """
        Test delete a node (HERITAGE_RESOURCE_PLACE) via node view

        """
        url = reverse('node', kwargs={'nodeid':HERITAGE_RESOURCE_PLACE_ID})
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)
        new_count = NODE_COUNT-PLACE_NODE_COUNT
        root = Node.objects.get(nodeid=ROOT_ID)
        node_count = len(root.get_downstream_nodes())
        self.assertEqual(node_count, new_count)
        edge_count = len(root.get_downstream_edges())
        self.assertEqual(edge_count, new_count)
