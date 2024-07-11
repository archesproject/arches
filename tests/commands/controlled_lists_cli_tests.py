import io
import os

from django.conf import settings
from django.core import management
from django.test.utils import captured_stdout

from arches.app.models.models import ControlledList
from tests.base_test import ArchesTestCase


# these tests can be run from the command line via
# python manage.py test tests.commands.controlled_lists_cli_tests --settings="tests.test_settings"


class ControlledListsExportTests(ArchesTestCase):

    @classmethod
    def setUpTestData(cls):
        from tests.views.controlled_lists_tests import ControlledListTests

        return ControlledListTests.setUpTestData()

    def test_export_controlled_list(self):
        file_path = os.path.join(settings.TEST_ROOT, "controlled_lists.xlsx")
        self.addCleanup(os.remove, file_path)
        output = io.StringIO()
        # packages command does not yet fully avoid print()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="export_controlled_lists",
                dest_dir=settings.TEST_ROOT,
                stdout=output,
            )
        self.assertTrue(os.path.exists(file_path))


class ControlledListsImportTests(ArchesTestCase):

    def test_import_controlled_list(self):
        input_file = os.path.join(
            settings.TEST_ROOT, "fixtures/data/controlled_lists.xlsx"
        )
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
        self.assertTrue(ControlledList.objects.filter(pk=list_pk).exists())

    ### TODO Add test for creating new language if language code not in db but found in import file
