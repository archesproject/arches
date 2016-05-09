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
                "value": "P131 is identified by",
                "classes": [{
                    "id": "6f38d2ca-e114-33a0-b4db-4f298e53be3d",
                    "value": "E82 Actor Appellation"
                }]
            },
            {
                "id": "5869a9ed-ebe5-3613-acc2-29c184737885",
                "value": "P74 has current or former residence",
                "classes": [{
                    "id": "12f08da7-e25c-3e10-8179-62ed76da5da0",
                    "value": "E53 Place"
                }]
            },
            {
                "id": "44813770-321a-370d-bb8f-ba619bcb4334",
                "value": "P75 possesses",
                "classes": [{
                    "id": "e02834c9-ae10-3659-a8e5-ccfdc1866e87",
                    "value": "E30 Right"
                }]
            },
            {
                "id": "e39e863c-0b62-39ae-8db7-e49b56fcbd1e",
                "value": "P76 has contact point",
                "classes": [{
                    "id": "7cee80d2-87e9-3a29-9d1e-f61d46d892ca",
                    "value": "E51 Contact Point"
                },{
                    "id": "ac777d6e-452a-3a10-80c9-5190b5d9f6f2",
                    "value": "E45 Address"
                }]
            }
        ]

        # comparing lists of dictionaries
        # from http://stackoverflow.com/questions/9845369/comparing-2-lists-consisting-of-dictionaries-with-unique-keys-in-python

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


    