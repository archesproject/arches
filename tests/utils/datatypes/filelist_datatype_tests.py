import uuid
from pathlib import Path
from unittest.mock import Mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.datastructures import MultiValueDict
from django.utils.translation import get_language

from arches.app.datatypes.datatypes import DataTypeFactory
from django.test import TestCase
from arches.app.models.system_settings import settings

# these tests can be run from the command line via
# python manage.py test tests.utils.datatypes.filelist_datatype_tests --settings="tests.test_settings"


class FileListDataTypeTests(TestCase):
    def test_bulk_import_path(self):
        datatype = DataTypeFactory().get_instance("file-list")
        resultingPath = datatype._get_bulk_import_file_path("filename.xls", "12345")
        expectedPath = Path(settings.UPLOADED_FILES_DIR) / "tmp" / "12345"

        self.assertEqual(resultingPath, expectedPath)

        resultingPath = datatype._get_bulk_import_file_path(
            "/test/path/filename.xls", "12345"
        )
        expectedPath = Path("/test/path")

        self.assertEqual(resultingPath, expectedPath)

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

    def test_get_files_from_request(self):
        datatype = DataTypeFactory().get_instance("file-list")
        nodeid = str(uuid.uuid4())
        tile_id = str(uuid.uuid4())

        file1 = SimpleUploadedFile("file1.png", b"content1", content_type="image/png")
        file2 = SimpleUploadedFile("file2.png", b"content2", content_type="image/png")
        preloaded = SimpleUploadedFile(
            "preloaded.png", b"preloaded", content_type="image/png"
        )

        node_key = f"file-list_{nodeid}"
        tile_key = f"file-list_{tile_id}-{nodeid}"

        mock_tile = Mock()
        mock_tile.tileid = tile_id
        request = Mock()

        with self.subTest("files found via nodeid key"):
            request.FILES = MultiValueDict({node_key: [file1, file2]})
            result = datatype._get_files_from_request(request, nodeid)
            self.assertEqual(result, [file1, file2])

        with self.subTest("preloaded and regular files are concatenated"):
            request.FILES = MultiValueDict(
                {f"{node_key}_preloaded": [preloaded], node_key: [file1]}
            )
            result = datatype._get_files_from_request(request, nodeid)
            self.assertEqual(result, [preloaded, file1])

        with self.subTest("falls back to tile-scoped key when nodeid key is empty"):
            request.FILES = MultiValueDict({tile_key: [file1, file2]})
            result = datatype._get_files_from_request(request, nodeid, tile=mock_tile)
            self.assertEqual(result, [file1, file2])

        with self.subTest("tile-scoped preloaded and regular files are concatenated"):
            request.FILES = MultiValueDict(
                {f"{tile_key}_preloaded": [preloaded], tile_key: [file1]}
            )
            result = datatype._get_files_from_request(request, nodeid, tile=mock_tile)
            self.assertEqual(result, [preloaded, file1])

        with self.subTest("nodeid key takes priority over tile-scoped key"):
            request.FILES = MultiValueDict({node_key: [file1], tile_key: [file2]})
            result = datatype._get_files_from_request(request, nodeid, tile=mock_tile)
            self.assertEqual(result, [file1])

        with self.subTest("no files, no tile → empty list"):
            request.FILES = MultiValueDict({})
            result = datatype._get_files_from_request(request, nodeid)
            self.assertEqual(result, [])

        with self.subTest("no files anywhere, tile provided → empty list"):
            request.FILES = MultiValueDict({})
            result = datatype._get_files_from_request(request, nodeid, tile=mock_tile)
            self.assertEqual(result, [])
