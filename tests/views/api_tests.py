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
from arches.app.models import models
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

        # Load the test package to provide resources graph.
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
        Uses GET and DELETE in testing.

        """
        # ==Arrange=========================================================================================

        test_resource_simple = {
            "displaydescription": " We're knights of the Round Table, we dance whene'er we're able.",
            "displayname": " Knights of Camelot",
            "graph_id": "330802c5-95bd-11e8-b7ac-acde48001122",
            "legacyid": "I have to push the pram a lot.",
            "map_popup": "We're knights of the Round Table, we dance whene'er we're able.",
            "resourceinstanceid": "075957c4-d97f-4986-8d27-c32b6dec8e62",
            "tiles": [
                {
                    "data": {
                        "46f4da0c-95bd-11e8-8f87-acde48001122": None,
                        "4f553551-95bd-11e8-8b48-acde48001122": "Knights of Camelot",
                        "65f87f4c-95bd-11e8-b7a6-acde48001122": "We're knights of the Round Table, we dance whene'er we're able.",
                    },
                    "nodegroup_id": "46f4da0c-95bd-11e8-8f87-acde48001122",
                    "parenttile_id": None,
                    "provisionaledits": None,
                    "resourceinstance_id": "075957c4-d97f-4986-8d27-c32b6dec8e62",
                    "sortorder": 0,
                    "tileid": "39cd6433-370c-471d-85a7-64de182fce6b",
                },
                {
                    "data": {
                        "be993840-95c3-11e8-b08a-acde48001122": None,
                        "dfb05368-95c3-11e8-809b-acde48001122": [
                            {
                                "file_id": "64d698ae-9c5f-433c-967a-f037261dc369",
                                "name": "ffffff",
                                "status": "",
                                "type": "",
                                "url": "/files/uploadedfiles/ffffff",
                            }
                        ],
                    },
                    "nodegroup_id": "be993840-95c3-11e8-b08a-acde48001122",
                    "parenttile_id": None,
                    "provisionaledits": None,
                    "resourceinstance_id": "075957c4-d97f-4986-8d27-c32b6dec8e62",
                    "sortorder": 0,
                    "tileid": "a559fff5-2113-49c6-a34e-2e8b92a08a90",
                },
                {
                    "data": {"e7364d1e-95c4-11e8-9e7c-acde48001122": None, "f08a3057-95c4-11e8-9761-acde48001122": 63.0},
                    "nodegroup_id": "e7364d1e-95c4-11e8-9e7c-acde48001122",
                    "parenttile_id": None,
                    "provisionaledits": None,
                    "resourceinstance_id": "075957c4-d97f-4986-8d27-c32b6dec8e62",
                    "sortorder": 0,
                    "tileid": "ecd96a8e-9f95-490a-8093-bbe157089656",
                },
                {
                    "data": {
                        "c0197fe6-95c5-11e8-8394-acde48001122": None,
                        "c7d493b3-95c5-11e8-b554-acde48001122": "true",
                        "df6311f3-95ed-11e8-a289-acde48001122": "true",
                    },
                    "nodegroup_id": "c0197fe6-95c5-11e8-8394-acde48001122",
                    "parenttile_id": None,
                    "provisionaledits": None,
                    "resourceinstance_id": "075957c4-d97f-4986-8d27-c32b6dec8e62",
                    "sortorder": 0,
                    "tileid": "1c115557-8a9d-47a7-994f-11624e2efc88",
                },
                {
                    "data": {
                        "2e3b04c0-95ed-11e8-b68c-acde48001122": None,
                        "38870840-95ed-11e8-b2a9-acde48001122": {
                            "features": [
                                {
                                    "geometry": {"coordinates": [-122.3368509095547, 37.10722439718975], "type": "Point"},
                                    "id": "c2923742-99bc-48dc-acd0-1236dc728582",
                                    "properties": {},
                                    "type": "Feature",
                                }
                            ],
                            "type": "FeatureCollection",
                        },
                    },
                    "nodegroup_id": "2e3b04c0-95ed-11e8-b68c-acde48001122",
                    "parenttile_id": None,
                    "provisionaledits": None,
                    "resourceinstance_id": "075957c4-d97f-4986-8d27-c32b6dec8e62",
                    "sortorder": 0,
                    "tileid": "7e981761-0605-42ec-82bb-db42113daa60",
                },
                {
                    "data": {
                        "318c9e2b-a017-11e8-a36c-0200ec49ad01": [
                            "8c08196e-90bb-4359-b4ca-733861409de6",
                            "118b4e63-4466-494c-94ac-4cb98886c372",
                        ],
                        "ba84cc78-95bd-11e8-b8f5-acde48001122": None,
                        "c386a030-95bd-11e8-bff6-acde48001122": "118b4e63-4466-494c-94ac-4cb98886c372",
                        "d3089738-95bd-11e8-aa23-acde48001122": "118b4e63-4466-494c-94ac-4cb98886c372",
                        "feee2b85-a017-11e8-8460-0200ec49ad01": [
                            "8c08196e-90bb-4359-b4ca-733861409de6",
                            "118b4e63-4466-494c-94ac-4cb98886c372",
                        ],
                    },
                    "nodegroup_id": "ba84cc78-95bd-11e8-b8f5-acde48001122",
                    "parenttile_id": None,
                    "provisionaledits": None,
                    "resourceinstance_id": "075957c4-d97f-4986-8d27-c32b6dec8e62",
                    "sortorder": 0,
                    "tileid": "dc342949-661e-4ed0-9234-97f18d9ae483",
                },
                {
                    "data": {
                        "340c4817-95c3-11e8-b9e1-acde48001122": None,
                        "3dcfea07-95c3-11e8-b4da-acde48001122": "3d4ad50d-d855-4e40-8e78-911922977ba8",
                        "4ff64c70-95c3-11e8-8c25-acde48001122": "ad1aa626-7380-4b1c-8133-11fa1fed05eb",
                        "57b9e1a1-a017-11e8-b8c2-0200ec49ad01": [
                            "9561c1ae-0ae8-478c-b465-33ae8f6f27ca",
                            "ccfc0ac3-17b1-4672-8183-e02d419fe133",
                        ],
                    },
                    "nodegroup_id": "340c4817-95c3-11e8-b9e1-acde48001122",
                    "parenttile_id": None,
                    "provisionaledits": None,
                    "resourceinstance_id": "075957c4-d97f-4986-8d27-c32b6dec8e62",
                    "sortorder": 0,
                    "tileid": "57ec7d61-e71c-481b-bcad-6ec9a0631dec",
                },
                {
                    "data": {
                        "10fef7c0-a017-11e8-99b0-0200ec49ad01": "2010-10",
                        "5ebe6bc2-95c4-11e8-9dac-acde48001122": "1926-01-06",
                        "d3e98b97-95c3-11e8-a9b2-acde48001122": None,
                    },
                    "nodegroup_id": "d3e98b97-95c3-11e8-a9b2-acde48001122",
                    "parenttile_id": None,
                    "provisionaledits": None,
                    "resourceinstance_id": "075957c4-d97f-4986-8d27-c32b6dec8e62",
                    "sortorder": 0,
                    "tileid": "0c63341c-0663-4c39-b554-df69f0bd7904",
                },
            ],
        }

        payload = JSONSerializer().serialize(test_resource_simple)
        content_type = "application/json"
        self.client.login(username="admin", password="admin")

        # ==POST============================================================================================

        # ==Act : POST resource to database (N.B. resourceid supplied will be overwritten by arches)========
        resp_post = self.client.post(
            reverse("resources", kwargs={"resourceid": "075957c4-d97f-4986-8d27-c32b6dec8e62"}) + "?format=arches-json",
            payload,
            content_type,
        )
        # ==Assert==========================================================================================
        self.assertEqual(resp_post.status_code, 201)  # resource created.
        my_resource = JSONDeserializer().deserialize(resp_post.content)  # get the resourceinstance returned.
        self.assertEqual(my_resource[0]["legacyid"], "I have to push the pram a lot.")  # Success, we were returned the right one.
        my_resource_resourceinstanceid = my_resource[0]["resourceinstanceid"]  # get resourceinstanceid.
        # ==================================================================================================

        # ==Act : GET confirmation that resource does now exist in database=================================
        resp_get_confirm = self.client.get(
            reverse("resources", kwargs={"resourceid": my_resource_resourceinstanceid}) + "?format=arches-json"
        )
        # ==Assert==========================================================================================
        self.assertEqual(resp_get_confirm.status_code, 200)  # Success, we got one.
        data_get_confirm = JSONDeserializer().deserialize(resp_get_confirm.content)
        self.assertEqual(
            data_get_confirm["tiles"][0]["data"]["65f87f4c-95bd-11e8-b7a6-acde48001122"],
            "We're knights of the Round Table, we dance whene'er we're able.",
        )  # Success, we got the right one.
        # ==================================================================================================

        # ==Arrange=========================================================================================

        # modify test_resource_simple
        test_resource_simple["tiles"][0]["data"][
            "65f87f4c-95bd-11e8-b7a6-acde48001122"
        ] = "We do routines and chorus scenes with footwork impec-cable.."
        test_resource_simple["legacyid"] = "we eat ham and jam and Spam a lot."  # legacyid has a unique index constraint.
        payload_modified = JSONSerializer().serialize(test_resource_simple)

        # ==PUT=============================================================================================

        # ==Act : GET confirmation that resource does not exist in database=================================
        with self.assertRaises(models.ResourceInstance.DoesNotExist) as context:
            resp_get = self.client.get(
                reverse("resources", kwargs={"resourceid": "075957c4-d97f-4986-8d27-c32b6dec8e62"}) + "?format=arches-json"
            )
        # ==Assert==========================================================================================
        self.assertTrue("Resource matching query does not exist." in str(context.exception))  # Check exception message.
        # ==================================================================================================

        # ==Act : PUT resource changes to database for new resourceinstanceid to create new resource=========
        resp_put_create = self.client.put(
            reverse("resources", kwargs={"resourceid": "075957c4-d97f-4986-8d27-c32b6dec8e62"}) + "?format=arches-json",
            payload_modified,
            content_type,
        )

        # ==Assert==========================================================================================
        self.assertEqual(resp_put_create.status_code, 201)  # resource created.
        resp_put_create_resource = JSONDeserializer().deserialize(resp_put_create.content)  # get the resourceinstance returned.
        self.assertEqual(
            resp_put_create_resource[0]["legacyid"], "we eat ham and jam and Spam a lot."
        )  # Success, we returned the right one.
        # ==================================================================================================

        # ==Act : GET confirmation that resource does now exist in database=================================
        resp_put_get_confirm = self.client.get(
            reverse("resources", kwargs={"resourceid": "075957c4-d97f-4986-8d27-c32b6dec8e62"}) + "?format=arches-json"
        )
        # ==Assert==========================================================================================
        self.assertEqual(resp_put_get_confirm.status_code, 200)  # Success, we got one.
        data_put_get_confirm = JSONDeserializer().deserialize(resp_put_get_confirm.content)

        tile = next(x for x in data_put_get_confirm["tiles"] if x["tileid"] == "39cd6433-370c-471d-85a7-64de182fce6b")
        self.assertEqual(
            tile["data"]["65f87f4c-95bd-11e8-b7a6-acde48001122"],
            "We do routines and chorus scenes with footwork impec-cable..",
        )  # Success, we got the right one.
        # ==================================================================================================

        # ==Act : PUT resource changes to database, with invalid URI========================================
        resp_put_uri_diff = self.client.put(
            reverse("resources", kwargs={"resourceid": "001fe587-ad3d-4d0d-a3c9-814028766434"}) + "?format=arches-json",
            payload_modified,
            content_type,
        )
        # ==Assert==========================================================================================
        self.assertEqual(resp_put_uri_diff.status_code, 400)  # Bad Request.
        # ==================================================================================================

        # ==Arrange=========================================================================================

        # modify resourceinstanceid on modified test_resource_simple to that of initial POST resource.
        test_resource_simple["resourceinstanceid"] = my_resource_resourceinstanceid
        test_resource_simple["legacyid"] = "we sing from the diaphragm a lot."  # legacyid has a unique index constraint.
        payload_modified = JSONSerializer().serialize(test_resource_simple)

        # ==Act : PUT resource changes to initial POST database resource to overwrite=======================
        resp_put = self.client.put(
            reverse("resources", kwargs={"resourceid": my_resource_resourceinstanceid}) + "?format=arches-json",
            payload_modified,
            content_type,
        )

        # ==Assert==========================================================================================
        self.assertEqual(resp_put.status_code, 201)  # resource created.
        data_resp_put_confirm_mod = JSONDeserializer().deserialize(resp_put.content)
        self.assertEqual(
            data_resp_put_confirm_mod[0]["legacyid"], "we sing from the diaphragm a lot."
        )  # Success, we returned the right one.
        # ==================================================================================================

        # ==Act : GET confirmation that resource is now changed in database=================================
        resp_get_confirm_mod = self.client.get(
            reverse("resources", kwargs={"resourceid": my_resource_resourceinstanceid}) + "?format=arches-json"
        )
        # ==Assert==========================================================================================
        self.assertEqual(resp_get_confirm_mod.status_code, 200)  # Success, we got one.
        data_get_confirm_mod = JSONDeserializer().deserialize(resp_get_confirm_mod.content)

        tile = next(x for x in data_put_get_confirm["tiles"] if x["tileid"] == "39cd6433-370c-471d-85a7-64de182fce6b")
        self.assertEqual(
            tile["data"]["65f87f4c-95bd-11e8-b7a6-acde48001122"],
            "We do routines and chorus scenes with footwork impec-cable..",
        )
        # ==================================================================================================

        # ==Act : DELETE resource from database=============================================================
        resp_delete = self.client.delete(reverse("resources", kwargs={"resourceid": my_resource_resourceinstanceid}))
        # ==Assert==========================================================================================
        self.assertEqual(resp_delete.status_code, 200)  # Success, we got rid of one.
        # ==================================================================================================

        # ==Act : GET confirmation that resource does not exist in database=================================
        with self.assertRaises(models.ResourceInstance.DoesNotExist) as context_del:
            resp_get_deleted = self.client.get(
                reverse("resources", kwargs={"resourceid": my_resource_resourceinstanceid}) + "?format=arches-json"
            )
        # ==Assert==========================================================================================
        self.assertTrue("Resource matching query does not exist." in str(context_del.exception))  # Check exception message.
        # ==================================================================================================
