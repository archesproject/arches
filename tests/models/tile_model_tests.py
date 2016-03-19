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

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core import management
from django.test import TestCase,SimpleTestCase
from arches.app.models.tile import Tile
from arches.app.models import models


# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"

def setUpModule():
    management.call_command('packages', operation='setup_db') 
    pass

def tearDownModule():
    pass

class TileTests(TestCase):

    def test_load_from_JSON(self):
        """
        Test that we can initialize a Tile object from JSON

        """

        json = '{"tiles": {"99999999-0000-0000-0000-000000000000": [], "99999999-0000-0000-0000-000000000001": [{"parenttile_id": null, "nodegroup_id": "99999999-0000-0000-0000-000000000001", "resourceinstance_id": "40000000-0000-0000-0000-000000000000", "tileid": "985da56d-316a-4f2e-8759-8e17b6cad918", "data": {"20000000-0000-0000-0000-000000000004": "TEST 2", "20000000-0000-0000-0000-000000000002": "TEST 1"}}]}, "resourceinstance_id": "40000000-0000-0000-0000-000000000000", "parenttile_id": null, "nodegroup_id": "21111111-0000-0000-0000-000000000000", "tileid": "", "data": null}'

        t = Tile(json)
        subTiles = t.tiles["99999999-0000-0000-0000-000000000001"]
        
        self.assertEqual(t.resourceinstance_id, "40000000-0000-0000-0000-000000000000")
        self.assertEqual(t.data, {})
        self.assertEqual(subTiles[0].data["20000000-0000-0000-0000-000000000002"], "TEST 1")


    def test_load_from_python_dict(self):
        """
        Test that we can initialize a Tile object from a Python dictionary

        """

        json = {
          "tiles": {
            "19999999-0000-0000-0000-000000000000": [{
                "tiles": {},
                "resourceinstance_id": "40000000-0000-0000-0000-000000000000",
                "parenttile_id": '',
                "nodegroup_id": "19999999-0000-0000-0000-000000000000",
                "tileid": "",
                "data": {
                  "20000000-0000-0000-0000-000000000004": "TEST 1",
                  "20000000-0000-0000-0000-000000000002": "TEST 2",
                  "20000000-0000-0000-0000-000000000003": "TEST 3"
                }
            }],
            "32999999-0000-0000-0000-000000000000": [{
                "tiles": {},
                "resourceinstance_id": "40000000-0000-0000-0000-000000000000",
                "parenttile_id": '',
                "nodegroup_id": "32999999-0000-0000-0000-000000000000",
                "tileid": "",
                "data": {
                  "20000000-0000-0000-0000-000000000004": "TEST 4",
                  "20000000-0000-0000-0000-000000000002": "TEST 5",
                }
            }]
          },
          "resourceinstance_id": "40000000-0000-0000-0000-000000000000",
          "parenttile_id": '',
          "nodegroup_id": "11111111-0000-0000-0000-000000000000",
          "tileid": "",
          "data": '{}'
        }

        t = Tile(json)
        subTiles = t.tiles["19999999-0000-0000-0000-000000000000"]
        
        self.assertEqual(t.resourceinstance_id, "40000000-0000-0000-0000-000000000000")
        self.assertEqual(t.data, {})
        self.assertEqual(subTiles[0].data["20000000-0000-0000-0000-000000000004"], "TEST 1")


    def test_save(self):
        """
        Test that we can initialize a Tile object from JSON

        """

        json = {
          "tiles": {
            "19999999-0000-0000-0000-000000000000": [{
                "tiles": {},
                "resourceinstance_id": "40000000-0000-0000-0000-000000000000",
                "parenttile_id": '',
                "nodegroup_id": "19999999-0000-0000-0000-000000000000",
                "tileid": "",
                "data": {
                  "20000000-0000-0000-0000-000000000004": "TEST 1",
                  "20000000-0000-0000-0000-000000000002": "TEST 2",
                  "20000000-0000-0000-0000-000000000003": "TEST 3"
                }
            }],
            "32999999-0000-0000-0000-000000000000": [{
                "tiles": {},
                "resourceinstance_id": "40000000-0000-0000-0000-000000000000",
                "parenttile_id": '',
                "nodegroup_id": "32999999-0000-0000-0000-000000000000",
                "tileid": "",
                "data": {
                  "20000000-0000-0000-0000-000000000004": "TEST 4",
                  "20000000-0000-0000-0000-000000000002": "TEST 5",
                }
            }]
          },
          "resourceinstance_id": "40000000-0000-0000-0000-000000000000",
          "parenttile_id": '',
          "nodegroup_id": "11111111-0000-0000-0000-000000000000",
          "tileid": "",
          "data": {}
        }

        t = Tile(json)
        t.save()

        tiles = models.Tile.objects.filter(resourceinstance_id="40000000-0000-0000-0000-000000000000")
        self.assertEqual(tiles.count(), 3)


       