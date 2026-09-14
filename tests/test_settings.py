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

from arches.settings import *

from django.utils.translation import gettext_lazy as _

PACKAGE_NAME = "arches"
APP_ROOT = ""
TEST_ROOT = os.path.normpath(os.path.join(ROOT_DIR, "..", "tests"))
STATICFILES_DIRS = []

RESOURCE_GRAPH_LOCATIONS = [
    os.path.join(TEST_ROOT, "fixtures", "resource_graphs"),
    os.path.join(
        TEST_ROOT,
        "fixtures",
        "testing_prj",
        "testing_prj",
        "pkg",
        "graphs",
        "resource_models",
    ),
    os.path.join(TEST_ROOT, "fixtures", "jsonld_base", "models"),
]
REFERENCE_DATA_FIXTURE_LOCATION = os.path.join(
    TEST_ROOT, "fixtures", "testing_prj", "testing_prj", "pkg", "reference_data"
)

ONTOLOGY_FIXTURES = os.path.join(TEST_ROOT, "fixtures", "ontologies", "test_ontology")
ONTOLOGY_PATH = os.path.join(TEST_ROOT, "fixtures", "ontologies", "cidoc_crm")
MEDIA_ROOT = os.path.join(TEST_ROOT, "fixtures", "data")

BUSINESS_DATA_FILES = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# Class for custom ES document generator and search functionality
ES_MAPPING_MODIFIER_CLASSES = [
    "tests.views.search_tests.TestEsMappingModifier",
    # Contributed by the bundled controlled lists application, exercised by
    # tests/extensions/controlled_lists/test_reference_es_mapping_modifier.py
    "arches.extensions.controlled_lists.search.references_es_mapping_modifier.ReferencesEsMappingModifier",
]

# Reference data index, so that the bundled controlled lists tests can build and
# query it. REFERENCES_INDEX_NAME comes from arches.settings.
ELASTICSEARCH_CUSTOM_INDEXES = [
    {
        "module": "arches.extensions.controlled_lists.search_indexes.reference_index.ReferenceIndex",
        "name": REFERENCES_INDEX_NAME,
        "should_update_asynchronously": True,
    },
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    "user_permission": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        "LOCATION": "user_permission_cache",
    },
    # Named by ARCHES_QUERYSETS_* in arches.settings; omitting them raises
    # arches_querysets.E001. Real backends rather than dummies: the querysets
    # tests assert query counts that assume these caches actually cache.
    "querysets_concepts": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "querysets_concepts_cache",
    },
    "querysets_resource_instances": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "querysets_resource_instances_cache",
    },
}

# Bundled applications are opt-in, so arches.settings does not install them.
# Arches' own test suite covers them, so it does.
#
# Order matters twice over. Django resolves management commands by iterating
# app configs in reverse, so an application earlier in INSTALLED_APPS wins:
# the bundled applications must precede "arches" for their command overrides
# (vue_components ships its own validate) to take effect. Templates and static
# files resolve the other way, so "arches.app" stays last. The project template
# arrives at the same order by listing "arches" in its trailing block.
_BUNDLED_APPS = (
    # Required by arches.extensions.controlled_lists, whose ListItem uses
    # ExclusionConstraint.
    "django.contrib.postgres",
    "rest_framework",
    "arches.extensions.querysets",
    "arches.extensions.vue_components",
    "arches.extensions.controlled_lists",
)
_TRAILING = ("arches.app", "django.contrib.admin")
_head = [app for app in INSTALLED_APPS if app not in _TRAILING]
_arches_at = _head.index("arches")
INSTALLED_APPS = (
    tuple(_head[:_arches_at]) + _BUNDLED_APPS + tuple(_head[_arches_at:]) + _TRAILING
)

LOGGING["loggers"]["django.request"]["level"] = "ERROR"
LOGGING["loggers"]["arches"]["level"] = "ERROR"

ELASTICSEARCH_PREFIX = "test"

# Fixtures the bundled controlled lists tests load by name.
FIXTURE_DIRS = [
    os.path.join(TEST_ROOT, "extensions", "controlled_lists", "fixtures", "data"),
]

ROOT_URLCONF = "tests.urls"
# django_hosts overrides ROOT_URLCONF per request, so the host map has to
# point at the same urlconf or requests bypass the bundled applications.
ROOT_HOSTCONF = "tests.hosts"

TEST_RUNNER = "arches.test.runner.ArchesTestRunner"
SILENCED_SYSTEM_CHECKS.append(
    "arches.W001"
)  # Cache backend does not support rate-limiting

FILE_TYPE_CHECKING = "lenient"

# could add Chrome, PhantomJS etc... here
LOCAL_BROWSERS = []  # ['Firefox']

ENABLE_USER_SIGNUP = True
FORCE_USER_SIGNUP_EMAIL_AUTHENTICATION = True

# https://docs.djangoproject.com/en/stable/topics/testing/overview/#password-hashing
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

ENABLE_TWO_FACTOR_AUTHENTICATION = False
FORCE_TWO_FACTOR_AUTHENTICATION = False

DATATYPE_LOCATIONS.append("tests.fixtures.datatypes")
ELASTICSEARCH_HOSTS = [
    {"scheme": "http", "host": "localhost", "port": ELASTICSEARCH_HTTP_PORT}
]
LANGUAGES = [
    ("de", _("German")),
    ("en", _("English")),
    ("en-gb", _("British English")),
    ("es", _("Spanish")),
    ("ar", _("Arabic")),
]

DOCKER = False

PERMISSION_DEFAULTS = {}

CELERY_CHECK_ONLY_INSPECT_BROKER = True


try:
    from arches.settings_local import *
except ImportError:
    pass

if DOCKER:
    try:
        from arches.settings_docker import *
    except ImportError:
        pass


# Tests shouldn't depend on celery running, so overwrite after settings_local import
# This is enough to fool check_if_celery_available()
CELERY_BROKER_URL = ""
