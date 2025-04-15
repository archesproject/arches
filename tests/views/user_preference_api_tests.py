import json
import uuid
from tests.base_test import ArchesTestCase
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from arches.app.models.models import UserPreference
from arches.app.models import models
from django.test.client import Client


# these tests can be run from the command line via
# python manage.py test tests.views.user_preference_api_tests --settings="tests.test_settings"


class UserPrefApiTest(ArchesTestCase):
    admin_preference_id = "d0e9ef74-d99f-4064-9a60-e91a6a8deab2"
    anonymous_preference_id = "d64e93a2-f46f-4c15-a927-b190878af738"

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        # Test admin user preference
        cls.user_preference = UserPreference.objects.create(
            userpreferenceid=cls.admin_preference_id,
            username=models.User.objects.get(username="admin"),
            preferencename="Admin test preference",
            appname="my app name",
            config=[
                {"overlayid": "7d0dffba-5bcf-4694-a5d7-3425ad97fa2b", "sortorder": 1},
                {"overlayid": "85c0cdd4-95d0-4350-bd9d-729f326fe1d5", "sortorder": 2},
            ],
        )
        # Test anonymous user preference
        cls.user_preference = UserPreference.objects.create(
            userpreferenceid=cls.anonymous_preference_id,
            username=models.User.objects.get(username="anonymous"),
            preferencename="Anonymous test preference",
            appname="my app name",
            config=[{"value": "True"}],
        )

    def user_preference_json_data(self, username):
        user_pref = {
            "username": username,
            "preferencename": "test preference",
            "appname": "my arches app",
            "config": [
                {"overlayid": "7d0dffba-5bcf-4694-a5d7-3425ad97fa2b", "sortorder": 1},
                {"overlayid": "85c0cdd4-95d0-4350-bd9d-729f326fe1d5", "sortorder": 2},
            ],
        }
        return user_pref

    def test_detail_get_identifier(self):
        self.client.login(username="admin", password="admin")
        response = self.client.get(
            reverse(
                "api_user_preference_detail_view",
                kwargs={"identifier": self.admin_preference_id},
            ),
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertFalse(isinstance(response_json, list))

    def test_detail_get_identifier_no_permission(self):
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(
                reverse(
                    "api_user_preference_detail_view",
                    kwargs={"identifier": self.admin_preference_id},
                ),
            )
            self.assertEqual(response.status_code, 403)

    def test_detail_get_invalid_identifier(self):
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(
                reverse(
                    "api_user_preference_detail_view",
                    kwargs={"identifier": str(uuid.uuid4())},
                ),
            )
            self.assertEqual(response.status_code, 404)

    def test_detail_get_no_identifier(self):
        # Show that providing no identifier returns the listView
        self.client.login(username="admin", password="admin")
        response = self.client.get(
            reverse("api_user_preference_detail_view", kwargs={"identifier": ""}),
        )
        response_json = json.loads(response.content)
        self.assertTrue(isinstance(response_json, list))

    def test_list_get(self):
        # Tests the anonymous user gets only the one user preference in the db
        response = self.client.get(
            reverse("api_user_preference_list_view"),
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertTrue(isinstance(response_json, list))
        self.assertTrue(len(response_json) == 1)

    def test_list_get_administrator_response(self):
        # Tests admin users can see all user preferences, not just their users
        self.client.login(username="admin", password="admin")
        response = self.client.get(
            reverse("api_user_preference_list_view"),
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertIsInstance(response_json, list)
        self.assertEqual(len(response_json), 2)

    def test_list_get_with_identifer(self):
        with self.assertRaises(NoReverseMatch):
            response = self.client.get(
                reverse(
                    "api_user_preference_list_view",
                    kwargs={"identifier": str(uuid.uuid4())},
                ),
            )

    def test_delete_valid(self):
        self.client.login(username="admin", password="admin")
        response = self.client.delete(
            reverse(
                "api_user_preference_detail_view",
                kwargs={"identifier": self.admin_preference_id},
            ),
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_unauthorised_user(self):
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.delete(
                reverse(
                    "api_user_preference_detail_view",
                    kwargs={"identifier": self.admin_preference_id},
                ),
            )
            self.assertEqual(response.status_code, 403)

    def test_delete_with_no_identifier(self):
        self.client.login(username="admin", password="admin")
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.delete(
                reverse("api_user_preference_detail_view", kwargs={"identifier": ""}),
            )
            self.assertEqual(response.status_code, 405)

    def test_delete_invalid_identifier(self):
        self.client.login(username="admin", password="admin")
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.delete(
                reverse(
                    "api_user_preference_detail_view",
                    kwargs={"identifier": str(uuid.uuid4())},
                ),
            )
            self.assertEqual(response.status_code, 404)

    def test_post_valid(self):
        self.client.login(username="admin", password="admin")

        user_pref = self.user_preference_json_data("admin")
        response = self.client.post(
            reverse("api_user_preference_list_view"),
            data=user_pref,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        response_json = json.loads(response.content)
        self.assertIn("userpreferenceid", response_json.keys())

    def test_post_missing_fields(self):
        self.client.login(username="admin", password="admin")
        user_pref = self.user_preference_json_data("admin")
        del user_pref["username"]
        del user_pref["config"]
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(
                reverse("api_user_preference_list_view"),
                data=user_pref,
                content_type="application/json",
            )
            response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 400)

    def test_post_unauthorised_user(self):
        user_pref = self.user_preference_json_data("anonymous")
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(
                reverse("api_user_preference_list_view"),
                data=user_pref,
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 403)

    def test_post_invalid_user(self):
        self.client.login(username="admin", password="admin")
        user_pref = self.user_preference_json_data("fakeuser")
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(
                reverse("api_user_preference_list_view"),
                data=user_pref,
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)

    def test_post_with_userpreferenceid(self):
        self.client.login(username="admin", password="admin")
        user_pref = self.user_preference_json_data("admin")
        user_pref["userpreferenceid"] = str(uuid.uuid4())
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(
                reverse("api_user_preference_list_view"),
                data=user_pref,
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)
