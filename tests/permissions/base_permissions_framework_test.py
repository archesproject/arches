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

from tests.base_test import ArchesTestCase

import os
from tests import test_settings
from tests.base_test import ArchesTestCase
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

class ArchesPermissionFrameworkTestCase(ArchesTestCase):
    def setUp(self):
        self.expected_resource_count = 2
        self.client = Client()
        self.data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
        self.resource_instance_id = "f562c2fa-48d3-4798-a723-10209806c068"
        self.user = User.objects.get(username="ben")
        self.group = Group.objects.get(pk=2)
        self.framework = self.FRAMEWORK()
        resource = Resource.objects.get(pk=self.resource_instance_id)
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
            test_pkg_path = os.path.join(test_settings.TEST_ROOT, "fixtures", "testing_prj", "testing_prj", "pkg")
            with captured_stdout():
                management.call_command("packages", operation="load_package", source=test_pkg_path, yes=True, verbosity=0)

        super().setUpClass()
        cls.add_users()

