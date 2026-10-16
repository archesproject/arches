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
from arches.app.models.models import Node, NodeGroup
from arches.app.models.resource import Resource
from arches.app.search.components.resource_type_filter import get_permitted_graphids
from arches.app.utils.permission_backend import user_can_read_resource
from arches.app.utils.permission_backend import user_has_resource_model_permissions
from arches.app.utils.permission_backend import get_restricted_users
from arches.app.utils.permission_backend import get_nodegroups_by_perm

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

    def test_get_permitted_graphids(self):
        """
        Tests if a user has access to a resource model based on nodegroup access

        """

        nodegroups = NodeGroup.objects.filter(
            node__graph_id=self.data_type_graphid
        ).distinct()
        permitted_nodegroups = get_nodegroups_by_perm(
            self.user, "models.read_nodegroup"
        )
        graphids = get_permitted_graphids(permitted_nodegroups)
        with self.subTest(graphids):
            self.assertTrue(self.data_type_graphid in graphids)

        for nodegroup in nodegroups:
            assign_perm("no_access_to_nodegroup", self.user, nodegroup)

        permitted_nodegroups = get_nodegroups_by_perm(
            self.user, "models.read_nodegroup"
        )
        graphids = get_permitted_graphids(permitted_nodegroups)
        with self.subTest(graphids):
            self.assertTrue(self.data_type_graphid not in graphids)

    def test_nodegroups_by_perm(self):
        # In this first case, user 'ben' has implicit read access to all nodegroups
        nodegroup_set = get_nodegroups_by_perm(self.user, "models.read_nodegroup")
        self.assertTrue(nodegroup_set)

        # For the case of edit and delete, access should succeed because implicitly users have all read, write, and delete
        nodegroup_set = get_nodegroups_by_perm(self.user, "models.delete_nodegroup")
        self.assertTrue(nodegroup_set)
        nodegroup_set = get_nodegroups_by_perm(self.user, "models.write_nodegroup")
        self.assertTrue(nodegroup_set)

        # If multiple perms, if any_perm is true, user should have access to node
        nodegroup_set = get_nodegroups_by_perm(
            self.user, ["models.read_nodegroup", "models.delete_nodegroup"]
        )
        self.assertTrue(nodegroup_set)
        nodegroup_set = get_nodegroups_by_perm(
            self.user, ["models.read_nodegroup", "models.delete_nodegroup"], False
        )
        self.assertTrue(nodegroup_set)

        nodegroups = NodeGroup.objects.filter(
            node__graph_id=self.data_type_graphid
        ).distinct()

        # Give user 'ben' explicit delete permission on one nodegroup - verify that group is returned
        first_nodegroup = nodegroups.first()
        assign_perm("models.delete_nodegroup", self.user, first_nodegroup)
        nodegroup_set = get_nodegroups_by_perm(
            self.user, ["models.read_nodegroup", "models.delete_nodegroup"], True
        )
        self.assertTrue(nodegroup_set)

        # If all permissions are required, this is OK as long as the user is logged in
        nodegroup_set = get_nodegroups_by_perm(
            self.user, ["models.read_nodegroup", "models.delete_nodegroup"], False
        )
        self.assertTrue(nodegroup_set)

        anonymous_user = User.objects.get(username="anonymous")
        # Anonymous user should be able to read by default, but not delete or edit
        nodegroup_set = get_nodegroups_by_perm(
            anonymous_user,
            [
                "models.read_nodegroup",
            ],
        )

        self.assertTrue(nodegroup_set)

        nodegroup_set = get_nodegroups_by_perm(
            anonymous_user, ["models.read_nodegroup", "models.delete_nodegroup"], False
        )
        self.assertFalse(nodegroup_set)

        nodegroup_set = get_nodegroups_by_perm(
            anonymous_user, ["models.read_nodegroup", "models.write_nodegroup"], False
        )
        self.assertFalse(nodegroup_set)
