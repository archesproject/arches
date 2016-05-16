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
        cls.E63_Beginning_of_Existence = "255bba42-8ffb-3796-9caa-807179a20d9a"
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
        results = Ontology().get_related_properties(ontology_concept_id=self.E63_Beginning_of_Existence, lang=lang)
        self.assertEqual(len(results), 1)
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
        # print JSONSerializer().serialize(list(results))
        expected_results = [
            {
                "ontology_property": {
                    "id": "c2b2aac9-2434-3e1e-b4a4-52a7a317ff72",
                    "value": "P92 brought into existence"
                },
                "ontology_classes": [
                    {
                        "id": "3f975fdf-518e-3ac6-9037-8a288f3bd6c4",
                        "value": "E19 Physical Object"
                    },
                    {
                        "id": "9ff08a71-8094-35ed-9005-d94abddefdfe",
                        "value": "E21 Person"
                    },
                    {
                        "id": "4bb246c3-e51e-32f9-a466-3003a17493c5",
                        "value": "E25 Man-Made Feature"
                    },
                    {
                        "id": "4389f634-920e-3cbb-bc3a-2a68eaa6df24",
                        "value": "E18 Physical Thing"
                    },
                    {
                        "id": "7cee80d2-87e9-3a29-9d1e-f61d46d892ca",
                        "value": "E51 Contact Point"
                    },
                    {
                        "id": "2bc61bb4-384d-3427-bc89-2320be9896f2",
                        "value": "E26 Physical Feature"
                    },
                    {
                        "id": "a8f7cd0b-8771-3b91-a827-422ff7a15250",
                        "value": "E55 Type"
                    },
                    {
                        "id": "8c2720ca-5c3f-3dd0-af7c-cf217f64babb",
                        "value": "E70 Thing"
                    },
                    {
                        "id": "c1f0e36c-770f-30f9-8241-30d44921c6c8",
                        "value": "E58 Measurement Unit"
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
                        "id": "c8b36269-f507-32fc-8624-2a9404390719",
                        "value": "E50 Date"
                    },
                    {
                        "id": "211d0da0-5fd2-3d83-bb88-c08c71b46feb",
                        "value": "E74 Group"
                    },
                    {
                        "id": "40a8beed-541b-35cd-b287-b7c345f998fe",
                        "value": "E40 Legal Body"
                    },
                    {
                        "id": "a89d6e8b-6f86-33cd-9084-b6c77165bed1",
                        "value": "E27 Site"
                    },
                    {
                        "id": "e276711d-008c-3380-934b-e048a6a0d665",
                        "value": "E48 Place Name"
                    },
                    {
                        "id": "31aab780-6dfa-3742-bd7a-7ef0310ed0b1",
                        "value": "E73 Information Object"
                    },
                    {
                        "id": "6f38d2ca-e114-33a0-b4db-4f298e53be3d",
                        "value": "E82 Actor Appellation"
                    },
                    {
                        "id": "48a1d09d-dc16-3903-9ad0-f2eba8b79b20",
                        "value": "E35 Title"
                    },
                    {
                        "id": "5d9e0c89-8d69-3a58-8c53-3f47236c86f7",
                        "value": "E90 Symbolic Object"
                    },
                    {
                        "id": "2c287084-c289-36b2-8328-853e381f0ed4",
                        "value": "E20 Biological Object"
                    },
                    {
                        "id": "b43d4537-6674-37cb-af6e-834b5d63c978",
                        "value": "E41 Appellation"
                    },
                    {
                        "id": "9ca9a75f-0eca-378a-a095-91574ad77a30",
                        "value": "E49 Time Appellation"
                    },
                    {
                        "id": "9cc69985-2a19-3fa6-abf5-addf02a52b90",
                        "value": "E38 Image"
                    },
                    {
                        "id": "fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9",
                        "value": "E22 Man-Made Object"
                    },
                    {
                        "id": "675b1b07-d25a-3539-b5d9-84ee73f3e39e",
                        "value": "E36 Visual Item"
                    },
                    {
                        "id": "a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8",
                        "value": "E24 Physical Man-Made Thing"
                    },
                    {
                        "id": "78b224a2-9271-3716-8c2e-c82302cdae9c",
                        "value": "E72 Legal Object"
                    },
                    {
                        "id": "4e75b119-d77b-3c1e-acf8-fbdfd197c9f1",
                        "value": "E56 Language"
                    },
                    {
                        "id": "7e62fc5e-947d-3806-bcd7-ce6bb716b6fe",
                        "value": "E37 Mark"
                    },
                    {
                        "id": "ae27d5a7-abfc-32e3-9927-99795abc53a4",
                        "value": "E75 Conceptual Object Appellation"
                    },
                    {
                        "id": "e02834c9-ae10-3659-a8e5-ccfdc1866e87",
                        "value": "E30 Right"
                    },
                    {
                        "id": "18a02c1c-38df-3f50-baf5-fc0b5bf2732d",
                        "value": "E89 Propositional Object"
                    },
                    {
                        "id": "3b35ea57-508c-352e-8d98-ec5cbc29c7a7",
                        "value": "E29 Design or Procedure"
                    },
                    {
                        "id": "b850529a-18cd-3fbc-9ab2-e1302ee000a6",
                        "value": "E84 Information Carrier"
                    },
                    {
                        "id": "a9888169-3160-3403-a8a2-3fa260b1ad16",
                        "value": "E78 Collection"
                    },
                    {
                        "id": "19e2c4fb-70b7-3913-be69-1c824a0bf23f",
                        "value": "E44 Place Appellation"
                    },
                    {
                        "id": "0df9cb10-1203-3efd-8d9e-448f5b02506b",
                        "value": "E32 Authority Document"
                    },
                    {
                        "id": "0fb4acc5-0860-3bac-a8f4-3f833baaca9d",
                        "value": "E28 Conceptual Object"
                    },
                    {
                        "id": "35bfed01-08dc-34b9-94a0-42facd1291ac",
                        "value": "E47 Spatial Coordinates"
                    },
                    {
                        "id": "af051b0a-be2f-39da-8f46-429a714e242c",
                        "value": "E39 Actor"
                    },
                    {
                        "id": "af1d24cc-428c-3689-bbd1-726d62ec5595",
                        "value": "E77 Persistent Item"
                    },
                    {
                        "id": "84a17c0c-78f2-3607-ba85-da1fc47def5a",
                        "value": "E31 Document"
                    },
                    {
                        "id": "558bfc6c-03fc-3f1a-81d2-95493448d4a9",
                        "value": "E71 Man-Made Thing"
                    },
                    {
                        "id": "fa1b039d-00cd-36e8-b03c-247176a6368d",
                        "value": "E33 Linguistic Object"
                    },
                    {
                        "id": "4e3d11b3-c6a8-3838-9a62-0571b84914fa",
                        "value": "E46 Section Definition"
                    },
                    {
                        "id": "15afdb47-2e96-3076-8a28-ec86a8fe4674",
                        "value": "E57 Material"
                    },
                    {
                        "id": "21fa6d60-095b-3044-9ca3-088e2cdab1f0",
                        "value": "E34 Inscription"
                    }
                ]
            }
        ]

        # comparing lists of dictionaries
        # from http://stackoverflow.com/questions/9845369/comparing-2-lists-consisting-of-dictionaries-with-unique-keys-in-python

        self.assertResults(results, expected_results)
        
        ret = []
        results = Ontology().get_related_properties(ontology_concept_id=self.E1_CRM_Entity, lang=lang)
        # self.assertEqual(len(results), 5)
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
        # self.assertResults(results, expected_results)

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
        # print JSONSerializer().serialize(list(result))
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
