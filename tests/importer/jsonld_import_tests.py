

import os
import json
import csv
from io import BytesIO
from tests import test_settings
from operator import itemgetter
from django.core import management
from django.test.client import RequestFactory, Client
from django.contrib.auth.models import User, Group, AnonymousUser
from django.urls import reverse
from tests.base_test import ArchesTestCase
from arches.app.utils.skos import SKOSReader
from arches.app.models.models import TileModel, ResourceInstance
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from arches.app.utils.data_management.resources.exporter import ResourceExporter as BusinessDataExporter
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter


# these tests can be run from the command line via
# python manage.py test tests/importer/jsonld_import_tests.py --settings="tests.test_settings"


class JsonLDExportTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        # This runs once per instantiation
        cls.loadOntology()
        cls.factory = RequestFactory()
        cls.client = Client()
        
        response = cls.client.post(reverse('get_token'), {'username': 'admin', 'password': 'admin'})
        cls.token = response.content

        skos = SKOSReader()
        rdf = skos.read_file('tests/fixtures/jsonld_base/rdm/jsonld_test_thesaurus.xml')
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file('tests/fixtures/jsonld_base/rdm/jsonld_test_collections.xml')
        ret = skos.save_concepts_from_skos(rdf)

        # Load up the models and data only once
        with open(os.path.join('tests/fixtures/jsonld_base/models/test_1_basic_object.json'), 'rU') as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile['graph'])

        with open(os.path.join('tests/fixtures/jsonld_base/models/test_2_complex_object.json'), 'rU') as f:
            archesfile2 = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile2['graph'])

    def setUp(self):
        # This runs every test
        #
        #self.token = response.content
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def tearDown(self):
        pass

    def test_1_basic_export(self):
        data = """{
            "@id": "http://localhost:8000/resources/221d1154-fa8e-11e9-9cbb-3af9d3b32b71",
            "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
            "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "test!"
            }"""

        url = reverse('resources', kwargs={"resourceid": "221d1154-fa8e-11e9-9cbb-3af9d3b32b71"})
        # response = self.client.put(url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.put(url, data=data, secure=False)
        print(f"test basic on {url} gets {response.status_code}")
        self.assertTrue(response.status_code == 201)
        js = response.json()
        print(f"Got create response: {js}")
