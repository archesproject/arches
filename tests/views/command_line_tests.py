"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import os
from tests import test_settings
from django.test.utils import captured_stdout
from django.core import management
from arches.app.models import models
from tests.base_test import ArchesTestCase
from django.test.client import Client

# these tests can be run from the command line via
# python manage.py test tests.views.command_line_tests --settings="tests.test_settings"


class CommandLineTests(ArchesTestCase):
    def setUp(self):
        self.expected_resource_count = 2
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        cls.data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
        if not models.GraphModel.objects.filter(pk=cls.data_type_graphid).exists():
            # TODO: Fix this to run inside transaction, i.e. after super().setUpClass()
            # https://github.com/archesproject/arches/issues/10719
            test_pkg_path = os.path.join(test_settings.TEST_ROOT, "fixtures", "testing_prj", "testing_prj", "pkg")
            with captured_stdout():
                management.call_command("packages", operation="load_package", source=test_pkg_path, yes=True, verbosity=0)

        super().setUpClass()

    def test_load_package(self):
        resources = models.ResourceInstance.objects.filter(graph_id=self.data_type_graphid)
        self.assertEqual(len(list(resources)), self.expected_resource_count)
