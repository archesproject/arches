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

# LOAD_V3_DATA_DURING_TESTS = True will engage the most extensive the of the v3
# data migration tests, which could add over a minute to the test process. It's
# recommended that this setting only be set to True in tests/settings_local.py
# and run in specific cases at the discretion of the developer.
LOAD_V3_DATA_DURING_TESTS = False

SEARCH_BACKEND = 'tests.base_test.TestSearchEngine'

RESOURCE_GRAPH_LOCATIONS = (os.path.join(TEST_ROOT, 'fixtures', 'resource_graphs'),)

ONTOLOGY_FIXTURES = os.path.join(TEST_ROOT, 'fixtures', 'ontologies')

BUSISNESS_DATA_FILES = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

ELASTICSEARCH_PREFIX = 'test'

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# could add Chrome, PhantomJS etc... here
LOCAL_BROWSERS = []  # ['Firefox']

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

OVERRIDE_RESOURCE_MODEL_LOCK = True

# Tell nose to measure coverage on the 'foo' and 'bar' apps
NOSE_ARGS = [
#    '--with-coverage',
    '--nologcapture',
    '--cover-package=arches',
    '--verbosity=1',
    '--cover-erase',
]

INSTALLED_APPS = INSTALLED_APPS + (
    'django_nose',
)

ONTOLOGY_PATH = os.path.join(ROOT_DIR, 'db', 'ontologies', 'cidoc_crm')
ONTOLOGY_BASE = 'cidoc_crm_v6.2.xml'
ONTOLOGY_BASE_VERSION = '6.2'
ONTOLOGY_BASE_NAME = 'CIDOC CRM v6.2'
ONTOLOGY_BASE_ID = 'e6e8db47-2ccf-11e6-927e-b8f6b115d7dd'
ONTOLOGY_EXT = [
    'CRMsci_v1.2.3.rdfs.xml',
    'CRMarchaeo_v1.4.rdfs.xml',
    'CRMgeo_v1.2.rdfs.xml',
    'CRMdig_v3.2.1.rdfs.xml',
    'CRMinf_v0.7.rdfs.xml',
    'arches_crm_enhancements.xml'
]

try:
    from settings_local import *
except ImportError:
    pass
