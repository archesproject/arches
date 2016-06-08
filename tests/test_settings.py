'''
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
'''

from arches.settings import *
import os
import inspect


PACKAGE_NAME = 'arches'
ROOT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
ROOT_DIR = os.path.normpath(os.path.join(ROOT_DIR, '..', 'arches'))
PACKAGE_ROOT = os.path.normpath(os.path.join(ROOT_DIR, '..', 'tests'))


RESOURCE_GRAPH_LOCATIONS = (os.path.join(PACKAGE_ROOT, 'fixtures', 'resource_graphs'),)

CONCEPT_SCHEME_LOCATIONS = (os.path.join(PACKAGE_ROOT, 'fixtures', 'authority_files'),)

ONTOLOGY_FIXTURES = os.path.join(PACKAGE_ROOT, 'fixtures', 'ontologies')

BUSISNESS_DATA_FILES = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Tell nose to measure coverage on the 'foo' and 'bar' apps
NOSE_ARGS = [
    '--with-coverage',
    '--nocapture', 
    '--cover-package=arches',
    '--verbosity=1',
    '--cover-erase',
]

INSTALLED_APPS = INSTALLED_APPS + (
    'django_nose',
)


try:
    from settings_local import *
except ImportError:
    pass


