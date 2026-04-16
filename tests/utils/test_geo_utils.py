from arches.app.utils.geo_utils import GeoUtils
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
import json

# these tests can be run from the command line via
# python manage.py test tests.utils.test_geo_utils --settings="tests.test_settings"


class ArcgisJsonToGeojsonTests(TestCase):
    def setUp(self):
        self.geo_utils = GeoUtils()

    def test_points(self):
        geom = (
            '{"x": -0.115, "y": 51.534, "spatialReference": {"wkid": 4326}},'
            '{"x": -0.113, "y": 51.536, "spatialReference": {"wkid": 4326}}'
        )
        result = self.geo_utils.arcgisjson_to_geojson(geom)

        self.assertEqual(result["type"], "FeatureCollection")
        self.assertEqual(len(result["features"]), 2)
        for feature in result["features"]:
            self.assertEqual(feature["type"], "Feature")
            self.assertEqual(feature["geometry"]["type"], "Point")
            self.assertIsInstance(feature["properties"], dict)

    def test_result_is_valid_geojson(self):
        geom = '{"x": -118.243, "y": 34.052, "spatialReference": {"wkid": 4326}}'
        result = self.geo_utils.arcgisjson_to_geojson(geom)

        self.assertTrue(
            GEOSGeometry(json.dumps(result["features"][0]["geometry"])).valid
        )


class GeoUtilsTests(TestCase):

    def test_convert_multipoint_to_single(self):
        geo_utils = GeoUtils()
        multi_part_geom = {
            "type": "MultiPoint",
            "coordinates": [
                [-73.984, 40.748],
                [-73.985, 40.749],
                [-73.986, 40.75],
                [-73.987, 40.751],
            ],
        }

        single_part_geom = geo_utils.convert_multipart_to_singlepart(multi_part_geom)

        with self.subTest(input=single_part_geom):
            self.assertEqual(len(single_part_geom["features"]), 4)

        with self.subTest(input=single_part_geom):
            self.assertTrue(
                GEOSGeometry(
                    json.dumps(single_part_geom["features"][0]["geometry"])
                ).valid
            )
