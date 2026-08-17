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

from unittest.mock import MagicMock, Mock, patch

from django.test import override_settings
from arches.app.models.resource import Resource
from tests.permissions.base_permissions_framework_test import (
    ArchesPermissionFrameworkTestCase,
)
from django.contrib.auth.models import User
from arches.app.models.models import ResourceInstance, Node
from arches.app.permissions.arches_default_allow import (
    ArchesDefaultAllowPermissionFramework,
)

# these tests can be run from the command line via
# python manage.py test tests.permissions.permission_tests --settings="tests.test_settings"


class ArchesDefaultAllowPermissionsTests(ArchesPermissionFrameworkTestCase):
    FRAMEWORK = ArchesDefaultAllowPermissionFramework

    def test_default_permissions(self):
        default_permissions = MagicMock()
        default_permissions.PERMISSION_DEFAULTS = {
            "330802c5-95bd-11e8-b7ac-acde48001122": [
                {
                    "id": self.group.id,
                    "type": "group",
                    "permissions": ["change_resourceinstance"],
                },
            ]
        }

        with patch(
            "arches.app.permissions.arches_permission_base.settings",
            default_permissions,
        ):
            with patch(
                "arches.app.permissions.arches_default_allow.settings",
                default_permissions,
            ):
                implicit_permission = self.framework.user_can_read_resource(
                    self.user, self.resource_instance_id
                )
                resource = ResourceInstance.objects.get(
                    resourceinstanceid=self.resource_instance_id
                )
                can_access_without_view_permission = (
                    self.framework.user_can_read_resource(
                        self.user, self.resource_instance_id
                    )
                )
                self.framework.assign_perm(
                    "view_resourceinstance", self.group, resource
                )
                can_access_with_view_permission = self.framework.user_can_read_resource(
                    self.user, self.resource_instance_id
                )
                perms = self.framework.get_default_permissions_objects(
                    self.user, cls=Resource
                )
                perms_invalid = self.framework.get_default_permissions_objects(
                    self.user, cls=self.__class__
                )
                self.assertGreater(len(perms), 0)
                self.assertEqual(len(perms_invalid), 0)
                # implicit permission is false here, because change_resourceinstance will negate implicit permissions
                self.assertFalse(implicit_permission)

                # cannot access the resource instance because view has not been specified
                self.assertFalse(can_access_without_view_permission)

                self.assertTrue(can_access_with_view_permission)

    def test_noaccess_default(self):
        default_permissions = MagicMock()
        default_permissions.PERMISSION_DEFAULTS = {
            "330802c5-95bd-11e8-b7ac-acde48001122": [
                {
                    "id": self.group.id,
                    "type": "group",
                    "permissions": ["no_access_to_resourceinstance"],
                },
            ]
        }

        with patch(
            "arches.app.permissions.arches_permission_base.settings",
            default_permissions,
        ):
            with patch(
                "arches.app.permissions.arches_default_allow.settings",
                default_permissions,
            ):
                resource = ResourceInstance.objects.get(
                    resourceinstanceid=self.resource_instance_id
                )
                result = self.framework.get_restricted_users(resource)
                self.assertIn(self.user.id, result["no_access"])

    def test_get_search_ui_permissions(self):

        with patch.object(
            self.framework,
            "get_resource_types_by_perm",
            Mock(return_value=["330802c5-95bd-11e8-b7ac-acde48001122"]),
        ):
            with patch.object(
                self.framework, "get_editable_resource_types", Mock(return_value=[""])
            ):
                mock = Mock()
                mock.id = self.user.id
                mock.is_superuser = False
                result = self.framework.get_search_ui_permissions(
                    mock,
                    {
                        "_source": {
                            "permissions": {
                                "users_without_read_perm": [],
                                "users_without_edit_perm": [self.user.id],
                            }
                        }
                    },
                    [],
                )
                self.assertTrue(result["can_read"])
                self.assertFalse(result["can_edit"])

    def test_user_cannot_view_without_permission(self):
        """
        Tests if a user is allowed to view a resource with implicit permissions and explicit permissions, but
        not without explicit permission if a permission other than 'view_resourceinstance' is assigned
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

        # default allow causes implicit permission to allow access to all resources.
        self.assertTrue(implicit_permission)

        # if any permission is specified that is not view_resourceinstance, deny.
        self.assertFalse(can_access_without_view_permission)

        # explicitly specifying view_resourceinstance
        self.assertTrue(can_access_with_view_permission)

    def test_process_new_user(self):
        user = User(
            id=1001,
            email="new_allow_users@example.com",
            first_name="new",
            last_name="allowUser",
            is_staff=False,
            is_superuser=False,
        )
        with patch.object(self.framework, "assign_perm", Mock()):
            filterMethod = Mock(
                name="filterMock",
                return_value=[Mock(name="ResourceInstanceMock", spec=ResourceInstance)],
            )
            with patch(
                "arches.app.models.models.ResourceInstance.objects.filter", filterMethod
            ):
                resourceObjectMock = Mock(Resource, name="objectMock", autospec=True)
                with patch(
                    "arches.app.permissions.arches_default_allow.Resource",
                    Mock(
                        name="resourceObjectMock",
                        return_value=resourceObjectMock,
                    ),
                ):
                    self.framework.process_new_user(user, False)
                    resourceObjectMock.index.assert_any_call()

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

    @patch("django.contrib.auth.models.User")
    def test_permission_search_filter(self, mock_User):
        mock_User.id = 12
        filter = self.framework.get_permission_search_filter(mock_User)
        filter_text = str(filter.dsl)
        self.assertIn("permissions.users_with_no_access", filter_text)
        self.assertIn(str(mock_User.id), filter_text)
