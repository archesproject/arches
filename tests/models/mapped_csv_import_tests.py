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
from arches.app.models.models import TileModel, ResourceInstance
from arches.app.models.concept import Concept
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.skos import SKOSReader
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.data_management.resources.importer import BusinessDataImporter


# these tests can be run from the command line via
# python manage.py test tests/models/mapped_csv_import_tests.py --pattern="*.py" --settings="tests.test_settings"


class mappedCSVFileImportTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        ResourceInstance.objects.all().delete()

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/data/concept_label_test_scheme.xml")
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/data/concept_label_test_collection.xml")
        ret = skos.save_concepts_from_skos(rdf)

        with open(os.path.join("tests/fixtures/data/json/cardinality_test_data/target.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        with open(os.path.join("tests/fixtures/data/json/cardinality_test_data/file-list.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

    @classmethod
    def tearDownClass(cls):
        pass

    def test_single_1(self):
        og_tile_count = TileModel.objects.count()
        BusinessDataImporter("tests/fixtures/data/csv/cardinality_test_data/single-1_to_1.csv").import_business_data()
        new_tile_count = TileModel.objects.count()
        tile_difference = new_tile_count - og_tile_count
        self.assertEqual(tile_difference, 1)

    def test_single_n_to_n(self):
        og_tile_count = TileModel.objects.count()
        BusinessDataImporter("tests/fixtures/data/csv/cardinality_test_data/single-n_to_n.csv").import_business_data()
        new_tile_count = TileModel.objects.count()
        tile_difference = new_tile_count - og_tile_count
        self.assertEqual(tile_difference, 2)

    def test_single_n_to_1(self):
        og_tile_count = TileModel.objects.count()
        BusinessDataImporter("tests/fixtures/data/csv/cardinality_test_data/single-n_to_1.csv").import_business_data()
        new_tile_count = TileModel.objects.count()
        tile_difference = new_tile_count - og_tile_count
        self.assertEqual(tile_difference, 1)

    def test_1_1(self):
        og_tile_count = TileModel.objects.count()
        BusinessDataImporter("tests/fixtures/data/csv/cardinality_test_data/1-1.csv").import_business_data()
        new_tile_count = TileModel.objects.count()
        tile_difference = new_tile_count - og_tile_count
        self.assertEqual(tile_difference, 2)

    def test_1_n(self):
        og_tile_count = TileModel.objects.count()
        BusinessDataImporter("tests/fixtures/data/csv/cardinality_test_data/1-n.csv").import_business_data()
        new_tile_count = TileModel.objects.count()
        tile_difference = new_tile_count - og_tile_count
        self.assertEqual(tile_difference, 3)

    def test_n_1(self):
        og_tile_count = TileModel.objects.count()
        BusinessDataImporter("tests/fixtures/data/csv/cardinality_test_data/n-1.csv").import_business_data()
        new_tile_count = TileModel.objects.count()
        tile_difference = new_tile_count - og_tile_count
        self.assertEqual(tile_difference, 4)

    def test_n_n(self):
        og_tile_count = TileModel.objects.count()
        BusinessDataImporter("tests/fixtures/data/csv/cardinality_test_data/n-n.csv").import_business_data()
        new_tile_count = TileModel.objects.count()
        tile_difference = new_tile_count - og_tile_count
        self.assertEqual(tile_difference, 6)

    def test_domain_label_import(self):
        og_tile_count = TileModel.objects.count()
        BusinessDataImporter("tests/fixtures/data/csv/domain_label_import.csv").import_business_data()
        new_tile_count = TileModel.objects.count()
        tile_difference = new_tile_count - og_tile_count
        self.assertEqual(tile_difference, 1)

    def test_concept_label_import(self):
        og_tile_count = TileModel.objects.count()
        BusinessDataImporter("tests/fixtures/data/csv/concept_label_import.csv").import_business_data()
        new_tile_count = TileModel.objects.count()
        tile_difference = new_tile_count - og_tile_count
        self.assertEqual(tile_difference, 1)

    def test_required_node_import(self):
        og_tile_count = TileModel.objects.count()
        BusinessDataImporter("tests/fixtures/data/csv/required_node_import.csv").import_business_data()
        new_tile_count = TileModel.objects.count()
        tile_difference = new_tile_count - og_tile_count
        self.assertEqual(tile_difference, 0)

    def test_required_child_node_import(self):
        og_tile_count = TileModel.objects.count()
        BusinessDataImporter("tests/fixtures/data/csv/required_child_node_import.csv").import_business_data()
        new_tile_count = TileModel.objects.count()
        tile_difference = new_tile_count - og_tile_count
        self.assertEqual(tile_difference, 0)

    def test_file_list_datatype_import(self):
        og_tile_count = TileModel.objects.count()
        BusinessDataImporter("tests/fixtures/data/csv/file_list_datatype_import.csv").import_business_data()
        new_tile_count = TileModel.objects.count()
        tile_difference = new_tile_count - og_tile_count
        self.assertEqual(tile_difference, 1)
