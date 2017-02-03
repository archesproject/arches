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
TEST_ROOT = os.path.normpath(os.path.join(ROOT_DIR, '..', 'tests'))


RESOURCE_GRAPH_LOCATIONS = (os.path.join(TEST_ROOT, 'fixtures', 'resource_graphs'),)

CONCEPT_SCHEME_LOCATIONS = (os.path.join(TEST_ROOT, 'fixtures', 'authority_files'),)

ONTOLOGY_FIXTURES = os.path.join(TEST_ROOT, 'fixtures', 'ontologies')

BUSISNESS_DATA_FILES = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# could add Chrome, PhantomJS etc... here
LOCAL_BROWSERS = [] #['Firefox']

# these are set in Travis CI
SAUCE_USERNAME = os.environ.get('SAUCE_USERNAME')
SAUCE_ACCESS_KEY = os.environ.get('SAUCE_ACCESS_KEY')

RUN_LOCAL = True
if SAUCE_USERNAME and SAUCE_ACCESS_KEY:
    RUN_LOCAL = False

# browser/os combinations to use with saucelabs
REMOTE_BROWSERS = [
    # {"platform": "Windows 8.1",
    #  "browserName": "internet explorer",
    #  "version": "11"},
    # {"platform": "Mac OS X 10.9",
    #  "browserName": "chrome",
    #  "version": "53"},
    # {"platform": "Linux",
    #  "browserName": "firefox",
    #  "version": "45"}
]

# Tell nose to measure coverage on the 'foo' and 'bar' apps
NOSE_ARGS = [
    '--with-coverage',
    '--nologcapture',
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
