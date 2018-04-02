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
import json
import couchdb
from tests import test_settings as settings
from django.contrib.auth.models import User, Group, AnonymousUser
from django.core.urlresolvers import reverse
from django.test import Client
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.models import MobileSurveyModel
from arches.app.views.mobile_survey import MobileSurveyManagerView, MobileSurveyResources
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests/views/mobile_survey_tests.py --pattern="*.py" --settings="tests.test_settings"


class MobileSurveyTests(ArchesTestCase):
    def setUp(self):
        mobile_survey = MobileSurvey()
        mobile_survey.name = "TEST MOBILE SURVEY"
        mobile_survey.description = "FOR TESTING"
        mobile_survey.active = True
        mobile_survey.createdby = User.objects.get(id=1)
        mobile_survey.lasteditedby = User.objects.get(id=1)
        mobile_survey.iconclass = "fa fa-building"
        mobile_survey.nodegroups = []
        mobile_survey.datadownloadconfig='{"download":false, "count":10, "resources":[], "custom":''}'
        mobile_survey.save()
        mobile_survey = MobileSurvey.objects.get(pk=mobile_survey.id)
        mobile_survey.save()
        self.mobile_survey = mobile_survey
        self.client = Client()

    def test_create_mobile_survey(self):
        """
        Test that a user can login and is redirected to the home page

        """

        self.client.login(username='admin', password='admin')
        url = reverse('mobile_survey_manager')
        post_data = {
            "datadownloadconfig": {"count":1000,"download":True,"resources":[],"custom":""},
            "startdate":"2018-01-29",
            "tilecache":"",
            "enddate":"2018-03-30",
            "createdby_id":1,
            "bounds":{"type":"FeatureCollection","features":[]},
            "cards":[],
            "lasteditedby_id":1,
            "groups":[],
            "active":False,
            "users":[],
            "id": str(self.mobile_survey.id),
            "name":"Catdog",
            "description":"a description"
            }

        post_data = JSONSerializer().serialize(post_data)
        content_type = 'application/x-www-form-urlencoded'
        response = self.client.post(url, post_data, content_type)
        response_json = json.loads(response.content)
        couch = couchdb.Server(settings.COUCHDB_URL)
        self.assertTrue(response_json['success'])
        self.assertTrue('project_' + str(self.mobile_survey.id) in couch)

    def test_delete_mobile_survey(self):
        """
        Test that a user can login and is redirected to the home page

        """

        self.client.login(username='admin', password='admin')
        url = reverse('mobile_survey_manager')
        post_data = {
            "id": str(self.mobile_survey.id)
            }

        post_data = JSONSerializer().serialize(post_data)
        content_type = 'application/x-www-form-urlencoded'
        response = self.client.delete(url, post_data, content_type)
        response_json = json.loads(response.content)
        couch = couchdb.Server(settings.COUCHDB_URL)
        self.assertFalse(MobileSurvey.objects.filter(pk=self.mobile_survey.id).exists())
        self.assertTrue('project_' + str(self.mobile_survey.id) not in couch)


    def test_load_couchdb(self):
        """
        Test that a user can login and is redirected to the home page

        """

        self.assertTrue(1==1)
