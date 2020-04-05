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
from arches.app.models.models import ResourceInstance, Node, GraphModel
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.datatypes import datatypes

from arches.app.search.mappings import (
    prepare_resource_relations_index,
    delete_resource_relations_index,
)

# these tests can be run from the command line via
# python manage.py test tests/datatypes/datatype_tests.py --pattern="*.py" --settings="tests.test_settings"


class DataTypeTests(ArchesTestCase):
    def setUp(self):
        self.graph = GraphModel.objects.get(pk="330802c5-95bd-11e8-b7ac-acde48001122")
        datatype_factory = datatypes.DataTypeFactory()
        nodes = self.graph.node_set.all()
        self.datatypes = {node.datatype: {"datatype": datatype_factory.get_instance(node.datatype), "node": node} for node in nodes}

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        test_pkg_path = os.path.join(test_settings.TEST_ROOT, "fixtures", "testing_prj", "testing_prj", "pkg")
        management.call_command("packages", operation="load_package", source=test_pkg_path, yes=True)
        delete_resource_relations_index()
        prepare_resource_relations_index(create=True)

    @classmethod
    def tearDownClass(cls):
        GraphModel.objects.all().delete()

    def test_string_validation(self):
        """
        Tests string datatype validation

        """
        datatype = self.datatypes["string"]["datatype"]
        errors = datatype.validate("cat")
        errors += datatype.validate(7)
        errors += datatype.validate(None)
        self.assertEqual(1, len(errors))
