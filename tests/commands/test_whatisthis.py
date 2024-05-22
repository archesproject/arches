# these tests can be run from the command line via
# python manage.py test tests.commands.test_whatisthis --settings="tests.test_settings"

import uuid
from io import StringIO

from django.core.management import call_command

from arches.app.models.graph import Graph
from tests.base_test import ArchesTestCase

class WhatIsThisTests(ArchesTestCase):
    arbitrary_uuid = uuid.uuid4()

    def test_match(self):
        g = Graph.new()
        out = StringIO()
        call_command("whatisthis", str(g.pk), stdout=out)
        # Produces hits on graph and node
        self.assertIn("This UUID is the primary key for 2 objects:", out.getvalue())

    def test_no_match(self):
        out = StringIO()
        call_command("whatisthis", str(self.arbitrary_uuid), stdout=out)
        self.assertIn("doesn't match", out.getvalue())
