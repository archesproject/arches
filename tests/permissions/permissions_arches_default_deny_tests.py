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
from tests.permissions.base_permissions_framework_test import ArchesPermissionFrameworkTestCase
from django.core import management
from django.urls import reverse
from django.test.client import RequestFactory, Client
from django.test.utils import captured_stdout
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from arches.app.models.models import GraphModel, ResourceInstance, Node
from arches.app.models.resource import Resource
from arches.app.permissions.arches_default_deny import ArchesDefaultDenyPermissionFramework

# these tests can be run from the command line via
# python manage.py test tests.permissions.permission_tests --settings="tests.test_settings"


class ArchesDefaultDenyPermissionTests(ArchesPermissionFrameworkTestCase):
    FRAMEWORK = ArchesDefaultDenyPermissionFramework

    def test_user_cannot_view_without_permission(self):
        """
        Tests if a user is _not_ allowed to view a resource with implicit permissions but is with explicit permissions, provided
        that 'view_resourceinstance' is assigned.
        """

        implicit_permission = self.framework.user_can_read_resource(self.user, self.resource_instance_id)
        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        self.framework.assign_perm("change_resourceinstance", self.group, resource)
        can_access_without_view_permission = self.framework.user_can_read_resource(self.user, self.resource_instance_id)
        self.framework.assign_perm("view_resourceinstance", self.group, resource)
        can_access_with_view_permission = self.framework.user_can_read_resource(self.user, self.resource_instance_id)
        self.assertTrue(
            implicit_permission is False and can_access_without_view_permission is False and can_access_with_view_permission is True
        )

    def test_user_has_resource_model_permissions(self):
        """
        Tests that a user cannot access an instance if they have no access to any nodegroup.
        
        """

        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        nodes = Node.objects.filter(graph_id=resource.graph_id)
        for node in nodes:
            if node.nodegroup:
                self.framework.assign_perm("no_access_to_nodegroup", self.group, node.nodegroup)
        hasperms = self.framework.user_has_resource_model_permissions(self.user, ["models.read_nodegroup"], resource)
        self.assertTrue(hasperms is False)

    def test_get_restricted_users(self):
        """
        Tests that users are properly identified as restricted.
        """

        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        self.framework.assign_perm("no_access_to_resourceinstance", self.group, resource)
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

        self.assertTrue(all(results) is True)
