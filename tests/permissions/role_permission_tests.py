from http import HTTPStatus

from django.contrib.auth.models import Group, Permission, User
from django.urls import reverse

from arches.app.models.graph import Graph
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
    user_is_resource_reviewer,
)
from arches.app.views.resource import ResourcePermissionDataView
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.permissions.role_permission_tests --settings="tests.test_settings"


def make_user(username, group_name, permission=None):
    """A user in group_name; given a permission, group_name is created holding only it."""
    if permission:
        group = Group.objects.create(name=group_name)
        group.permissions.add(
            Permission.objects.get(
                codename=permission, content_type__app_label="models"
            )
        )
    else:
        group = Group.objects.get(name=group_name)
    user = User.objects.create(username=username)
    user.groups.add(group)
    return user


class ResourceEditorRoleTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.editor = make_user("role_editor", "Resource Editor")

        cls.crowdsource_editor = make_user("role_crowdsource", "Crowdsource Editor")

        cls.guest = make_user("role_guest", "Guest")

        cls.superuser = User.objects.create(username="role_super", is_superuser=True)

        cls.custom_editor = make_user("role_custom", "Custom Editors", "edit_resources")

    def test_user_is_resource_editor(self):
        self.assertTrue(user_is_resource_editor(self.editor))
        self.assertTrue(user_is_resource_editor(self.crowdsource_editor))
        self.assertTrue(user_is_resource_editor(self.superuser))
        self.assertTrue(user_is_resource_editor(self.custom_editor))
        self.assertFalse(user_is_resource_editor(self.guest))

    def test_editor_endpoint_follows_permission(self):
        url = reverse("etl_manager")
        for user, expected in [
            (self.editor, HTTPStatus.OK),
            (self.crowdsource_editor, HTTPStatus.OK),
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
        cls.exporter = make_user("role_exporter", "Resource Exporter")

        cls.guest = make_user("role_guest", "Guest")

        cls.superuser = User.objects.create(username="role_super", is_superuser=True)

        cls.custom_exporter = make_user(
            "role_custom", "Custom Exporters", "export_resources"
        )

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
        cls.app_admin = make_user("role_app_admin", "Application Administrator")

        cls.guest = make_user("role_guest", "Guest")

        cls.superuser = User.objects.create(username="role_super", is_superuser=True)

        cls.custom_admin = make_user(
            "role_custom", "Custom App Admins", "manage_application"
        )

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
        cls.graph_editor = make_user("role_graph_editor", "Graph Editor")

        cls.guest = make_user("role_guest", "Guest")

        cls.superuser = User.objects.create(username="role_super", is_superuser=True)

        cls.custom_editor = make_user(
            "role_custom", "Custom Graph Editors", "manage_graphs"
        )

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
        cls.rdm_admin = make_user("role_rdm_admin", "RDM Administrator")

        cls.guest = make_user("role_guest", "Guest")

        cls.superuser = User.objects.create(username="role_super", is_superuser=True)

        cls.custom_admin = make_user("role_custom", "Custom RDM Admins", "manage_rdm")

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
        cls.sys_admin = make_user("role_sys_admin", "System Administrator")

        cls.guest = make_user("role_guest", "Guest")

        cls.custom_admin = make_user(
            "role_custom", "Custom System Admins", "edit_system_settings"
        )

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

    def test_system_settings_graph_designer_needs_permission(self):
        graph_editor = make_user("role_graph_only", "Graph Editor")
        url = reverse(
            "graph_designer",
            kwargs={"graphid": settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID},
        )
        self.client.force_login(graph_editor)
        self.assertEqual(self.client.get(url).status_code, HTTPStatus.FORBIDDEN)


class ResourceReviewerRoleTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.reviewer = make_user("role_reviewer", "Resource Reviewer")

        cls.guest = make_user("role_guest", "Guest")

        cls.superuser = User.objects.create(username="role_super", is_superuser=True)

        cls.custom_reviewer = make_user(
            "role_custom", "Custom Reviewers", "review_resources"
        )

        graph = Graph.objects.create_graph(
            name="ROLE_PERMISSIONS_TEST_GRAPH", is_resource=False
        )
        graph.isresource = True
        graph.resource_instance_lifecycle_id = (
            settings.DEFAULT_RESOURCE_INSTANCE_LIFECYCLE_ID
        )
        graph.save(validate=False)
        cls.resource = ResourceInstance.objects.create(graph=graph)

    def test_user_is_resource_reviewer(self):
        self.assertTrue(user_is_resource_reviewer(self.reviewer))
        self.assertTrue(user_is_resource_reviewer(self.superuser))
        self.assertTrue(user_is_resource_reviewer(self.custom_reviewer))
        self.assertFalse(user_is_resource_reviewer(self.guest))

    def test_permissions_panel_flags_follow_permission(self):
        permissions = ResourcePermissionDataView().get_instance_permissions(
            self.resource
        )
        flags = {
            (identity["type"], identity["name"]): identity["is_editor_or_reviewer"]
            for identity in permissions["identities"]
        }
        self.assertTrue(flags[("user", "role_custom")])
        self.assertTrue(flags[("group", "Custom Reviewers")])
        self.assertTrue(flags[("group", "Resource Editor")])
        self.assertFalse(flags[("user", "role_guest")])
        self.assertFalse(flags[("group", "Guest")])
