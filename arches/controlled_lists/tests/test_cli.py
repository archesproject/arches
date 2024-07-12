import io
import os

from django.core import management
from django.test import TestCase
from django.test.utils import captured_stdout

from arches.controlled_lists.models import List

# Change TEST_ROOT context for just Controlled Lists
from arches.settings import ROOT_DIR

TEST_ROOT = os.path.normpath(os.path.join(ROOT_DIR, "controlled_lists/tests"))


# these tests can be run from the command line via
# python manage.py test arches.controlled_lists.tests.cli_tests --settings="tests.test_settings"


class ListExportPackageTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        from arches.controlled_lists.tests.test_views import ListTests

        return ListTests.setUpTestData()

    def test_export_controlled_list(self):
        file_path = os.path.join(TEST_ROOT, "controlled_lists.xlsx")
        self.addCleanup(os.remove, file_path)
        output = io.StringIO()
        # packages command does not yet fully avoid print()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="export_controlled_lists",
                dest_dir=TEST_ROOT,
                stdout=output,
            )
        self.assertTrue(os.path.exists(file_path))


class ListImportPackageTests(TestCase):

    def test_import_controlled_list(self):
        input_file = os.path.join(TEST_ROOT, "data/controlled_lists.xlsx")
        output = io.StringIO()
        # packages command does not yet fully avoid print()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="import_controlled_lists",
                source=input_file,
                stdout=output,
            )
        list_pk = "e962bdaf-8243-4fbb-bd43-39bc1f54c168"
        self.assertTrue(List.objects.filter(pk=list_pk).exists())

    ### TODO Add test for creating new language if language code not in db but found in import file
