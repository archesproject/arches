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
import json
import csv
from io import BytesIO
from tests import test_settings
from operator import itemgetter
from django.core import management
from tests.base_test import ArchesTestCase
from arches.app.utils.skos import SKOSReader
from arches.app.models.models import TileModel, ResourceInstance
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from arches.app.utils.data_management.resources.exporter import ResourceExporter as BusinessDataExporter
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter


# these tests can be run from the command line via
# python manage.py test tests/exporter/resource_export_tests.py --settings="tests.test_settings"


class BusinessDataExportTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        cls.loadOntology()

    def setUp(self):
        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/data/concept_label_test_scheme.xml")
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/data/concept_label_test_collection.xml")
        ret = skos.save_concepts_from_skos(rdf)

        with open(os.path.join("tests/fixtures/resource_graphs/resource_export_test.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

    @classmethod
    def tearDownClass(cls):
        pass

    def test_csv_export(self):
        BusinessDataImporter("tests/fixtures/data/csv/resource_export_test.csv").import_business_data()

        export = BusinessDataExporter("csv", configs="tests/fixtures/data/csv/resource_export_test.mapping", single_file=True).export()

        csv_output = list(csv.DictReader(export[0]["outputfile"].getvalue().split("\r\n")))[0]
        csvinputfile = "tests/fixtures/data/csv/resource_export_test.csv"
        csv_input = list(csv.DictReader(open(csvinputfile, "rU", encoding="utf-8"), restkey="ADDITIONAL", restval="MISSING"))[0]

        self.assertDictEqual(dict(csv_input), dict(csv_output))

    def test_json_export(self):
        def deep_sort(obj):
            """
            Recursively sort list or dict nested lists. Taken from
            https://stackoverflow.com/questions/18464095/how-to-achieve-assertdictequal-with-assertsequenceequal-applied-to-values
            """

            if isinstance(obj, dict):
                _sorted = {}
                for key in sorted(obj):
                    _sorted[key] = deep_sort(obj[key])

            elif isinstance(obj, list):
                new_list = []
                for val in obj:
                    new_list.append(deep_sort(val))
                try:
                    _sorted = sorted(new_list, key=itemgetter("tileid"))
                except:
                    _sorted = new_list

            else:
                _sorted = obj

            return _sorted

        BusinessDataImporter("tests/fixtures/data/json/resource_export_business_data_truth.json").import_business_data()

        export = BusinessDataExporter("json").export("ab74af76-fa0e-11e6-9e3e-026d961c88e6")

        json_export = deep_sort(json.loads(export[0]["outputfile"].getvalue()))

        json_truth = deep_sort(json.load(open("tests/fixtures/data/json/resource_export_business_data_truth.json")))

        self.assertDictEqual(json_export, json_truth)
