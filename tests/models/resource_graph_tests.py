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

import os
from tests import test_settings
from tests.base_test import ArchesTestCase
from arches.app.models import models
from arches.management.commands.package_utils import resource_graphs
from arches.app.models.models import Node

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"


class ResourceGraphTests(ArchesTestCase):

    def test_initial_node_import(self):
        """
        Test that correct number of nodes load

        """

        count_before = Node.objects.count()

        resource_graphs.load_graphs(os.path.join(test_settings.RESOURCE_GRAPH_LOCATIONS))

        self.assertEqual(Node.objects.count()-count_before, 112)


    # def test_intial_edge_import(self):
    #     """
    #     Test that correct number of edges load

    #     """
