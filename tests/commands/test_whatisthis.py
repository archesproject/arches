# these tests can be run from the command line via
# python manage.py test tests.commands.test_whatisthis --settings="tests.test_settings"

import uuid
from io import StringIO

from django.core.management import call_command

from tests.base_test import ArchesTestCase

class WhatIsThisTests(ArchesTestCase):
    arbitrary_uuid = uuid.uuid4()

    def test_no_match(self):
        out = StringIO()
        call_command("whatisthis", str(self.arbitrary_uuid), stdout=out)
        self.assertIn("doesn't match", out.getvalue())
