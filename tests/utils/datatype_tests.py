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

import json
import os
import uuid

from arches.app.datatypes.base import BaseDataType
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.models.models import Language
from arches.app.models.tile import Tile
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as resource_graph_importer
from arches.app.utils.i18n import LanguageSynchronizer
from tests.base_test import ArchesTestCase, sync_overridden_test_settings_to_arches
from django.test import override_settings


# these tests can be run from the command line via
# python manage.py test tests.utils.datatype_tests --settings="tests.test_settings"


class BooleanDataTypeTests(ArchesTestCase):
    def test_validate(self):
        boolean = DataTypeFactory().get_instance("boolean")

        for good in ["true", "false", "yes", "no", None]:
            with self.subTest(input=good):
                no_errors = boolean.validate(good)
                self.assertEqual(len(no_errors), 0)

        for bad in ["garbage", "True", "False", "None"]:
            with self.subTest(input=bad):
                errors = boolean.validate(bad)
                self.assertEqual(len(errors), 1)

    def test_tile_transform(self):
        boolean = DataTypeFactory().get_instance("boolean")

        truthy_values = []
        falsy_values = []
        for truthy in truthy_values:
            with self.subTest(input=truthy):
                self.assertTrue(boolean.transform_value_for_tile(truthy))
        for falsy in falsy_values:
            with self.subTest(input=falsy):
                self.assertFalse(boolean.transform_value_for_tile(falsy))

        with self.assertRaises(ValueError):
            boolean.transform_value_for_tile(None)

class GeoJsonDataTypeTest(ArchesTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        LanguageSynchronizer.synchronize_settings_with_db()

        with open(os.path.join("tests/fixtures/resource_graphs/Resource Test Model.json"), "r") as f:
            archesfile = JSONDeserializer().deserialize(f)
            
        resource_graph_importer(archesfile["graph"])
        cls.search_model_graphid = uuid.UUID("c9b37a14-17b3-11eb-a708-acde48001122")

    @classmethod
    def tearDownClass(cls):
        models.GraphModel.objects.filter(pk=cls.search_model_graphid).delete()
        super().tearDownClass()

    def test_validate_reduce_byte_size(self):
        with open("tests/fixtures/problematic_excessive_vertices.geojson") as f:
            geom = json.load(f)
        geom_datatype = DataTypeFactory().get_instance("geojson-feature-collection")
        errors = geom_datatype.validate(geom)
        self.assertEqual(len(errors), 0)        

    @override_settings(
        DATA_VALIDATION_BBOX = [(
            12.948801570473677,
            52.666192057898854
        ),
        (
            12.948801570473677,
            52.26439571958821
        ),
        (
            13.87818788958171,
            52.26439571958821
        ),
        (
            13.87818788958171,
            52.666192057898854
        ),
        (
            12.948801570473677,
            52.666192057898854
        )]
    )
    def test_validate_bbox(self):
        with sync_overridden_test_settings_to_arches():
            geom_datatype = DataTypeFactory().get_instance("geojson-feature-collection")

            with self.subTest(bbox="invalid"):
                geom = json.loads('{"type": "FeatureCollection","features": [{"type": "Feature","properties": {},"geometry": {"coordinates": [14.073244400935238,19.967099711627156],"type": "Point"}}]}')
                errors = geom_datatype.validate(geom)
                self.assertEqual(len(errors), 1)

            with self.subTest(bbox="valid"):
                geom = json.loads('{"type": "FeatureCollection","features": [{"type": "Feature","properties": {},"geometry": {"coordinates": [13.400257324930152,52.50578474077699],"type": "Point"}}]}')
                errors = geom_datatype.validate(geom)
                self.assertEqual(len(errors), 0)
    
    def test_get_map_source(self):
        geom_datatype = DataTypeFactory().get_instance("geojson-feature-collection")
        node = models.Node.objects.get(pk='c9b37f96-17b3-11eb-a708-acde48001122')
        nodeconfig = json.loads(node.config.value)
        nodeconfig["minzoom"] = 12
        nodeconfig["maxzoom"] = 15
        node.config.value = json.dumps(nodeconfig)
        node.save()
        result = geom_datatype.get_map_source(node)
        map_source = json.loads(result["source"])

        with self.subTest(input=result):
            self.assertEqual(result["name"], 'resources-c9b37f96-17b3-11eb-a708-acde48001122')

        with self.subTest(input=map_source):
            self.assertEqual(map_source["tiles"][0], "/mvt/c9b37f96-17b3-11eb-a708-acde48001122/{z}/{x}/{y}.pbf")

        with self.subTest(input=map_source):
            self.assertTrue("minzoom" in map_source and "maxzoom" in map_source)


class BaseDataTypeTests(ArchesTestCase):
    def test_get_tile_data_only_none(self):
        base = BaseDataType()
        node_id = str(uuid.uuid4())
        resourceinstance_id = str(uuid.uuid4())
        tile_data = {node_id: None}
        tile_holding_only_none = Tile({
            "resourceinstance_id": resourceinstance_id,
            "parenttile_id": "",
            "nodegroup_id": node_id,
            "tileid": "",
            "data": tile_data,
        })

        self.assertEqual(base.get_tile_data(tile_holding_only_none), tile_data)


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


class NonLocalizedStringDataTypeTests(ArchesTestCase):
    def test_string_validate(self):
        string = DataTypeFactory().get_instance("non-localized-string")
        some_errors = string.validate(float(1.2))
        self.assertGreater(len(some_errors), 0)
        no_errors = string.validate("Hello World")
        self.assertEqual(len(no_errors), 0)

    def test_string_clean(self):
        string = DataTypeFactory().get_instance("non-localized-string")
        nodeid1 = "72048cb3-adbc-11e6-9ccf-14109fd34195"
        nodeid2 = "72048cb3-adbc-11e6-9ccf-14109fd34196"
        resourceinstanceid = "40000000-0000-0000-0000-000000000000"

        json_empty_strings = {
            "resourceinstance_id": resourceinstanceid,
            "parenttile_id": "",
            "nodegroup_id": nodeid1,
            "tileid": "",
            "data": {nodeid1: "''", nodeid2: ""},
        }
        tile1 = Tile(json_empty_strings)
        string.clean(tile1, nodeid1)
        self.assertIsNone(tile1.data[nodeid1])
        string.clean(tile1, nodeid2)
        self.assertIsNone(tile1.data[nodeid2])


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
