from django.utils.translation import get_language
from arches.app.datatypes.datatypes import DataTypeFactory
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.utils.datatypes.filelist_datatype_tests --settings="tests.test_settings"


class FileListDataTypeTests(ArchesTestCase):

    def test_tile_transform(self):
        value = [
            {
                "name": "testfile.png",
                "altText": "Test File",
                "attribution": "archesproject",
                "description": "A File for Testing",
                "title": "Test File",
            }
        ]
        datatype = DataTypeFactory().get_instance("file-list")
        language = get_language()

        with self.subTest(input="testfile.png"):
            tile_value = datatype.transform_value_for_tile(value)
            self.assertEqual(tile_value[0]["name"], "testfile.png")

        with self.subTest(input=value):
            tile_value = datatype.transform_value_for_tile(value)
            self.assertEqual(tile_value[0]["name"], "testfile.png")
            self.assertEqual(tile_value[0]["altText"][language]["value"], "Test File")
            self.assertEqual(tile_value[0]["attribution"][language]["value"], "archesproject")
            self.assertEqual(tile_value[0]["description"][language]["value"], "A File for Testing")
            self.assertEqual(tile_value[0]["title"][language]["value"], "Test File")
