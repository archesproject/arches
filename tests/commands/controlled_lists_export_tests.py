import os, io
from django.conf import settings
from django.core import management

from tests.base_test import ArchesTestCase


# these tests can be run from the command line via
# python manage.py test tests.commands.controlled_lists_export_tests --settings="tests.test_settings"


class ControlledListsExportTests(ArchesTestCase):

    @classmethod
    def setUpTestData(cls):
        from tests.views.controlled_lists_tests import ControlledListTests
        return ControlledListTests.setUpTestData()

    def test_export_controlled_list(self):
        file_path = os.path.join(settings.TEST_ROOT, "controlled_lists.xlsx")
        self.addCleanup(os.remove, file_path)
        output = io.StringIO()
        management.call_command("packages", operation='export_controlled_lists', dest_dir=settings.TEST_ROOT, stdout=output)
        self.assertTrue(os.path.exists(file_path))
