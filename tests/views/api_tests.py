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

import json
import os
import uuid

from arches.app.utils.i18n import LanguageSynchronizer
from tests import test_settings
from tests.base_test import ArchesTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import management
from django.test.client import RequestFactory, Client
from django.test.utils import captured_stdout
from unittest.mock import patch, MagicMock

from arches.app.views.api import APIBase
from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

# these tests can be run from the command line via
# python manage.py test tests.views.api_tests --settings="tests.test_settings"


class APITests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
        if not models.GraphModel.objects.filter(pk=cls.data_type_graphid).exists():
            # TODO: Fix this to run inside transaction, i.e. after super().setUpClass()
            # https://github.com/archesproject/arches/issues/10719
            test_pkg_path = os.path.join(
                test_settings.TEST_ROOT, "fixtures", "testing_prj", "testing_prj", "pkg"
            )
            with captured_stdout():
                management.call_command(
                    "packages",
                    operation="load_package",
                    source=test_pkg_path,
                    yes=True,
                    verbosity=0,
                )

        super().setUpClass()
        cls.loadOntology()
        LanguageSynchronizer.synchronize_settings_with_db()
        with open(
            os.path.join("tests/fixtures/resource_graphs/unique_graph_shape.json"), "r"
        ) as f:
            json = JSONDeserializer().deserialize(f)
            cls.unique_graph = Graph(json["graph"][0])
            cls.unique_graph.publish(user=None)
            cls.unique_graph.save()

        with open(
            os.path.join("tests/fixtures/resource_graphs/ambiguous_graph_shape.json"),
            "r",
        ) as f:
            json = JSONDeserializer().deserialize(f)
            cls.ambiguous_graph = Graph(json["graph"][0])
            cls.ambiguous_graph.publish(user=None)
            cls.ambiguous_graph.save()

        with open(
            os.path.join("tests/fixtures/resource_graphs/phase_type_assignment.json"),
            "r",
        ) as f:
            json = JSONDeserializer().deserialize(f)
            cls.phase_type_assignment_graph = Graph(json["graph"][0])
            cls.phase_type_assignment_graph.publish(user=None)
            cls.phase_type_assignment_graph.save()

        cls.data_type_graph = Graph.objects.get(pk=cls.data_type_graphid)
        cls.test_prj_user = models.ResourceInstance.objects.filter(
            graph=cls.data_type_graph
        ).first()

    def get_tile_by_id(self, tileid, tiles):
        for tile in tiles:
            if tile["tileid"] == tileid:
                return tile
        return None

    def test_api_base_view(self):
        """
        Test that our custom header parameters get pushed on to the GET QueryDict

        """
        factory = RequestFactory(HTTP_X_ARCHES_VER="2.1")
        view = APIBase.as_view()

        request = factory.get(reverse("api_node_value", kwargs={}), {"ver": "2.0"})
        request.user = None
        with self.assertLogs("django.request", level="WARNING"):
            response = view(request)
        self.assertEqual(request.GET.get("ver"), "2.0")

        request = factory.get(reverse("api_node_value"), kwargs={})
        request.user = None
        with self.assertLogs("django.request", level="WARNING"):
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
                        "4f553551-95bd-11e8-8b48-acde48001122": {
                            "en": {"value": "Knights of Camelot", "direction": "ltr"}
                        },
                        "65f87f4c-95bd-11e8-b7a6-acde48001122": {
                            "en": {
                                "value": "We're knights of the Round Table, we dance whene'er we're able.",
                                "direction": "ltr",
                            }
                        },
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
                    "data": {
                        "e7364d1e-95c4-11e8-9e7c-acde48001122": None,
                        "f08a3057-95c4-11e8-9761-acde48001122": 63.0,
                    },
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
                                    "geometry": {
                                        "coordinates": [
                                            -122.3368509095547,
                                            37.10722439718975,
                                        ],
                                        "type": "Point",
                                    },
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
        with captured_stdout():
            resp_post = self.client.post(
                reverse(
                    "resources",
                    kwargs={"resourceid": "075957c4-d97f-4986-8d27-c32b6dec8e62"},
                )
                + "?format=arches-json",
                payload,
                content_type,
            )
        # ==Assert==========================================================================================
        self.assertEqual(resp_post.status_code, 201)  # resource created.
        my_resource = JSONDeserializer().deserialize(
            resp_post.content
        )  # get the resourceinstance returned.
        self.assertEqual(
            my_resource[0]["legacyid"], "I have to push the pram a lot."
        )  # Success, we were returned the right one.
        my_resource_resourceinstanceid = my_resource[0][
            "resourceinstanceid"
        ]  # get resourceinstanceid.
        # ==================================================================================================

        # ==Act : GET confirmation that resource does now exist in database=================================
        resp_get_confirm = self.client.get(
            reverse("resources", kwargs={"resourceid": my_resource_resourceinstanceid})
            + "?format=arches-json"
        )
        # ==Assert==========================================================================================
        self.assertEqual(resp_get_confirm.status_code, 200)  # Success, we got one.
        data_get_confirm = JSONDeserializer().deserialize(resp_get_confirm.content)
        tile = self.get_tile_by_id(
            "39cd6433-370c-471d-85a7-64de182fce6b", data_get_confirm["tiles"]
        )
        self.assertEqual(
            tile["data"]["65f87f4c-95bd-11e8-b7a6-acde48001122"]["en"]["value"],
            "We're knights of the Round Table, we dance whene'er we're able.",
        )  # Success, we got the right one.
        # ==================================================================================================

        # ==Arrange=========================================================================================

        # modify test_resource_simple
        test_resource_simple["tiles"][0]["data"][
            "65f87f4c-95bd-11e8-b7a6-acde48001122"
        ] = {
            "en": {
                "value": "We do routines and chorus scenes with footwork impec-cable..",
                "direction": "ltr",
            }
        }
        test_resource_simple["legacyid"] = (
            "we eat ham and jam and Spam a lot."  # legacyid has a unique index constraint.
        )
        payload_modified = JSONSerializer().serialize(test_resource_simple)

        # ==PUT=============================================================================================

        # ==Act : GET confirmation that resource does not exist in database=================================
        with self.assertRaises(models.ResourceInstance.DoesNotExist) as context:
            with self.assertLogs("django.request", level="ERROR"):
                resp_get = self.client.get(
                    reverse(
                        "resources",
                        kwargs={"resourceid": "075957c4-d97f-4986-8d27-c32b6dec8e62"},
                    )
                    + "?format=arches-json"
                )
        # ==Assert==========================================================================================
        self.assertTrue(
            "Resource matching query does not exist." in str(context.exception)
        )  # Check exception message.
        # ==================================================================================================

        # ==Act : PUT resource changes to database for new resourceinstanceid to create new resource=========
        with captured_stdout():
            resp_put_create = self.client.put(
                reverse(
                    "resources",
                    kwargs={"resourceid": "075957c4-d97f-4986-8d27-c32b6dec8e62"},
                )
                + "?format=arches-json",
                payload_modified,
                content_type,
            )

        # ==Assert==========================================================================================
        self.assertEqual(resp_put_create.status_code, 201)  # resource created.
        resp_put_create_resource = JSONDeserializer().deserialize(
            resp_put_create.content
        )  # get the resourceinstance returned.
        self.assertEqual(
            resp_put_create_resource[0]["legacyid"],
            "we eat ham and jam and Spam a lot.",
        )  # Success, we returned the right one.
        # ==================================================================================================

        # ==Act : GET confirmation that resource does now exist in database=================================
        resp_put_get_confirm = self.client.get(
            reverse(
                "resources",
                kwargs={"resourceid": "075957c4-d97f-4986-8d27-c32b6dec8e62"},
            )
            + "?format=arches-json"
        )
        # ==Assert==========================================================================================
        self.assertEqual(resp_put_get_confirm.status_code, 200)  # Success, we got one.
        data_put_get_confirm = JSONDeserializer().deserialize(
            resp_put_get_confirm.content
        )
        tile = self.get_tile_by_id(
            "39cd6433-370c-471d-85a7-64de182fce6b", data_put_get_confirm["tiles"]
        )
        self.assertEqual(
            tile["data"]["65f87f4c-95bd-11e8-b7a6-acde48001122"]["en"]["value"],
            "We do routines and chorus scenes with footwork impec-cable..",
        )  # Success, we got the right one.
        # ==================================================================================================

        # ==Act : PUT resource changes to database, with invalid URI========================================
        with self.assertLogs("django.request", level="WARNING"):
            resp_put_uri_diff = self.client.put(
                reverse(
                    "resources",
                    kwargs={"resourceid": "001fe587-ad3d-4d0d-a3c9-814028766434"},
                )
                + "?format=arches-json",
                payload_modified,
                content_type,
            )
        # ==Assert==========================================================================================
        self.assertEqual(resp_put_uri_diff.status_code, 400)  # Bad Request.
        # ==================================================================================================

        # ==Arrange=========================================================================================

        # modify resourceinstanceid on modified test_resource_simple to that of initial POST resource.
        test_resource_simple["resourceinstanceid"] = my_resource_resourceinstanceid
        test_resource_simple["legacyid"] = (
            "we sing from the diaphragm a lot."  # legacyid has a unique index constraint.
        )
        payload_modified = JSONSerializer().serialize(test_resource_simple)

        # ==Act : PUT resource changes to initial POST database resource to overwrite=======================
        with captured_stdout():
            resp_put = self.client.put(
                reverse(
                    "resources", kwargs={"resourceid": my_resource_resourceinstanceid}
                )
                + "?format=arches-json",
                payload_modified,
                content_type,
            )

        # ==Assert==========================================================================================
        self.assertEqual(resp_put.status_code, 201)  # resource created.
        data_resp_put_confirm_mod = JSONDeserializer().deserialize(resp_put.content)
        self.assertEqual(
            data_resp_put_confirm_mod[0]["legacyid"],
            "we sing from the diaphragm a lot.",
        )  # Success, we returned the right one.
        # ==================================================================================================

        # ==Act : GET confirmation that resource is now changed in database=================================
        resp_get_confirm_mod = self.client.get(
            reverse("resources", kwargs={"resourceid": my_resource_resourceinstanceid})
            + "?format=arches-json"
        )
        # ==Assert==========================================================================================
        self.assertEqual(resp_get_confirm_mod.status_code, 200)  # Success, we got one.
        data_get_confirm_mod = JSONDeserializer().deserialize(
            resp_get_confirm_mod.content
        )
        tile = self.get_tile_by_id(
            "39cd6433-370c-471d-85a7-64de182fce6b", data_get_confirm_mod["tiles"]
        )
        self.assertEqual(
            tile["data"]["65f87f4c-95bd-11e8-b7a6-acde48001122"]["en"]["value"],
            "We do routines and chorus scenes with footwork impec-cable..",
        )
        # ==================================================================================================

        # ==Act : DELETE resource from database=============================================================
        resp_delete = self.client.delete(
            reverse("resources", kwargs={"resourceid": my_resource_resourceinstanceid})
        )
        # ==Assert==========================================================================================
        self.assertEqual(resp_delete.status_code, 200)  # Success, we got rid of one.
        # ==================================================================================================

        # ==Act : GET confirmation that resource does not exist in database=================================
        with self.assertRaises(models.ResourceInstance.DoesNotExist) as context_del:
            with self.assertLogs("django.request", level="ERROR"):
                resp_get_deleted = self.client.get(
                    reverse(
                        "resources",
                        kwargs={"resourceid": my_resource_resourceinstanceid},
                    )
                    + "?format=arches-json"
                )
        # ==Assert==========================================================================================
        self.assertTrue(
            "Resource matching query does not exist." in str(context_del.exception)
        )  # Check exception message.
        # ==================================================================================================

    def test_get_resource_jsonld_invalid_no_ontology(self):
        # Bypass validation in .save()
        Graph.objects.filter(pk=self.data_type_graph.pk).update(ontology=None)

        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(
                reverse("resources", kwargs={"resourceid": str(self.test_prj_user.pk)})
                + "?format=json-ld"
            )

        self.assertEqual(response.status_code, 400)


