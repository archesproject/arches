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
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from arches.app.models.resource import Resource


# these tests can be run from the command line via
# python manage.py test tests.permissions --settings="tests.test_settings"


class ArchesPermissionFrameworkTestCase(ArchesTestCase):
    graph_fixtures = ["Data_Type_Model"]
    data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
    resource_instance_id = "f562c2fa-48d3-4798-a723-10209806c068"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_users()
        cls.expected_resource_count = 2
        cls.user = User.objects.get(username="ben")
        cls.group = Group.objects.get(pk=2)
        cls.legacy_load_testing_package()
        cls.framework = cls.FRAMEWORK()
        cls.resource = Resource.objects.get(pk=cls.resource_instance_id)
        cls.resource.graph_id = cls.data_type_graphid
        cls.resource.remove_resource_instance_permissions()
