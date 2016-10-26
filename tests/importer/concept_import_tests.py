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
from operator import itemgetter
from tests import test_settings
from tests.base_test import ArchesTestCase
from django.core import management
from arches.app.models.concept import Concept
from arches.app.models.models import Concept as django_concept_model
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.management.commands.package_utils import authority_files

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"


class conceptImportTests(ArchesTestCase):
	@classmethod
	def setUpClass(cls):
		management.call_command('packages', operation='import_json', source='tests/fixtures/resource_graphs/archesv4_resource.json')
		se = SearchEngineFactory().create()
		se.delete_index(index='concept_labels')
		se.delete_index(index='term')
		se.create_index(index='concept_labels')
		se.create_index(index='term')

	@classmethod
	def tearDownClass(cls):
		se = SearchEngineFactory().create()
		se.delete_index(index='concept_labels')
		se.delete_index(index='term')
		se.create_index(index='concept_labels')
		se.create_index(index='term')


	def test_hierarchical_relationships(self):
		result = JSONDeserializer().deserialize(JSONSerializer().serialize(Concept().get(id='708e87fd-35bc-3270-b322-b551cd63c589', include_subconcepts=True, depth_limit=1)))
		children = len(result['subconcepts'])
		self.assertEqual(children, 3)


	def test_value_import(self):
		result = JSONDeserializer().deserialize(JSONSerializer().serialize(Concept().get(id='32d8ca56-2aa1-3890-b95b-3fbb119460ad', include_subconcepts=True, depth_limit=1)))
		values = len(result['values'])
		self.assertEqual(values, 5)


	def test_authority_file_import(self):
		og_concept_count = len(django_concept_model.objects.all())
		path_to_files = os.path.join(test_settings.PACKAGE_ROOT, 'fixtures', 'authority_files')
		authority_files.load_authority_files(path_to_files, break_on_error=True)
		new_concept_count = len(django_concept_model.objects.all())
		self.assertEqual(new_concept_count - og_concept_count, 43)
