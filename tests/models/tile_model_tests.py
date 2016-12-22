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

from django.db import connection
from django.core import management
from tests.base_test import ArchesTestCase
from arches.app.models.tile import Tile
from arches.app.models import models


# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"

class TileTests(ArchesTestCase):

    @classmethod
    def setUpClass(cls):
        sql = """
        INSERT INTO node_groups(nodegroupid, legacygroupid, cardinality)
            VALUES ('99999999-0000-0000-0000-000000000001', '', 'n');

        INSERT INTO node_groups(nodegroupid, legacygroupid, cardinality)
            VALUES ('32999999-0000-0000-0000-000000000000', '', 'n');

        INSERT INTO node_groups(nodegroupid, legacygroupid, cardinality)
            VALUES ('19999999-0000-0000-0000-000000000000', '', 'n');

        INSERT INTO node_groups(nodegroupid, legacygroupid, cardinality)
            VALUES ('21111111-0000-0000-0000-000000000000', '', 'n');
        """

        cursor = connection.cursor()
        cursor.execute(sql)

    @classmethod
    def tearDownClass(cls):
        sql = """
        DELETE FROM public.node_groups
        WHERE nodegroupid = '99999999-0000-0000-0000-000000000001' OR
        nodegroupid = '32999999-0000-0000-0000-000000000000' OR
        nodegroupid = '19999999-0000-0000-0000-000000000000' OR
        nodegroupid = '21111111-0000-0000-0000-000000000000'

        """

        cursor = connection.cursor()
        cursor.execute(sql)

    def setUp(self):
        cursor = connection.cursor()
        cursor.execute("Truncate public.tiles Cascade;")

    def tearDown(self):
        pass

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
            "nodegroup_id": "20000000-0000-0000-0000-000000000001",
            "tileid": "",
            "data": {}
        }

        t = Tile(json)
        subTiles = t.tiles["19999999-0000-0000-0000-000000000000"]

        self.assertEqual(t.resourceinstance_id, "40000000-0000-0000-0000-000000000000")
        self.assertEqual(t.data, {})
        self.assertEqual(subTiles[0].data["20000000-0000-0000-0000-000000000004"], "TEST 1")


    # def test_save(self):
    #     """
    #     Test that we can save a Tile object back to the database
    #
    #     """
    #
    #     json = {
    #         "tiles": {
    #             "19999999-0000-0000-0000-000000000000": [{
    #                 "tiles": {},
    #                 "resourceinstance_id": "40000000-0000-0000-0000-000000000000",
    #                 "parenttile_id": '',
    #                 "nodegroup_id": "19999999-0000-0000-0000-000000000000",
    #                 "tileid": "",
    #                 "data": {
    #                   "20000000-0000-0000-0000-000000000004": "TEST 1",
    #                   "20000000-0000-0000-0000-000000000002": "TEST 2",
    #                   "20000000-0000-0000-0000-000000000003": "TEST 3"
    #                 }
    #             }],
    #             "32999999-0000-0000-0000-000000000000": [{
    #                 "tiles": {},
    #                 "resourceinstance_id": "40000000-0000-0000-0000-000000000000",
    #                 "parenttile_id": '',
    #                 "nodegroup_id": "32999999-0000-0000-0000-000000000000",
    #                 "tileid": "",
    #                 "data": {
    #                   "20000000-0000-0000-0000-000000000004": "TEST 4",
    #                   "20000000-0000-0000-0000-000000000002": "TEST 5",
    #                 }
    #             }]
    #         },
    #         "resourceinstance_id": "40000000-0000-0000-0000-000000000000",
    #         "parenttile_id": '',
    #         "nodegroup_id": "20000000-0000-0000-0000-000000000001",
    #         "tileid": "",
    #         "data": {}
    #     }
    #
    #     t = Tile(json)
    #     t.save(index=False)
    #
    #     tiles = Tile.objects.filter(resourceinstance_id="40000000-0000-0000-0000-000000000000")
    #     self.assertEqual(tiles.count(), 3)

    def test_simple_get(self):
        """
        Test that we can get a Tile object

        """

        json = {
            "tiles": {},
            "resourceinstance_id": "40000000-0000-0000-0000-000000000000",
            "parenttile_id": '',
            "nodegroup_id": "20000000-0000-0000-0000-000000000001",
            "tileid": "",
            "data": {
              "20000000-0000-0000-0000-000000000004": "TEST 1"
            }
        }

        t = Tile(json)
        t.save(index=False)

        t2 = Tile.objects.get(tileid=t.tileid)

        self.assertEqual(t.tileid, t2.tileid)
        self.assertEqual(t2.data["20000000-0000-0000-0000-000000000004"], "TEST 1")

    # def test_validation(self):
    #     """
    #     Test that we can get a Tile object

    #     """

    #     json = {
    #         "tiles": {},
    #         "resourceinstance_id": "40000000-0000-0000-0000-000000000000",
    #         "parenttile_id": '',
    #         "nodegroup_id": "20000000-0000-0000-0000-000000000001",
    #         "tileid": "",
    #         "data": {
    #           "20000000-0000-0000-0000-000000000004": "TEST 1"
    #         }
    #     }

    #     t = Tile(json)
    #     self.assertTrue(t.validate()['is_valid'])

    #     json['data']['20000000-0000-0000-0000-000000000004'] = ''

    #     t2 = Tile(json)
    #     self.assertFalse(t2.validate()['is_valid'])
