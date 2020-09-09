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
import uuid
from tests import test_settings
from arches.app.utils.couch import Couch
import couchdb
from django.test import TestCase
from django.core import management
from arches.app.models import models
from django.urls import reverse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.test.client import Client

# these tests can be run from the command line via
# python manage.py test tests/views/command_line_tests.py --pattern="*.py" --settings="tests.test_settings"


class CommandLineTests(TestCase):
    def setUp(self):
        self.survey_id = "d309d38e-29b9-45c0-b0f5-542f34a4576a"
        self.expected_resource_count = 2
        self.data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
        self.client = Client()

    def tearDown(self):
        management.call_command("mobile", operation="delete_surveys", id=self.survey_id)
        models.ResourceInstance.objects.filter(graph_id=self.data_type_graphid).delete()

    @classmethod
    def setUpClass(cls):
        test_pkg_path = os.path.join(test_settings.TEST_ROOT, "fixtures", "testing_prj", "testing_prj", "pkg")
        management.call_command("packages", operation="load_package", source=test_pkg_path, yes=True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_load_package(self):
        resources = models.ResourceInstance.objects.filter(graph_id=self.data_type_graphid)
        self.assertEqual(len(list(resources)), self.expected_resource_count)

    def test_mobile_survey(self):
        data = {  # note that cards and resourceid belong to datatype testing model in testing_prj/pkg
            "id": self.survey_id,
            "name": "test_project",
            "active": True,
            "createdby_id": None,
            "lasteditedby_id": None,
            "startdate": "2020-01-26",
            "enddate": "2025-03-07",
            "description": "desc here 1",
            "bounds": {
                "features": [
                    {
                        "geometry": {
                            "coordinates": [
                                [
                                    [-0.194220532242397, 51.46274256605967],
                                    [0.01817698974429, 51.46437979012592],
                                    [0.013905389416863, 51.56284140042993],
                                    [-0.191845725821395, 51.56047215557854],
                                    [-0.194220532242397, 51.46274256605967],
                                ]
                            ],
                            "type": "Polygon",
                        },
                        "properties": {},
                        "type": "Feature",
                    }
                ],
                "type": "FeatureCollection",
            },
            "tilecache": None,
            "onlinebasemaps": {"default": "mapbox://styles/mapbox/streets-v9"},
            "datadownloadconfig": {"download": False, "count": 100, "resources": ["330802c5-95bd-11e8-b7ac-acde48001122"], "custom": None},
            "users": [1],
            "groups": [],
            "cards": [
                "62b84902-95ec-11e8-86d3-acde48001122",
                "c5e3afde-95c5-11e8-a63f-acde48001122",
                "8cc075cc-95eb-11e8-bb88-acde48001122",
                "35be1c14-95ed-11e8-8db0-acde48001122",
                "c1bd336b-95bd-11e8-98d6-acde48001122",
                "4e3c81e8-95bd-11e8-b2d6-acde48001122",
                "28c343d4-95c5-11e8-9fb6-acde48001122",
                "3bd30b02-95c3-11e8-8f15-acde48001122",
                "de301d4a-95c3-11e8-b74b-acde48001122",
                "5d9d643d-95c4-11e8-848a-acde48001122",
            ],
        }
        payload = JSONSerializer().serialize(data)
        content_type = "application/x-www-form-urlencoded"
        self.client.login(username="admin", password="admin")
        resp = {"success": False}
        try:
            raw_resp = self.client.post(reverse("collector_designer", kwargs={"surveyid": self.survey_id}), payload, content_type)
            resp = JSONDeserializer().deserialize(raw_resp.content)
        except couchdb.http.Unauthorized:
            # try again
            print("Not authorized to post to couch")
            pass

        self.assertTrue(resp["success"])

        test_survey_id = ""
        # management.call_command("mobile", operation="sync_survey", id=self.survey_id)
        couch = Couch()
        couchdbs = [dbname for dbname in couch.couch]
        for db in couchdbs:
            survey_id_from_db = db[-36:]
            if self.survey_id == survey_id_from_db:
                test_survey_id = survey_id_from_db

        self.assertTrue(self.survey_id == test_survey_id)
