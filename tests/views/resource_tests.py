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

from unittest.mock import MagicMock, patch
from arches.app.views.resource import ResourcePermissionDataView
from tests.base_test import ArchesTestCase
from django.urls import reverse
from arches.app.models.models import EditLog, ResourceInstance
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from tests.utils.search_test_utils import sync_es
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from guardian.shortcuts import (
    assign_perm,
    get_perms,
)

from tests.utils.permission_test_utils import add_users

# these tests can be run from the command line via
# python manage.py test tests.views.resource_tests --settings="tests.test_settings"


class CommandLineTests(ArchesTestCase):
    graph_fixtures = ["Data_Type_Model", "4564-referenced", "4564-person"]
    data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
    resource_instance_id = "f562c2fa-48d3-4798-a723-10209806c068"
    reference_graphid = "e3d4505e-bfa7-11e9-b4dc-0242ac160002"
    reference_nodeid = "fc3c8080-bfa7-11e9-b4dc-0242ac160002"
    person_graphid = "0c6269e8-bfa8-11e9-bd39-0242ac160002"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        add_users()
        cls.legacy_load_testing_package()
        cls.expected_resource_count = 2
        user = User.objects.get(username="ben")
        edit_records = EditLog.objects.filter(
            resourceinstanceid=cls.resource_instance_id
        ).filter(edittype="create")
        for edit in edit_records:
            edit.userid = user.id
            edit.save()

    def test_resource_instance_permission_assignment(self):
        """
        Test that we can assign resource instance permissions

        """
        self.client.login(username="ben", password="Test12345!")

        payload = {
            "selectedIdentities": [
                {
                    "type": "group",
                    "id": 2,
                    "selectedPermissions": [
                        {"codename": "change_resourceinstance"},
                        {"codename": "delete_resourceinstance"},
                    ],
                }
            ],
            "selectedInstances": [{"resourceinstanceid": self.resource_instance_id}],
        }

        url = reverse("resource_permission_data")
        post_data = JSONSerializer().serialize(payload)
        content_type = "application/x-www-form-urlencoded"
        self.client.post(url, post_data, content_type)
        group = Group.objects.get(pk=payload["selectedIdentities"][0]["id"])
        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        assigned_perms = get_perms(group, resource)
        self.assertTrue(
            "change_resourceinstance" in assigned_perms
            and "delete_resourceinstance" in assigned_perms
        )

    def test_resource_instance_permission_deletion(self):
        """
        Test that we can delete resource instance permissions

        """
        self.client.login(username="ben", password="Test12345!")

        payload = {
            "selectedIdentities": [
                {
                    "type": "group",
                    "id": 2,
                    "selectedPermissions": [
                        {"codename": "change_resourceinstance"},
                        {"codename": "delete_resourceinstance"},
                    ],
                }
            ],
            "selectedInstances": [{"resourceinstanceid": self.resource_instance_id}],
        }

        url = reverse("resource_permission_data")
        post_data = JSONSerializer().serialize(payload)
        content_type = "application/x-www-form-urlencoded"
        group = Group.objects.get(pk=payload["selectedIdentities"][0]["id"])
        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        assign_perm("delete_resourceinstance", group, resource)
        self.client.delete(url, post_data, content_type)
        assigned_perms = get_perms(group, resource)
        self.assertTrue(
            "change_resourceinstance" not in assigned_perms
            and "delete_resourceinstance" not in assigned_perms
        )

    def test_user_cannot_view_without_permission(self):
        """
        Test we cannot access the report without the 'view_resourceinstance' permission

        """
        self.client.login(username="ben", password="Test12345!")
        url = reverse(
            "resource_report", kwargs={"resourceid": self.resource_instance_id}
        )
        group = Group.objects.get(pk=2)
        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        assign_perm("change_resourceinstance", group, resource)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(url)
        self.assertTrue(response.status_code == 403)

    def test_user_cannot_edit_without_permission(self):
        """
        Test we cannot access the resource editor without the 'edit_resourceinstance' permission

        """
        self.client.login(username="ben", password="Test12345!")
        url = reverse(
            "resource_editor", kwargs={"resourceid": self.resource_instance_id}
        )
        group = Group.objects.get(pk=2)
        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        assign_perm("view_resourceinstance", group, resource)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(url)
        self.assertTrue(response.status_code == 403)

    def test_get_instance_permissions(self):
        default_permissions = MagicMock()
        group = Group.objects.get(name="Resource Exporter")
        default_permissions.PERMISSION_DEFAULTS = {
            "330802c5-95bd-11e8-b7ac-acde48001122": [
                {
                    "id": group.id,
                    "type": "group",
                    "permissions": ["view_resourceinstance"],
                },
            ]
        }

        with patch(
            "arches.app.permissions.arches_permission_base.settings",
            default_permissions,
        ):

            resource = ResourceInstance.objects.get(
                resourceinstanceid=self.resource_instance_id
            )

            rev = ResourcePermissionDataView()

            assign_perm("view_resourceinstance", group, resource)
            permissions = rev.get_instance_permissions(resource)
            group_dict = next(
                item for item in permissions["identities"] if item["id"] == group.id
            )

            self.assertGreater(len(group_dict["system_permissions"]), 0)

    def test_user_cannot_delete_without_permission(self):
        """
        Test we cannot delete an instance without the 'delete_resourceinstance' permission

        """
        self.client.login(username="ben", password="Test12345!")
        url = reverse(
            "resource_editor", kwargs={"resourceid": self.resource_instance_id}
        )
        group = Group.objects.get(pk=2)
        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        assign_perm("change_resourceinstance", group, resource)
        with self.assertLogs("django.request", level="ERROR"):
            response = self.client.delete(url)
        self.assertTrue(response.status_code == 500)

    def test_user_cannot_access_with_no_access(self):
        """
        Test we cannot read, edit, or delete an instance without the 'delete_resourceinstance' permission

        """
        self.client.login(username="ben", password="Test12345!")
        group = Group.objects.get(pk=2)
        user = User.objects.get(username="ben")
        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        view_url = reverse(
            "resource_report", kwargs={"resourceid": self.resource_instance_id}
        )
        edit_url = reverse(
            "resource_editor", kwargs={"resourceid": self.resource_instance_id}
        )
        assign_perm("view_resourceinstance", group, resource)
        assign_perm("change_resourceinstance", group, resource)
        assign_perm("delete_resourceinstance", group, resource)
        assign_perm("no_access_to_resourceinstance", user, resource)
        with self.assertLogs("django.request", level="WARNING"):
            view = self.client.get(view_url)
        with self.assertLogs("django.request", level="WARNING"):
            edit = self.client.get(edit_url)
        with self.assertLogs("django.request", level="ERROR"):
            delete = self.client.delete(edit_url)
        self.assertTrue(
            view.status_code == 403
            and edit.status_code == 403
            and delete.status_code == 500
        )

    def test_user_can_view_with_permission(self):
        """
        Test we can access a report with the 'view_resourceinstance' permission

        """
        self.client.login(username="sam", password="Test12345!")
        url = reverse(
            "resource_report", kwargs={"resourceid": self.resource_instance_id}
        )
        group = Group.objects.get(pk=2)
        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        assign_perm("view_resourceinstance", group, resource)
        response = self.client.get(url)
        self.assertTrue(response.status_code == 200)

    def test_user_can_edit_with_permission(self):
        """
        Test we can access the resource editor page with the 'edit_resourceinstance' permission

        """
        self.client.login(username="sam", password="Test12345!")
        url = reverse(
            "resource_editor", kwargs={"resourceid": self.resource_instance_id}
        )
        group = Group.objects.get(pk=2)
        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        assign_perm("change_resourceinstance", group, resource)
        response = self.client.get(url)
        self.assertTrue(response.status_code == 200)

    def test_user_can_delete_with_permission(self):
        """
        Test we can delete an instance with the 'delete_resourceinstance' permission

        """
        self.client.login(username="sam", password="Test12345!")
        url = reverse(
            "resource_editor", kwargs={"resourceid": self.resource_instance_id}
        )
        group = Group.objects.get(pk=2)
        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        assign_perm("delete_resourceinstance", group, resource)
        response = self.client.delete(url)
        self.assertTrue(response.status_code == 200)

    def test_crud_allowed_if_no_explicit_permissions(self):
        """
        Test a user can access the report and editor of a resource and delete an instance if no explict permissions are
        assigned to the group

        """
        self.client.login(username="sam", password="Test12345!")
        view_url = reverse(
            "resource_report", kwargs={"resourceid": self.resource_instance_id}
        )
        edit_url = reverse(
            "resource_editor", kwargs={"resourceid": self.resource_instance_id}
        )
        view = self.client.get(view_url)
        edit = self.client.get(edit_url)
        delete = self.client.delete(edit_url)
        self.assertEqual(view.status_code, 200)
        self.assertEqual(edit.status_code, 200)
        self.assertEqual(delete.status_code, 200)

    def test_get_related_resource(self):
        se = SearchEngineFactory().create()
        user = User.objects.get(username="admin")
        is_related_to_valueid = "ac41d9be-79db-4256-b368-2f4559cfbe55"
        en_preflabel = "is related to"
        person_resourceid = "b6754e7a-7f18-40d1-93fe-61763d37d55e"
        person_resource = Resource(
            graph_id=self.person_graphid, resourceinstanceid=person_resourceid
        )
        person_resource.save()

        reference_resourceid = "380b8364-50e6-4f5b-af08-0ea3ab56a406"
        reference_resource = Resource(
            graph_id=self.reference_graphid, resourceinstanceid=reference_resourceid
        )
        reference_resource.save()
        reference_tile = Tile.get_blank_tile(
            self.reference_nodeid, reference_resourceid
        )
        reference_tile.data[self.reference_nodeid] = [
            {
                "resourceName": "",
                "ontologyProperty": is_related_to_valueid,
                "inverseOntologyProperty": is_related_to_valueid,
                "resourceId": person_resourceid,
            }
        ]
        reference_tile.save()
        sync_es(se)
        ret = reference_resource.get_related_resources(user=user)
        relationship = ret["resource_relationships"][0]["relationshiptype_label"]
        self.assertEqual(relationship, en_preflabel)

    def test_resource_report_good(self):
        self.client.login(username="admin", password="admin")
        url = reverse(
            "resource_report", kwargs={"resourceid": self.resource_instance_id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_resource_report_for_missing_resource(self):
        self.client.login(username="admin", password="admin")
        resource = Resource.objects.get(resourceinstanceid=self.resource_instance_id)
        resource.delete()
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(
                reverse(
                    "resource_report", kwargs={"resourceid": self.resource_instance_id}
                )
            )
        self.assertEqual(response.status_code, 404)
