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

from operator import itemgetter
from tests import test_settings
from tests.base_test import ArchesTestCase
from django.core import management
from arches.app.models.ontology import Concept
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"


class conceptImportTests(ArchesTestCase):
	@classmethod
	def setUpClass(cls):
		management.call_command('packages', operation='import_json', source='tests/fixtures/resource_graphs/archesv4_resource.json') 

	@classmethod
	def tearDownClass(cls):
		pass


	def test_hierarchical_relationships(self):
		result = JSONDeserializer().deserialize(JSONSerializer().serialize(Concept().get(id='708e87fd-35bc-3270-b322-b551cd63c589', include_subconcepts=True, depth_limit=1)))
		children = len(result['subconcepts'])
		self.assertEqual(children, 3)


	def test_value_import(self):
		result = JSONDeserializer().deserialize(JSONSerializer().serialize(Concept().get(id='32d8ca56-2aa1-3890-b95b-3fbb119460ad', include_subconcepts=True, depth_limit=1)))
		values = len(result['values'])
		self.assertEqual(values, 5)