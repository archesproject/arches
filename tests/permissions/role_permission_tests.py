from http import HTTPStatus

from django.contrib.auth.models import Group, Permission, User
from django.urls import reverse

from arches.app.models.models import UserPreference
from arches.app.utils.permission_backend import (
    user_is_resource_editor,
    user_is_resource_exporter,
)
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


class ResourceExporterRoleTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.exporter = User.objects.create(username="role_exporter")
        cls.exporter.groups.add(Group.objects.get(name="Resource Exporter"))

        cls.guest = User.objects.create(username="role_guest")
        cls.guest.groups.add(Group.objects.get(name="Guest"))

        cls.superuser = User.objects.create(username="role_super", is_superuser=True)

        custom_group = Group.objects.create(name="Custom Exporters")
        custom_group.permissions.add(
            Permission.objects.get(
                codename="export_resources", content_type__app_label="models"
            )
        )
        cls.custom_exporter = User.objects.create(username="role_custom")
        cls.custom_exporter.groups.add(custom_group)

    def test_user_is_resource_exporter(self):
        self.assertTrue(user_is_resource_exporter(self.exporter))
        self.assertTrue(user_is_resource_exporter(self.superuser))
        self.assertTrue(user_is_resource_exporter(self.custom_exporter))
        self.assertFalse(user_is_resource_exporter(self.guest))

    def test_export_endpoint_refuses_without_permission(self):
        self.client.force_login(self.guest)
        response = self.client.get(reverse("export_results"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("auth"), response.url)


class ApplicationAdministratorRoleTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.app_admin = User.objects.create(username="role_app_admin")
        cls.app_admin.groups.add(Group.objects.get(name="Application Administrator"))

        cls.guest = User.objects.create(username="role_guest")
        cls.guest.groups.add(Group.objects.get(name="Guest"))

        cls.superuser = User.objects.create(username="role_super", is_superuser=True)

        custom_group = Group.objects.create(name="Custom App Admins")
        custom_group.permissions.add(
            Permission.objects.get(
                codename="manage_application", content_type__app_label="models"
            )
        )
        cls.custom_admin = User.objects.create(username="role_custom")
        cls.custom_admin.groups.add(custom_group)

        cls.other_preference = UserPreference.objects.create(
            username=User.objects.create(username="role_other"),
            preferencename="someone else's preference",
            config=[],
        )

    def test_all_users_preferences_follow_permission(self):
        url = reverse("api_user_preference_list_view")
        other_id = str(self.other_preference.userpreferenceid)
        for user, sees_others in [
            (self.app_admin, True),
            (self.custom_admin, True),
            (self.superuser, True),
            (self.guest, False),
        ]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(url)
                if sees_others:
                    self.assertContains(response, other_id)
                else:
                    self.assertNotContains(response, other_id)

    def test_admin_only_endpoint_follows_permission(self):
        url = reverse("api_user_preference_list_view")
        for user, allowed in [
            (self.app_admin, True),
            (self.custom_admin, True),
            (self.superuser, True),
            (self.guest, False),
        ]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.post(
                    url, data={}, content_type="application/json"
                )
                if allowed:
                    self.assertNotEqual(response.status_code, HTTPStatus.FORBIDDEN)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_map_layer_manager_redirects_without_permission(self):
        self.client.force_login(self.guest)
        response = self.client.get(reverse("map_layer_manager"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("auth"), response.url)


class GraphEditorRoleTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.graph_editor = User.objects.create(username="role_graph_editor")
        cls.graph_editor.groups.add(Group.objects.get(name="Graph Editor"))

        cls.guest = User.objects.create(username="role_guest")
        cls.guest.groups.add(Group.objects.get(name="Guest"))

        cls.superuser = User.objects.create(username="role_super", is_superuser=True)

        custom_group = Group.objects.create(name="Custom Graph Editors")
        custom_group.permissions.add(
            Permission.objects.get(
                codename="manage_graphs", content_type__app_label="models"
            )
        )
        cls.custom_editor = User.objects.create(username="role_custom")
        cls.custom_editor.groups.add(custom_group)

    def test_graph_manager_follows_permission(self):
        url = reverse("graph", kwargs={"graphid": ""})
        for user, expected in [
            (self.graph_editor, HTTPStatus.OK),
            (self.custom_editor, HTTPStatus.OK),
            (self.superuser, HTTPStatus.OK),
            (self.guest, HTTPStatus.FOUND),
        ]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected)
