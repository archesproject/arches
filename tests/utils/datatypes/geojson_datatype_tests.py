import json
import os
import uuid

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.test.utils import sync_overridden_test_settings_to_arches
from tests.base_test import ArchesTestCase
from django.test import override_settings

# these tests can be run from the command line via
# python manage.py test tests.utils.datatypes.geojson_datatype_tests --settings="tests.test_settings"


class GeoJsonDataTypeTest(ArchesTestCase):
    search_model_graphid = uuid.UUID("c9b37a14-17b3-11eb-a708-acde48001122")
    graph_fixtures = ["Resource Test Model"]

    def test_validate_reduce_byte_size(self):
        with open("tests/fixtures/problematic_excessive_vertices.geojson") as f:
            geom = json.load(f)
        geom_datatype = DataTypeFactory().get_instance("geojson-feature-collection")
        errors = geom_datatype.validate(geom)
        self.assertEqual(len(errors), 0)

    @override_settings(
        DATA_VALIDATION_BBOX=[
            (12.948801570473677, 52.666192057898854),
            (12.948801570473677, 52.26439571958821),
            (13.87818788958171, 52.26439571958821),
            (13.87818788958171, 52.666192057898854),
            (12.948801570473677, 52.666192057898854),
        ]
    )
    def test_validate_bbox(self):
        with sync_overridden_test_settings_to_arches():
            geom_datatype = DataTypeFactory().get_instance("geojson-feature-collection")

            with self.subTest(bbox="invalid"):
                geom = json.loads(
                    '{"type": "FeatureCollection","features": [{"type": "Feature","properties": {},"geometry": {"coordinates": [14.073244400935238,19.967099711627156],"type": "Point"}}]}'
                )
                errors = geom_datatype.validate(geom)
                self.assertEqual(len(errors), 1)

            with self.subTest(bbox="valid"):
                geom = json.loads(
                    '{"type": "FeatureCollection","features": [{"type": "Feature","properties": {},"geometry": {"coordinates": [13.400257324930152,52.50578474077699],"type": "Point"}}]}'
                )
                errors = geom_datatype.validate(geom)
                self.assertEqual(len(errors), 0)

    def test_get_map_source(self):
        geom_datatype = DataTypeFactory().get_instance("geojson-feature-collection")
        node = models.Node.objects.get(pk="c9b37f96-17b3-11eb-a708-acde48001122")
        nodeconfig = json.loads(node.config.value)
        nodeconfig["minzoom"] = 12
        nodeconfig["maxzoom"] = 15
        node.config.value = json.dumps(nodeconfig)

        result = geom_datatype.get_map_source(node)
        map_source = json.loads(result["source"])

        with self.subTest(input=result):
            self.assertEqual(
                result["name"], "resources-c9b37f96-17b3-11eb-a708-acde48001122"
            )

        with self.subTest(input=map_source):
            self.assertEqual(
                map_source["tiles"][0],
                "/mvt/c9b37f96-17b3-11eb-a708-acde48001122/{z}/{x}/{y}.pbf",
            )

        with self.subTest(input=map_source):
            self.assertTrue("minzoom" in map_source and "maxzoom" in map_source)

    def test_check_valid_geojson_geom(self):
        geom_datatype = DataTypeFactory().get_instance("geojson-feature-collection")
        geojson_filename = os.path.join(
            "tests", "fixtures", "data", "json", "geojson_with_properties.json"
        )
        with open(geojson_filename, "r") as geojson_file:
            geom_json = geojson_file.read()
            geom_datatype.check_geojson_value(json.loads(geom_json))
            geom_datatype.validate(json.loads(geom_json))

    def test_check_geom_property_cleaning(self):
        geom_datatype = DataTypeFactory().get_instance("geojson-feature-collection")
        document = {"geometries": [], "points": []}
        tile = models.TileModel()
        tile.id = uuid.uuid4()
        tile.nodegroup_id = uuid.uuid4()
        geojson_filename = os.path.join(
            "tests", "fixtures", "data", "json", "geojson_with_properties.json"
        )
        with open(geojson_filename, "r") as geojson_file:
            geom_json = json.loads(geojson_file.read())
            geom_datatype.validate(geom_json)
            self.assertEqual(
                geom_json["features"][0]["properties"]["name"], "Test with properties"
            )
            geom_datatype.append_to_document(
                document=document,
                nodevalue=geom_json,
                tile=tile,
                nodeid=uuid.uuid4(),
            )
            for geometry in document["geometries"]:
                self.assertEqual(geometry["geom"]["properties"], {})
                for feature in geometry["geom"]["features"]:
                    self.assertEqual(feature["properties"], {})
