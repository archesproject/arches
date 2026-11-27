from http import HTTPStatus

from django.contrib.auth.models import Group, Permission, User
from django.urls import reverse

from arches.app.models.models import ResourceInstance, UserPreference
from arches.app.models.system_settings import settings
from arches.app.permissions.arches_default_allow import (
    ArchesDefaultAllowPermissionFramework,
)
from arches.app.permissions.arches_default_deny import (
    ArchesDefaultDenyPermissionFramework,
)
from arches.app.utils.permission_backend import (
    user_can_read_concepts,
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


class RDMAdministratorRoleTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.rdm_admin = User.objects.create(username="role_rdm_admin")
        cls.rdm_admin.groups.add(Group.objects.get(name="RDM Administrator"))

        cls.guest = User.objects.create(username="role_guest")
        cls.guest.groups.add(Group.objects.get(name="Guest"))

        cls.superuser = User.objects.create(username="role_super", is_superuser=True)

        custom_group = Group.objects.create(name="Custom RDM Admins")
        custom_group.permissions.add(
            Permission.objects.get(
                codename="manage_rdm", content_type__app_label="models"
            )
        )
        cls.custom_admin = User.objects.create(username="role_custom")
        cls.custom_admin.groups.add(custom_group)

    def test_user_can_read_concepts(self):
        self.assertTrue(user_can_read_concepts(self.rdm_admin))
        self.assertTrue(user_can_read_concepts(self.superuser))
        self.assertTrue(user_can_read_concepts(self.custom_admin))
        self.assertFalse(user_can_read_concepts(self.guest))

    def test_rdm_redirects_without_permission(self):
        self.client.force_login(self.guest)
        response = self.client.get(reverse("rdm", kwargs={"conceptid": ""}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("auth"), response.url)


class SystemAdministratorRoleTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.sys_admin = User.objects.create(username="role_sys_admin")
        cls.sys_admin.groups.add(Group.objects.get(name="System Administrator"))

        cls.guest = User.objects.create(username="role_guest")
        cls.guest.groups.add(Group.objects.get(name="Guest"))

        custom_group = Group.objects.create(name="Custom System Admins")
        custom_group.permissions.add(
            Permission.objects.get(
                codename="edit_system_settings", content_type__app_label="models"
            )
        )
        cls.custom_admin = User.objects.create(username="role_custom")
        cls.custom_admin.groups.add(custom_group)

    def test_system_settings_resource_refused_without_permission(self):
        # An unsaved instance: the test DB has no system settings resource, and a
        # missing one makes the allow framework permit before this check runs.
        resource = ResourceInstance(pk=settings.SYSTEM_SETTINGS_RESOURCE_ID)
        for framework in (
            ArchesDefaultAllowPermissionFramework(),
            ArchesDefaultDenyPermissionFramework(),
        ):
            for user, refused in [
                (self.sys_admin, False),
                (self.custom_admin, False),
                (self.guest, True),
            ]:
                with self.subTest(
                    framework=type(framework).__name__, user=user.username
                ):
                    result = framework.check_resource_instance_permissions(
                        user, None, "change_resourceinstance", resource=resource
                    )
                    if refused:
                        self.assertIs(result["permitted"], False)
                    else:
                        self.assertIsNot(result["permitted"], False)
