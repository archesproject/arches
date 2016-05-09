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

from operator import itemgetter
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
        management.call_command('packages', operation='import_json', source='tests/fixtures/resource_graphs/archesv4_resource.json') 
        cls.E39_Actor = "af051b0a-be2f-39da-8f46-429a714e242c"
        cls.E1_CRM_Entity = "c03db431-4564-34eb-ba86-4c8169e4276c"

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_related_classes(self):
        """
        test make sure we can retrieve the appropriate classes and properties that relate to the given class 

        """

        result = Ontology().get_related_properties(ontology_concept_id=self.E39_Actor, lang='en-US')
        self.assertEqual(len(result['properties']), 4)

        expected_results = [
            {
                "id": "68dd1374-d854-3b4e-bca3-95d41675fb2f",
                "value": "P131_is_identified_by",
                "classes": [{
                    "id": "6f38d2ca-e114-33a0-b4db-4f298e53be3d",
                    "value": "E82_Actor_Appellation"
                }]
            },
            {
                "id": "5869a9ed-ebe5-3613-acc2-29c184737885",
                "value": "P74_has_current_or_former_residence",
                "classes": [{
                    "id": "12f08da7-e25c-3e10-8179-62ed76da5da0",
                    "value": "E53_Place"
                }]
            },
            {
                "id": "44813770-321a-370d-bb8f-ba619bcb4334",
                "value": "P75_possesses",
                "classes": [{
                    "id": "e02834c9-ae10-3659-a8e5-ccfdc1866e87",
                    "value": "E30_Right"
                }]
            },
            {
                "id": "e39e863c-0b62-39ae-8db7-e49b56fcbd1e",
                "value": "P76_has_contact_point",
                "classes": [{
                    "id": "7cee80d2-87e9-3a29-9d1e-f61d46d892ca",
                    "value": "E51_Contact_Point"
                },{
                    "id": "ac777d6e-452a-3a10-80c9-5190b5d9f6f2",
                    "value": "E45_Address"
                }]
            }
        ]

        # comparing lists of dictionaries
        # from http://stackoverflow.com/questions/9845369/comparing-2-lists-consisting-of-dictionaries-with-unique-keys-in-python

        self.assertResults(result, expected_results)

        result = Ontology().get_related_properties(ontology_concept_id=self.E1_CRM_Entity, lang='en-US')
        self.assertEqual(len(result['properties']), 5)

        print JSONSerializer().serialize(result)

        expected_results = [
            {
                "id": "9bf487d8-c0a3-3510-b228-1b5cd74f4c56",
                "value": "P1_is_identified_by",
                "classes": [
                    {
                        "id": "b43d4537-6674-37cb-af6e-834b5d63c978",
                        "value": "E41_Appellation"
                    },
                    {
                        "id": "48a1d09d-dc16-3903-9ad0-f2eba8b79b20",
                        "value": "E35_Title"
                    },
                    {
                        "id": "fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c",
                        "value": "E42_Identifier"
                    },
                    {
                        "id": "19e2c4fb-70b7-3913-be69-1c824a0bf23f",
                        "value": "E44_Place_Appellation"
                    },
                    {
                        "id": "ac777d6e-452a-3a10-80c9-5190b5d9f6f2",
                        "value": "E45_Address"
                    },
                    {
                        "id": "4e3d11b3-c6a8-3838-9a62-0571b84914fa",
                        "value": "E46_Section_Definition"
                    },
                    {
                        "id": "35bfed01-08dc-34b9-94a0-42facd1291ac",
                        "value": "E47_Spatial_Coordinates"
                    },
                    {
                        "id": "e276711d-008c-3380-934b-e048a6a0d665",
                        "value": "E48_Place_Name"
                    },
                    {
                        "id": "9ca9a75f-0eca-378a-a095-91574ad77a30",
                        "value": "E49_Time_Appellation"
                    },
                    {
                        "id": "c8b36269-f507-32fc-8624-2a9404390719",
                        "value": "E50_Date"
                    },
                    {
                        "id": "7cee80d2-87e9-3a29-9d1e-f61d46d892ca",
                        "value": "E51_Contact_Point"
                    },
                    {
                        "id": "ae27d5a7-abfc-32e3-9927-99795abc53a4",
                        "value": "E75_Conceptual_Object_Appellation"
                    },
                    {
                        "id": "6f38d2ca-e114-33a0-b4db-4f298e53be3d",
                        "value": "E82_Actor_Appellation"
                    }
                ],
            },
            {
                "id": "2f8fd82d-2679-3d69-b697-7efe545e76ab",
                "value": "P2_has_type",
                "classes": [
                    {
                        "id": "a8f7cd0b-8771-3b91-a827-422ff7a15250",
                        "value": "E55_Type"
                    },
                    {
                        "id": "4e75b119-d77b-3c1e-acf8-fbdfd197c9f1",
                        "value": "E56_Language"
                    },
                    {
                        "id": "15afdb47-2e96-3076-8a28-ec86a8fe4674",
                        "value": "E57_Material"
                    },
                    {
                        "id": "c1f0e36c-770f-30f9-8241-30d44921c6c8",
                        "value": "E58_Measurement_Unit"
                    }
                ]
            },
            {
                "id": "fd06e07d-057b-38aa-99ac-1add45f9f217",
                "value": "P3_has_note",
                "classes": [
                    {
                        "id": "6e30fbe8-5a0d-3de8-be79-4ec6ebf4db39",
                        "value": "E62_String"
                    }
                ]
            },
            {
                "id": "356c8ba7-0114-32c3-861f-8432bc46e963",
                "value": "P48_has_preferred_identifier",
                "classes": [
                    {
                        "id": "fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c",
                        "value": "E42_Identifier"
                    }
                ]
            },
            {
                "id": "ada26737-46ff-3a34-8aed-7b70117c34aa",
                "value": "P137_exemplifies",
                "classes": [
                    {
                        "id": "a8f7cd0b-8771-3b91-a827-422ff7a15250",
                        "value": "E55_Type"
                    },
                    {
                        "id": "4e75b119-d77b-3c1e-acf8-fbdfd197c9f1",
                        "value": "E56_Language"
                    },
                    {
                        "id": "15afdb47-2e96-3076-8a28-ec86a8fe4674",
                        "value": "E57_Material"
                    },
                    {
                        "id": "c1f0e36c-770f-30f9-8241-30d44921c6c8",
                        "value": "E58_Measurement_Unit"
                    }
                ]
            }
        ]

        # comparing lists of dictionaries
        # from http://stackoverflow.com/questions/9845369/comparing-2-lists-consisting-of-dictionaries-with-unique-keys-in-python

        self.assertResults(result, expected_results)

    def assertResults(self, result, expected_results):
        result['properties'] = sorted(result['properties'], key=itemgetter("id"))
        expected_results = sorted(expected_results, key=itemgetter("id"))

        pairs = zip(result['properties'], expected_results)
        self.assertFalse(any(x['id'] != y['id'] for x, y in pairs))
        self.assertFalse(any(x['value'] != y['value'] for x, y in pairs))
        
        for x, y in pairs:
            x['classes'] = sorted(x['classes'], key=itemgetter("id"))
            y['classes'] = sorted(y['classes'], key=itemgetter("id"))
            class_pairs = zip(x['classes'], y['classes'])
            self.assertFalse(any(x['id'] != y['id'] for x, y in class_pairs))
            self.assertFalse(any(x['value'] != y['value'] for x, y in class_pairs))

    