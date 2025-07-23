from arches.app.datatypes.datatypes import DataTypeFactory
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.utils.datatypes.filelist_datatype_tests --settings="tests.test_settings"


class FileListDataTypeTests(ArchesTestCase):

    def test_tile_transform(self):
        value = [
            {
                "status": "uploaded",
                "name": "testfile.png",
                "type": "image/png",
                "file_id": "62b7bdeb-d171-4f98-9573-566e13e8632a",
                "size": 238297,
                "url": "/files/62b7bdeb-d171-4f98-9573-566e13e8632a",
                "accepted": True,
                "renderer": "5e05aa2e-5db0-4922-8938-b4d2b7919733",
            }
        ]
        datatype = DataTypeFactory().get_instance("file-list")
        value = self.value

        with self.subTest(input=value):
            tile_value = datatype.transform_value_for_tile(value)
            self.assertEqual(tile_value[0]["name"], "testfile.png")

        with self.subTest(input="testfile.png"):
            tile_value = datatype.transform_value_for_tile(value)
            self.assertEqual(tile_value[0]["name"], "testfile.png")
