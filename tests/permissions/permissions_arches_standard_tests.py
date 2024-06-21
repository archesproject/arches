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

from unittest import mock
from tests.permissions.base_permissions_framework_test import (
    ArchesPermissionFrameworkTestCase,
)
from django.contrib.auth.models import User
from arches.app.models.models import ResourceInstance, Node
from arches.app.permissions.arches_standard import ArchesStandardPermissionFramework

# these tests can be run from the command line via
# python manage.py test tests.permissions.permission_tests --settings="tests.test_settings"


class ArchesStandardPermissionTests(ArchesPermissionFrameworkTestCase):
    FRAMEWORK = ArchesStandardPermissionFramework

    def test_user_cannot_view_without_permission(self):
        """
        Tests if a user is allowed to view a resource with implicit permissions and explicit permissions, but
        not without explicit permission if a permission other than 'view_resourceinstance' is assigned.
        """

        implicit_permission = self.framework.user_can_read_resource(
            self.user, self.resource_instance_id
        )
        resource = ResourceInstance.objects.get(
            resourceinstanceid=self.resource_instance_id
        )
        self.framework.assign_perm("change_resourceinstance", self.group, resource)
        can_access_without_view_permission = self.framework.user_can_read_resource(
            self.user, self.resource_instance_id
        )
        self.framework.assign_perm("view_resourceinstance", self.group, resource)
        can_access_with_view_permission = self.framework.user_can_read_resource(
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
        nodes = Node.objects.filter(graph_id=resource.graph_id)
        for node in nodes:
            if node.nodegroup:
                self.framework.assign_perm(
                    "no_access_to_nodegroup", self.group, node.nodegroup
                )
        hasperms = self.framework.user_has_resource_model_permissions(
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
        self.framework.assign_perm(
            "no_access_to_resourceinstance", self.group, resource
        )
        ben = self.user
        jim = User.objects.get(username="jim")
        sam = User.objects.get(username="sam")
        admin = User.objects.get(username="admin")
        self.framework.assign_perm("view_resourceinstance", ben, resource)
        self.framework.assign_perm("change_resourceinstance", jim, resource)

        restrictions = self.framework.get_restricted_users(resource)

        results = [
            jim.id in restrictions["cannot_read"],
            ben.id in restrictions["cannot_write"],
            sam.id in restrictions["cannot_delete"],
            sam.id in restrictions["no_access"],
            admin.id not in restrictions["cannot_read"],
            admin.id not in restrictions["cannot_write"],
            admin.id not in restrictions["cannot_delete"],
            admin.id not in restrictions["no_access"],
        ]

        for result in results:
            with self.subTest(result=result):
                self.assertTrue(result)

    @mock.patch("django.contrib.auth.models.User")
    def test_permission_search_filter(self, mock_User):
        mock_User.id = 12
        filter = self.framework.get_permission_search_filter(mock_User)
        filter_text = str(filter.dsl)
        self.assertIn("permissions.users_with_no_access", filter_text)
        self.assertIn(str(mock_User.id), filter_text)

    # @mock.patch()
    # @mock.patch("arches.app.models.models.ResourceInstance")
    # def test_permission(self, mock_resourceinstance):
    #     values = self.framework.get_index_values(mock_resourceinstance)
    #     print(values)
