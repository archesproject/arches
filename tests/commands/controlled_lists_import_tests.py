import os, io
from django.conf import settings
from django.core import management
from arches.app.models.models import (
    ControlledList,
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    ControlledListItemValue,
    DValueType,
    Language
)

from tests.base_test import ArchesTestCase


# these tests can be run from the command line via
# python manage.py test tests.commands.controlled_lists_import_tests --settings="tests.test_settings"


class ControlledListsImportTests(ArchesTestCase):

    # @classmethod
    # def setUpTestData(cls):
    #     from tests.views.controlled_lists_tests import ControlledListTests
    #     return ControlledListTests.setUpTestData()

    def test_import_controlled_list(self):
        input_file = os.path.join(settings.TEST_ROOT, "fixtures/data/controlled_lists.xlsx")
        output = io.StringIO()
        management.call_command("packages", operation='import_controlled_lists', source=input_file, stdout=output)
        self.assertTrue(ControlledList.objects.filter(pk="e962bdaf-8243-4fbb-bd43-39bc1f54c168"))

    ### TODO Add test for creating new language if language code not in db but found in import file
