'''
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
'''

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os
from tests import test_settings
from django.test import TestCase,SimpleTestCase
from arches.app.models.app_settings import AppSettings
from arches.app.models.models import Nodes
import codecs


# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"

def setUpModule():
    if os.path.isfile(get_path_to_settings_local()):
        os.remove(get_path_to_settings_local())

def tearDownModule():
    if os.path.isfile(get_path_to_settings_local()):
        os.remove(get_path_to_settings_local())

def get_path_to_settings_local():
    return os.path.join(test_settings.PACKAGE_ROOT, 'settings_local.py')

class AppSettingsTests(TestCase):

    def test_update_setting(self):
        """
        Test that we can write a setting to the settings_local.py file

        """

        old_app_settings = AppSettings(path_to_settings_file='tests.test_settings')
        mode = old_app_settings.set('MODE', 'TEST')
        old_app_settings.save()

        new_app_settings = AppSettings(path_to_settings_file='tests.test_settings')
        self.assertTrue('TEST' == new_app_settings.get('MODE'))

        found = False
        with codecs.open(get_path_to_settings_local()) as f:
            for line in f:
                if "MODE = 'TEST'" in line:
                    found = True

        self.assertTrue(found)
