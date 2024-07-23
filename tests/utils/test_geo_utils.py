from arches.app.utils.geo_utils import GeoUtils
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
import json

# these tests can be run from the command line via
# python manage.py test tests.utils.test_geo_utils --settings="tests.test_settings"


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
