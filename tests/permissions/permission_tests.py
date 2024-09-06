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
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm
from arches.app.models.models import GraphModel, ResourceInstance, Node
from arches.app.models.resource import Resource
from arches.app.utils.permission_backend import user_can_read_resource
from arches.app.utils.permission_backend import user_has_resource_model_permissions
from arches.app.utils.permission_backend import get_restricted_users

# these tests can be run from the command line via
# python manage.py test tests.permissions.permission_tests --settings="tests.test_settings"


class PermissionTests(ArchesTestCase):
    def setUp(self):
        self.expected_resource_count = 2
        self.data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
        self.resource_instance_id = "f562c2fa-48d3-4798-a723-10209806c068"
        self.user = User.objects.get(username="ben")
        self.group = Group.objects.get(pk=2)
        resource = Resource.objects.get(pk=self.resource_instance_id)
        resource.graph_id = self.data_type_graphid
        resource.remove_resource_instance_permissions()

    @classmethod
    def add_users(cls):
        profiles = (
            {
                "name": "ben",
                "email": "ben@test.com",
                "password": "Test12345!",
                "groups": ["Graph Editor", "Resource Editor"],
            },
            {
                "name": "sam",
                "email": "sam@test.com",
                "password": "Test12345!",
                "groups": ["Graph Editor", "Resource Editor", "Resource Reviewer"],
            },
            {
                "name": "jim",
                "email": "jim@test.com",
                "password": "Test12345!",
                "groups": ["Graph Editor", "Resource Editor"],
            },
        )

        for profile in profiles:
            try:
                user = User.objects.create_user(
                    username=profile["name"],
                    email=profile["email"],
                    password=profile["password"],
                )
                user.save()

                for group_name in profile["groups"]:
                    group = Group.objects.get(name=group_name)
                    group.user_set.add(user)

            except Exception as e:
                print(e)

    @classmethod
    def setUpClass(cls):
        cls.data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
        if not GraphModel.objects.filter(pk=cls.data_type_graphid).exists():
            # TODO: Fix this to run inside transaction, i.e. after super().setUpClass()
            # https://github.com/archesproject/arches/issues/10719
            test_pkg_path = os.path.join(
                test_settings.TEST_ROOT, "fixtures", "testing_prj", "testing_prj", "pkg"
            )
            with captured_stdout():
                management.call_command(
                    "packages",
                    operation="load_package",
                    source=test_pkg_path,
                    yes=True,
                    verbosity=0,
                )

        super().setUpClass()
        cls.add_users()

    def test_user_cannot_view_without_permission(self):
        """
        Tests if a user is allowed to view a resource with implicit permissions and explicit permissions, but
        not without explicit permission if a permission other than 'view_resourceinstance' is assigned.
        """

        implicit_permission = user_can_read_resource(
            self.user, self.resource_instance_id
        )
        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        assign_perm("change_resourceinstance", self.group, resource)
        can_access_without_view_permission = user_can_read_resource(
            self.user, self.resource_instance_id
        )
        assign_perm("view_resourceinstance", self.group, resource)
        can_access_with_view_permission = user_can_read_resource(
            self.user, self.resource_instance_id
        )
        self.assertTrue(implicit_permission)
        self.assertFalse(can_access_without_view_permission)
        self.assertTrue(can_access_with_view_permission)

    def test_user_has_resource_model_permissions(self):
        """
        Tests that a user cannot access an instance if they have no access to any nodegroup.

        """

        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        nodes = (
            Node.objects.filter(graph_id=resource.graph_id)
            .exclude(nodegroup__isnull=True)
            .select_related("nodegroup")
        )
        for node in nodes:
            assign_perm("no_access_to_nodegroup", self.group, node.nodegroup)
        hasperms = user_has_resource_model_permissions(
            self.user, ["models.read_nodegroup"], resource
        )
        self.assertFalse(hasperms)

    def test_get_restricted_users(self):
        """
        Tests that users are properly identified as restricted.
        """

        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        assign_perm("no_access_to_resourceinstance", self.group, resource)
        ben = self.user
        jim = User.objects.get(username="jim")
        sam = User.objects.get(username="sam")
        admin = User.objects.get(username="admin")
        assign_perm("view_resourceinstance", ben, resource)
        assign_perm("change_resourceinstance", jim, resource)

        restrictions = get_restricted_users(resource)

        results = [
            ("jim", "cannot_read", jim.id in restrictions["cannot_read"]),
            ("ben", "cannot_write", ben.id in restrictions["cannot_write"]),
            ("sam", "cannot_delete", sam.id in restrictions["cannot_delete"]),
            ("sam", "no_access", sam.id in restrictions["no_access"]),
            (
                "admin",
                "not in cannot_read",
                admin.id not in restrictions["cannot_read"],
            ),
            (
                "admin",
                "not in cannot_write",
                admin.id not in restrictions["cannot_write"],
            ),
            (
                "admin",
                "not in cannot_delete",
                admin.id not in restrictions["cannot_delete"],
            ),
            ("admin", "not in no_access", admin.id not in restrictions["no_access"]),
        ]

        for result in results:
            with self.subTest(user=result[0], restriction=result[1]):
                self.assertTrue(result[2])
