"""
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
"""

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import Language
from arches.app.models.tile import Tile
from tests.base_test import ArchesTestCase


# these tests can be run from the command line via
# python manage.py test tests/utils/datatype_tests.py --pattern="*.py" --settings="tests.test_settings"


class StringDataTypeTests(ArchesTestCase):
    def test_string_validate(self):
        string = DataTypeFactory().get_instance("string")
        some_errors = string.validate("")
        self.assertGreater(len(some_errors), 0)
        no_errors = string.validate({"en": {"value": "hello", "direction": "ltr"}})
        self.assertEqual(len(no_errors), 0)

    def test_tile_transform(self):
        string = DataTypeFactory().get_instance("string")
        new_language = Language(code="fa", name="Fake", default_direction="ltr", scope="system")
        new_language.save()
        tile_value = string.transform_value_for_tile("hello|fa")
        self.assertEqual(type(tile_value), dict)
        self.assertTrue("fa" in tile_value.keys())
        new_language.delete()

    def test_tile_clean(self):
        string = DataTypeFactory().get_instance("string")
        nodeid = "72048cb3-adbc-11e6-9ccf-14109fd34195"
        resourceinstanceid = "40000000-0000-0000-0000-000000000000"

        json_all_empty_strings = {
            "resourceinstance_id": resourceinstanceid,
            "parenttile_id": "",
            "nodegroup_id": nodeid,
            "tileid": "",
            "data": {nodeid: {"en": {"value": "", "direction": "ltr"}}},
        }
        tile1 = Tile(json_all_empty_strings)
        string.clean(tile1, nodeid)

        self.assertIsNone(tile1.data[nodeid])

        json_some_empty_strings = {
            "resourceinstance_id": resourceinstanceid,
            "parenttile_id": "",
            "nodegroup_id": nodeid,
            "tileid": "",
            "data": {nodeid: {
                "en": {"value": "", "direction": "ltr"},
                "de": {"value": "danke", "direction": "ltr"},
            }},
        }
        tile2 = Tile(json_some_empty_strings)
        string.clean(tile2, nodeid)

        self.assertIsNotNone(tile2.data[nodeid])


class URLDataTypeTests(ArchesTestCase):
    def test_validate(self):
        url = DataTypeFactory().get_instance("url")

        # Valid tile
        no_errors = url.validate({"url": "https://www.google.com/", "url_label": "Google"})
        self.assertEqual(len(no_errors), 0)
        # Invalid URL
        some_errors_invalid_url = url.validate({"url": "google", "url_label": "Google"})
        self.assertEqual(len(some_errors_invalid_url), 1)
        # No URL added - cannot save label without URL
        some_errors_no_url = url.validate({"url_label": "Google"})
        self.assertEqual(len(some_errors_no_url), 1)
        # No URL added - with url empty string in object
        some_errors_no_url = url.validate({"url": "", "url_label": "Google"})
        self.assertEqual(len(some_errors_no_url), 1)

    def test_pre_tile_save(self):
        url = DataTypeFactory().get_instance("url")

        nodeid = "c0ed4b2a-c4cc-11ee-9626-00155de1df34"
        resourceinstanceid = "40000000-0000-0000-0000-000000000000"

        url_no_label = {
            "resourceinstance_id": resourceinstanceid,
            "parenttile_id": "",
            "nodegroup_id": nodeid,
            "tileid": "",
            "data": {nodeid: {"url": "https://www.google.com/"}},
        }
        tile1 = Tile(url_no_label)
        url.pre_tile_save(tile1, nodeid)
        self.assertIsNotNone(tile1.data[nodeid])
        self.assertTrue("url_label" in tile1.data[nodeid])
        self.assertFalse(tile1.data[nodeid]["url_label"])

        url_with_label = {
            "resourceinstance_id": resourceinstanceid,
            "parenttile_id": "",
            "nodegroup_id": nodeid,
            "tileid": "",
            "data": {nodeid: {"url": "https://www.google.com/", "url_label": "Google"}},
        }
        tile2 = Tile(url_with_label)
        url.pre_tile_save(tile2, nodeid)
        self.assertIsNotNone(tile2.data[nodeid])
        self.assertTrue("url_label" in tile2.data[nodeid])
        self.assertTrue(tile2.data[nodeid]["url_label"])

    def test_clean(self):
        url = DataTypeFactory().get_instance("url")

        nodeid = "c0ed4b2a-c4cc-11ee-9626-00155de1df34"
        resourceinstanceid = "40000000-0000-0000-0000-000000000000"

        empty_data = {
            "resourceinstance_id": resourceinstanceid,
            "parenttile_id": "",
            "nodegroup_id": nodeid,
            "tileid": "",
            "data": {nodeid: {"url": "", "url_label": ""}},
        }
        tile1 = Tile(empty_data)
        url.clean(tile1, nodeid)
        self.assertIsNone(tile1.data[nodeid])

    def test_pre_structure_tile_data(self):
        url = DataTypeFactory().get_instance("url")

        nodeid = "c0ed4b2a-c4cc-11ee-9626-00155de1df34"
        resourceinstanceid = "40000000-0000-0000-0000-000000000000"

        data_without_label = {
            "resourceinstance_id": resourceinstanceid,
            "parenttile_id": "",
            "nodegroup_id": nodeid,
            "tileid": "",
            "data": {nodeid: {"url": ""}},
        }
        tile1 = Tile(data_without_label)
        url.pre_structure_tile_data(tile1, nodeid)
        self.assertIsNotNone(tile1.data[nodeid])
        self.assertTrue("url_label" in tile1.data[nodeid])
        self.assertFalse(tile1.data[nodeid]["url_label"])
