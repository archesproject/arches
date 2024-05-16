from django.conf import settings
from django.core import management
from arches.app.models.models import (
    ControlledList,
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    ControlledListItemValue,
    DValueType,
    Language,
)

from tests.base_test import ArchesTestCase


# these tests can be run from the command line via
# python manage.py test tests.commands.controlled_lists_import_export_tests --settings="tests.test_settings"


class ControlledListsImportExportTests(ArchesTestCase):

    @classmethod
    def setUpTestData(cls):
        from tests.views.controlled_lists_tests import ControlledListTests
        return ControlledListTests.setUpTestData()

    
    def test_export_controlled_list(self):
        management.call_command("packages", operation='export_controlled_lists', dest_dir=settings.TEST_ROOT)