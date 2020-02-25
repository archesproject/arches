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

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os
from tests import test_settings

# from tests.base_test import ArchesTestCase
from django.test import TestCase
from django.core import management
from arches.app.models import models

# python manage.py test tests/views/command_line_tests.py --pattern="*.py" --settings="tests.test_settings"


class CommandLineTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        test_pkg_path = os.path.join(test_settings.TEST_ROOT, "fixtures", "testing_prj", "testing_prj", "pkg")
        management.call_command("packages", operation="load_package", source=test_pkg_path, yes=True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_load_package(self):
        data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
        resources = models.ResourceInstance.objects.filter(graph_id=data_type_graphid)
        self.assertEqual(len(list(resources)), 2)
