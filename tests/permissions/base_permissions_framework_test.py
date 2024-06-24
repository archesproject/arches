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
from tests.utils.permission_test_utils import add_users
from django.core import management
from django.test.utils import captured_stdout
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from arches.app.models.models import GraphModel
from arches.app.models.resource import Resource


# these tests can be run from the command line via
# python manage.py test tests.permissions --settings="tests.test_settings"


class ArchesPermissionFrameworkTestCase(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        add_users()
        cls.expected_resource_count = 2
        cls.data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
        cls.resource_instance_id = "f562c2fa-48d3-4798-a723-10209806c068"
        cls.user = User.objects.get(username="ben")
        cls.group = Group.objects.get(pk=2)
        cls.framework = cls.FRAMEWORK()
        resource = Resource.objects.get(pk=cls.resource_instance_id)
        resource.graph_id = cls.data_type_graphid
        resource.remove_resource_instance_permissions()

    @classmethod
    def setUpClass(cls):
        cls.data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
        if not GraphModel.objects.filter(pk=cls.data_type_graphid).exists():
            # TODO: Fix this to run inside transaction, i.e. after super().setUpClass()
            # https://github.com/archesproject/arches/issues/10719
            test_pkg_path = os.path.join(
                test_settings.TEST_ROOT, "fixtures", "testing_prj", "testing_prj", "pkg"
            )
            path_to_cheesy_image = os.path.join(
                test_pkg_path, "uploadedfiles", "test.png"
            )
            cls.addClassCleanup(os.unlink, path_to_cheesy_image)
            with captured_stdout():
                management.call_command(
                    "packages",
                    operation="load_package",
                    source=test_pkg_path,
                    yes=True,
                    verbosity=0,
                )

        super().setUpClass()
