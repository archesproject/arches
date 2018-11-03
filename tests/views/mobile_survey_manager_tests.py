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
import json
from django.core import management
from tests import test_settings as settings
from tests.base_test import ArchesTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.test.client import RequestFactory, Client
from arches.app.views.auth import LoginView, GetTokenView
from arches.app.views.concept import RDMView
from arches.app.views.mobile_survey import MobileSurveyManagerView
from arches.app.utils.middleware import SetAnonymousUser
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.management.commands.packages import Command as PackageCommand
from arches.app.models.models import GraphModel

# these tests can be run from the command line via
# python manage.py test tests/views/mobile_survey_manager_tests.py --pattern="*.py" --settings="tests.test_settings"


class MobileSurveyManagerTests(ArchesTestCase):
    def setUp(self):
        management.call_command('packages', operation='load_package', source=settings.TEST_PACKAGE, yes='y', setup_db=False)
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@archesproject.org', 'password')
        self.user.save()

        rdm_admin_group = Group.objects.get(name='RDM Administrator')
        self.user.groups.add(rdm_admin_group)

        self.anonymous_user = User.objects.get(username='anonymous')

    def tearDown(self):
        self.user.delete()


    def test_package_load(self):
        """
        Test if package loaded

        """
        self.assertTrue(0 < GraphModel.objects.all())

    def test_save_mobile_survey(self):
        self.factory = RequestFactory()
        self.client.login(username='admin', password='admin')
        json_path = os.path.join(settings.TEST_ROOT, 'fixtures', 'mobile_surveys', 'test-package-msm.json')
        with open(json_path) as f:
            mobile_survey = json.load(f)
        url = reverse('mobile_survey_manager')
        response = self.client.post(url, json.dumps(mobile_survey), 'application/json')
        self.assertTrue(response.status_code == 200)
