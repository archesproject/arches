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
from tests.base_test import ArchesTestCase
from django.urls import reverse
from django.test.client import RequestFactory, Client
from arches.app.views.api import APIBase
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

from django.contrib.auth.models import User, Group, AnonymousUser

# these tests can be run from the command line via
# python manage.py test tests/views/api_tests.py --pattern="*.py" --settings="tests.test_settings"


class APITests(ArchesTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        geojson_nodeid = "3ebc6785-fa61-11e6-8c85-14109fd34195"
        cls.loadOntology()
        # with open(os.path.join("tests/fixtures/resource_graphs/unique_graph_shape.json"), "rU") as f:
        #     json = JSONDeserializer().deserialize(f)
        #     cls.unique_graph = Graph(json["graph"][0])
        #     cls.unique_graph.save()

        # with open(os.path.join("tests/fixtures/resource_graphs/ambiguous_graph_shape.json"), "rU") as f:
        #     json = JSONDeserializer().deserialize(f)
        #     cls.ambiguous_graph = Graph(json["graph"][0])
        #     cls.ambiguous_graph.save()

        # with open(os.path.join("tests/fixtures/resource_graphs/phase_type_assignment.json"), "rU") as f:
        #     json = JSONDeserializer().deserialize(f)
        #     cls.phase_type_assignment_graph = Graph(json["graph"][0])
        #     cls.phase_type_assignment_graph.save()
        
        # cls.factory = RequestFactory()
        # cls.client = Client()
        cls.user = User.objects.create_user("test", "test@archesproject.org", "password")
        

        # # Looks like we need to load the resource graph.. this is from resource_tests.py
        from django.core import management
        test_pkg_path = os.path.join(test_settings.TEST_ROOT, "fixtures", "testing_prj", "testing_prj", "pkg")
        management.call_command("packages", operation="load_package", source=test_pkg_path, yes=True)


    def test_api_base_view(self):
        """
        Test that our custom header parameters get pushed on to the GET QueryDict

        """

        factory = RequestFactory(HTTP_X_ARCHES_VER="2.1")
        view = APIBase.as_view()

        request = factory.get(reverse("mobileprojects", kwargs={}), {"ver": "2.0"})
        request.user = None
        response = view(request)
        self.assertEqual(request.GET.get("ver"), "2.0")

        request = factory.get(reverse("mobileprojects"), kwargs={})
        request.user = None
        response = view(request)
        self.assertEqual(request.GET.get("ver"), "2.1")


    def test_api_resources_post_archesjson(self):
        """
        Test that resources POST accepts arches-json format data.

        """

        # test update a ResourceTestModel resource 
        test_resource = {
            "displaydescription": "undefined",
            "displayname": "undefined",
            "graph_id": "c9b37a14-17b3-11eb-a708-acde48001122",
            "legacyid": "ARCHES",
            "map_popup": "undefined",
            "resourceinstanceid": "c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae",
            "tiles": [
                {
                    "data": {
                        "c9b37b7c-17b3-11eb-a708-acde48001122": "Foo ResourceTestModel"
                    },
                    "nodegroup_id": "c9b37b7c-17b3-11eb-a708-acde48001122",
                    "resourceinstance_id": "c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae",
                    "sortorder": 0,
                    "tileid": "9b7b8897-d4a0-4735-b1fe-9d82d9890740"
                },
                {
                    "data": {
                        "c9b37f96-17b3-11eb-a708-acde48001122": {
                            "features": [
                                {
                                    "geometry": {
                                        "coordinates": [
                                            [
                                                [
                                                    -1.7933273753688184,
                                                    51.56492920592859
                                                ],
                                                [
                                                    -1.7932521887532005,
                                                    51.564204760266338
                                                ],
                                                [
                                                    -1.7899815709831444,
                                                    51.563854217899379
                                                ],
                                                [
                                                    -1.7899815709831444,
                                                    51.564882467846988
                                                ],
                                                [
                                                    -1.7933273753688184,
                                                    51.56492920592859
                                                ]
                                            ]
                                        ],
                                        "type": "Polygon"
                                    },
                                    "id": "b11df9f801aa89ba1250ffc6843801e2",
                                    "properties": {
                                        "nodeId": "c9b37f96-17b3-11eb-a708-acde48001122"
                                    },
                                    "type": "Feature"
                                }
                            ],
                            "type": "FeatureCollection"
                        }
                    },
                    "nodegroup_id": "c9b37f96-17b3-11eb-a708-acde48001122",
                    "resourceinstance_id": "c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae",
                    "sortorder": 0,
                    "tileid": "16d2eb37-d5df-43d4-a930-937fcacd9db1"
                },
                {
                    "data": {
                        "c9b38568-17b3-11eb-a708-acde48001122": "2021-05-06"
                    },
                    "nodegroup_id": "c9b38568-17b3-11eb-a708-acde48001122",
                    "resourceinstance_id": "c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae",
                    "sortorder": 0,
                    "tileid": "b729b441-3240-420f-9a39-98244c8244e8"
                },
                {
                    "data": {
                        "c9b38aea-17b3-11eb-a708-acde48001122": "Foo ResourceTestModel Sensitive"
                    },
                    "nodegroup_id": "c9b38aea-17b3-11eb-a708-acde48001122",
                    "resourceinstance_id": "c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae",
                    "sortorder": 0,
                    "tileid": "e7f0a6db-045e-4aee-b490-c7d2f0d36b14"
                },
                {
                    "data": {
                        "c9b3828e-17b3-11eb-a708-acde48001122": "2021-05-06"
                    },
                    "nodegroup_id": "c9b3828e-17b3-11eb-a708-acde48001122",
                    "resourceinstance_id": "c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae",
                    "sortorder": 0,
                    "tileid": "71d169e7-bcf4-4354-ac90-0ea9f7fb3f4c"
                }
            ]
        }
        test_resource_simple = {
            "displaydescription": "Test Resource Desc",
            "displayname": "Test Resource dname",
            "graph_id": "c9b37a14-17b3-11eb-a708-acde48001122",
            "legacyid": "ARCHES",
            "map_popup": "undefined",
            "resourceinstanceid": "c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae", 
            "tiles": []          
        }

        # KH - Try with simple payload? Try with complex payload?
        #payload = JSONSerializer().serialize(test_resource)
        payload = JSONSerializer().serialize(test_resource_simple)
        
        content_type = "application/json"

        # KH - What is this 'as_view'? I', not using it, should I be?
        view = APIBase.as_view()



        #==THIS CALLS YOUR FUNCTION CODE!!===="inspired by the elegant auth_tests"==================================================================================================

        self.client.login(username="admin", password="admin")

        try:

            # KH - We gonna GET to check it's not in there?
            raw_resp0 = self.client.get(reverse("resources", 
                                        kwargs={"resourceid":"c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae"})
                                        +"?format=arches-json")

            print("\n**GET Response ON c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae***********************************************************\n")
            print(raw_resp0)
            print("\n*************************************************************\n")
            # KH - can we trust this? Is it doing what we think it's doing?
            # self.assertTrue(raw_resp0.status_code == 404) # Success, we not got one.
        except Exception as e: 
            print("\n*************************************************************\n")
            print("GET unable to find that which was absent " + str(e))
            print(type(e))
            print(e.args)
            print("\n*************************************************************\n")
            self.assertTrue(str(e) == "Resource matching query does not exist.")







        resp = {"success": False}
        raw_resp = self.client.post(reverse("resources", 
                                            kwargs={"resourceid":"c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae"})
                                            +"?format=arches-json",
                                            payload, 
                                            content_type)
        print("\n**POST CALL ON c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae***********************************************************\n")
        print(raw_resp)
        print("\n*************************************************************\n")
        
        # KH - can we trust this? Is it doing what we think it's doing?
        self.assertTrue(raw_resp.status_code == 201) # resource created.

        # KH - What are you going to do with this now ya got it?
        resp = JSONDeserializer().deserialize(raw_resp.content)
        print("\n**Response ON c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae***********************************************************\n")
        print(resp)
        print("\n*************************************************************\n")

        # KH - We gonna GET to check it's in there?
        raw_resp2 = self.client.get(reverse("resources", 
                                    kwargs={"resourceid":"c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae"})
                                    +"?format=arches-json")
        
        # KH - can we trust this? Is it doing what we think it's doing?
        self.assertTrue(raw_resp2.status_code == 200) # Success, we got one.
        
        print("\n**GET CALL ON c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae***********************************************************\n")
        # KH - What are you going to do with this now ya got it?
        resp2 = JSONDeserializer().deserialize(raw_resp2.content)
        print(resp2)
        print("\n*************************************************************\n")