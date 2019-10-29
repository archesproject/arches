

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
# python manage.py test tests/exporter/jsonld_export_tests.py --settings="tests.test_settings"


class JsonLDExportTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        # This runs once per instantiation
        cls.loadOntology()
        cls.factory = RequestFactory()
        cls.client = Client()

        #cls.client.login(username='admin', password='admin')
        #cls.user = User.objects.get(username='anonymous')

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
        BusinessDataImporter('tests/fixtures/jsonld_base/data/test_1_instance.json').import_business_data()

        with open(os.path.join('tests/fixtures/jsonld_base/models/test_2_complex_object.json'), 'rU') as f:
            archesfile2 = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile2['graph'])
        BusinessDataImporter('tests/fixtures/jsonld_base/data/test_2_instances.json').import_business_data()  

    def setUp(self):
        # This runs every test
        #response = self.client.post(reverse('get_token'), {'username': 'admin', 'password': 'admin'})
        #self.token = response.content
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def tearDown(self):
        pass

    def test_0_missing_resource(self):
        # this 'resources' is from urls.py
        url = reverse('resources', kwargs={"resourceid": "00000000-f6b5-11e9-8f09-a4d18cec433a"})
        response = self.client.get(url, secure=False)
        print(f"test missing on {url} gets {response.status_code}")
        self.assertTrue(response.status_code == 404)

    def test_1_basic_export(self):
        # ef52726c-f6b1-11e9-b47f-a4d18cec433a
        url = reverse('resources', kwargs={"resourceid": "e6412598-f6b5-11e9-8f09-a4d18cec433a"})
        # response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(url, secure=False)
        print(f"test basic on {url} gets {response.status_code}")
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue('@id' in js)
        self.assertTrue(js['@id'] == "http://localhost:8000/resources/e6412598-f6b5-11e9-8f09-a4d18cec433a")
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P3_has_note" in js)
        self.assertTrue(js["http://www.cidoc-crm.org/cidoc-crm/P3_has_note"] == "Test Text Here")

    def test_2a_complex_export_data(self):
        # 24d0d25a-fa75-11e9-b369-3af9d3b32b71  -- data types
        url = reverse('resources', kwargs={"resourceid": "24d0d25a-fa75-11e9-b369-3af9d3b32b71"})
        response = self.client.get(url, secure=False) 
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue('@id' in js)
        self.assertTrue(js['@id'] == "http://localhost:8000/resources/24d0d25a-fa75-11e9-b369-3af9d3b32b71")
        self.assertTrue('@type' in js)
        self.assertTrue(js['@type'] == "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object")
        # Test string data type
        self.assertTrue('http://www.cidoc-crm.org/cidoc-crm/P3_has_note' in js)        
        self.assertTrue(js['http://www.cidoc-crm.org/cidoc-crm/P3_has_note'] == "Test Data")
        # Test number data type
        self.assertTrue('http://www.cidoc-crm.org/cidoc-crm/P57_has_number_of_parts' in js)
        self.assertTrue(js['http://www.cidoc-crm.org/cidoc-crm/P57_has_number_of_parts'] == 10)
        # Test date data type
        self.assertTrue('http://www.cidoc-crm.org/cidoc-crm/P160_has_temporal_projection' in js)
        ts = js['http://www.cidoc-crm.org/cidoc-crm/P160_has_temporal_projection']
        self.assertTrue('http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin' in ts)
        dt = ts['http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin']
        self.assertTrue(type(dt) == dict)
        self.assertTrue('@value' in dt)
        self.assertTrue(dt['@value'] == "2019-10-01")
        self.assertTrue('@type' in dt)
        self.assertTrue(dt['@type'] == "http://www.w3.org/2001/XMLSchema#dateTime")
        # Test domain data type
        self.assertTrue('http://www.cidoc-crm.org/cidoc-crm/P79_beginning_is_qualified_by' in ts)
        self.assertTrue(ts['http://www.cidoc-crm.org/cidoc-crm/P79_beginning_is_qualified_by'] == 'example')

    def test_2b_complex_export_concepts(self):
        # 24d0d25a-fa75-11e9-b369-3af9d3b32b71  -- also concepts
        url = reverse('resources', kwargs={"resourceid": "24d0d25a-fa75-11e9-b369-3af9d3b32b71"})
        response = self.client.get(url, secure=False) 
        self.assertTrue(response.status_code == 200)
        js = response.json()

        # concept
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P2_has_type" in js)
        c1 = js['http://www.cidoc-crm.org/cidoc-crm/P2_has_type']
        self.assertTrue(type(c1) == dict)
        self.assertTrue(c1['@id'] == "http://localhost:8000/concepts/6bac5802-a6f8-427c-ba5f-d4b30d5b070e")
        self.assertTrue(c1['http://www.w3.org/2000/01/rdf-schema#label'] == "Single Type A")        

        # concept-list
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P45_consists_of" in js)
        mats = js['http://www.cidoc-crm.org/cidoc-crm/P45_consists_of']
        self.assertTrue(type(mats) == list)
        mat1 = mats[0]
        self.assertTrue(type(mat1) == dict)
        # Note that the list is not ordered, and hence can be either a or b
        self.assertTrue(mat1['@id'] in ['http://localhost:8000/concepts/36c8d7a3-32e7-49e4-bd4c-2169a06b240a',
            "http://localhost:8000/concepts/9b61c995-71d8-4bce-987b-0ffa3da4c71c"])
        self.assertTrue(mat1['@type'] == 'http://www.cidoc-crm.org/cidoc-crm/E57_Material')

        # meta concepts
        self.assertTrue('http://www.cidoc-crm.org/cidoc-crm/P101_had_as_general_use' in js)
        cl1 = js['http://www.cidoc-crm.org/cidoc-crm/P101_had_as_general_use']
        self.assertTrue(type(cl1) == dict)
        self.assertTrue(cl1['@id'] == 'http://localhost:8000/concepts/fb457e76-e018-41e7-9be3-0f986816450a')
        self.assertTrue(cl1['@type'] == 'http://www.cidoc-crm.org/cidoc-crm/E55_Type')
        self.assertTrue(cl1['http://www.w3.org/2000/01/rdf-schema#label'] == "Test Type A")

        self.assertTrue('http://www.cidoc-crm.org/cidoc-crm/P2_has_type' in cl1)