class ResourceInstanceLifecycleStatesTest(ArchesTestCase):
    @patch("arches.app.models.models.ResourceInstanceLifecycleState.objects.all")
    def test_get_all_lifecycle_states(self, mock_all):
        lifecycle_state1 = models.ResourceInstanceLifecycleState(
            id=uuid.uuid4(), name="State 1"
        )
        lifecycle_state2 = models.ResourceInstanceLifecycleState(
            id=uuid.uuid4(), name="State 2"
        )
        mock_all.return_value = [lifecycle_state1, lifecycle_state2]

        response = self.client.get(reverse("api_resource_instance_lifecycle_states"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()[0]["name"], "State 1")
        self.assertEqual(response.json()[1]["name"], "State 2")


class ResourceInstanceLifecycleStateTest(ArchesTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.lifecycle_state_id = uuid.uuid4()
        self.new_lifecycle_state_id = uuid.uuid4()
        self.resource_instance_id = uuid.uuid4()
        self.resource_id = uuid.uuid4()

    @patch("arches.app.models.models.ResourceInstance.objects.get")
    def test_get_lifecycle_state(self, mock_get):
        lifecycle_state = models.ResourceInstanceLifecycleState(
            id=self.lifecycle_state_id, name="State 1"
        )
        mock_resource_instance = MagicMock(
            resource_instance_lifecycle_state=lifecycle_state
        )
        mock_get.return_value = mock_resource_instance

        response = self.client.get(
            reverse(
                "api_resource_instance_lifecycle_state",
                args=[self.resource_instance_id],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "State 1")

    @patch("arches.app.models.resource.Resource.objects.get")
    @patch("arches.app.models.models.ResourceInstanceLifecycleState.objects.get")
    @patch(
        "arches.app.models.resource.Resource.update_resource_instance_lifecycle_state"
    )
    def test_post_lifecycle_state(
        self, mock_update, mock_get_lifecycle_state, mock_get_resource
    ):
        self.client.login(username="testuser", password="testpass")

        original_lifecycle_state = models.ResourceInstanceLifecycleState(
            id=self.lifecycle_state_id, name="State 1"
        )
        new_lifecycle_state = models.ResourceInstanceLifecycleState(
            id=self.new_lifecycle_state_id, name="State 2"
        )

        # Configure the mock to return actual instances
        mock_get_resource.return_value = Resource(
            pk=self.resource_id,
            resource_instance_lifecycle_state=original_lifecycle_state,
        )
        mock_get_lifecycle_state.return_value = new_lifecycle_state
        mock_update.return_value = new_lifecycle_state

        response = self.client.post(
            reverse("api_resource_instance_lifecycle_state", args=[self.resource_id]),
            data=json.dumps(str(self.new_lifecycle_state_id)),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["original_resource_instance_lifecycle_state"]["name"],
            "State 1",
        )
        self.assertEqual(
            response.json()["current_resource_instance_lifecycle_state"]["name"],
            "State 2",
        )
