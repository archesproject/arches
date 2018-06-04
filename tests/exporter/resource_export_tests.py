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
import json
from operator import itemgetter
from tests import test_settings
from tests.base_test import ArchesTestCase
from django.core import management
from arches.app.models.models import TileModel, ResourceInstance
from arches.app.models.concept import Concept
from arches.app.utils.skos import SKOSReader
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.data_management.resources.importer import  BusinessDataImporter
from arches.app.utils.data_management.resources.exporter import  ResourceExporter as BusinessDataExporter
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer



class BusinessDataExportTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        ResourceInstance.objects.all().delete()

        skos = SKOSReader()
        rdf = skos.read_file('tests/fixtures/data/concept_label_test_scheme.xml')
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file('tests/fixtures/data/concept_label_test_collection.xml')
        ret = skos.save_concepts_from_skos(rdf)

        with open(os.path.join('tests/fixtures/data/json/cardinality_test_data/target.json'), 'rU') as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile['graph'])

        BusinessDataImporter('tests/fixtures/data/csv/cardinality_test_data/single-1_to_1.csv').import_business_data()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_csv_export(self):
        export = BusinessDataExporter('csv', configs='tests/fixtures/data/csv/cardinality_test_data/single-1_to_1.mapping', single_file=True).export('8e672ab0-c6e2-11e6-9725-685b3597724b')
        csv_export = filter(lambda export: 'csv' in export['name'], export)[0]['outputfile'].getvalue().split('\r')
        self.assertEqual(len(csv_export), 3)

    def test_json_export(self):
        export = BusinessDataExporter('json').export('8e672ab0-c6e2-11e6-9725-685b3597724b')
        json_export = json.loads(export[0]['outputfile'].getvalue())
        number_of_resources = len(json_export['business_data']['resources'])
        self.assertEqual(number_of_resources, 1)

    # def test_jsonld_export(self):
    #     og_tile_count = TileModel.objects.count()
    #     BusinessDataExporter('jsonld').export('8e672ab0-c6e2-11e6-9725-685b3597724b')
    #     new_tile_count = TileModel.objects.count()
    #     tile_difference = new_tile_count - og_tile_count
    #     self.assertEqual(tile_difference, 1)
    #
    # def test_rdf_export(self):
    #     og_tile_count = TileModel.objects.count()
    #     BusinessDataExporter('rdf').export('8e672ab0-c6e2-11e6-9725-685b3597724b')
    #     new_tile_count = TileModel.objects.count()
    #     tile_difference = new_tile_count - og_tile_count
    #     self.assertEqual(tile_difference, 1)
