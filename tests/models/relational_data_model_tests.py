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
from tests.base_test import ArchesTestCase
from django.core import management
from django.test.utils import captured_stdout
from arches.app.models.models import DDataType
from arches.app.models.graph import Graph
from django.db import connection


# these tests can be run from the command line via
# python manage.py test tests.models.relational_data_model_tests --settings="tests.test_settings"


class RelationalDataModelTests(ArchesTestCase):
    custom_data_type_graphid = None
    custom_datatype_graph_filename = None
    custom_string_datatype_filename = None
    datatype_filename = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create the Datatype Graph if it doesn't exist
        if not Graph.objects.filter(graphid=cls.custom_data_type_graphid).exists():
            with captured_stdout():
                management.call_command(
                    "packages",
                    operation="import_graphs",
                    source=cls.custom_datatype_graph_filename,
                    verbosity=0,
                )

    @classmethod
    def setUpTestData(cls):
        super().loadOntology()
        cls.custom_data_type_graphid = "ceed156d-aadf-4a13-b383-c044624c64bb"
        cls.custom_datatype_graph_filename = os.path.join(
            test_settings.TEST_ROOT,
            "fixtures",
            "resource_graphs",
            "relational_data_model_tests.json",
        )
        cls.custom_string_datatype_filename = os.path.join(
            test_settings.TEST_ROOT,
            "fixtures",
            "datatypes",
            "extended_string_datatype.py",
        )
        custom_string_datatype_name = "extended-string-datatype"
        custom_string_datatype = DDataType.objects.filter(datatype=custom_string_datatype_name)

        if custom_string_datatype is None or len(custom_string_datatype) != 1:
            management.call_command("datatype", "register", source=cls.custom_string_datatype_filename, verbosity=0)

    def test_extended_string_postgres_datatype(self):
        """
        Test that the generated Postgres datatype is JSON
        """
        # Create the relational data model views
        sql = f"select public.__arches_create_resource_model_views('%s'::uuid);" % RelationalDataModelTests.custom_data_type_graphid
        cursor = connection.cursor()
        cursor.execute(sql)
        # row = cursor.fetchone()
        # print("Result: %s" % str(row))

        schema_name = "relational_data_model_tests"
        view_name = "custom_datatypes"
        column_name = "extended_string_datatype"
        expected_datatype = "jsonb"

        validation_sql = f"""
            select data_type from information_schema.columns
            where table_schema = '%s'
            and table_name = '%s'
            and column_name = '%s'
        """ % (
            schema_name,
            view_name,
            column_name,
        )

        cursor.execute(validation_sql)
        row = cursor.fetchone()

        assert row is not None and row[0] == expected_datatype
