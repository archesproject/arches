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

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import Language
from tests.base_test import ArchesTestCase


# these tests can be run from the command line via
# python manage.py test tests/utils/datatype_tests.py --settings="tests.test_settings"


class StringDataTypeTests(ArchesTestCase):
    def test_string_validate(self):
        string = DataTypeFactory().get_instance("string")
        some_errors = string.validate("")
        self.assertGreater(len(some_errors), 0)
        no_errors = string.validate({"en": {"value": "hello", "direction": "ltr"}})
        self.assertEqual(len(no_errors), 0)

    def test_tile_transform(self):
        string = DataTypeFactory().get_instance("string")
        new_language = Language(code="fa", name="Fake", default_direction="ltr", scope="system")
        new_language.save()
        tile_value = string.transform_value_for_tile("hello|fa")
        self.assertEqual(type(tile_value), dict)
        self.assertTrue("fa" in tile_value.keys())
        new_language.delete()
