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
import couchdb
from couchdb.design import ViewDefinition
from tests import test_settings as settings
from django.contrib.auth.models import User, Group, AnonymousUser
from django.core.urlresolvers import reverse
from django.test import Client
from arches.app.models import models
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.models import MobileSurveyModel
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.views.mobile_survey import MobileSurveyManagerView, MobileSurveyResources
from tests.base_test import ArchesTestCase
from arches.app.utils.data_management.resources.importer import BusinessDataImporter


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
        mobile_survey.datadownloadconfig={"download":False, "count":10, "resources":[], "custom":""}
        mobile_survey.id = '08960fb5-385b-11e8-add6-c4b301baab9f'
        mobile_survey.save()
        mobile_survey = MobileSurvey.objects.get(pk=mobile_survey.id)
        mobile_survey.save()
        self.mobile_survey = mobile_survey
        self.client = Client()
        with open(os.path.join('tests/fixtures/resource_graphs/Mobile Survey Test.json'), 'rU') as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile['graph'])
        BusinessDataImporter('tests/fixtures/data/mobile_survey_test_data.json').import_business_data()

    def tearDown(self):
        couch = couchdb.Server(settings.COUCHDB_URL)
        if 'project_08960fb5-385b-11e8-add6-c4b301baab9f' in couch:
            del couch['project_08960fb5-385b-11e8-add6-c4b301baab9f']

    def post_mobile_survey(self, post_data):
        self.client.login(username='admin', password='admin')
        url = reverse('mobile_survey_manager')
        post_data = JSONSerializer().serialize(post_data)
        content_type = 'application/x-www-form-urlencoded'
        response = self.client.post(url, post_data, content_type)
        return json.loads(response.content)

    def test_create_mobile_survey(self):
        """
        Test that creation of a mobile survey creates a corresponding couch database.

        """

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
            "name":"test survey",
            "description":"a description"
            }

        response_json = self.post_mobile_survey(post_data)
        couch = couchdb.Server(settings.COUCHDB_URL)
        self.assertTrue(response_json['success'])
        self.assertTrue('project_' + str(self.mobile_survey.id) in couch)

    def test_load_couchdb(self):
        """
        Test that resource instances and tiles load into a mobile survey's couchdb

        """

        post_data = {
            "datadownloadconfig": {"count":1000,"download":True,"resources":['d84a098c-368b-11e8-bafc-c4b301baab9f'],"custom":""},
            "startdate":"2018-01-29",
            "tilecache":"",
            "enddate":"2018-03-30",
            "createdby_id":1,
            "bounds":{"type":"FeatureCollection","features":[]},
            "cards":['fe035187-368b-11e8-bf56-c4b301baab9f', '4215f135-369c-11e8-9544-c4b301baab9f'],
            "lasteditedby_id":1,
            "groups":[],
            "active":False,
            "users":[],
            "id": str(self.mobile_survey.id),
            "name":"test survey",
            "description":"a description"
        }

        response_json = self.post_mobile_survey(post_data)
        couch = couchdb.Server(settings.COUCHDB_URL)

        resources = 0
        tiles = 0

        if 'project_' + str(self.mobile_survey.id) in couch:
            db = couch['project_' + str(self.mobile_survey.id)]
            view = ViewDefinition('tests', 'all', '''function(doc) {emit(doc._id, null);}''')
            view.get_doc(db)
            view.sync(db)
            for item in db.view('_design/tests/_view/all', include_docs=True):
                if item.doc['type'] == 'tile':
                    tiles += 1
                if item.doc['type'] == 'resource':
                    resources += 1

            # tile_count = len(db.find({'selector': {'type': 'tile'}}))
            # resource_count = len(db.find({'selector': {'type': 'resource'}}))
        else:
            print '{0} is not in couch'.format('project_' + str(self.mobile_survey.id))

        self.assertEqual(tiles, 2)
        self.assertEqual(resources,1)

    def test_delete_mobile_survey(self):
        """
        Test that deletion of a mobile survey deletes its couchdb

        """

        self.client.login(username='admin', password='admin')
        url = reverse('mobile_survey_manager')
        post_data = {
            "id": str(self.mobile_survey.id)
            }

        post_data = JSONSerializer().serialize(post_data)
        content_type = 'application/x-www-form-urlencoded'
        self.client.delete(url, post_data, content_type)
        couch = couchdb.Server(settings.COUCHDB_URL)
        self.assertFalse(MobileSurvey.objects.filter(pk=self.mobile_survey.id).exists())
        self.assertTrue('project_' + str(self.mobile_survey.id) not in couch)
