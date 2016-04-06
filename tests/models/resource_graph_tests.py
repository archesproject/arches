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
from arches.app.models import models
from arches.app.models.resource_graphs import ResourceGraph
from arches.app.utils.betterJSONSerializer import JSONSerializer


class ResourceGraphTests(ArchesTestCase):

    @classmethod
    def setUpClass(cls):
        #resource_graphs.load_graphs(os.path.join(test_settings.RESOURCE_GRAPH_LOCATIONS))
        
        cls.NODE_NODETYPE_BRANCH_ID = '22000000-0000-0000-0000-000000000001'
        # cls.HERITAGE_RESOURCE_PLACE_ID = '9b35fd39-6668-4b44-80fb-d50d0e5211a2'
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

    def test_branch_append(self):
        graph = ResourceGraph(self.rootNode)
        graph.append_branch('P1', branchmetadataid=self.NODE_NODETYPE_BRANCH_ID) 

        
        pass
