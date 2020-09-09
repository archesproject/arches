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

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
Replace this with more appropriate tests for your application.
"""

import os
import json
from tests import test_settings
from tests.base_test import ArchesTestCase
from django.core import management
from django.urls import reverse
from django.test.client import RequestFactory, Client
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm, get_perms, remove_perm, get_group_perms, get_user_perms
from arches.app.models.models import ResourceInstance, Node
from arches.app.models.resource import Resource
from arches.app.utils.permission_backend import get_editable_resource_types
from arches.app.utils.permission_backend import get_resource_types_by_perm
from arches.app.utils.permission_backend import user_can_read_resource
from arches.app.utils.permission_backend import user_can_edit_resource
from arches.app.utils.permission_backend import user_can_read_concepts
from arches.app.utils.permission_backend import user_has_resource_model_permissions
from arches.app.utils.permission_backend import get_restricted_users

# these tests can be run from the command line via
# python manage.py test tests/permissions/permission_tests.py --pattern="*.py" --settings="tests.test_settings"


class PermissionTests(ArchesTestCase):
    def setUp(self):
        self.expected_resource_count = 2
        self.client = Client()
        self.data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
        self.resource_instance_id = "f562c2fa-48d3-4798-a723-10209806c068"
        self.user = User.objects.get(username="ben")
        self.group = Group.objects.get(pk=2)
        resource = Resource(pk=self.resource_instance_id)
        resource.graph_id = self.data_type_graphid
        resource.remove_resource_instance_permissions()

    def tearDown(self):
        ResourceInstance.objects.filter(graph_id=self.data_type_graphid).delete()

    @classmethod
    def add_users(cls):
        profiles = (
            {"name": "ben", "email": "ben@test.com", "password": "Test12345!", "groups": ["Graph Editor", "Resource Editor"]},
            {
                "name": "sam",
                "email": "sam@test.com",
                "password": "Test12345!",
                "groups": ["Graph Editor", "Resource Editor", "Resource Reviewer"],
            },
            {"name": "jim", "email": "jim@test.com", "password": "Test12345!", "groups": ["Graph Editor", "Resource Editor"]},
        )

        for profile in profiles:
            try:
                user = User.objects.create_user(username=profile["name"], email=profile["email"], password=profile["password"])
                user.save()
                print(("Added: {0}, password: {1}".format(user.username, user.password)))

                for group_name in profile["groups"]:
                    group = Group.objects.get(name=group_name)
                    group.user_set.add(user)

            except Exception as e:
                print(e)

    @classmethod
    def setUpClass(cls):
        test_pkg_path = os.path.join(test_settings.TEST_ROOT, "fixtures", "testing_prj", "testing_prj", "pkg")
        management.call_command("packages", operation="load_package", source=test_pkg_path, yes=True)
        cls.add_users()


    @classmethod
    def tearDownClass(cls):
        pass

    def test_user_cannot_view_without_permission(self):
        """
        Tests if a user is allowed to view a resource with implicit permissions and explicit permissions, but
        not without explicit permission if a permission other than 'view_resourceinstance' is assigned.
        """

        implicit_permission = user_can_read_resource(self.user, self.resource_instance_id)
        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        assign_perm("change_resourceinstance", self.group, resource)
        can_access_without_view_permission = user_can_read_resource(self.user, self.resource_instance_id)
        assign_perm("view_resourceinstance", self.group, resource)
        can_access_with_view_permission = user_can_read_resource(self.user, self.resource_instance_id)
        self.assertTrue(
            implicit_permission is True and can_access_without_view_permission is False and can_access_with_view_permission is True
        )

    def test_user_has_resource_model_permissions(self):
        """
        Tests that a user cannot access an instance if they have no access to any nodegroup.
        
        """

        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        nodes = Node.objects.filter(graph_id=resource.graph_id)
        for node in nodes:
            if node.nodegroup:
                assign_perm("no_access_to_nodegroup", self.group, node.nodegroup)
        hasperms = user_has_resource_model_permissions(self.user, ["models.read_nodegroup"], resource)
        self.assertTrue(hasperms is False)

    def test_get_restricted_users(self):
        """
        Tests that users are properly identified as restricted.
        """

        resource = ResourceInstance.objects.get(resourceinstanceid=self.resource_instance_id)
        assign_perm("no_access_to_resourceinstance", self.group, resource)
        ben = self.user
        jim = User.objects.get(username="jim")
        sam = User.objects.get(username="sam")
        admin = User.objects.get(username="admin")
        assign_perm("view_resourceinstance", ben, resource)
        assign_perm("change_resourceinstance", jim, resource)

        restrictions = get_restricted_users(resource)

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
