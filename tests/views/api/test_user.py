from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

# these tests can be run from the command line via
# python manage.py test tests.views.api.test_user --settings="tests.test_settings"


class UserAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.visitor = User.objects.create(
            username="visitor",
            first_name="Esperanza",
            last_name="Spalding",
        )
        cls.visitor.set_password("jazz")
        cls.visitor.save()

    def test_logged_in_user(self):
        self.client.force_login(self.visitor)
        response = self.client.get(reverse("api_user"))
        self.assertContains(
            response,
            '{"first_name": "Esperanza", "last_name": "Spalding", "username": "visitor"}',
            status_code=HTTPStatus.OK,
        )
        self.assertNotContains(response, "password")

    def test_anonymous_user(self):
        response = self.client.get(reverse("api_user"))
        self.assertContains(
            response,
            '{"first_name": "", "last_name": "", "username": "anonymous"}',
            status_code=HTTPStatus.OK,
        )
        self.assertNotContains(response, "password")

    def test_inactive_user(self):
        self.visitor.is_active = False
        self.visitor.save()

        self.client.force_login(self.visitor)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(reverse("api_user"))
        self.assertContains(
            response,
            "This account is no longer active.",
            status_code=HTTPStatus.FORBIDDEN,
        )
