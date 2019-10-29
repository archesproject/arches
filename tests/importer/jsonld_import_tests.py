

import os
import json
import csv
import base64
from io import BytesIO
from tests import test_settings
from operator import itemgetter
from django.core import management
from django.test.client import RequestFactory, Client
from django.contrib.auth.models import User, Group, AnonymousUser
from django.urls import reverse
from django.db import connection
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

        sql = """
            INSERT INTO public.oauth2_provider_application(
                id,client_id, redirect_uris, client_type, authorization_grant_type,
                client_secret,
                name, user_id, skip_authorization, created, updated)
            VALUES (
                44,'{oauth_client_id}', 'http://localhost:8000/test', 'public', 'client-credentials',
                '{oauth_client_secret}',
                'TEST APP', {user_id}, false, '1-1-2000', '1-1-2000');
            INSERT INTO public.oauth2_provider_accesstoken(
                token, expires, scope, application_id, user_id, created, updated)
                VALUES ('{token}', '1-1-2068', 'read write', 44, {user_id}, '1-1-2018', '1-1-2018');
        """

        cls.token = 'abc'
        cls.oauth_client_id = 'AAac4uRQSqybRiO6hu7sHT50C4wmDp9fAmsPlCj9'
        cls.oauth_client_secret = '7fos0s7qIhFqUmalDI1QiiYj0rAtEdVMY4hYQDQjOxltbRCBW3dIydOeMD4MytDM9ogCPiYFiMBW6o6ye5bMh5dkeU7pg1cH86wF6Bap9Ke2aaAZaeMPejzafPSj96ID'

        sql = sql.format(
            token=cls.token,
            user_id=1,  # admin is 1
            oauth_client_id=cls.oauth_client_id,
            oauth_client_secret=cls.oauth_client_secret
        )

        cursor = connection.cursor()
        cursor.execute(sql)

        key = '{0}:{1}'.format(cls.oauth_client_id, cls.oauth_client_secret)
        cls.client = Client(HTTP_AUTHORIZATION='Bearer %s' % cls.token)

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
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def tearDown(self):
        pass

    def test_1_basic_import(self):
        data = """{
            "@id": "http://localhost:8000/resources/221d1154-fa8e-11e9-9cbb-3af9d3b32b71",
            "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
            "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "test!"
            }"""

        url = reverse('resources_graphid', kwargs={"graphid": "bf734b4e-f6b5-11e9-8f09-a4d18cec433a", "resourceid": "221d1154-fa8e-11e9-9cbb-3af9d3b32b71"})
        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.assertTrue(response.status_code == 201)
        js = response.json()
        if type(js) == list:
            js = js[0]

        self.assertTrue('@id' in js)
        self.assertTrue(js['@id'] == "http://localhost:8000/resources/221d1154-fa8e-11e9-9cbb-3af9d3b32b71")
        self.assertTrue('http://www.cidoc-crm.org/cidoc-crm/P3_has_note' in js)
        self.assertTrue(js['http://www.cidoc-crm.org/cidoc-crm/P3_has_note'] == 'test!')
