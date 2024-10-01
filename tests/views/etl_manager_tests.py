from http import HTTPStatus

from django.contrib.auth.models import Group, User
from django.urls import reverse

from arches.app.models.models import ETLModule, LoadEvent
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.views.etl_manager_tests --settings="tests.test_settings"


class ETLManagerTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        resource_editor_group = Group.objects.get(name="Resource Editor")
        cls.admin = User.objects.get(username="admin")
        cls.anonymous = User.objects.get(username="anonymous")
        cls.full_name_user = User.objects.create(first_name="Full", last_name="Name")
        cls.full_name_user.groups.add(resource_editor_group)
        cls.csv_module = ETLModule.objects.get(name="Import Single CSV")
        cls.admin_load_event = LoadEvent(user=cls.admin, etl_module=cls.csv_module)
        cls.admin_load_event.save()
        cls.full_name_load_event = LoadEvent(
            user=cls.full_name_user, etl_module=cls.csv_module
        )
        cls.full_name_load_event.save()

    def test_user_model_not_serialized_on_load_event(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("etl_manager"), QUERY_STRING="action=loadEvent"
        )
        self.assertNotContains(response, "password")
        self.assertContains(response, '"user_displayname": "admin"')

    def test_user_displayname_formatting(self):
        self.client.force_login(self.full_name_user)
        response = self.client.get(
            reverse("etl_manager"), QUERY_STRING="action=loadEvent"
        )
        self.assertContains(response, '"user_displayname": "Full Name"')

    def test_insufficent_permissions(self):
        self.client.force_login(self.anonymous)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(reverse("etl_manager"))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
