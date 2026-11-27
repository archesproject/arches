from http import HTTPStatus

from django.contrib.auth.models import Group, Permission, User
from django.urls import reverse

from arches.app.utils.permission_backend import user_is_resource_editor
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.permissions.role_permission_tests --settings="tests.test_settings"


class ResourceEditorRoleTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.editor = User.objects.create(username="role_editor")
        cls.editor.groups.add(Group.objects.get(name="Resource Editor"))

        cls.guest = User.objects.create(username="role_guest")
        cls.guest.groups.add(Group.objects.get(name="Guest"))

        cls.superuser = User.objects.create(username="role_super", is_superuser=True)

        custom_group = Group.objects.create(name="Custom Editors")
        custom_group.permissions.add(
            Permission.objects.get(
                codename="edit_resources", content_type__app_label="models"
            )
        )
        cls.custom_editor = User.objects.create(username="role_custom")
        cls.custom_editor.groups.add(custom_group)

    def test_user_is_resource_editor(self):
        self.assertTrue(user_is_resource_editor(self.editor))
        self.assertTrue(user_is_resource_editor(self.superuser))
        self.assertTrue(user_is_resource_editor(self.custom_editor))
        self.assertFalse(user_is_resource_editor(self.guest))

    def test_editor_endpoint_follows_permission(self):
        url = reverse("etl_manager")
        for user, expected in [
            (self.editor, HTTPStatus.OK),
            (self.custom_editor, HTTPStatus.OK),
            (self.superuser, HTTPStatus.OK),
            (self.guest, HTTPStatus.FORBIDDEN),
        ]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(url, QUERY_STRING="action=loadEvent")
                self.assertEqual(response.status_code, expected)
