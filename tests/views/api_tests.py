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
from django.core import management
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
        with open(os.path.join("tests/fixtures/resource_graphs/unique_graph_shape.json"), "rU") as f:
            json = JSONDeserializer().deserialize(f)
            cls.unique_graph = Graph(json["graph"][0])
            cls.unique_graph.save()

        with open(os.path.join("tests/fixtures/resource_graphs/ambiguous_graph_shape.json"), "rU") as f:
            json = JSONDeserializer().deserialize(f)
            cls.ambiguous_graph = Graph(json["graph"][0])
            cls.ambiguous_graph.save()

        with open(os.path.join("tests/fixtures/resource_graphs/phase_type_assignment.json"), "rU") as f:
            json = JSONDeserializer().deserialize(f)
            cls.phase_type_assignment_graph = Graph(json["graph"][0])
            cls.phase_type_assignment_graph.save()

        cls.user = User.objects.create_user("test", "test@archesproject.org", "password")        

        # Load the resource graph.
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


    def test_api_resources_archesjson(self):
        """
        Test that resources POST and PUT accept arches-json format data.

        """
        #==Arrange==================================================================================================

        test_resource_simple = {
            "displaydescription": "Test Resource Desc",
            "displayname": "Test Resource dname",
            "graph_id": "c9b37a14-17b3-11eb-a708-acde48001122",
            "legacyid": "ARCHES_api",
            "map_popup": "undefined",
            "resourceinstanceid": "c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae", 
            "tiles": []          
        }
        test_resource_simple_modified = {
            "displaydescription": "Test Resource Desc",
            "displayname": "Test Resource dname",
            "graph_id": "c9b37a14-17b3-11eb-a708-acde48001122",
            "legacyid": "ARCHES_api_MOD",
            "map_popup": "undefined",
            "resourceinstanceid": "c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae", 
            "tiles": []          
        }

        payload = JSONSerializer().serialize(test_resource_simple)
        payload_modified = JSONSerializer().serialize(test_resource_simple_modified)
        
        content_type = "application/json"

        self.client.login(username="admin", password="admin")

        #==Act : GET confirmation that resource does not exist in database=========================================
        try:
            resp_get = self.client.get(reverse("resources", 
                                        kwargs={"resourceid":"c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae"})
                                        +"?format=arches-json")
        except Exception as e: 
        #==Assert==================================================================================================
            self.assertTrue(str(e) == "Resource matching query does not exist.") # Check exception message.



        #==Act : POST resource to database=========================================================================
        resp_post = self.client.post(reverse("resources", 
                                            kwargs={"resourceid":"c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae"})
                                            +"?format=arches-json",
                                            payload, 
                                            content_type)
        #==Assert==================================================================================================
        self.assertTrue(resp_post.status_code == 201) # resource created.


        

        #==Act : GET confirmation that resource does now exist in database=========================================
        resp_get_confirm = self.client.get(reverse("resources", 
                                    kwargs={"resourceid":"c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae"})
                                    +"?format=arches-json")        
        #==Assert==================================================================================================
        self.assertTrue(resp_get_confirm.status_code == 200) # Success, we got one.        
        data_get_confirm = JSONDeserializer().deserialize(resp_get_confirm.content)
        self.assertTrue(data_get_confirm["legacyid"]=="ARCHES_api") # Success, we got the right one.

        

        #==Act : PUT resource changes to database==================================================================
        resp_put = self.client.put(reverse("resources", 
                                            kwargs={"resourceid":"c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae"})
                                            +"?format=arches-json",
                                            payload_modified, 
                                            content_type)
        #==Assert==================================================================================================
        self.assertTrue(resp_put.status_code == 201) # resource created.



        #==Act : GET confirmation that resource is now changed in database=========================================
        resp_get_confirm_mod = self.client.get(reverse("resources", 
                                    kwargs={"resourceid":"c29e5caf-6c8d-422b-a2ac-f5f5d99e4dae"})
                                    +"?format=arches-json")        
        #==Assert==================================================================================================
        self.assertTrue(resp_get_confirm_mod.status_code == 200) # Success, we got one.     
        data_get_confirm_mod = JSONDeserializer().deserialize(resp_get_confirm_mod.content)
        self.assertTrue(data_get_confirm_mod["legacyid"]=="ARCHES_api_MOD") # Success, we got the right one.