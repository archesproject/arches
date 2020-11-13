

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

        with open(os.path.join('tests/fixtures/jsonld_base/models/5136_res_inst_plus_res_inst.json'), 'rU') as f:
            archesfile2 = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile2['graph'])
        BusinessDataImporter('tests/fixtures/jsonld_base/data/test_3_instances.json').import_business_data()  

        with open(os.path.join('tests/fixtures/jsonld_base/models/nesting_test.json'), 'rU') as f:
            archesfile2 = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile2['graph'])
        BusinessDataImporter('tests/fixtures/jsonld_base/data/test_nest_instances.json').import_business_data()  

        with open(os.path.join('tests/fixtures/jsonld_base/models/4564-person.json'), 'rU') as f:
            archesfile2 = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile2['graph'])        

        with open(os.path.join('tests/fixtures/jsonld_base/models/4564-group.json'), 'rU') as f:
            archesfile2 = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile2['graph']) 

        with open(os.path.join('tests/fixtures/jsonld_base/models/4564-referenced.json'), 'rU') as f:
            archesfile2 = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile2['graph']) 
        BusinessDataImporter('tests/fixtures/jsonld_base/data/test_4564_group.json').import_business_data()
        BusinessDataImporter('tests/fixtures/jsonld_base/data/test_4564_reference.json').import_business_data()

        management.call_command('datatype', 'register', source='tests/fixtures/datatypes/color.py')
        management.call_command('datatype', 'register', source='tests/fixtures/datatypes/semantic_like.py')

        with open(os.path.join('tests/fixtures/jsonld_base/models/5299-basic.json'), 'rU') as f:
            archesfile2 = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile2['graph']) 
        BusinessDataImporter('tests/fixtures/jsonld_base/data/test_5299_instances.json').import_business_data()        

        with open(os.path.join('tests/fixtures/jsonld_base/models/5299_complex.json'), 'rU') as f:
            archesfile2 = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile2['graph']) 
        BusinessDataImporter('tests/fixtures/jsonld_base/data/test_5299_complex.json').import_business_data()       


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

    def _create_url(self, resource_id):
        base_url = reverse("resources", kwargs={"resourceid": resource_id})

        return base_url + "?format=json-ld"

    def test_0_missing_resource(self):
        # this 'resources' is from urls.py
        self.client.login(username="admin", password="admin")
        url = self._create_url(resource_id="00000000-f6b5-11e9-8f09-a4d18cec433a")
        response = self.client.get(url, secure=False)
        print(f"test missing on {url} gets {response.status_code}")
        self.assertTrue(response.status_code == 404)

    def test_1_basic_export(self):
        # ef52726c-f6b1-11e9-b47f-a4d18cec433a
        url = self._create_url(resource_id="e6412598-f6b5-11e9-8f09-a4d18cec433a")
        # response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(url, secure=False)
        print(f"test basic on {url} gets {response.status_code}")
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/e6412598-f6b5-11e9-8f09-a4d18cec433a")
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P3_has_note" in js)
        self.assertTrue(js["http://www.cidoc-crm.org/cidoc-crm/P3_has_note"] == "Test Text Here")

    def test_2a_complex_export_data(self):
        # 24d0d25a-fa75-11e9-b369-3af9d3b32b71  -- data types
        url = self._create_url(resource_id="24d0d25a-fa75-11e9-b369-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/24d0d25a-fa75-11e9-b369-3af9d3b32b71")
        self.assertTrue("@type" in js)
        self.assertTrue(js["@type"] == "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object")
        # Test string data type
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P3_has_note" in js)
        self.assertTrue(js["http://www.cidoc-crm.org/cidoc-crm/P3_has_note"] == "Test Data")
        # Test number data type
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P57_has_number_of_parts" in js)
        self.assertTrue(js["http://www.cidoc-crm.org/cidoc-crm/P57_has_number_of_parts"] == 10)
        # Test date data type
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P160_has_temporal_projection" in js)
        ts = js["http://www.cidoc-crm.org/cidoc-crm/P160_has_temporal_projection"]
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin" in ts)
        dt = ts["http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin"]
        self.assertTrue(type(dt) == dict)
        self.assertTrue("@value" in dt)
        self.assertTrue(dt["@value"] == "2019-10-01")
        self.assertTrue("@type" in dt)
        self.assertTrue(dt["@type"] == "http://www.w3.org/2001/XMLSchema#dateTime")
        # Test domain data type
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P79_beginning_is_qualified_by" in ts)
        self.assertTrue(ts["http://www.cidoc-crm.org/cidoc-crm/P79_beginning_is_qualified_by"] == "example")

    def test_2b_complex_export_concepts(self):
        # 24d0d25a-fa75-11e9-b369-3af9d3b32b71  -- also concepts
        url = self._create_url(resource_id="24d0d25a-fa75-11e9-b369-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()

        # concept
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P2_has_type" in js)
        c1 = js["http://www.cidoc-crm.org/cidoc-crm/P2_has_type"]
        self.assertTrue(type(c1) == dict)
        self.assertTrue(c1["@id"] == "http://localhost:8000/concepts/6bac5802-a6f8-427c-ba5f-d4b30d5b070e")
        self.assertTrue(c1["http://www.w3.org/2000/01/rdf-schema#label"] == "Single Type A")

        # concept-list
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P45_consists_of" in js)
        mats = js["http://www.cidoc-crm.org/cidoc-crm/P45_consists_of"]
        self.assertTrue(type(mats) == list)
        mat1 = mats[0]
        self.assertTrue(type(mat1) == dict)
        # Note that the list is not ordered, and hence can be either a or b
        self.assertTrue(
            mat1["@id"]
            in [
                "http://localhost:8000/concepts/36c8d7a3-32e7-49e4-bd4c-2169a06b240a",
                "http://localhost:8000/concepts/9b61c995-71d8-4bce-987b-0ffa3da4c71c",
            ]
        )
        self.assertTrue(mat1["@type"] == "http://www.cidoc-crm.org/cidoc-crm/E57_Material")

        # This is #5136
        # meta concepts
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P101_had_as_general_use" in js)
        cl1 = js["http://www.cidoc-crm.org/cidoc-crm/P101_had_as_general_use"]
        self.assertTrue(type(cl1) == dict)
        self.assertTrue(cl1["@id"] == "http://localhost:8000/concepts/fb457e76-e018-41e7-9be3-0f986816450a")
        self.assertTrue(cl1["@type"] == "http://www.cidoc-crm.org/cidoc-crm/E55_Type")
        self.assertTrue(cl1["http://www.w3.org/2000/01/rdf-schema#label"] == "Test Type A")

        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P2_has_type" in cl1)
        mt1 = cl1["http://www.cidoc-crm.org/cidoc-crm/P2_has_type"]
        self.assertTrue(mt1["@id"] == "http://localhost:8000/concepts/14c92c17-5e2f-413a-95c2-3c5e41ee87d2")

    def test_2c_complex_export_resinst(self):
        # 12bbf5bc-fa85-11e9-91b8-3af9d3b32b71

        # Resource-Instance
        url = self._create_url(resource_id="12bbf5bc-fa85-11e9-91b8-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P46i_forms_part_of" in js)
        ri = js["http://www.cidoc-crm.org/cidoc-crm/P46i_forms_part_of"]
        self.assertTrue(type(ri) == dict)
        self.assertTrue(ri["@id"] == "http://localhost:8000/resources/24d0d25a-fa75-11e9-b369-3af9d3b32b71")
        self.assertTrue(ri["@type"] == "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object")

        # Resource-Instance-List
        url = self._create_url(resource_id="396dcffa-fa8a-11e9-b6e7-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P130_shows_features_of" in js)
        ril = js["http://www.cidoc-crm.org/cidoc-crm/P130_shows_features_of"]
        self.assertTrue(type(ril) == list)
        self.assertTrue(
            ril[0]["@id"]
            in [
                "http://localhost:8000/resources/24d0d25a-fa75-11e9-b369-3af9d3b32b71",
                "http://localhost:8000/resources/12bbf5bc-fa85-11e9-91b8-3af9d3b32b71",
            ]
        )

        # res-inst with concept
        # 9c400558-fa8a-11e9-b6e7-3af9d3b32b71
        # This is #5136 too, applied to a resource-instance

        url = self._create_url(resource_id="9c400558-fa8a-11e9-b6e7-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P132_overlaps_with" in js)
        ri = js["http://www.cidoc-crm.org/cidoc-crm/P132_overlaps_with"]
        self.assertTrue(ri["@id"] == "http://localhost:8000/resources/24d0d25a-fa75-11e9-b369-3af9d3b32b71")

        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P2_has_type" in ri)
        rit = ri["http://www.cidoc-crm.org/cidoc-crm/P2_has_type"]
        self.assertTrue(rit["@id"] == "http://localhost:8000/concepts/fb457e76-e018-41e7-9be3-0f986816450a")

    def test_3_5136_meta_resinst(self):
        # '45fbd100-fb60-11e9-98e3-3af9d3b32b71'

        url = self._create_url(resource_id="45fbd100-fb60-11e9-98e3-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/45fbd100-fb60-11e9-98e3-3af9d3b32b71")
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P10i_contains" in js)
        contained = js["http://www.cidoc-crm.org/cidoc-crm/P10i_contains"]
        self.assertTrue("@id" in contained)
        self.assertTrue(contained["@id"] == "http://localhost:8000/resources/24d0d25a-fa75-11e9-b369-3af9d3b32b71")
        # this will fail
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P10i_contains" in contained)
        meta = contained["http://www.cidoc-crm.org/cidoc-crm/P10i_contains"]
        self.assertTrue("@id" in meta)
        self.assertTrue(meta["@id"] == "http://localhost:8000/resources/12bbf5bc-fa85-11e9-91b8-3af9d3b32b71")

    def test_nesting_permutations_concept(self):
        # This tests nesting permutations of concept and concept-list

        url = self._create_url(resource_id="6edd753e-fbf0-11e9-9ca4-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/6edd753e-fbf0-11e9-9ca4-3af9d3b32b71")

        # test c->c
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P2_has_type" in js)
        typ = js["http://www.cidoc-crm.org/cidoc-crm/P2_has_type"]
        self.assertTrue(typ["@id"] == "http://localhost:8000/concepts/fb457e76-e018-41e7-9be3-0f986816450a")
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P127_has_broader_term" in typ)
        self.assertTrue("http://www.w3.org/2000/01/rdf-schema#label" in typ)
        self.assertTrue(typ["http://www.w3.org/2000/01/rdf-schema#label"] == "Test Type A")
        brd = typ["http://www.cidoc-crm.org/cidoc-crm/P127_has_broader_term"]
        self.assertTrue(brd["@id"] == "http://localhost:8000/concepts/14c92c17-5e2f-413a-95c2-3c5e41ee87d2")
        self.assertTrue("http://www.w3.org/2000/01/rdf-schema#label" in brd)
        self.assertTrue(brd["http://www.w3.org/2000/01/rdf-schema#label"] == "Meta Type A")

        # test cl -> c

        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P45_consists_of" in js)
        self.assertTrue(type(js["http://www.cidoc-crm.org/cidoc-crm/P45_consists_of"]) == list)
        mats = [
            "http://localhost:8000/concepts/9b61c995-71d8-4bce-987b-0ffa3da4c71c",
            "http://localhost:8000/concepts/36c8d7a3-32e7-49e4-bd4c-2169a06b240a",
        ]
        mat1 = js["http://www.cidoc-crm.org/cidoc-crm/P45_consists_of"][0]
        mat2 = js["http://www.cidoc-crm.org/cidoc-crm/P45_consists_of"][1]
        self.assertTrue(mat1["@id"] in mats)
        self.assertTrue(mat2["@id"] in mats and mat1["@id"] != mat2["@id"])
        metatype = "http://localhost:8000/concepts/6bac5802-a6f8-427c-ba5f-d4b30d5b070e"
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P2_has_type" in mat1)
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P2_has_type" in mat2)
        self.assertTrue(mat1["http://www.cidoc-crm.org/cidoc-crm/P2_has_type"]["@id"] == metatype)
        self.assertTrue(mat2["http://www.cidoc-crm.org/cidoc-crm/P2_has_type"]["@id"] == metatype)

        # test cl -> cl

        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P101_had_as_general_use" in js)
        self.assertTrue(type(js["http://www.cidoc-crm.org/cidoc-crm/P101_had_as_general_use"]) == list)
        use1 = js["http://www.cidoc-crm.org/cidoc-crm/P101_had_as_general_use"][0]
        use2 = js["http://www.cidoc-crm.org/cidoc-crm/P101_had_as_general_use"][1]

        useids = [
            "http://localhost:8000/concepts/1df7e2d6-08b2-4fc6-9152-30b72931ba0c",
            "http://localhost:8000/concepts/be4ee3ba-37e4-4e37-b401-069d750734b7",
        ]
        metaids = [
            "http://localhost:8000/concepts/5f32de86-d6be-40ac-a7d3-6999471c4e6e",
            "http://localhost:8000/concepts/babcafca-138f-43e6-b32e-22050d482304",
        ]

        self.assertTrue(use1["@id"] in useids)
        self.assertTrue(use2["@id"] in useids and use1["@id"] != use2["@id"])
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P2_has_type" in use1)
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P2_has_type" in use2)
        self.assertTrue(use1["http://www.cidoc-crm.org/cidoc-crm/P2_has_type"][0]["@id"] in metaids)
        self.assertTrue(use1["http://www.cidoc-crm.org/cidoc-crm/P2_has_type"][1]["@id"] in metaids)
        self.assertTrue(use2["http://www.cidoc-crm.org/cidoc-crm/P2_has_type"][0]["@id"] in metaids)
        self.assertTrue(use2["http://www.cidoc-crm.org/cidoc-crm/P2_has_type"][1]["@id"] in metaids)

        # test c -> cl

        url = self._create_url(resource_id="bbc1651a-fbf3-11e9-9ca4-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/bbc1651a-fbf3-11e9-9ca4-3af9d3b32b71")

        p1 = "http://www.cidoc-crm.org/cidoc-crm/P137_exemplifies"
        p2 = "http://www.cidoc-crm.org/cidoc-crm/P2_has_type"

        tier2ids = [
            "http://localhost:8000/concepts/14c92c17-5e2f-413a-95c2-3c5e41ee87d2",
            "http://localhost:8000/concepts/dcd28b8a-0840-4a7f-a0d6-0341438552e6",
        ]

        self.assertTrue(p1 in js)
        self.assertTrue(type(js[p1]) == dict)
        self.assertTrue(js[p1]["@id"] == "http://localhost:8000/concepts/fb457e76-e018-41e7-9be3-0f986816450a")
        self.assertTrue(p2 in js[p1])
        self.assertTrue(type(js[p1][p2]) == list)
        self.assertTrue(js[p1][p2][0]["@id"] in tier2ids)
        self.assertTrue(js[p1][p2][1]["@id"] in tier2ids)

    def test_nesting_permutations_res_inst(self):

        # This tests nesting resource-instance and resource-instance-list permutations

        # ri -> ri

        url = self._create_url(resource_id="a16ea9a4-fbf1-11e9-9ca4-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/a16ea9a4-fbf1-11e9-9ca4-3af9d3b32b71")

        p1 = "http://www.cidoc-crm.org/cidoc-crm/P10_falls_within"
        p2 = "http://www.cidoc-crm.org/cidoc-crm/P10i_contains"
        self.assertTrue(p1 in js)
        self.assertTrue(type(js[p1]) == dict)
        tier1id = "http://localhost:8000/resources/24d0d25a-fa75-11e9-b369-3af9d3b32b71"
        tier2id = "http://localhost:8000/resources/12bbf5bc-fa85-11e9-91b8-3af9d3b32b71"

        self.assertTrue(js[p1]["@id"] == tier1id)
        self.assertTrue(p2 in js[p1])
        self.assertTrue(js[p1][p2]["@id"] == tier2id)

        # ril -> ri

        url = self._create_url(resource_id="d323639a-fbf1-11e9-9ca4-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/d323639a-fbf1-11e9-9ca4-3af9d3b32b71")

        prop = "http://www.cidoc-crm.org/cidoc-crm/P130_shows_features_of"
        self.assertTrue(prop in js)
        self.assertTrue(type(js[prop]) == list)
        tier1ids = [
            "http://localhost:8000/resources/24d0d25a-fa75-11e9-b369-3af9d3b32b71",
            "http://localhost:8000/resources/396dcffa-fa8a-11e9-b6e7-3af9d3b32b71",
        ]
        tier2id = "http://localhost:8000/resources/12bbf5bc-fa85-11e9-91b8-3af9d3b32b71"

        self.assertTrue(js[prop][0]["@id"] in tier1ids)
        self.assertTrue(js[prop][1]["@id"] in tier1ids)
        self.assertTrue(prop in js[prop][0])
        self.assertTrue(prop in js[prop][1])
        self.assertTrue(js[prop][0][prop]["@id"] == tier2id)
        self.assertTrue(js[prop][0][prop]["@id"] == tier2id)
        self.assertTrue(js[prop][1][prop]["@id"] == tier2id)
        self.assertTrue(js[prop][1][prop]["@id"] == tier2id)

        # ril -> ril

        url = self._create_url(resource_id="b588fae8-fbf1-11e9-9ca4-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/b588fae8-fbf1-11e9-9ca4-3af9d3b32b71")

        prop = "http://www.cidoc-crm.org/cidoc-crm/P133_is_separated_from"
        self.assertTrue(prop in js)
        self.assertTrue(type(js[prop]) == list)
        tier1ids = [
            "http://localhost:8000/resources/12bbf5bc-fa85-11e9-91b8-3af9d3b32b71",
            "http://localhost:8000/resources/24d0d25a-fa75-11e9-b369-3af9d3b32b71",
        ]
        tier2ids = [
            "http://localhost:8000/resources/9c400558-fa8a-11e9-b6e7-3af9d3b32b71",
            "http://localhost:8000/resources/396dcffa-fa8a-11e9-b6e7-3af9d3b32b71",
        ]

        self.assertTrue(js[prop][0]["@id"] in tier1ids)
        self.assertTrue(js[prop][1]["@id"] in tier1ids)
        self.assertTrue(prop in js[prop][0])
        self.assertTrue(prop in js[prop][1])
        self.assertTrue(js[prop][0][prop][0]["@id"] in tier2ids)
        self.assertTrue(js[prop][0][prop][1]["@id"] in tier2ids)
        self.assertTrue(js[prop][1][prop][0]["@id"] in tier2ids)
        self.assertTrue(js[prop][1][prop][1]["@id"] in tier2ids)

    def test_nesting_permutations_res_inst_concept(self):

        # ril -> cl
        url = self._create_url(resource_id="d1d2ce8e-fbf3-11e9-9ca4-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/d1d2ce8e-fbf3-11e9-9ca4-3af9d3b32b71")

        p1 = "http://www.cidoc-crm.org/cidoc-crm/P62_depicts"
        p2 = "http://www.cidoc-crm.org/cidoc-crm/P2_has_type"
        t1ids = [
            "http://localhost:8000/resources/12345678-abcd-11e9-9cbb-3af9d3b32b71",
            "http://localhost:8000/resources/12bbf5bc-fa85-11e9-91b8-3af9d3b32b71",
        ]
        t2ids = [
            "http://localhost:8000/concepts/6458c29a-e043-46f7-b89b-bb6f50be9f78",
            "http://localhost:8000/concepts/fb457e76-e018-41e7-9be3-0f986816450a",
        ]

        self.assertTrue(p1 in js)
        self.assertTrue(type(js[p1]) == list)
        self.assertTrue(js[p1][0]["@id"] in t1ids)
        self.assertTrue(js[p1][1]["@id"] in t1ids)
        self.assertTrue(p2 in js[p1][0])
        self.assertTrue(p2 in js[p1][1])
        self.assertTrue(js[p1][0][p2][0]["@id"] in t2ids)
        self.assertTrue(js[p1][0][p2][1]["@id"] in t2ids)
        self.assertTrue(js[p1][1][p2][0]["@id"] in t2ids)
        self.assertTrue(js[p1][1][p2][1]["@id"] in t2ids)

    def test_4564_export(self):

        # test that the class of the referenced resource-instance is used, not the current model's class
        # for the node.  This is the export side of #4564

        # dc277c1a-fc32-11e9-9201-3af9d3b32b71 references cba81b1a-fc32-11e9-9201-3af9d3b32b71

        url = self._create_url(resource_id="dc277c1a-fc32-11e9-9201-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/dc277c1a-fc32-11e9-9201-3af9d3b32b71")
        prop = "http://www.cidoc-crm.org/cidoc-crm/P51_has_former_or_current_owner"
        self.assertTrue(prop in js)
        ref = js[prop]
        self.assertTrue(js[prop]["@id"] == "http://localhost:8000/resources/cba81b1a-fc32-11e9-9201-3af9d3b32b71")

        url = self._create_url(resource_id="cba81b1a-fc32-11e9-9201-3af9d3b32b71")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js2 = response.json()
        self.assertTrue("@id" in js2)
        self.assertTrue(js2["@id"] == "http://localhost:8000/resources/cba81b1a-fc32-11e9-9201-3af9d3b32b71")

        self.assertTrue(ref["@type"] == "http://www.cidoc-crm.org/cidoc-crm/E74_Group")
        self.assertTrue(js2["@type"] == ref["@type"])

    def test_5299_basic(self):

        url = self._create_url(resource_id="c76f74ba-071a-11ea-8c2d-acde48001122")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/c76f74ba-071a-11ea-8c2d-acde48001122")
        prop = "http://www.cidoc-crm.org/cidoc-crm/P108i_was_produced_by"
        self.assertTrue(prop in js)
        ref = js[prop]
        note = "http://www.cidoc-crm.org/cidoc-crm/P3_has_note"
        self.assertTrue(note in ref)
        self.assertTrue(ref[note] == "Production")
        self.assertTrue(note in js)
        self.assertTrue(js[note] == "#ff00ff")

    def test_5299_complex(self):
        # 7f90ff58-0722-11ea-b628-acde48001122

        url = self._create_url(resource_id="7f90ff58-0722-11ea-b628-acde48001122")
        response = self.client.get(url, secure=False)
        self.assertTrue(response.status_code == 200)
        js = response.json()
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/7f90ff58-0722-11ea-b628-acde48001122")
        prop = "http://www.cidoc-crm.org/cidoc-crm/P108i_was_produced_by"
        self.assertTrue(prop in js)
        ref = js[prop]
        p2 = "http://www.cidoc-crm.org/cidoc-crm/P10i_contains"
        conts = ref[p2]

        self.assertTrue(len(conts) == 2)
        self.assertTrue(conts[0]['@type'] == "http://www.cidoc-crm.org/cidoc-crm/E4_Period")
        self.assertTrue(conts[1]['@type'] == "http://www.cidoc-crm.org/cidoc-crm/E4_Period")        

        note = 'http://www.cidoc-crm.org/cidoc-crm/P3_has_note'
        ts = 'http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span'
        if note in conts[0]:
            self.assertTrue(conts[0][note] == "Note")
            self.assertTrue(ts in conts[1])
            tsdata = conts[1][ts]
        else:
            self.assertTrue(conts[1][note] == "Note")
            self.assertTrue(ts in conts[0])
            tsdata = conts[0][ts]

        botb = 'http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin'
        self.assertTrue(tsdata[botb]['@value'] == "2019-11-01")

