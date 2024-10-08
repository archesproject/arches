import os
import shutil
from pathlib import Path

from unittest.mock import Mock, patch

from django.conf import settings
from django.test import SimpleTestCase
from django.test.utils import override_settings

from arches.app.utils.file_validator import FileValidator

# these tests can be run from the command line via
# python manage.py test tests.utils.test_file_validator.FileValidatorTests --settings="tests.test_settings"


class MockFile:
    @staticmethod
    def read():
        """Return a jagged csv file (invalid row length)"""
        return b"col1,col2\ndata1"

    @staticmethod
    def seek(offset):
        return


class MockFileType:
    def __init__(self, extension):
        self.extension = extension


class FileValidatorTests(SimpleTestCase):
    """FILE_TYPE_CHECKING defaults to 'lenient': overridden as necessary."""

    validator = FileValidator()
    mock_file = MockFile()

    @override_settings(FILE_TYPE_CHECKING=None)
    def test_no_file_checking(self):
        errors = self.validator.validate_file_type(self.mock_file)
        self.assertEqual(errors, [])

    @patch("filetype.guess", Mock(return_value=None))
    def test_check_unknown_filetype_lenient(self):
        errors = self.validator.validate_file_type(self.mock_file)
        self.assertEqual(errors, [])

    @patch("filetype.guess", Mock(return_value=None))
    @override_settings(FILE_TYPE_CHECKING="strict")
    def test_check_unknown_filetype_strict(self):
        with self.assertLogs("arches.app.utils.file_validator", level="ERROR"):
            errors = self.validator.validate_file_type(self.mock_file)
        self.assertEqual(errors, ["File type is not permitted: None"])

    @patch("filetype.guess", Mock(return_value=MockFileType("suspicious")))
    def test_filetype_not_listed(self):
        with self.assertLogs("arches.app.utils.file_validator", level="ERROR"):
            errors = self.validator.validate_file_type(self.mock_file)
        self.assertEqual(errors, ["Unsafe file type suspicious"])

    @patch("filetype.guess", Mock(return_value=None))
    def test_check_invalid_csv(self):
        with self.assertLogs("arches.app.utils.file_validator", level="ERROR"):
            errors = self.validator.validate_file_type(self.mock_file, extension="csv")
        self.assertEqual(errors, ["Invalid csv file"])

    @patch("filetype.guess", Mock(return_value=None))
    def test_check_invalid_json(self):
        with self.assertLogs("arches.app.utils.file_validator", level="ERROR"):
            errors = self.validator.validate_file_type(self.mock_file, extension="json")
        self.assertEqual(errors, ["Invalid json file"])

    @patch("filetype.guess", Mock(return_value=None))
    def test_check_invalid_jpeg_lenient(self):
        errors = self.validator.validate_file_type(self.mock_file, extension="jpeg")
        self.assertEqual(errors, [])

    @patch("filetype.guess", Mock(return_value=None))
    @override_settings(FILE_TYPE_CHECKING="strict")
    def test_check_invalid_jpeg_strict(self):
        with self.assertLogs("arches.app.utils.file_validator", level="ERROR"):
            errors = self.validator.validate_file_type(self.mock_file, extension="jpeg")
        self.assertEqual(errors, ["Cannot validate file"])

    @patch("filetype.guess", Mock(return_value=None))
    def test_check_invalid_jpeg_lenient(self):
        errors = self.validator.validate_file_type(self.mock_file, extension="jpeg")
        self.assertEqual(errors, [])

    @patch("filetype.guess", Mock(return_value=None))
    @override_settings(FILE_TYPE_CHECKING="strict")
    def test_check_invalid_but_not_in_listed_types(self):
        with self.assertLogs("arches.app.utils.file_validator", level="ERROR"):
            errors = self.validator.validate_file_type(
                self.mock_file, extension="notlisted"
            )
        self.assertEqual(errors, ["File type is not permitted: notlisted"])

    @patch("filetype.guess", Mock(return_value=None))
    def test_check_dsstore_lenient(self):
        """In lenient mode, we assume these might be present in .zip files."""
        with self.assertLogs("arches.app.utils.file_validator", level="WARN"):
            errors = self.validator.validate_file_type(
                self.mock_file, extension="DS_Store"
            )
        self.assertEqual(errors, [])

    @patch("filetype.guess", Mock(return_value=None))
    @override_settings(FILE_TYPE_CHECKING="strict")
    def test_check_dsstore_strict(self):
        with self.assertLogs("arches.app.utils.file_validator", level="ERROR"):
            errors = self.validator.validate_file_type(
                self.mock_file, extension="DS_Store"
            )
        self.assertEqual(errors, ["File type is not permitted: DS_Store"])

    @patch("filetype.guess", Mock(return_value=None))
    @patch("arches.app.utils.file_validator.load_workbook", lambda file, **kwargs: None)
    def test_valid_xlsx(self):
        errors = self.validator.validate_file_type(self.mock_file, extension="xlsx")
        self.assertEqual(errors, [])

    @patch("filetype.guess", Mock(return_value=None))
    def test_invalid_xlsx(self):
        with self.assertLogs("arches.app.utils.file_validator", level="ERROR"):
            errors = self.validator.validate_file_type(self.mock_file, extension="xlsx")
        self.assertEqual(errors, ["Invalid xlsx workbook"])

    def test_zip(self):
        # Zip up the files in the tests/fixtures/uploadedfiles dir
        # Currently, contains a single .csv file and an empty dir.
        dir_to_zip = Path(settings.MEDIA_ROOT) / "uploadedfiles"
        zip_file_path = shutil.make_archive("test", "zip", dir_to_zip, dir_to_zip)
        self.addCleanup(os.unlink, zip_file_path)

        with open(zip_file_path, "rb") as file:
            errors = self.validator.validate_file_type(file)
        self.assertEqual(errors, [])

        with (
            open(zip_file_path, "rb") as file,
            self.modify_settings(FILE_TYPES={"remove": "csv"}),
            self.assertLogs("arches.app.utils.file_validator", level="ERROR"),
        ):
            errors = self.validator.validate_file_type(file)
        self.assertEqual(
            errors, ["File type is not permitted: csv", "Unsafe zip file contents"]
        )
