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

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm
from arches.app.models.models import Node
from arches.app.models.resource import Resource
from arches.app.utils.permission_backend import user_can_read_resource
from arches.app.utils.permission_backend import user_has_resource_model_permissions
from arches.app.utils.permission_backend import get_restricted_users
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.permissions.permission_tests --settings="tests.test_settings"


class PermissionTests(ArchesTestCase):
    graph_fixtures = ["Data_Type_Model"]
    data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
    resource_instance_id = "f562c2fa-48d3-4798-a723-10209806c068"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_users()
        cls.expected_resource_count = 2
        cls.user = cls.test_users["ben"]
        cls.group = Group.objects.get(pk=2)
        cls.legacy_load_testing_package()
        cls.resource = Resource.objects.get(pk=cls.resource_instance_id)
        cls.resource.graph_id = cls.data_type_graphid
        cls.resource.remove_resource_instance_permissions()

    def test_user_cannot_view_without_permission(self):
        """
        Tests if a user is allowed to view a resource with implicit permissions and explicit permissions, but
        not without explicit permission if a permission other than 'view_resourceinstance' is assigned.
        """

        implicit_permission = user_can_read_resource(
            self.user, self.resource_instance_id
        )
        assign_perm("change_resourceinstance", self.group, self.resource)
        can_access_without_view_permission = user_can_read_resource(
            self.user, self.resource_instance_id
        )
        assign_perm("view_resourceinstance", self.group, self.resource)
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

        nodes = (
            Node.objects.filter(graph_id=self.resource.graph_id)
            .exclude(nodegroup__isnull=True)
            .select_related("nodegroup")
        )
        for node in nodes:
            assign_perm("no_access_to_nodegroup", self.group, node.nodegroup)
        hasperms = user_has_resource_model_permissions(
            self.user, ["models.read_nodegroup"], self.resource
        )
        self.assertFalse(hasperms)

    def test_get_restricted_users(self):
        """
        Tests that users are properly identified as restricted.
        """
        assign_perm("no_access_to_resourceinstance", self.group, self.resource)
        ben = self.user
        jim = self.test_users["jim"]
        sam = self.test_users["sam"]
        admin = self.test_users["admin"]
        assign_perm("view_resourceinstance", ben, self.resource)
        assign_perm("change_resourceinstance", jim, self.resource)

        restrictions = get_restricted_users(self.resource)

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
