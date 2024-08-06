from http import HTTPStatus

from django.contrib.auth.models import User
from django.test.utils import override_settings
from django.urls import reverse

from tests.base_test import ArchesTestCase, sync_overridden_test_settings_to_arches

# these tests can be run from the command line via
# python manage.py test tests.views.api.test_auth --settings="tests.test_settings"


class AuthAPITests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.visitor = User.objects.create(
            username="visitor",
            first_name="Esperanza",
            last_name="Spalding",
        )
        cls.visitor.set_password("jazz")
        cls.visitor.save()

    def test_login_success(self):
        response = self.client.post(
            reverse("api_login"),
            {"username": "visitor", "password": "jazz"},
            content_type="application/json",
        )
        self.assertContains(
            response,
            '{"first_name": "Esperanza", "last_name": "Spalding", "username": "visitor"}',
            status_code=HTTPStatus.OK,
        )
        self.assertNotContains(response, "password")

    @override_settings(FORCE_TWO_FACTOR_AUTHENTICATION=True)
    def test_login_rejected_two_factor_enabled(self):
        with (
            sync_overridden_test_settings_to_arches(),
            self.assertLogs("django.request", level="WARNING"),
        ):
            response = self.client.post(
                reverse("api_login"),
                {"username": "visitor", "password": "jazz"},
                content_type="application/json",
            )
        self.assertContains(
            response,
            "Two-factor authentication required.",
            status_code=HTTPStatus.UNAUTHORIZED,
        )

    def test_login_failure_missing_credentials(self):
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(
                reverse("api_login"), {}, content_type="application/json"
            )
        self.assertContains(
            response,
            "Invalid username and/or password.",
            status_code=HTTPStatus.UNAUTHORIZED,
        )

    def test_login_failure_wrong_credentials(self):
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(
                reverse("api_login"),
                {"username": "visitor", "password": "garbage"},
                content_type="application/json",
            )
        self.assertContains(
            response,
            "Invalid username and/or password.",
            status_code=HTTPStatus.UNAUTHORIZED,
        )

    def test_login_failure_inactive_user(self):
        self.visitor.is_active = False
        self.visitor.save()
        with (
            self.modify_settings(
                AUTHENTICATION_BACKENDS={
                    "prepend": "django.contrib.auth.backends.AllowAllUsersModelBackend"
                }
            ),
            self.assertLogs("django.request", level="WARNING"),
        ):
            response = self.client.post(
                reverse("api_login"),
                {"username": "visitor", "password": "jazz"},
                content_type="application/json",
            )
        self.assertContains(
            response,
            "This account is no longer active.",
            status_code=HTTPStatus.FORBIDDEN,
        )

    def test_login_get_not_allowed(self):
        with self.assertLogs("django.request", level="WARNING"):
            self.client.get(
                reverse("api_login"), status_code=HTTPStatus.METHOD_NOT_ALLOWED
            )

    def test_logout(self):
        self.client.force_login(self.visitor)
        response = self.client.post(reverse("api_logout"))
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertEqual(response.wsgi_request.user.username, "")
