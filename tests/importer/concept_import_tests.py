"""
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
"""

import os
from operator import itemgetter
from tests import test_settings
from tests.base_test import ArchesTestCase
from django.core import management
from arches.app.models.concept import Concept
from arches.app.models.models import Concept as django_concept_model
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory

# these tests can be run from the command line via
# python manage.py test tests/importer/concept_import_tests.py --pattern="*.py" --settings="tests.test_settings"


class conceptImportTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        se = SearchEngineFactory().create()
        se.delete_index(index="terms,concepts")
        se.create_index(index="terms,concepts")
        # management.call_command('packages', operation='import_graphs', source='tests/fixtures/resource_graphs/archesv4_resource.json')

    @classmethod
    def tearDownClass(cls):
        se = SearchEngineFactory().create()
        se.delete_index(index="terms,concepts")
        se.create_index(index="terms,concepts")

    # def test_hierarchical_relationships(self):
    #   result = JSONDeserializer().deserialize(JSONSerializer().serialize(Concept().get(id='09bf4b42-51a8-4ff2-9210-c4e4ae0e6755', include_subconcepts=True, depth_limit=1)))
    #   children = len(result['subconcepts'])
    #   self.assertEqual(children, 3)
    #
    #
    # def test_value_import(self):
    #   result = JSONDeserializer().deserialize(JSONSerializer().serialize(Concept().get(id='f2bb7a67-d3b3-488f-af39-e0773585c23a', include_subconcepts=True, depth_limit=1)))
    #   values = len(result['values'])
    #   self.assertEqual(values, 5)
