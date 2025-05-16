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
from tests.permissions.base_permissions_framework_test import (
    ArchesPermissionFrameworkTestCase,
)
from arches.app.models.models import Node
from arches.app.permissions.arches_default_deny import (
    ArchesDefaultDenyPermissionFramework,
)

# these tests can be run from the command line via
# python manage.py test tests.permissions.permissions_arches_default_deny_tests --settings="tests.test_settings"


class ArchesDefaultDenyPermissionTests(ArchesPermissionFrameworkTestCase):
    FRAMEWORK = ArchesDefaultDenyPermissionFramework

    def test_default_permissions(self):
        default_permissions = MagicMock()
        default_permissions.PERMISSION_DEFAULTS = {
            "330802c5-95bd-11e8-b7ac-acde48001122": [
                {
                    "id": self.group.id,
                    "type": "group",
                    "permissions": ["view_resourceinstance"],
                },
            ]
        }

        with patch(
            "arches.app.permissions.arches_permission_base.settings",
            default_permissions,
        ):
            with patch(
                "arches.app.permissions.arches_default_deny.settings",
                default_permissions,
            ):
                default_permission = self.framework.user_can_read_resource(
                    self.user, self.resource_instance_id
                )

                # implicit permission is true here, because we've specified that the user has view_resourceinstance on this
                # type of resource
                self.assertTrue(default_permission)

    def test_user_cannot_view_without_permission(self):
        """
        Tests if a user is _not_ allowed to view a resource with implicit permissions but is with explicit permissions, provided
        that 'view_resourceinstance' is assigned.
        """

        implicit_permission = self.framework.user_can_read_resource(
            self.user, self.resource_instance_id
        )
        self.framework.assign_perm("change_resourceinstance", self.group, self.resource)
        can_access_without_view_permission = self.framework.user_can_read_resource(
            self.user, self.resource_instance_id
        )
        self.framework.assign_perm("view_resourceinstance", self.group, self.resource)
        can_access_with_view_permission = self.framework.user_can_read_resource(
            self.user, self.resource_instance_id
        )
        self.assertFalse(implicit_permission)
        self.assertFalse(can_access_without_view_permission)
        self.assertTrue(can_access_with_view_permission)

    def test_user_has_resource_model_permissions(self):
        """
        Tests that a user cannot access an instance if they have no access to any nodegroup.

        """

        nodes = Node.objects.filter(graph_id=self.resource.graph_id)
        for node in nodes:
            if node.nodegroup:
                self.framework.assign_perm(
                    "no_access_to_nodegroup", self.group, node.nodegroup
                )
        hasperms = self.framework.user_has_resource_model_permissions(
            self.user, ["models.read_nodegroup"], self.resource
        )
        self.assertFalse(hasperms)

    def test_get_search_ui_permissions(self):

        with patch.object(
            self.framework,
            "get_resource_types_by_perm",
            Mock(return_value=["330802c5-95bd-11e8-b7ac-acde48001122"]),
        ):
            with patch.object(
                self.framework, "get_editable_resource_types", Mock(return_value=[""])
            ):
                user_mock = Mock()
                user_mock.is_superuser = False
                result = self.framework.get_search_ui_permissions(
                    user_mock,
                    {
                        "_source": {
                            "permissions": {
                                "groups_read": [self.group.id],
                                "groups_edit": [],
                            }
                        }
                    },
                    [self.group.id],
                )
                self.assertTrue(result["can_read"])
                self.assertFalse(result["can_edit"])
