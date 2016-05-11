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

from operator import itemgetter, attrgetter
from tests import test_settings
from tests.base_test import ArchesTestCase
from django.core import management
from arches.app.models.ontology import Ontology
from arches.app.utils.betterJSONSerializer import JSONSerializer

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"


class OntologyModelTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        #management.call_command('packages', operation='import_json', source='tests/fixtures/resource_graphs/archesv4_resource.json') 
        cls.E39_Actor = "af051b0a-be2f-39da-8f46-429a714e242c"
        cls.E1_CRM_Entity = "c03db431-4564-34eb-ba86-4c8169e4276c"
        cls.E77_Persistent_Item = "af1d24cc-428c-3689-bbd1-726d62ec5595"

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_related_classes(self):
        """
        test make sure we can retrieve the appropriate classes and properties that relate to the given class 

        """

        ret = []
        lang = 'en-US'
        results = Ontology().get_related_properties(ontology_concept_id=self.E39_Actor, lang=lang)
        self.assertEqual(len(results), 4)
        for result in results:
            item = {
                'ontology_property':{
                    'value': result['ontology_property'].get_preflabel(lang=lang).value,
                    'id': result['ontology_property'].id
                },
                'ontology_classes':[]
            }
            for ontology_class in result['ontology_classes']:
                item['ontology_classes'].append({
                    'value': ontology_class.get_preflabel(lang=lang).value,
                    'id': ontology_class.id
                })
            ret.append(item)
        results = ret
        #print JSONSerializer().serialize(list(results))
        expected_results = [
            {
                "ontology_property": {
                    "id": "68dd1374-d854-3b4e-bca3-95d41675fb2f",
                    "value": "P131 is identified by"
                },
                "ontology_classes": [
                    {
                        "id": "6f38d2ca-e114-33a0-b4db-4f298e53be3d",
                        "value": "E82 Actor Appellation"
                    }
                ]
            },
            {
                "ontology_property": {
                    "id": "5869a9ed-ebe5-3613-acc2-29c184737885",
                    "value": "P74 has current or former residence"
                },
                "ontology_classes": [
                    {
                        "id": "12f08da7-e25c-3e10-8179-62ed76da5da0",
                        "value": "E53 Place"
                    }
                ]
            },
            {
                "ontology_property": {
                    "id": "44813770-321a-370d-bb8f-ba619bcb4334",
                    "value": "P75 possesses"
                },
                "ontology_classes": [
                    {
                        "id": "e02834c9-ae10-3659-a8e5-ccfdc1866e87",
                        "value": "E30 Right"
                    }
                ]
            },
            {
                "ontology_property": {
                    "id": "e39e863c-0b62-39ae-8db7-e49b56fcbd1e",
                    "value": "P76 has contact point"
                },
                "ontology_classes": [
                    {
                        "id": "7cee80d2-87e9-3a29-9d1e-f61d46d892ca",
                        "value": "E51 Contact Point"
                    },
                    {
                        "id": "ac777d6e-452a-3a10-80c9-5190b5d9f6f2",
                        "value": "E45 Address"
                    }
                ]
            }
        ]

        # comparing lists of dictionaries
        # from http://stackoverflow.com/questions/9845369/comparing-2-lists-consisting-of-dictionaries-with-unique-keys-in-python

        self.assertResults(results, expected_results)
        
        ret = []
        results = Ontology().get_related_properties(ontology_concept_id=self.E1_CRM_Entity, lang=lang)
        self.assertEqual(len(results), 5)
        for result in results:
            item = {
                'ontology_property':{
                    'value': result['ontology_property'].get_preflabel(lang=lang).value,
                    'id': result['ontology_property'].id
                },
                'ontology_classes':[]
            }
            for ontology_class in result['ontology_classes']:
                item['ontology_classes'].append({
                    'value': ontology_class.get_preflabel(lang=lang).value,
                    'id': ontology_class.id
                })
            ret.append(item)
        results = ret
        expected_results = [
            {
                "ontology_property": {
                    "id": "9bf487d8-c0a3-3510-b228-1b5cd74f4c56",
                    "value": "P1 is identified by"
                },
                "ontology_classes": [
                    {
                        "id": "e276711d-008c-3380-934b-e048a6a0d665",
                        "value": "E48 Place Name"
                    },
                    {
                        "id": "6f38d2ca-e114-33a0-b4db-4f298e53be3d",
                        "value": "E82 Actor Appellation"
                    },
                    {
                        "id": "7cee80d2-87e9-3a29-9d1e-f61d46d892ca",
                        "value": "E51 Contact Point"
                    },
                    {
                        "id": "48a1d09d-dc16-3903-9ad0-f2eba8b79b20",
                        "value": "E35 Title"
                    },
                    {
                        "id": "b43d4537-6674-37cb-af6e-834b5d63c978",
                        "value": "E41 Appellation"
                    },
                    {
                        "id": "19e2c4fb-70b7-3913-be69-1c824a0bf23f",
                        "value": "E44 Place Appellation"
                    },
                    {
                        "id": "35bfed01-08dc-34b9-94a0-42facd1291ac",
                        "value": "E47 Spatial Coordinates"
                    },
                    {
                        "id": "ae27d5a7-abfc-32e3-9927-99795abc53a4",
                        "value": "E75 Conceptual Object Appellation"
                    },
                    {
                        "id": "ac777d6e-452a-3a10-80c9-5190b5d9f6f2",
                        "value": "E45 Address"
                    },
                    {
                        "id": "fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c",
                        "value": "E42 Identifier"
                    },
                    {
                        "id": "4e3d11b3-c6a8-3838-9a62-0571b84914fa",
                        "value": "E46 Section Definition"
                    },
                    {
                        "id": "c8b36269-f507-32fc-8624-2a9404390719",
                        "value": "E50 Date"
                    },
                    {
                        "id": "9ca9a75f-0eca-378a-a095-91574ad77a30",
                        "value": "E49 Time Appellation"
                    }
                ]
            },
            {
                "ontology_property": {
                    "id": "ada26737-46ff-3a34-8aed-7b70117c34aa",
                    "value": "P137 exemplifies"
                },
                "ontology_classes": [
                    {
                        "id": "a8f7cd0b-8771-3b91-a827-422ff7a15250",
                        "value": "E55 Type"
                    },
                    {
                        "id": "4e75b119-d77b-3c1e-acf8-fbdfd197c9f1",
                        "value": "E56 Language"
                    },
                    {
                        "id": "c1f0e36c-770f-30f9-8241-30d44921c6c8",
                        "value": "E58 Measurement Unit"
                    },
                    {
                        "id": "15afdb47-2e96-3076-8a28-ec86a8fe4674",
                        "value": "E57 Material"
                    }
                ]
            },
            {
                "ontology_property": {
                    "id": "2f8fd82d-2679-3d69-b697-7efe545e76ab",
                    "value": "P2 has type"
                },
                "ontology_classes": [
                    {
                        "id": "a8f7cd0b-8771-3b91-a827-422ff7a15250",
                        "value": "E55 Type"
                    },
                    {
                        "id": "4e75b119-d77b-3c1e-acf8-fbdfd197c9f1",
                        "value": "E56 Language"
                    },
                    {
                        "id": "c1f0e36c-770f-30f9-8241-30d44921c6c8",
                        "value": "E58 Measurement Unit"
                    },
                    {
                        "id": "15afdb47-2e96-3076-8a28-ec86a8fe4674",
                        "value": "E57 Material"
                    }
                ]
            },
            {
                "ontology_property": {
                    "id": "fd06e07d-057b-38aa-99ac-1add45f9f217",
                    "value": "P3 has note"
                },
                "ontology_classes": [
                    {
                        "id": "6e30fbe8-5a0d-3de8-be79-4ec6ebf4db39",
                        "value": "E62 String"
                    }
                ]
            },
            {
                "ontology_property": {
                    "id": "356c8ba7-0114-32c3-861f-8432bc46e963",
                    "value": "P48 has preferred identifier"
                },
                "ontology_classes": [
                    {
                        "id": "fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c",
                        "value": "E42 Identifier"
                    }
                ]
            }
        ]

        #print JSONSerializer().serialize(results)
        self.assertResults(results, expected_results)

    def test_get_superclasses(self):
        """
        test to make sure we can get a distinct list of super classes of a given ontolgy class 

        """

        ontology_concepts = Ontology().get_superclasses(id=self.E39_Actor, lang='en-US')
        self.assertEqual(3, len(ontology_concepts))
        
        ontology_concepts = sorted(ontology_concepts, key=attrgetter("id"))
        classes = sorted([self.E39_Actor, self.E77_Persistent_Item, self.E1_CRM_Entity])
        pairs = zip(classes, ontology_concepts)
        self.assertFalse(any(x != y.id for x, y in pairs))

    def test_get_sub_classes(self):
        pass

    def test_get_relatable_classes_and_properties(self):
        data = {
            "childedges": [
                {
                    "name": None,
                    "edgeid": "a2c06110-16f5-11e6-b8fe-af29a288d01a",
                    "domainnode_id": "20000000-0000-0000-0000-000000000001",
                    "rangenode_id": "20000000-0000-0000-0000-000000000002",
                    "ontologyclass_id": "9bf487d8-c0a3-3510-b228-1b5cd74f4c56",
                    "graphmetadata_id": None,
                    "description": None
                },
                {
                    "name": None,
                    "edgeid": "a2c06660-16f5-11e6-b8fe-a37f8a08ca7b",
                    "domainnode_id": "20000000-0000-0000-0000-000000000001",
                    "rangenode_id": "20000000-0000-0000-0000-000000000004",
                    "ontologyclass_id": "fd06e07d-057b-38aa-99ac-1add45f9f217",
                    "graphmetadata_id": None,
                    "description": None
                },
                {
                    "name": None,
                    "edgeid": "a2c063b8-16f5-11e6-b8fe-b7d2f22d7012",
                    "domainnode_id": "20000000-0000-0000-0000-000000000001",
                    "rangenode_id": "20000000-0000-0000-0000-000000000003",
                    "ontologyclass_id": "2f8fd82d-2679-3d69-b697-7efe545e76ab",
                    "graphmetadata_id": None,
                    "description": None
                }
            ],
            "parentnode": [
                {
                    "ontologyclass_id": "c03db431-4564-34eb-ba86-4c8169e4276c",
                    "description": "Group to hold unique keys used by Arches",
                    "istopnode": False,
                    "validations": [],
                    "nodeid": "20000000-0000-0000-0000-000000000001",
                    "datatype": "semantic",
                    "nodegroup_id": "20000000-0000-0000-0000-000000000001",
                    "graphmetadata_id": None,
                    "name": "KEYS",
                    "cardinality": "n"
                }
            ]
        }
        result = Ontology().get_valid_ontology_concepts(data['parentnode'][0], child_properties=data['childedges'])
        print JSONSerializer().serialize(list(result))
        pass

    def assertResults(self, result, expected_results):
        result = sorted(result, key=lambda res: res['ontology_property']['id'])
        expected_results = sorted(expected_results, key=lambda res: res['ontology_property']['id'])
        pairs = zip(result, expected_results)
        self.assertFalse(any(x['ontology_property']['id'] != y['ontology_property']['id'] for x, y in pairs))
        self.assertFalse(any(x['ontology_property']['value'] != y['ontology_property']['value'] for x, y in pairs))

        for x, y in pairs:
            x['ontology_classes'] = sorted(x['ontology_classes'], key=itemgetter("id"))
            y['ontology_classes'] = sorted(y['ontology_classes'], key=itemgetter("id"))
            class_pairs = zip(x['ontology_classes'], y['ontology_classes'])
            self.assertFalse(any(x['id'] != y['id'] for x, y in class_pairs))
            self.assertFalse(any(x['value'] != y['value'] for x, y in class_pairs))
