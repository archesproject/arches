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


class StripZMTests(TestCase):
    def setUp(self):
        self.geo_utils = GeoUtils()

    def test_none_returns_none(self):
        self.assertIsNone(self.geo_utils._strip_z_m(None))

    def test_point_strips_z(self):
        geom = {"type": "Point", "coordinates": [1.0, 2.0, 3.0]}
        self.geo_utils._strip_z_m(geom)
        self.assertEqual(geom["coordinates"], [1.0, 2.0])

    def test_point_strips_z_and_m(self):
        geom = {"type": "Point", "coordinates": [1.0, 2.0, 3.0, 4.0]}
        self.geo_utils._strip_z_m(geom)
        self.assertEqual(geom["coordinates"], [1.0, 2.0])

    def test_linestring_strips_z(self):
        geom = {
            "type": "LineString",
            "coordinates": [[0.0, 1.0, 100.0], [2.0, 3.0, 200.0]],
        }
        self.geo_utils._strip_z_m(geom)
        self.assertEqual(geom["coordinates"], [[0.0, 1.0], [2.0, 3.0]])

    def test_polygon_strips_z(self):
        geom = {
            "type": "Polygon",
            "coordinates": [
                [[0.0, 0.0, 10.0], [1.0, 0.0, 10.0], [1.0, 1.0, 10.0], [0.0, 0.0, 10.0]]
            ],
        }
        self.geo_utils._strip_z_m(geom)
        self.assertEqual(
            geom["coordinates"],
            [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 0.0]]],
        )

    def test_geometry_collection_strips_z(self):
        geom = {
            "type": "GeometryCollection",
            "geometries": [
                {"type": "Point", "coordinates": [1.0, 2.0, 3.0]},
                {
                    "type": "LineString",
                    "coordinates": [[0.0, 0.0, 5.0], [1.0, 1.0, 6.0]],
                },
                {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [0.0, 0.0, 10.0],
                            [1.0, 0.0, 10.0],
                            [1.0, 1.0, 10.0],
                            [0.0, 0.0, 10.0],
                        ]
                    ],
                },
            ],
        }
        self.geo_utils._strip_z_m(geom)
        self.assertEqual(geom["geometries"][0]["coordinates"], [1.0, 2.0])
        self.assertEqual(geom["geometries"][1]["coordinates"], [[0.0, 0.0], [1.0, 1.0]])
        self.assertEqual(
            geom["geometries"][2]["coordinates"],
            [[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 0.0]]],
        )

    def test_geometry_collection_empty_geometries(self):
        geom = {"type": "GeometryCollection", "geometries": []}
        self.geo_utils._strip_z_m(geom)
        self.assertEqual(geom["geometries"], [])


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
