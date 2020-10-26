import os
import json
import csv
import base64
import datetime
from io import BytesIO
from tests import test_settings
from operator import itemgetter
from django.core import management
from django.test.client import RequestFactory, Client
from django.contrib.auth.models import User, Group, AnonymousUser
from django.urls import reverse
from django.db import connection
from tests.base_test import ArchesTestCase, CREATE_TOKEN_SQL
from arches.app.utils.skos import SKOSReader
from arches.app.models.models import TileModel, ResourceInstance
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from arches.app.utils.data_management.resources.exporter import ResourceExporter as BusinessDataExporter
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.data_management.resources.formats import rdffile
from arches.app.utils.data_management.resources.formats.rdffile import JsonLdReader
from pyld.jsonld import expand

# these tests can be run from the command line via
# python manage.py test tests/importer/jsonld_import_tests.py --settings="tests.test_settings"


class JsonLDImportTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        # This runs once per instantiation
        cls.loadOntology()
        cls.factory = RequestFactory()
        cls.token = "abc123"
        cls.client = Client(HTTP_AUTHORIZATION="Bearer %s" % cls.token)

        sql_str = CREATE_TOKEN_SQL.format(token=cls.token, user_id=1)
        cursor = connection.cursor()
        cursor.execute(sql_str)

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/jsonld_base/rdm/jsonld_test_thesaurus.xml")
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/jsonld_base/rdm/jsonld_test_collections.xml")
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/jsonld_base/rdm/5098-thesaurus.xml")
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/jsonld_base/rdm/5098-collections.xml")
        ret = skos.save_concepts_from_skos(rdf)

        # Load up the models and data only once
        with open(os.path.join("tests/fixtures/jsonld_base/models/test_1_basic_object.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        with open(os.path.join("tests/fixtures/jsonld_base/models/test_2_complex_object.json"), "rU") as f:
            archesfile2 = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile2["graph"])

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/jsonld_base/rdm/5098-thesaurus.xml")
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/jsonld_base/rdm/5098-collections.xml")
        ret = skos.save_concepts_from_skos(rdf)

        with open(os.path.join("tests/fixtures/jsonld_base/models/5098_concept_list.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        management.call_command("datatype", "register", source="tests/fixtures/datatypes/color.py")
        management.call_command("datatype", "register", source="tests/fixtures/datatypes/semantic_like.py")

        with open(os.path.join("tests/fixtures/jsonld_base/models/5299-basic.json"), "rU") as f:
            archesfile2 = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile2["graph"])
        with open(os.path.join("tests/fixtures/jsonld_base/models/5299_complex.json"), "rU") as f:
            archesfile2 = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile2["graph"])

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/jsonld_base/rdm/5600-external-thesaurus.xml")
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/jsonld_base/rdm/5600-external-collections.xml")
        ret = skos.save_concepts_from_skos(rdf)

        # Load up the models and data only once
        with open(os.path.join("tests/fixtures/jsonld_base/models/5121_false_ambiguity.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        with open(os.path.join("tests/fixtures/jsonld_base/models/5121_external_model.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        with open(os.path.join("tests/fixtures/jsonld_base/models/6235_parenttile_id.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

    def setUp(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def tearDown(self):
        pass

    def _create_url(self, graph_id, resource_id):
        base_url = reverse(
            "resources_graphid",
            kwargs={"graphid": graph_id, "resourceid": resource_id},
        )

        return base_url + "?format=json-ld"

    def test_context_caching(self):
        data = {
            "@context": "https://linked.art/ns/v1/linked-art.json",
            "id": "https://linked.art/example/object/3",
            "type": "HumanMadeObject",
            "_label": "Black and White Photograph of 'St. Sebastian'",
            "classified_as": [{"id": "http://vocab.getty.edu/aat/300128359", "type": "Type", "_label": "Black and White Photograph"}],
        }

        fetch = rdffile.fetch

        def tempFetch(url):
            raise Exception("This should not happen becauase we cached the doc")

        # rdffile.fetch = tempFetch

        # # first we test that we can override the fetch function and confirm that it gets called
        # with self.assertRaises(Exception):
        #     jsonld_document = expand(data)

        # now set the function back and test normally
        rdffile.fetch = fetch
        jsonld_document = expand(data)
        self.assertTrue(data["@context"] in rdffile.docCache)

        # now set it to the temp fetch and confirm that the tempFetch isn't called on subsequent uses as it was initially
        rdffile.fetch = tempFetch
        jsonld_document = expand(data)
        rdffile.fetch = fetch

        # now invalidate the cache and make sure it refreshes the doc
        rdffile.docCache[data["@context"]]["expires"] = datetime.datetime.now()
        jsonld_document = expand(data)
        self.assertTrue(rdffile.docCache[data["@context"]]["expires"] > datetime.datetime.now())
        self.assertTrue(data["@context"] in rdffile.docCache)

    def test_1_basic_import(self):
        data = """{
            "@id": "http://localhost:8000/resources/221d1154-fa8e-11e9-9cbb-3af9d3b32b71",
            "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
            "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "test!"
            }"""

        url = self._create_url(
            graph_id="bf734b4e-f6b5-11e9-8f09-a4d18cec433a",
            resource_id="221d1154-fa8e-11e9-9cbb-3af9d3b32b71",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertEqual(response.status_code, 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/221d1154-fa8e-11e9-9cbb-3af9d3b32b71")
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P3_has_note" in js)
        self.assertTrue(js["http://www.cidoc-crm.org/cidoc-crm/P3_has_note"] == "test!")

    def test_1b_basic_post(self):
        data = """{
            "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
            "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "test!"
            }"""

        url = self._create_url(
            graph_id="bf734b4e-f6b5-11e9-8f09-a4d18cec433a",
            resource_id="",
        )

        response = self.client.post(url, data=data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertEqual(response.status_code, 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        self.assertTrue("@id" in js)
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P3_has_note" in js)
        self.assertTrue(js["http://www.cidoc-crm.org/cidoc-crm/P3_has_note"] == "test!")

    def test_2_complex_import_data(self):
        # Note that this tests #5136, as the P101 -> P2 is a concept with a concept
        data = """
            {
                "@id": "http://localhost:8000/resources/12345678-abcd-11e9-9cbb-3af9d3b32b71",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
                "http://www.cidoc-crm.org/cidoc-crm/P101_had_as_general_use": {
                    "@id": "http://localhost:8000/concepts/fb457e76-e018-41e7-9be3-0f986816450a",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                    "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": {
                        "@id": "http://localhost:8000/concepts/14c92c17-5e2f-413a-95c2-3c5e41ee87d2",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                        "http://www.w3.org/2000/01/rdf-schema#label": "Meta Type A"
                    },
                    "http://www.w3.org/2000/01/rdf-schema#label": "Test Type A"
                },
                "http://www.cidoc-crm.org/cidoc-crm/P160_has_temporal_projection": {
                    "@id": "http://localhost:8000/tile/9c1ec6b9-1094-427f-acf6-e9c3fca643b6/node/127193ea-fa6d-11e9-b369-3af9d3b32b71",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span",
                    "http://www.cidoc-crm.org/cidoc-crm/P79_beginning_is_qualified_by": "example",
                    "http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin": {
                        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                        "@value": "2019-10-01"
                    }
                },
                "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": {
                    "@id": "http://localhost:8000/concepts/6bac5802-a6f8-427c-ba5f-d4b30d5b070e",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                    "http://www.w3.org/2000/01/rdf-schema#label": "Single Type A"
                },
                "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "Test Data",
                "http://www.cidoc-crm.org/cidoc-crm/P45_consists_of": [
                    {
                        "@id": "http://localhost:8000/concepts/9b61c995-71d8-4bce-987b-0ffa3da4c71c",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E57_Material",
                        "http://www.w3.org/2000/01/rdf-schema#label": "material b"
                    },
                    {
                        "@id": "http://localhost:8000/concepts/36c8d7a3-32e7-49e4-bd4c-2169a06b240a",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E57_Material",
                        "http://www.w3.org/2000/01/rdf-schema#label": "material a"
                    }
                ],
                "http://www.cidoc-crm.org/cidoc-crm/P57_has_number_of_parts": 12
            }
        """

        url = self._create_url(
            graph_id="ee72fb1e-fa6c-11e9-b369-3af9d3b32b71",
            resource_id="12345678-abcd-11e9-9cbb-3af9d3b32b71",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertEqual(response.status_code, 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/12345678-abcd-11e9-9cbb-3af9d3b32b71")

        hagu = "http://www.cidoc-crm.org/cidoc-crm/P101_had_as_general_use"
        p2 = "http://www.cidoc-crm.org/cidoc-crm/P2_has_type"
        temp = "http://www.cidoc-crm.org/cidoc-crm/P160_has_temporal_projection"
        qual = "http://www.cidoc-crm.org/cidoc-crm/P79_beginning_is_qualified_by"
        note = "http://www.cidoc-crm.org/cidoc-crm/P3_has_note"
        pts = "http://www.cidoc-crm.org/cidoc-crm/P57_has_number_of_parts"

        self.assertTrue(hagu in js)
        use = js[hagu]
        self.assertTrue("@id" in use)
        self.assertTrue(use["@id"] == "http://localhost:8000/concepts/fb457e76-e018-41e7-9be3-0f986816450a")
        self.assertTrue(p2 in use)
        self.assertTrue(use[p2]["@id"] == "http://localhost:8000/concepts/14c92c17-5e2f-413a-95c2-3c5e41ee87d2")
        self.assertTrue(temp in js)
        proj = js[temp]
        self.assertTrue(qual in proj)
        self.assertTrue(proj[qual] == "example")
        self.assertTrue(note in js)
        self.assertTrue(js[note] == "Test Data")
        self.assertTrue(pts in js)
        self.assertTrue(js[pts] == 12)

    def test_2b_complex_multiple(self):
        data = """
            {
                "@id": "http://localhost:8000/resources/5e9baff0-109b-11ea-957a-acde48001122",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
                "http://www.cidoc-crm.org/cidoc-crm/P101_had_as_general_use": {
                    "@id": "http://localhost:8000/concepts/fb457e76-e018-41e7-9be3-0f986816450a",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                    "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": {
                        "@id": "http://localhost:8000/concepts/dcd28b8a-0840-4a7f-a0d6-0341438552e6",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                        "http://www.w3.org/2000/01/rdf-schema#label": "Meta Type B"
                    },
                    "http://www.w3.org/2000/01/rdf-schema#label": "Test Type A"
                },
                "http://www.cidoc-crm.org/cidoc-crm/P160_has_temporal_projection": [
                    {
                        "@id": "http://localhost:8000/tile/7e0371da-c62f-46c1-899b-d1e9419a76d5/node/127193ea-fa6d-11e9-b369-3af9d3b32b71",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span",
                        "http://www.cidoc-crm.org/cidoc-crm/P79_beginning_is_qualified_by": "example 2"
                    },
                    {
                        "@id": "http://localhost:8000/tile/8cc347a4-265d-4a06-8327-e198e1d1d0c5/node/127193ea-fa6d-11e9-b369-3af9d3b32b71",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span",
                        "http://www.cidoc-crm.org/cidoc-crm/P79_beginning_is_qualified_by": "example",
                        "http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin": {
                            "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                            "@value": "1903-10-28"
                        }
                    },
                    {
                        "@id": "http://localhost:8000/tile/6011c512-47e9-46c3-b6f3-034dcc6f2a9d/node/127193ea-fa6d-11e9-b369-3af9d3b32b71",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span",
                        "http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin": {
                            "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                            "@value": "2019-11-15"
                        }
                    },
                    {
                        "@id": "http://localhost:8000/tile/7d42af30-4d00-434f-95d4-7a3b3f9bfec8/node/127193ea-fa6d-11e9-b369-3af9d3b32b71",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span",
                        "http://www.cidoc-crm.org/cidoc-crm/P79_beginning_is_qualified_by": "example"
                    }
                ],
                "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": {
                    "@id": "http://localhost:8000/concepts/6bac5802-a6f8-427c-ba5f-d4b30d5b070e",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                    "http://www.w3.org/2000/01/rdf-schema#label": "Single Type A"
                },
                "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": [
                    "asdfasdfa",
                    "1903-10-21"
                ],
                "http://www.cidoc-crm.org/cidoc-crm/P45_consists_of": {
                    "@id": "http://localhost:8000/concepts/36c8d7a3-32e7-49e4-bd4c-2169a06b240a",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E57_Material",
                    "http://www.w3.org/2000/01/rdf-schema#label": "material a"
                },
                "http://www.cidoc-crm.org/cidoc-crm/P57_has_number_of_parts": [
                    2,
                    1
                ]
            } 
        """

        url = self._create_url(
            graph_id="ee72fb1e-fa6c-11e9-b369-3af9d3b32b71",
            resource_id="5e9baff0-109b-11ea-957a-acde48001122",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertEqual(response.status_code, 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/5e9baff0-109b-11ea-957a-acde48001122")

        pts = "http://www.cidoc-crm.org/cidoc-crm/P57_has_number_of_parts"
        note = "http://www.cidoc-crm.org/cidoc-crm/P3_has_note"
        temp = "http://www.cidoc-crm.org/cidoc-crm/P160_has_temporal_projection"
        qual = "http://www.cidoc-crm.org/cidoc-crm/P79_beginning_is_qualified_by"
        botb = "http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin"

        self.assertTrue(pts in js)
        self.assertTrue(set(js[pts]) == set([1, 2]))
        self.assertTrue(note in js)
        self.assertTrue(set(js[note]) == set(["asdfasdfa", "1903-10-21"]))
        self.assertTrue(temp in js)
        temps = js[temp]
        self.assertTrue(len(temps) == 4)
        for t in temps:
            if qual in t:
                self.assertTrue(t[qual] in ["example", "example 2"])
            if botb in t:
                self.assertTrue(t[botb]["@value"] in ["2019-11-15", "1903-10-28"])

    def test_3_5098_concepts(self):
        data = """
            {
                "@id": "http://localhost:8000/resources/0b4439a8-beca-11e9-b4dc-0242ac160002",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E21_Person",
                "http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by": {
                    "@id": "http://localhost:8000/tile/cad329aa-1802-416e-bbce-5f71e21b1a47/node/accb030c-bec9-11e9-b4dc-0242ac160002",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object",
                    "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": [
                        {
                            "@id": "http://localhost:8000/concepts/c3c4b8a8-39bb-41e7-af45-3a0c60fa4ddf",
                            "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                            "http://www.w3.org/2000/01/rdf-schema#label": "Concept 2"
                        },
                        {
                            "@id": "http://localhost:8000/concepts/0bb450bc-8fe3-46cb-968e-2b56849e6e96",
                            "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                            "http://www.w3.org/2000/01/rdf-schema#label": "Concept 1"
                        }
                    ]
                }
            }
        """

        url = self._create_url(
            graph_id="92ccf5aa-bec9-11e9-bd39-0242ac160002",
            resource_id="0b4439a8-beca-11e9-b4dc-0242ac160002",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertEqual(response.status_code, 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        print(f"Got JSON for test 3: {js}")

        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/0b4439a8-beca-11e9-b4dc-0242ac160002")

        types = js["http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by"]["http://www.cidoc-crm.org/cidoc-crm/P2_has_type"]
        self.assertTrue(type(types) == list)
        self.assertTrue(len(types) == 2)
        cids = [
            "http://localhost:8000/concepts/c3c4b8a8-39bb-41e7-af45-3a0c60fa4ddf",
            "http://localhost:8000/concepts/0bb450bc-8fe3-46cb-968e-2b56849e6e96",
        ]
        self.assertTrue(types[0]["@id"] in cids)
        self.assertTrue(types[1]["@id"] in cids)
        self.assertTrue(types[0]["@id"] != types[1]["@id"])

    def test_4_5098_resinst(self):
        # Make instances for this new one to reference
        BusinessDataImporter("tests/fixtures/jsonld_base/data/test_2_instances.json").import_business_data()
        data = """
            {
                "@id": "http://localhost:8000/resources/abcd1234-1234-1129-b6e7-3af9d3b32b71",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
                "http://www.cidoc-crm.org/cidoc-crm/P130_shows_features_of": [
                    {
                        "@id": "http://localhost:8000/resources/12bbf5bc-fa85-11e9-91b8-3af9d3b32b71",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object"
                    },
                    {
                        "@id": "http://localhost:8000/resources/24d0d25a-fa75-11e9-b369-3af9d3b32b71",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object"
                    }
                ],
                "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "res inst list import"
            }
        """

        url = self._create_url(
            graph_id="ee72fb1e-fa6c-11e9-b369-3af9d3b32b71",
            resource_id="abcd1234-1234-1129-b6e7-3af9d3b32b71",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        print(f"Test 4: {response.content}")

        self.assertEqual(response.status_code, 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        # print(f"Got json for test 4: {js}")
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/abcd1234-1234-1129-b6e7-3af9d3b32b71")
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P130_shows_features_of" in js)
        feats = js["http://www.cidoc-crm.org/cidoc-crm/P130_shows_features_of"]
        self.assertTrue(type(feats) == list)
        self.assertTrue(len(feats) == 2)
        rids = [
            "http://localhost:8000/resources/12bbf5bc-fa85-11e9-91b8-3af9d3b32b71",
            "http://localhost:8000/resources/24d0d25a-fa75-11e9-b369-3af9d3b32b71",
        ]
        self.assertTrue(feats[0]["@id"] in rids)
        self.assertTrue(feats[1]["@id"] in rids)

        # test that the default ontologyProperties and inverseOntologyProperties are used
        tiles = TileModel.objects.filter(resourceinstance_id="abcd1234-1234-1129-b6e7-3af9d3b32b71")
        for tile in tiles:
            if "ae93f844-fa6d-11e9-b369-3af9d3b32b71" in tile.data:
                self.assertEqual(
                    tile.data["ae93f844-fa6d-11e9-b369-3af9d3b32b71"][0]["ontologyProperty"],
                    "http://www.cidoc-crm.org/cidoc-crm/P62_depicts",
                )
                self.assertEqual(
                    tile.data["ae93f844-fa6d-11e9-b369-3af9d3b32b71"][0]["inverseOntologyProperty"],
                    "http://www.cidoc-crm.org/cidoc-crm/P62i_is_depicted_by",
                )

    def test_5_5098_resinst_branch(self):
        # 2019-11-01 - Conversely this fails, as it is in a branch
        BusinessDataImporter("tests/fixtures/jsonld_base/data/test_2_instances.json").import_business_data()

        data = """
            {
                "@id": "http://localhost:8000/resources/7fffffff-faa1-11e9-84de-3af9d3b32b71",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
                "http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by": {
                    "@id": "http://localhost:8000/tile/a4896405-5c73-49f4-abd3-651911e82fde/node/51c3ede8-faa1-11e9-84de-3af9d3b32b71",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object",
                    "http://www.cidoc-crm.org/cidoc-crm/P128i_is_carried_by": [
                        {
                            "@id": "http://localhost:8000/resources/24d0d25a-fa75-11e9-b369-3af9d3b32b71",
                            "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object"
                        },
                        {
                            "@id": "http://localhost:8000/resources/12bbf5bc-fa85-11e9-91b8-3af9d3b32b71",
                            "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object"
                        }
                    ]
                }
            }
        """

        # Load up the models and data only once
        with open(os.path.join("tests/fixtures/jsonld_base/models/5098_b_resinst.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        url = self._create_url(
            graph_id="40dbcffa-faa1-11e9-84de-3af9d3b32b71",
            resource_id="7fffffff-faa1-11e9-84de-3af9d3b32b71",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertEqual(response.status_code, 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        print(f"Got json for test 5: {js}")
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/7fffffff-faa1-11e9-84de-3af9d3b32b71")
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by" in js)
        feats = js["http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by"]["http://www.cidoc-crm.org/cidoc-crm/P128i_is_carried_by"]
        self.assertTrue(type(feats) == list)
        self.assertTrue(len(feats) == 2)

    def test_6_5126_collection_filter(self):
        # 2019-11-01 - Fails due to #5126, the concept is not checked against the collection

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/jsonld_base/rdm/5126-thesaurus.xml")
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/jsonld_base/rdm/5126-collections.xml")
        ret = skos.save_concepts_from_skos(rdf)

        # Load up the models and data only once
        with open(os.path.join("tests/fixtures/jsonld_base/models/5126_collection_ambiguity.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        data = """
            {
                "@id": "http://localhost:8000/resources/69a4af50-c055-11e9-b4dc-0242ac160002",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
                "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": {
                    "@id": "http://vocab.getty.edu/aat/300404216",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                    "http://www.w3.org/2000/01/rdf-schema#label": "aquarelles (paintings)"
                }
            }
        """
        url = self._create_url(
            graph_id="09e3dc8a-c055-11e9-b4dc-0242ac160002",
            resource_id="69a4af50-c055-11e9-b4dc-0242ac160002",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        print(f"Test 6 response: {response.content}")

        self.assertTrue(response.status_code == 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        print(f"Got JSON for test 6: {js}")
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/69a4af50-c055-11e9-b4dc-0242ac160002")

        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P2_has_type" in js)
        typ = js["http://www.cidoc-crm.org/cidoc-crm/P2_has_type"]
        self.assertTrue(typ["@id"] == "http://vocab.getty.edu/aat/300404216")

    def test_7_5121_branches(self):
        # 2019-11-01 - This fails due to #5121, the presence of content is not used to rule out the resource-instance branch
        data = """
            {
                "@id": "http://localhost:8000/resources/87654321-c000-1100-b400-0242ac160002",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E21_Person",
                "http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by": {
                    "@id": "http://localhost:8000/tile/17fa1306-d48f-434e-ad37-fc4c9b09d979/node/d1af9e9e-bf96-11e9-b4dc-0242ac160002",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object",
                    "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": {
                        "@id": "http://localhost:8000/concepts/0bb450bc-8fe3-46cb-968e-2b56849e6e96",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                        "http://www.w3.org/2000/01/rdf-schema#label": "Concept 1"
                    },
                    "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "Test Content"
                }
            }
        """

        url = self._create_url(
            graph_id="9f716aa2-bf96-11e9-bd39-0242ac160002",
            resource_id="87654321-c000-1100-b400-0242ac160002",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        print(f"Test 7 response: {response.content}")

        self.assertTrue(response.status_code == 201)
        js = response.json()
        if type(js) == list:
            js = js[0]

        print(f"Got JSON for test 7: {js}")
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/87654321-c000-1100-b400-0242ac160002")

        lo = js["http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by"]
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P3_has_note" in lo)
        self.assertTrue(lo["http://www.cidoc-crm.org/cidoc-crm/P3_has_note"] == "Test Content")

    def test_7b_5121_branches(self):

        # This loads the referenced resource, 2a615f66...001122
        BusinessDataImporter("tests/fixtures/jsonld_base/data/test_5121b_reference_instances.json").import_business_data()

        # The third node is the resource-instance, as has_note is required in the semantic branch
        # So none of the three nodes are ambiguous and should all load at the same time

        data = """
            {
                "@id": "http://localhost:8000/resources/87654321-c000-1100-b400-0242ac160002",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E21_Person",
                "http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by": [{
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object",
                    "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": {
                        "@id": "http://localhost:8000/concepts/0bb450bc-8fe3-46cb-968e-2b56849e6e96",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                        "http://www.w3.org/2000/01/rdf-schema#label": "Concept 1"
                    },
                    "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "Test Content"
                },
                {
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object",
                    "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "No Concept, still unique"
                },
                {
                    "@id": "http://localhost:8000/resources/2a615f66-114d-11ea-8de7-acde48001122",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object"
                }]
            }
        """

        url = self._create_url(
            graph_id="9f716aa2-bf96-11e9-bd39-0242ac160002",
            resource_id="87654321-c000-1100-b400-0242ac160002",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        print(f"Test 7b response: {response.content}")

        self.assertTrue(response.status_code == 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        rtb = "http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by"
        note = "http://www.cidoc-crm.org/cidoc-crm/P3_has_note"

        self.assertTrue(rtb in js)
        self.assertTrue(len(js[rtb]) == 3)

        for r in js[rtb]:
            hasnote = note in r
            isres = r["@id"].startswith("http://localhost:8000/resources/")
            self.assertTrue((hasnote and not isres) or (isres and not hasnote))
            self.assertTrue(not (hasnote and isres))

    def test_8_4564_resinst_models(self):

        with open(os.path.join("tests/fixtures/jsonld_base/models/4564-person.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])
        with open(os.path.join("tests/fixtures/jsonld_base/models/4564-group.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])
        with open(os.path.join("tests/fixtures/jsonld_base/models/4564-referenced.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        aux_data = """
            {
                "@id": "http://localhost:8000/resources/923a5fa8-bfa8-11e9-bd39-0242ac160002",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E74_Group",
                "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "Test Group"
            }
        """

        url = self._create_url(
            graph_id="2c03ddcc-bfa8-11e9-b4dc-0242ac160002",
            resource_id="923a5fa8-bfa8-11e9-bd39-0242ac160002",
        )

        response = self.client.put(url, data=aux_data, HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertTrue(response.status_code == 201)

        data = """
            {
                "@id": "http://localhost:8000/resources/940a2c82-bfa8-11e9-bd39-0242ac160002",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
                "http://www.cidoc-crm.org/cidoc-crm/P51_has_former_or_current_owner": {
                        "@id": "http://localhost:8000/resources/923a5fa8-bfa8-11e9-bd39-0242ac160002",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E74_Group"
                }
            }
        """

        url = self._create_url(
            graph_id="e3d4505e-bfa7-11e9-b4dc-0242ac160002",
            resource_id="940a2c82-bfa8-11e9-bd39-0242ac160002",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        print(f"Test 8 response: {response.content}")

        # this does not currently work
        self.assertTrue(response.status_code == 201)
        js = response.json()
        if type(js) == list:
            js = js[0]

        print(f"Got JSON for test 8: {js}")
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/940a2c82-bfa8-11e9-bd39-0242ac160002")
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P51_has_former_or_current_owner" in js)
        owner = js["http://www.cidoc-crm.org/cidoc-crm/P51_has_former_or_current_owner"]
        self.assertTrue(owner["@id"] == "http://localhost:8000/resources/923a5fa8-bfa8-11e9-bd39-0242ac160002")

    def test_9_5299_basic(self):
        url = self._create_url(
            graph_id="0cadd978-071a-11ea-8d9a-acde48001122",
            resource_id="faceb004-dead-11e9-bd39-0242ac160002",
        )

        data = """
            {
                "@id": "http://localhost:8000/resources/faceb004-dead-11e9-bd39-0242ac160002",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
                "http://www.cidoc-crm.org/cidoc-crm/P108i_was_produced_by": {
                    "@id": "http://localhost:8000/tile/1580cf8b-1ead-42b7-a22a-cc92bff0aafb/node/1ae420ba-071a-11ea-8d9a-acde48001122",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
                    "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "Production"
                },
                "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "#ff00ff"
            }
        """

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        print(f"Test 9 response: {response.content}")

        self.assertTrue(response.status_code == 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        prod = "http://www.cidoc-crm.org/cidoc-crm/P108i_was_produced_by"
        note = "http://www.cidoc-crm.org/cidoc-crm/P3_has_note"

        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/faceb004-dead-11e9-bd39-0242ac160002")
        self.assertTrue(prod in js)
        prodjs = js[prod]
        self.assertTrue(note in prodjs)
        self.assertTrue(prodjs[note] == "Production")
        self.assertTrue(note in js)
        self.assertTrue(js[note] == "#ff00ff")

    def test_a_5299_complex(self):
        url = self._create_url(
            graph_id="f348bbda-0721-11ea-b628-acde48001122",
            resource_id="deadface-0000-11e9-bd39-0242ac160002",
        )

        data = """
            {
                "@id": "http://localhost:8000/resources/deadface-0000-11ea-b628-acde48001122",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
                "http://www.cidoc-crm.org/cidoc-crm/P108i_was_produced_by": {
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
                    "http://www.cidoc-crm.org/cidoc-crm/P10i_contains": [
                        {
                            "@type": "http://www.cidoc-crm.org/cidoc-crm/E4_Period",
                            "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "Import Note"
                        },
                        {
                            "@type": "http://www.cidoc-crm.org/cidoc-crm/E4_Period",
                            "http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span": {
                                "@type": "http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span",
                                "http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin": {
                                    "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                                    "@value": "2018-01-01"
                                }
                            }
                        }
                    ]
                }
            }
        """

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        print(f"Test 9 response: {response.content}")

        self.assertTrue(response.status_code == 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/deadface-0000-11e9-bd39-0242ac160002")

        prod = "http://www.cidoc-crm.org/cidoc-crm/P108i_was_produced_by"
        note = "http://www.cidoc-crm.org/cidoc-crm/P3_has_note"
        conts = "http://www.cidoc-crm.org/cidoc-crm/P10i_contains"
        ts = "http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span"
        botb = "http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin"
        prodjs = js[prod]
        contl = prodjs[conts]

        self.assertTrue(len(contl) == 2)
        if note in contl[0]:
            print(f"note data: {contl[0]}")
            self.assertTrue(contl[0][note] == "Import Note")
            jsts = contl[1][ts]
        else:
            print(f"note data: {contl[1]}")
            self.assertTrue(contl[1][note] == "Import Note")
            jsts = contl[0][ts]
        self.assertTrue(jsts[botb]["@value"] == "2018-01-01")

    def test_b_5600_concept_label(self):

        with open(os.path.join("tests/fixtures/jsonld_base/models/5600-external-label.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        data = """
            {
                "@id": "http://localhost:8000/resources/61787e78-0e3f-11ea-b4f1-acde48001122",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
                "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": {
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E42_Identifier",
                    "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "madonna bla bla",
                    "http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by": {
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object",
                        "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "sale bla bla"
                    }
                },
                "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": {
                    "@id": "http://vocab.getty.edu/aat/300033898",
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                    "http://www.w3.org/2000/01/rdf-schema#label": "History"
                },
                "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "visual work of madonna bla bla"
            }     
        """

        url = self._create_url(
            graph_id="9d2c2ca0-0e3d-11ea-b4f1-acde48001122",
            resource_id="61787e78-0e3f-11ea-b4f1-acde48001122",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")

        print(f"\n\n\nTest b response: {response.content}")
        self.assertTrue(response.status_code == 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/61787e78-0e3f-11ea-b4f1-acde48001122")

    def test_c_path_with_array(self):

        with open(os.path.join("tests/fixtures/jsonld_base/models/string_to_path_basic.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        data = """
            {
                "@id": "http://localhost:8000/resources/5683f462-107d-11ea-b7e9-acde48001122",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E21_Person",
                "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": [
                    {
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E41_Appellation",
                        "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "remy pour la russie"
                    },
                    {
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E41_Appellation",
                        "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": {
                            "@id": "http://vocab.getty.edu/aat/300033898",
                            "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                            "http://www.w3.org/2000/01/rdf-schema#label": "History"
                        },
                        "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "remy"
                    }
                ],
                "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "remy"
            }
        """

        url = self._create_url(
            graph_id="d5456066-107c-11ea-b7e9-acde48001122",
            resource_id="5683f462-107d-11ea-b7e9-acde48001122",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        print(f"\n\n\nTest c response: {response.content}")

        self.assertTrue(response.status_code == 201)

        js = response.json()
        if type(js) == list:
            js = js[0]
        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/5683f462-107d-11ea-b7e9-acde48001122")

        idby = "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by"
        self.assertTrue(idby in js)
        self.assertTrue(len(js[idby]) == 2)

    def test_d_path_with_array_2(self):
        data = """
            {
                "@id": "http://localhost:8000/resources/10000000-109b-11ea-957a-acde48001122",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
                "http://www.cidoc-crm.org/cidoc-crm/P57_has_number_of_parts": [
                    2,
                    1
                ]
            }     
        """

        url = self._create_url(
            graph_id="ee72fb1e-fa6c-11e9-b369-3af9d3b32b71",
            resource_id="10000000-109b-11ea-957a-acde48001122",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/10000000-109b-11ea-957a-acde48001122")
        pts = "http://www.cidoc-crm.org/cidoc-crm/P57_has_number_of_parts"
        self.assertTrue(pts in js)
        self.assertTrue(set(js[pts]) == set([1, 2]))

    def test_e_path_with_array_resinst(self):
        # 2019-11-27 - Passing with extra @id checks in rdffile
        data = """
            {
                "@id": "http://localhost:8000/resources/8e870000-114e-11ea-8de7-acde48001122",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E21_Person",
                "http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by": [
                    {
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object",
                        "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "test 1"
                    },
                    {
                        "@id": "http://localhost:8000/resources/2a615f66-114d-11ea-8de7-acde48001122",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object"
                    }
                ]
            }
        """

        url = self._create_url(
            graph_id="9f716aa2-bf96-11e9-bd39-0242ac160002",
            resource_id="8e870000-114e-11ea-8de7-acde48001122",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertEqual(response.status_code, 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/8e870000-114e-11ea-8de7-acde48001122")

        rtb = "http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by"
        note = "http://www.cidoc-crm.org/cidoc-crm/P3_has_note"
        self.assertTrue(rtb in js)
        self.assertTrue(len(js[rtb]) == 2)
        rtb1 = js[rtb][0]
        rtb2 = js[rtb][1]
        if note in rtb1:
            self.assertTrue(rtb2["@id"].startswith("http://localhost:8000/resources"))
        else:
            self.assertTrue(rtb1["@id"].startswith("http://localhost:8000/resources"))


    def test_f_big_nest_mess(self):

        data = """{
            "@id": "http://localhost:8000/resources/c3b693cc-1542-11ea-b353-acde48001122",
            "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
            "http://www.cidoc-crm.org/cidoc-crm/P108i_was_produced_by": [
                {
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
                "http://www.cidoc-crm.org/cidoc-crm/P10_falls_within": [
                    {
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
                    "http://www.cidoc-crm.org/cidoc-crm/P14_carried_out_by": {
                        "@id": "http://localhost:8000/resources/5e9baff0-109b-11ea-957a-acde48001122",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E21_Person"
                    },
                    "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "asdf",
                    "http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span": {
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span",
                        "http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin": {
                        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                        "@value": "2019-12-03"
                        },
                        "http://www.cidoc-crm.org/cidoc-crm/P82b_end_of_the_end": {
                        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                        "@value": "2019-12-05"
                        },
                        "http://www.cidoc-crm.org/cidoc-crm/P83_had_at_least_duration": {
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E54_Dimension",
                        "http://www.cidoc-crm.org/cidoc-crm/P90_has_value": 1
                        }
                    }
                    },
                    {
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
                    "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "second part",
                    "http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span": {
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span",
                        "http://www.cidoc-crm.org/cidoc-crm/P83_had_at_least_duration": {
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E54_Dimension",
                        "http://www.cidoc-crm.org/cidoc-crm/P90_has_value": 6
                        }
                    }
                    }
                ]
                },
                {
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
                "http://www.cidoc-crm.org/cidoc-crm/P10_falls_within": {
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
                    "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "bar",
                    "http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span": {
                    "@type": "http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span",
                    "http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin": {
                        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                        "@value": "2019-12-07"
                    },
                    "http://www.cidoc-crm.org/cidoc-crm/P82b_end_of_the_end": {
                        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
                        "@value": "2019-12-08"
                    }
                    }
                }
                }
            ],
            "http://www.cidoc-crm.org/cidoc-crm/P138i_has_representation": {
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E36_Visual_Item",
                "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": {
                "@id": "http://localhost:8000/concepts/36c8d7a3-32e7-49e4-bd4c-2169a06b240a",
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                "http://www.w3.org/2000/01/rdf-schema#label": "material a"
                }
            }
            }
            """

        with open(os.path.join("tests/fixtures/jsonld_base/models/nest_test.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        url = self._create_url(
            graph_id="9b596906-1540-11ea-b353-acde48001122",
            resource_id="c3b693cc-1542-11ea-b353-acde48001122",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.assertEqual(response.status_code, 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        self.assertTrue("@id" in js)
        self.assertTrue(js["@id"] == "http://localhost:8000/resources/c3b693cc-1542-11ea-b353-acde48001122")

        # TODO - more asserts to make sure data is saved correctly

    def test_g_6235_parenttile(self):

        data = """{
            "@id": "http://localhost:8000/resources/05f314d0-7a7b-4408-8d9b-f0b61f1fb27d",
            "@type": "http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object",
            "http://www.cidoc-crm.org/cidoc-crm/P108i_was_produced_by": {
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
                "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": {
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E41_Appellation",
                "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "a"
                },
                "http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span": {
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E52_Time-Span",
                "http://www.cidoc-crm.org/cidoc-crm/P82a_begin_of_the_begin": {
                    "@type": "http://www.w3.org/2001/XMLSchema#dateTime", "@value": "2020-07-08"}
                },
                "http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by": {
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object",
                "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "b"
                }
            },
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by": {
                "@type": "http://www.cidoc-crm.org/cidoc-crm/E41_Appellation",
                "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "test 1"
            }
            }
            """

        url = self._create_url(
            graph_id="0bc001c2-c163-11ea-8354-3af9d3b32b71",
            resource_id="05f314d0-7a7b-4408-8d9b-f0b61f1fb27d",
        )

        response = self.client.put(url, data=data, HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(response.status_code, 201)

        js = response.json()
        if type(js) == list:
            js = js[0]

        # And validate that all three of E52, E33 and E41 are there

        prod = js["http://www.cidoc-crm.org/cidoc-crm/P108i_was_produced_by"]
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by" in prod)
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span" in prod)
        self.assertTrue("http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by" in prod)
