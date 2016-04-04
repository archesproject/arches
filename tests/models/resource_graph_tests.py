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
from arches.app.models import models
from arches.management.commands.package_utils import resource_graphs
from arches.app.models.models import Node

def setUpModule():
    resource_graphs.load_graphs(os.path.join(test_settings.RESOURCE_GRAPH_LOCATIONS))

NODE_COUNT = 112

class ResourceGraphTests(ArchesTestCase):

    def test_graph_import(self):
        """
        Test that correct number of nodes and edges load

        """
        root = Node.objects.get(nodeid='d8f4db21-343e-4af3-8857-f7322dc9eb4b')
        node_count = len(root.get_downstream_nodes())
        self.assertEqual(node_count, NODE_COUNT-1)
        edge_count = len(root.get_downstream_edges())
        self.assertEqual(edge_count, NODE_COUNT-1)

    def test_graph_manager(self):
        """
        Test the graph manager view

        """
        c = Client()
        response = c.get(reverse('graph', kwargs={'nodeid':'d8f4db21-343e-4af3-8857-f7322dc9eb4b'}))
        graph = json.loads(response.context['graph'])
        node_count = len(graph['nodes'])
        self.assertEqual(node_count, NODE_COUNT)
        edge_count = len(graph['edges'])
        self.assertEqual(edge_count, NODE_COUNT-1)
