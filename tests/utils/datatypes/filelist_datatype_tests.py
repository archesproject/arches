from django.utils.translation import get_language
from arches.app.datatypes.datatypes import DataTypeFactory
from django.test import TestCase

# these tests can be run from the command line via
# python manage.py test tests.utils.datatypes.filelist_datatype_tests --settings="tests.test_settings"


class FileListDataTypeTests(TestCase):

    def test_tile_transform(self):
        value1 = "testfile1.png,testfile2.png"

        value2 = [
            {
                "name": "testfile3.png",
                "altText": "Test File 3",
                "attribution": "archesproject",
                "description": "A File for Testing",
                "title": "Test File 3",
            },
            {
                "name": "testfile4.png",
                "altText": {"en": {"value": "Test File 4", "direction": "ltr"}},
                "attribution": {"en": {"value": "archesproject", "direction": "ltr"}},
                "description": {
                    "en": {"value": "A File for Testing", "direction": "ltr"}
                },
                "title": {"en": {"value": "Test File 4", "direction": "ltr"}},
            },
        ]

        datatype = DataTypeFactory().get_instance("file-list")
        language = get_language()

        with self.subTest("comma-separated string input"):
            tile_value = datatype.transform_value_for_tile(value1)
            self.assertEqual(tile_value[0]["name"], "testfile1.png")
            self.assertEqual(tile_value[1]["name"], "testfile2.png")

        with self.subTest("dictionary input"):
            tile_value = datatype.transform_value_for_tile(value2[0])
            self.assertEqual(tile_value[0]["name"], "testfile3.png")
            self.assertEqual(tile_value[0]["altText"][language]["value"], "Test File 3")
            self.assertEqual(
                tile_value[0]["attribution"][language]["value"], "archesproject"
            )
            self.assertEqual(
                tile_value[0]["description"][language]["value"], "A File for Testing"
            )
            self.assertEqual(tile_value[0]["title"][language]["value"], "Test File 3")

        with self.subTest("A list of dictionaries input"):
            tile_value = datatype.transform_value_for_tile(value2)
            self.assertEqual(tile_value[1]["name"], "testfile4.png")
            self.assertEqual(tile_value[1]["altText"][language]["value"], "Test File 4")
            self.assertEqual(
                tile_value[1]["attribution"][language]["value"], "archesproject"
            )
            self.assertEqual(
                tile_value[1]["description"][language]["value"], "A File for Testing"
            )
            self.assertEqual(tile_value[1]["title"][language]["value"], "Test File 4")
