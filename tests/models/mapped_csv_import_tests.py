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
from arches.app.models.models import TileModel, ResourceInstance
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.management.commands.package_utils import authority_files
from arches.app.utils.data_management.arches_file_importer import ArchesFileImporter
from arches.app.utils.data_management.csv_importer import  CSVFileImporter


# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"


class mappedCSVFileImportTests(ArchesTestCase):
	@classmethod
	def setUpClass(cls):
		pass

	def setUp(self):
		ResourceInstance.objects.all().delete()
		ArchesFileImporter(os.path.join('tests/fixtures/data/json/cardinality_test_data/target.json')).import_all()

	@classmethod
	def tearDownClass(cls):
		pass

	def test_single_1(self):
		og_tile_count = TileModel.objects.count()
		CSVFileImporter('tests/fixtures/data/json/cardinality_test_data/single-1.csv').import_all()
		new_tile_count = TileModel.objects.count()
		tile_difference = new_tile_count - og_tile_count
		self.assertEqual(tile_difference, 1)
