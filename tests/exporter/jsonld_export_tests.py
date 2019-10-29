

import os
import json
import csv
from io import BytesIO
from tests import test_settings
from operator import itemgetter
from django.core import management
from django.test.client import RequestFactory, Client
from django.urls import reverse
from tests.base_test import ArchesTestCase
from arches.app.utils.skos import SKOSReader
from arches.app.models.models import TileModel, ResourceInstance
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from arches.app.utils.data_management.resources.exporter import ResourceExporter as BusinessDataExporter
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter


# these tests can be run from the command line via
# python manage.py test tests/exporter/jsonld_export_tests.py --settings="tests.test_settings"


class JsonLDExportTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        # This runs once per instantiation
        cls.loadOntology()
        cls.factory = RequestFactory()
        cls.client = Client()
        skos = SKOSReader()
        rdf = skos.read_file('tests/fixtures/data/concept_label_test_scheme.xml')
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file('tests/fixtures/data/concept_label_test_collection.xml')
        ret = skos.save_concepts_from_skos(rdf)

        # Load up the models once
        # As we need to test resource-instance and resource-instance-list
        with open(os.path.join('tests/fixtures/jsonld_base/models/test_1_basic_object.json'), 'rU') as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile['graph'])

    def setUp(self):
        # This runs every test
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def tearDown(self):
        pass


    def test_missing_resource(self):
        # this is from urls.py
        url = reverse('resources', kwargs={"resourceid": "00000000-f6b5-11e9-8f09-a4d18cec433a"})
        response = self.client.get(url)
        print(f"test missing on {url} gets {response.status_code}")
        self.assertTrue(response.status_code == 404)

    def test_basic_export(self):
        # ef52726c-f6b1-11e9-b47f-a4d18cec433a
        BusinessDataImporter('tests/fixtures/jsonld_base/data/test_1_instance.json').import_business_data()

        response = self.client.get(reverse('resources', kwargs={"resourceid": "e6412598-f6b5-11e9-8f09-a4d18cec433a"}))
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue('@id' in js)
        self.assertTrue(js['@id'] == "http://localhost:8000/resources/e6412598-f6b5-11e9-8f09-a4d18cec433a")
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P3_has_note" in js)
        self.assertTrue(js["http://www.cidoc-crm.org/cidoc-crm/P3_has_note"] == "Test Text Here")
