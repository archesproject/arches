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

import os
from tests import test_settings
from tests.base_test import ArchesTestCase
from django.core import management
from django.test.utils import captured_stdout
from django.urls import reverse
from arches.app.models.models import GraphModel, ResourceInstance, EditLog
from django.test.client import RequestFactory, Client
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm, get_perms, remove_perm, get_group_perms, get_user_perms

# these tests can be run from the command line via
# python manage.py test tests.views.resource_tests --settings="tests.test_settings"


def add_users():
    profiles = (
        {"name": "ben", "email": "ben@test.com", "password": "Test12345!", "groups": ["Graph Editor", "Resource Editor"]},
        {
            "name": "sam",
            "email": "sam@test.com",
            "password": "Test12345!",
            "groups": ["Graph Editor", "Resource Editor", "Resource Reviewer"],
        },
        # {'name': 'jim', 'email': 'jim@test.com', 'password': 'Test12345!', 'groups': ['Graph Editor', 'Resource Editor']},
    )

    for profile in profiles:
        user = User.objects.create_user(username=profile["name"], email=profile["email"], password=profile["password"])

        for group_name in profile["groups"]:
            group = Group.objects.get(name=group_name)
            group.user_set.add(user)


class CommandLineTests(ArchesTestCase):
    def setUp(self):
        self.expected_resource_count = 2
        self.client = Client()
        user = User.objects.get(username="ben")
        edit_records = EditLog.objects.filter(resourceinstanceid=self.resource_instance_id).filter(edittype="create")
        for edit in edit_records:
            edit.userid = user.id
            edit.save()

    def tearDown(self):
        ResourceInstance.objects.filter(graph_id=self.data_type_graphid).delete()
        EditLog.objects.filter(resourceinstanceid=self.resource_instance_id).filter(edittype="create").delete()

    @classmethod
    def setUpClass(cls):
        cls.data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
        cls.resource_instance_id = "f562c2fa-48d3-4798-a723-10209806c068"

        if not GraphModel.objects.filter(pk=cls.data_type_graphid).exists():
            # TODO: Fix this to run inside transaction, i.e. after super().setUpClass()
            # https://github.com/archesproject/arches/issues/10719
            test_pkg_path = os.path.join(test_settings.TEST_ROOT, "fixtures", "testing_prj", "testing_prj", "pkg")
            with captured_stdout():
                management.call_command("packages", operation="load_package", source=test_pkg_path, yes=True, verbosity=0)

        super().setUpClass()
        add_users()

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
                    "selectedPermissions": [{"codename": "change_resourceinstance"}, {"codename": "delete_resourceinstance"}],
                }
            ],
            "selectedInstances": [{"resourceinstanceid": self.resource_instance_id}],
        }

        url = reverse("resource_permission_data")
        post_data = JSONSerializer().serialize(payload)
        content_type = "application/x-www-form-urlencoded"
        self.client.post(url, post_data, content_type)
        group = Group.objects.get(pk=payload["selectedIdentities"][0]["id"])
        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        assigned_perms = get_perms(group, resource)
        self.assertTrue("change_resourceinstance" in assigned_perms and "delete_resourceinstance" in assigned_perms)

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
                    "selectedPermissions": [{"codename": "change_resourceinstance"}, {"codename": "delete_resourceinstance"}],
                }
            ],
            "selectedInstances": [{"resourceinstanceid": self.resource_instance_id}],
        }

        url = reverse("resource_permission_data")
        post_data = JSONSerializer().serialize(payload)
        content_type = "application/x-www-form-urlencoded"
        group = Group.objects.get(pk=payload["selectedIdentities"][0]["id"])
        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        assign_perm("delete_resourceinstance", group, resource)
        self.client.delete(url, post_data, content_type)
        assigned_perms = get_perms(group, resource)
        self.assertTrue("change_resourceinstance" not in assigned_perms and "delete_resourceinstance" not in assigned_perms)

    def test_user_cannot_view_without_permission(self):
        """
        Test we cannot access the report without the 'view_resourceinstance' permission

        """
        self.client.login(username="ben", password="Test12345!")
        url = reverse("resource_report", kwargs={"resourceid": self.resource_instance_id})
        group = Group.objects.get(pk=2)
        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        assign_perm("change_resourceinstance", group, resource)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(url)
        self.assertTrue(response.status_code == 403)

    def test_user_cannot_edit_without_permission(self):
        """
        Test we cannot access the resource editor without the 'edit_resourceinstance' permission

        """
        self.client.login(username="ben", password="Test12345!")
        url = reverse("resource_editor", kwargs={"resourceid": self.resource_instance_id})
        group = Group.objects.get(pk=2)
        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        assign_perm("view_resourceinstance", group, resource)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(url)
        self.assertTrue(response.status_code == 403)

    def test_user_cannot_delete_without_permission(self):
        """
        Test we cannot delete an instance without the 'delete_resourceinstance' permission

        """
        self.client.login(username="ben", password="Test12345!")
        url = reverse("resource_editor", kwargs={"resourceid": self.resource_instance_id})
        group = Group.objects.get(pk=2)
        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
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
        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        view_url = reverse("resource_report", kwargs={"resourceid": self.resource_instance_id})
        edit_url = reverse("resource_editor", kwargs={"resourceid": self.resource_instance_id})
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
        self.assertTrue(view.status_code == 403 and edit.status_code == 403 and delete.status_code == 500)

    def test_user_can_view_with_permission(self):
        """
        Test we can access a report with the 'view_resourceinstance' permission

        """
        self.client.login(username="sam", password="Test12345!")
        url = reverse("resource_report", kwargs={"resourceid": self.resource_instance_id})
        group = Group.objects.get(pk=2)
        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        assign_perm("view_resourceinstance", group, resource)
        response = self.client.get(url)
        self.assertTrue(response.status_code == 200)

    def test_user_can_edit_with_permission(self):
        """
        Test we can access the resource editor page with the 'edit_resourceinstance' permission

        """
        self.client.login(username="sam", password="Test12345!")
        url = reverse("resource_editor", kwargs={"resourceid": self.resource_instance_id})
        group = Group.objects.get(pk=2)
        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        assign_perm("change_resourceinstance", group, resource)
        response = self.client.get(url)
        self.assertTrue(response.status_code == 200)

    def test_user_can_delete_with_permission(self):
        """
        Test we can delete an instance with the 'delete_resourceinstance' permission

        """
        self.client.login(username="sam", password="Test12345!")
        url = reverse("resource_editor", kwargs={"resourceid": self.resource_instance_id})
        group = Group.objects.get(pk=2)
        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        assign_perm("delete_resourceinstance", group, resource)
        response = self.client.delete(url)
        self.assertTrue(response.status_code == 200)

    def test_crud_allowed_if_no_explicit_permissions(self):
        """
        Test a user can access the report and editor of a resource and delete an instance if no explict permissions are
        assigned to the group

        """
        self.client.login(username="sam", password="Test12345!")
        view_url = reverse("resource_report", kwargs={"resourceid": self.resource_instance_id})
        edit_url = reverse("resource_editor", kwargs={"resourceid": self.resource_instance_id})
        view = self.client.get(view_url)
        edit = self.client.get(edit_url)
        delete = self.client.delete(edit_url)
        self.assertTrue(view.status_code == 200 and edit.status_code == 200 and delete.status_code == 200)
