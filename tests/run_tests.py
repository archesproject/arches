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


import sys
import os
from django.test.utils import get_runner
from tests import test_settings


def run_all(argv=None):
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"

    if argv is None or len(argv[1:]) == 0:
        argv = ["tests"]

    TestRunner = get_runner(test_settings)
    test_runner = TestRunner([], interactive=True)
    failures = test_runner.run_tests(argv)
    sys.exit(failures)


if __name__ == "__main__":
    run_all(sys.argv)
