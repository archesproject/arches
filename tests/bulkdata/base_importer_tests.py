import uuid

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase

from arches.app.etl_modules.base_import_module import BaseImportModule

# these tests can be run from the command line via
# python manage.py test tests.bulkdata.base_importer_tests --settings="tests.test_settings"


class BaseImporterSimpleTests(TestCase):
    def test_detect_loadid_mismatch(self):
        request = HttpRequest()
        request.method = "POST"
        request.user = User.objects.first()
        request.POST.__setitem__("load_id", uuid.uuid4())

        with self.assertRaisesMessage(
            ValueError, "loadid from request does not match loadid argument"
        ):
            BaseImportModule(request=request, loadid=uuid.uuid4())
