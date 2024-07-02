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
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from arches.app.models.system_settings import SystemSettings

# these tests can be run from the command line via
# python manage.py test tests.models.system_settings_tests --settings="tests.test_settings"


class SystemSettingsTests(SimpleTestCase):
    @mock.patch.dict(os.environ, {"DJANGO_SETTINGS_MODULE": ""})
    def test_improper_access(self):
        """Accessing settings during the Django startup phase fails loudly."""
        settings_obj = SystemSettings()
        with self.assertRaises(ImproperlyConfigured):
            settings_obj.ARBITRARY_KEY
        with self.assertRaises(ImproperlyConfigured):
            settings_obj.setting_exists("ARBITRARY_KEY")
