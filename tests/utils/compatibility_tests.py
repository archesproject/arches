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

from arches.app.utils.compatibility import is_arches_compatible
from tests.base_test import ArchesTestCase
from arches import VERSION


# these tests can be run from the command line via
# python manage.py test tests/utils/compatibility_tests.py --settings="tests.test_settings"


class CompatibilityTests(ArchesTestCase):
    def test_compatibility(self):
        self.assertTrue(is_arches_compatible())

    def test_min_patch_version_too_high(self):
        min_version = (VERSION[0], VERSION[1], VERSION[2] + 1)
        max_version = (VERSION[0], VERSION[1], VERSION[2] + 2)
        self.assertFalse(is_arches_compatible(min_version, max_version))

    def test_max_patch_version_too_low(self):
        min_version = (VERSION[0], VERSION[1], VERSION[2] - 1)
        max_version = (VERSION[0], VERSION[1], VERSION[2] - 2)
        self.assertFalse(is_arches_compatible(min_version, max_version))

    def test_min_feature_version_too_high(self):
        min_version = (VERSION[0], VERSION[1] + 1)
        max_version = (VERSION[0], VERSION[1] + 2)
        self.assertFalse(is_arches_compatible(min_version, max_version))

    def test_max_feature_version_too_low(self):
        min_version = (VERSION[0], VERSION[1] - 1)
        max_version = (VERSION[0], VERSION[1] - 2)
        self.assertFalse(is_arches_compatible(min_version, max_version))

    def test_major_version_too_high(self):
        min_version = (VERSION[0] + 1,)
        max_version = (VERSION[0] + 2,)
        self.assertFalse(is_arches_compatible(min_version, max_version))

    def test_major_version_too_low(self):
        min_version = (VERSION[0] - 1,)
        max_version = (VERSION[0] - 2,)
        self.assertFalse(is_arches_compatible(min_version, max_version))
