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

import inspect
import os
from datetime import datetime, timedelta
from contextlib import suppress

from arches.settings_utils import *

try:
    from django.utils.translation import gettext_lazy as _
    from corsheaders.defaults import default_headers
except ImportError:  # unable to import prior to installing requirements
    pass

#########################################
###          STATIC SETTINGS          ###
#########################################

STREAMLINE_IMPORT = True

MODE = "PROD"  # options are either "PROD" or "DEV" (installing with Dev mode set, gets you extra dependencies)
DEBUG = True
INTERNAL_IPS = ("127.0.0.1",)

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        "NAME": "arches",  # Or path to database file if using sqlite3.
        "USER": "postgres",  # Not used with sqlite3.
        "PASSWORD": "postgis",  # Not used with sqlite3.
        "HOST": "localhost",  # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "5432",  # Set to empty string for default. Not used with sqlite3.
        "POSTGIS_TEMPLATE": "template_postgis",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
PG_SUPERUSER = ""
PG_SUPERUSER_PW = ""

# from http://django-guardian.readthedocs.io/en/stable/configuration.html#anonymous-user-name
ANONYMOUS_USER_NAME = None

ELASTICSEARCH_HTTP_PORT = (
    9200  # this should be in increments of 200, eg: 9400, 9600, 9800
)
SEARCH_BACKEND = "arches.app.search.search.SearchEngine"
SEARCH_THUMBNAILS = False
# see http://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch
ELASTICSEARCH_HOSTS = [
    {"scheme": "https", "host": "localhost", "port": ELASTICSEARCH_HTTP_PORT}
]

# Comment out this line for a development setup after running the ubuntu_setup.sh script
ELASTICSEARCH_CONNECTION_OPTIONS = {"request_timeout": 30}

# Uncomment this line for a development setup after running the ubuntu_setup.sh script (do not use in production)
# ELASTICSEARCH_CONNECTION_OPTIONS = {"request_timeout": 30, "verify_certs": False, "basic_auth": ("elastic", "E1asticSearchforArche5")}

# If you need to connect to Elasticsearch via an API key instead of username/password, use the syntax below:
# ELASTICSEARCH_CONNECTION_OPTIONS = {"request_timeout": 30, "verify_certs": False, "api_key": "<ENCODED_API_KEY>"}
# ELASTICSEARCH_CONNECTION_OPTIONS = {"request_timeout": 30, "verify_certs": False, "api_key": ("<ID>", "<API_KEY>")}

# Your Elasticsearch instance needs to be configured with xpack.security.enabled=true to use API keys - update elasticsearch.yml or .env file and restart.

# Set the ELASTIC_PASSWORD environment variable in either the docker-compose.yml or .env file to the password you set for the elastic user,
# otherwise a random password will be generated.

# API keys can be generated via the Elasticsearch API: https://www.elastic.co/guide/en/elasticsearch/reference/current/security-api-create-api-key.html
# Or Kibana: https://www.elastic.co/guide/en/kibana/current/api-keys.html

# a prefix to append to all elasticsearch indexes, note: must be lower case
ELASTICSEARCH_PREFIX = "arches"


# a list of objects of the form below
# {
#     'module': dotted path to the Classname within a python module,
#     'name': name of the custom index  <-- follow ES index naming rules
# }
ELASTICSEARCH_CUSTOM_INDEXES = []
# [{
#     'module': 'my_project.search_indexes.sample_index.SampleIndex',
#     'name': 'my_new_custom_index',
#     'should_update_asynchronously': False
# }]

THUMBNAIL_GENERATOR = None  # "arches.app.utils.thumbnail_generator.ThumbnailGenerator"
GENERATE_THUMBNAILS_ON_DEMAND = (
    False  # True to generate a thumnail on request if it doens't exist
)
MIN_FILE_SIZE_T0_GENERATE_THUMBNAIL = (
    150000  # yet to be implemented, in bytes eg: 150000 = 150kb
)

# This should point to the url where you host your site
# Make sure to use a trailing slash
PUBLIC_SERVER_ADDRESS = "http://localhost:8000/"

KIBANA_URL = "http://localhost:5601/"
KIBANA_CONFIG_BASEPATH = "kibana"  # must match Kibana config.yml setting (server.basePath) but without the leading slash,
# also make sure to set server.rewriteBasePath: true
USE_SEMANTIC_RESOURCE_RELATIONSHIPS = True
ROOT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
APP_ROOT = os.path.join(ROOT_DIR, "app")
PACKAGE_ROOT = ROOT_DIR
PACKAGE_NAME = PACKAGE_ROOT.split(os.sep)[-1]
RESOURCE_IMPORT_LOG = "arches/logs/resource_import.log"
FILE_VIEWER_DOWNLOAD_LIMIT = (
    1073741824  # limit of file viewer download source files in bytes
)
RESOURCE_FORMATTERS = {
    "csv": "arches.app.utils.data_management.resources.formats.csvfile.CsvWriter",
    "json": "arches.app.utils.data_management.resources.formats.archesfile.ArchesFileWriter",
    "tilecsv": "arches.app.utils.data_management.resources.formats.csvfile.TileCsvWriter",
    "tilexl": "arches.app.utils.data_management.resources.formats.excel.ExcelWriter",
    "shp": "arches.app.utils.data_management.resources.formats.shpfile.ShpWriter",
    "xml": "arches.app.utils.data_management.resources.formats.rdffile.RdfWriter",
    "pretty-xml": "arches.app.utils.data_management.resources.formats.rdffile.RdfWriter",
    "json-ld": "arches.app.utils.data_management.resources.formats.rdffile.JsonLdWriter",
    "n3": "arches.app.utils.data_management.resources.formats.rdffile.RdfWriter",
    "nt": "arches.app.utils.data_management.resources.formats.rdffile.RdfWriter",
    "trix": "arches.app.utils.data_management.resources.formats.rdffile.RdfWriter",
    "html": "arches.app.utils.data_management.resources.formats.htmlfile.HtmlWriter",
}

# Hide nodes and cards in a report that have no data
HIDE_EMPTY_NODES_IN_REPORT = False

# Set the ontolgoy namespace prefixes to use in the UI, set the namespace to '' omit a prefix
# Users can also override existing namespaces as well if you like
ONTOLOGY_NAMESPACES = {
    #'http://my_namespace_here/': 'some_ns',
    #'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'RDF' <-- note the all caps
    "http://www.cidoc-crm.org/cidoc-crm/": "",
    "http://www.ics.forth.gr/isl/CRMarchaeo/": "",
    "http://www.ics.forth.gr/isl/CRMdig/": "",
    "http://www.ics.forth.gr/isl/CRMgeo/": "",
    "http://www.ics.forth.gr/isl/CRMinf/": "",
    "http://www.ics.forth.gr/isl/CRMsci/": "",
}

ONTOLOGY_DIR = os.path.join(ROOT_DIR, "ontologies")

# Used in the JSON-LD export for determining which external concept scheme URI
# to use in preference for the URI of a concept. If there is no match, the default
# Arches host URI will be used (eg http://localhost/concepts/123f323f-...)
PREFERRED_CONCEPT_SCHEMES = [
    "http://vocab.getty.edu/aat/",
    "http://www.cidoc-crm.org/cidoc-crm/",
]
JSONLD_CONTEXT_CACHE_TIMEOUT = 43800  # in minutes (43800 minutes ~= 1 month)

# This is the namespace to use for export of data (for RDF/XML for example)
# Ideally this should point to the url where you host your site
# Make sure to use a trailing slash
ARCHES_NAMESPACE_FOR_DATA_EXPORT = PUBLIC_SERVER_ADDRESS

# This is used to indicate whether the data in the CSV and SHP exports should be
# ordered as seen in the resource cards or not.
EXPORT_DATA_FIELDS_IN_CARD_ORDER = False

RDM_JSONLD_CONTEXT = {"arches": ARCHES_NAMESPACE_FOR_DATA_EXPORT}

PREFERRED_COORDINATE_SYSTEMS = (
    {
        "name": "Geographic",
        "srid": "4326",
        "proj4": "+proj=longlat +datum=WGS84 +no_defs",
        "default": True,
    },  # Required
)

ANALYSIS_COORDINATE_SYSTEM_SRID = 3857  # Coord sys units must be meters

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

RESOURCE_EDITOR_GROUPS = ("Resource Editor", "Crowdsource Editor")

# Unique session cookie ensures that logins are treated separately for each app
SESSION_COOKIE_NAME = "arches"

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  #<-- Only need to uncomment this for testing without an actual email server
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = "xxxx@xxx.com"
# EMAIL_HOST_PASSWORD = 'xxxxxxx'
# EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# If True, allows for user self creation via the signup view. If False, users can only be created via the Django admin view.
ENABLE_USER_SIGNUP = True

# If True, users must authenticate their accout via email to complete the account creation process.
FORCE_USER_SIGNUP_EMAIL_AUTHENTICATION = True

POSTGIS_VERSION = (3, 0, 0)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "America/Chicago"
USE_TZ = False


# see https://docs.djangoproject.com/en/2.2/topics/i18n/translation/#how-django-discovers-language-preference
# to see how LocaleMiddleware tries to determine the user's language preference
# (make sure to check your accept headers as they will override the LANGUAGE_CODE setting!)
# also see get_language_from_request in django.utils.translation.trans_real.py
# to see how the language code is derived in the actual code

####### TO GENERATE .PO FILES DO THE FOLLOWING ########
# run the following commands
# language codes used in the command should be in the form (which is slightly different
# form the form used in the LANGUAGE_CODE and LANGUAGES settings below):
# --local={countrycode}_{REGIONCODE} <-- countrycode is lowercase, regioncode is uppercase, also notice the underscore instead of hyphen
# commands to run (to generate files for "British English, German, and Spanish"):
# django-admin.py makemessages --ignore=env/* --local=de --local=en --local=en_GB --local=es  --extension=htm,py
# django-admin.py compilemessages


# default language of the application
# language code needs to be all lower case with the form:
# {langcode}-{regioncode} eg: en, en-gb ....
# a list of language codes can be found here http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en"

# list of languages to display in the language switcher,
# if left empty or with a single entry then the switch won't be displayed
# language codes need to be all lower case with the form:
# {langcode}-{regioncode} eg: en, en-gb ....
# a list of language codes can be found here http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGES = [
    # ("de", _("German")),
    ("en", "English"),
    # ("en-gb", _("British English")),
    # ("es", _("Spanish")),
    # ("ar", _("Arabic")),
]

# override this to permenantly display/hide the language switcher
SHOW_LANGUAGE_SWITCH = len(LANGUAGES) > 1

# the path where your translation strings are stored
LOCALE_PATHS = [
    os.path.join(ROOT_DIR, "locale"),
]

# Sets default max upload size to 15MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 15728640

# By setting RESTRICT_MEDIA_ACCESS to True, media file requests will be
# served by Django rather than your web server (e.g. Apache). This allows file requests to be checked against nodegroup permissions.
# However, this will adversely impact performace when serving large files or during periods of high traffic.
RESTRICT_MEDIA_ACCESS = False


# By setting RESTRICT_CELERY_EXPORT_FOR_ANONYMOUS_USER to True, if the user is attempting
# to export search results above the SEARCH_EXPORT_IMMEDIATE_DOWNLOAD_THRESHOLD
# value and is not signed in with a user account then the request will not be allowed.
RESTRICT_CELERY_EXPORT_FOR_ANONYMOUS_USER = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(ROOT_DIR)

# URL that handles the media served from MEDIA_ROOT, used for managing stored files.
# It must end in a slash if set to a non-empty value.
MEDIA_URL = "/files/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(ROOT_DIR, "staticfiles")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

# when hosting Arches under a sub path set this value to the sub path eg : "/{sub_path}/"
FORCE_SCRIPT_NAME = None

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = "/media/admin/"

STATICFILES_DIRS = build_staticfiles_dirs(
    app_root=ROOT_DIR
)  # app_root=ROOT_DIR is a workaround to find `node_modules` when running Arches without a project
TEMPLATES = build_templates_config(debug=DEBUG)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "arches.settings_utils.ArchesApplicationsStaticFilesFinder",
    "arches.settings_utils.CoreArchesStaticFilesFinderBuildDirectory",
    "arches.settings_utils.CoreArchesStaticFilesFinderMediaRoot",
    "arches.settings_utils.CoreArchesStaticFilesFinderNodeModules",
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = "django-insecure-c7ky-mc6vdnv+avp0r@(a)8y^51ex=25nogq@+q5$fnc*mxwdi"
JWT_KEY = SECRET_KEY
JWT_TOKEN_EXPIRATION = 50  # days before the token becomes stale
JWT_ALGORITHM = "HS256"

# OAuth settings
# https://django-oauth-toolkit.readthedocs.io/en/latest/settings.html
OAUTH2_PROVIDER = {"ACCESS_TOKEN_EXPIRE_SECONDS": 36000}

# This is the client id you get when you register a new application
# see https://arches.readthedocs.io/en/stable/api/#authentication
OAUTH_CLIENT_ID = ""  # '9JCibwrWQ4hwuGn5fu2u1oRZSs9V6gK8Vu8hpRC4'

AUTHENTICATION_BACKENDS = (
    "arches.app.utils.email_auth_backend.EmailAuthenticationBackend",
    "oauth2_provider.backends.OAuth2Backend",
    "django.contrib.auth.backends.ModelBackend",  # this is default
    "arches.app.permissions.arches_permission_base.PermissionBackend",
    "arches.app.utils.external_oauth_backend.ExternalOauthAuthenticationBackend",
)

INSTALLED_APPS = (
    "webpack_loader",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django_hosts",
    "arches",
    "arches.app.models",
    "arches.management",
    "guardian",
    "captcha",
    "revproxy",
    "corsheaders",
    "oauth2_provider",
    "django_celery_results",
)

# Placing this last ensures any templates provided by Arches Applications
# take precedence over core arches templates in arches/app/templates.
INSTALLED_APPS += ("arches.app",)

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    #'arches.app.utils.middleware.TokenMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "arches.app.utils.middleware.ModifyAuthorizationHeader",
    "oauth2_provider.middleware.OAuth2TokenMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "arches.app.utils.middleware.SetAnonymousUser",
]

MIDDLEWARE.insert(  # this must resolve to first MIDDLEWARE entry
    0, "django_hosts.middleware.HostsRequestMiddleware"
)

MIDDLEWARE.append(  # this must resolve last MIDDLEWARE entry
    "django_hosts.middleware.HostsResponseMiddleware"
)

WEBPACK_LOADER = {
    "DEFAULT": {
        "STATS_FILE": os.path.join(ROOT_DIR, "..", "webpack/webpack-stats.json"),
    },
}

WEBPACK_DEVELOPMENT_SERVER_PORT = 9000

ROOT_URLCONF = "arches.urls"
ROOT_HOSTCONF = "arches.hosts"

DEFAULT_HOST = "arches"

WSGI_APPLICATION = "arches.wsgi.application"

try:
    CORS_ALLOW_HEADERS = list(default_headers) + [
        "x-authorization",
    ]
except Exception as e:
    if __name__ == "__main__":
        print(e)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
    },
    "handlers": {
        "file": {
            "level": "WARNING",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
            "class": "logging.FileHandler",
            "filename": os.path.join(ROOT_DIR, "arches.log"),
            "formatter": "console",
        },
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "loggers": {
        "arches": {
            "handlers": ["file", "console"],
            "level": "WARNING",
            "propagate": True,
        }
    },
}

LOGIN_URL = "auth"
# Rate limit for authentication views
# See options (including None or python callables):
# https://django-ratelimit.readthedocs.io/en/stable/rates.html#rates-chapter
RATE_LIMIT = "5/m"

PROFILE_LOG_BASE = os.path.join(ROOT_DIR, "logs")

BULK_IMPORT_BATCH_SIZE = 2000

SYSTEM_SETTINGS_LOCAL_PATH = os.path.join(
    ROOT_DIR, "db", "system_settings", "Arches_System_Settings_Local.json"
)
SYSTEM_SETTINGS_RESOURCE_ID = "a106c400-260c-11e7-a604-14109fd34195"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "arches.app.utils.password_validation.NumericPasswordValidator"
    },  # Passwords cannot be entirely numeric
    {
        "NAME": "arches.app.utils.password_validation.SpecialCharacterValidator",  # Passwords must contain special characters
        "OPTIONS": {
            "special_characters": ("!", "@", "#", ")", "(", "*", "&", "^", "%", "$")
        },
    },
    {
        "NAME": "arches.app.utils.password_validation.HasNumericCharacterValidator"
    },  # Passwords must contain 1 or more numbers
    {
        "NAME": "arches.app.utils.password_validation.HasUpperAndLowerCaseValidator"
    },  # Passwords must contain upper and lower characters
    {
        "NAME": "arches.app.utils.password_validation.MinLengthValidator",  # Passwords must meet minimum length requirement
        "OPTIONS": {"min_length": 9},
    },
]

USE_LIVERELOAD = False
LIVERELOAD_PORT = 35729  # usually only used in development, 35729 is default for livereload browser extensions

ENABLE_CAPTCHA = True
# RECAPTCHA_PUBLIC_KEY = ''
# RECAPTCHA_PRIVATE_KEY = ''
# RECAPTCHA_USE_SSL = False
NOCAPTCHA = True
# RECAPTCHA_PROXY = 'http://127.0.0.1:8000'
SILENCED_SYSTEM_CHECKS = ["guardian.W001"]

if DEBUG is True:
    SILENCED_SYSTEM_CHECKS += ["captcha.recaptcha_test_key_error"]

# group to assign users who self sign up via the web ui
USER_SIGNUP_GROUP = "Crowdsource Editor"

# external oauth configuration
EXTERNAL_OAUTH_CONFIGURATION = {
    "default_user_groups": [],
    "user_domains": [],
    "uid_claim": "",
    "app_id": "",
    "app_secret": "",
    "scopes": [],
    "authorization_endpoint": "",
    "validate_id_token": True,  # AVOID setting this to False
    "token_endpoint": "",
    "jwks_uri": "",
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    },
    "user_permission": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "user_permission_cache",
    },
}

DEFAULT_RESOURCE_IMPORT_USER = {"username": "admin", "userid": 1}

# Example of a custom time wheel configuration:
# TIMEWHEEL_DATE_TIERS = {
#     "name": "Millennium",
#     "interval": 1000,
#     "root": True,
#     "child": {
#             "name": "Cen",
#             "interval": 100,
#             "range": {"min": 1500, "max": 2000},
#             "child": {
#                 "name": "Decade",
#                 "interval": 10,
#                 "range": {"min": 1750, "max": 2000}
#           }
#       }
#   }
TIMEWHEEL_DATE_TIERS = None

# Identify the usernames and duration (seconds) for which you want to cache the timewheel
CACHE_BY_USER = {"default": 3600 * 24, "anonymous": 3600 * 24}  # 24hrs  # 24hrs

BYPASS_UNIQUE_CONSTRAINT_TILE_VALIDATION = False
BYPASS_REQUIRED_VALUE_TILE_VALIDATION = False

DATE_IMPORT_EXPORT_FORMAT = (
    "%Y-%m-%d"  # Custom date format for dates imported from and exported to csv
)

DATE_FORMATS = {
    # Keep index values the same for formats in the python and javascript arrays.
    "Python": [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d",
        "%Y-%m",
        "%Y",
        "-%Y",
    ],
    "JavaScript": [
        "YYYY-MM-DDTHH:mm:ss.sssZ",
        "YYYY-MM-DDTHH:mm:ssZ",
        "YYYY-MM-DD HH:mm:ssZ",
        "YYYY-MM-DD",
        "YYYY-MM",
        "YYYY",
        "-YYYY",
    ],
    "Elasticsearch": [
        "yyyy-MM-dd'T'HH:mm:ss.SSSZZZZZ",
        "yyyy-MM-dd'T'HH:mm:ss.SSSZ",
        "yyyy-MM-dd'T'HH:mm:ssZZZZZ",
        "yyyy-MM-dd'T'HH:mm:ssZ",
        "yyyy-MM-dd HH:mm:ssZZZZZ",
        "yyyy-MM-dd",
        "yyyy-MM",
        "yyyy",
        "-yyyy",
    ],
}

API_MAX_PAGE_SIZE = 500

UUID_REGEX = (
    "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)

OAUTH2_PROVIDER = {"ACCESS_TOKEN_EXPIRE_SECONDS": 604800}  # one week

#######################################
###       END STATIC SETTINGS       ###
#######################################


##########################################
###   RUN TIME CONFIGURABLE SETTINGS   ###
##########################################

PHONE_REGEX = r"^\+\d{8,15}$"
SEARCH_ITEMS_PER_PAGE = 5
SEARCH_EXPORT_LIMIT = 100000
SEARCH_EXPORT_IMMEDIATE_DOWNLOAD_THRESHOLD = 2000  # The maximum number of instances a user can download from search export without celery

# The maximum number of instances a user can download using HTML format from search export without celery
SEARCH_EXPORT_IMMEDIATE_DOWNLOAD_THRESHOLD_HTML_FORMAT = 10

RELATED_RESOURCES_PER_PAGE = 15
RELATED_RESOURCES_EXPORT_LIMIT = 10000
SEARCH_DROPDOWN_LENGTH = 100

# a lower number will give more "Fuzzy" matches, recomend between 0-4,
# see "prefix_length" at https://www.elastic.co/guide/en/elasticsearch/reference/6.7/query-dsl-fuzzy-query.html#_parameters_7
SEARCH_TERM_SENSITIVITY = 3

WORDS_PER_SEARCH_TERM = (
    10  # set to None for unlimited number of words allowed for search terms
)
SEARCH_RESULT_LIMIT = 10000  # should be less than or equal to elasticsearch configuration, index.max_result_window (default = 10,000)

ETL_USERNAME = "ETL"  # override this setting in your packages settings.py file

GOOGLE_ANALYTICS_TRACKING_ID = None

DEFAULT_GEOCODER = "10000000-0000-0000-0000-010000000000"

SPARQL_ENDPOINT_PROVIDERS = (
    {
        "SPARQL_ENDPOINT_PROVIDER": "arches.app.utils.data_management.sparql_providers.aat_provider.AAT_Provider"
    },
)

APP_NAME = "Arches"
APP_VERSION = None

APP_TITLE = "Arches | Heritage Data Management"
COPYRIGHT_TEXT = "All Rights Reserved."
COPYRIGHT_YEAR = "2016"

# Bounding box for geometry data validation. By default set to coordinate system bounding box.
# NOTE: This is not used by the front end of the application.
DATA_VALIDATION_BBOX = [(-180, -90), (-180, 90), (180, 90), (180, -90), (-180, -90)]

RESOURCE_GRAPH_LOCATIONS = (
    # Put strings here, like "/home/data/resource_graphs" or "C:/data/resource_graphs".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT_DIR, "db", "graphs", "branches"),
    os.path.join(ROOT_DIR, "db", "graphs", "resource_models"),
)

BUSINESS_DATA_FILES = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

PERMISSION_LOCATIONS = [
    "arches.app.permissions",
]
DATATYPE_LOCATIONS = [
    "arches.app.datatypes",
]
FUNCTION_LOCATIONS = [
    "arches.app.functions",
]
SEARCH_COMPONENT_LOCATIONS = [
    "arches.app.search.components",
]

ETL_MODULE_LOCATIONS = [
    "arches.app.etl_modules",
]

FILE_TYPE_CHECKING = "lenient"
FILE_TYPES = [
    "bmp",
    "gif",
    "jpg",
    "jpeg",
    "json",
    "pdf",
    "png",
    "psd",
    "rtf",
    "tif",
    "tiff",
    "xlsx",
    "csv",
    "zip",
]
FILENAME_GENERATOR = "arches.app.utils.storage_filename_generator.generate_filename"
UPLOADED_FILES_DIR = "uploadedfiles"

MAPBOX_API_KEY = ""  # Put your Mapbox key here!

# links to sprites and glyphs for use on map
MAPBOX_SPRITES = "mapbox://sprites/mapbox/basic-v9"
MAPBOX_GLYPHS = "mapbox://fonts/mapbox/{fontstack}/{range}.pbf"

DEFAULT_MAP_ZOOM = 0
MAP_MIN_ZOOM = 0
MAP_MAX_ZOOM = 20

# Map filter auto adjusts map extent to fit results. If False, map extent will not change when filtering results.
MAP_FILTER_AUTO_ZOOM_ENABLED = True

# If True, users can make edits to graphs that are locked
# (generally because they have resource intances saved against them)
# Changing this setting to True and making graph modifications may result in
# disagreement between your Resource Models and Resource Instances potentially
# causing your application to break.
OVERRIDE_RESOURCE_MODEL_LOCK = False

# If True, allows users to selectively enable two-factor authentication
ENABLE_TWO_FACTOR_AUTHENTICATION = False

# If True, users cannot log in unless they have enabled two-factor authentication
FORCE_TWO_FACTOR_AUTHENTICATION = False

# bounds for search results hex binning fabric (search grid).
# a smaller bbox will give you less distortion in hexes and better performance
DEFAULT_BOUNDS = {
    "type": "FeatureCollection",
    "features": [
        {
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [[-122, -52], [128, -52], [128, 69], [-122, 69], [-122, -52]]
                ],
            },
            "type": "Feature",
            "properties": {},
        }
    ],
}

# size to use for hex binning search results on map (in km)
HEX_BIN_SIZE = 100
# binning uses elasticsearch GeoHash grid aggregation.
# precision for binning is set based on GeoHash precision, see this table:
# https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-geohashgrid-aggregation.html#_cell_dimensions_at_the_equator
# high precision binning may result in performance issues.
HEX_BIN_PRECISION = 4

ALLOWED_POPUP_HOSTS = []

TILESERVER_URL = None

CELERY_BROKER_URL = ""  # RabbitMQ --> "amqp://guest:guest@localhost",  Redis --> "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_BACKEND = (
    "django-db"  # Use 'django-cache' if you want to use your cache as your backend
)
CELERY_TASK_SERIALIZER = "json"
CELERY_SEARCH_EXPORT_EXPIRES = 24 * 3600  # seconds
CELERY_SEARCH_EXPORT_CHECK = 3600  # seconds

CELERY_BEAT_SCHEDULE = {
    "delete-expired-search-export": {
        "task": "arches.app.tasks.delete_file",
        "schedule": CELERY_SEARCH_EXPORT_CHECK,
    },
    "notification": {
        "task": "arches.app.tasks.message",
        "schedule": CELERY_SEARCH_EXPORT_CHECK,
        "args": ("Celery Beat is Running",),
    },
}

# Set to True if you want to send celery tasks to the broker without being able to detect celery.
# This might be necessary if the worker pool is regulary fully active, with no idle workers, or if
# you need to run the celery task using solo pool (e.g. on Windows). You may need to provide another
# way of monitoring celery so you can detect the background task not being available.
CELERY_CHECK_ONLY_INSPECT_BROKER = False

AUTO_REFRESH_GEOM_VIEW = True
TILE_CACHE_TIMEOUT = 600  # seconds
CLUSTER_DISTANCE_MAX = 5000  # meters
GRAPH_MODEL_CACHE_TIMEOUT = None  # seconds * hours * days = ~1mo

CANTALOUPE_DIR = os.path.join(ROOT_DIR, UPLOADED_FILES_DIR)
CANTALOUPE_HTTP_ENDPOINT = "http://localhost:8182/"

ACCESSIBILITY_MODE = False

# Dictionary containing any additional context items for customising email templates
with suppress(NameError):  # need to suppress i18n NameError for test runner
    EXTRA_EMAIL_CONTEXT = {
        "salutation": _("Hi"),
        "expiration": (
            datetime.now() + timedelta(seconds=CELERY_SEARCH_EXPORT_EXPIRES)
        ).strftime("%A, %d %B %Y"),
    }

RENDERERS = [
    {
        "name": "imagereader",
        "title": "Image Reader",
        "description": "Displays most image file types",
        "id": "5e05aa2e-5db0-4922-8938-b4d2b7919733",
        "iconclass": "fa fa-camera",
        "component": "views/components/cards/file-renderers/imagereader",
        "ext": "",
        "type": "image/*",
        "exclude": "tif,tiff,psd",
    },
    {
        "name": "pdfreader",
        "title": "PDF Reader",
        "description": "Displays pdf files",
        "id": "09dec059-1ee8-4fbd-85dd-c0ab0428aa94",
        "iconclass": "fa fa-file",
        "component": "views/components/cards/file-renderers/pdfreader",
        "ext": "pdf",
        "type": "application/pdf",
        "exclude": "tif,tiff,psd",
    },
]

# --- JSON LD sortorder generating functions --- #
#
# The functions in the array below will be called in the order given with the json-ld of the node
#   that should have sortorder set on the resulting tile.  The config below sorts (meaninglessly)
#   by URI, however more complex, use case specific functions can be implemented based on local
#   ontology choice and requirements. Examples might be to sort by some value, language (as shown),
#   type, classification or any other feature.
# Set JSON_LD_SORT to True to enable the sorting
#
# Example: This would sort fields by P72_has_language, and apply an order based on the referenced
#          entity in the lookup hash
#
# JSON_LD_SORT_LANGUAGE = {None: 10000, 'urn:uuid:38729dbe-6d1c-48ce-bf47-e2a18945600e': 0,
#    "urn:uuid:a1d82c77-ebd6-4215-ab85-2c0b6a68a0e8": 1,
#    'urn:uuid:7e6c493b-6434-4b3a-9513-02df44b78d24': 2}
# JSON_LD_SORT_LANGUAGE_PROP = 'http://www.cidoc-crm.org/cidoc-crm/P72_has_language'
#
# def langsort(x):
#    langs = x._json_ld.get(JSON_LD_SORT_LANGUAGE_PROP,[{'@id': None}])
#    if not langs or not '@id' in langs[0]:
#        langs = [{'@id':None}]
#    scores = [JSON_LD_SORT_LANGUAGE.get(x['@id'], 10000) for x in langs]
#    return min(scores)

JSON_LD_SORT = False
JSON_LD_SORT_FUNCTIONS = [lambda x: x.get("@id", "~")]

# --- JSON LD run-time data manipulation --- #
#
# This function will be applied to the data to be loaded, immediately before it is sent to the
#   Reader to be processed. This can correct any errors in the data, or potentially do some
#   significant series of transformations to get the data into the right form for Arches


def JSON_LD_FIX_DATA_FUNCTION(data, jsdata, model):
    return jsdata


# If either of the following PERMISSION settings is changed, you must run a reindex.
PERMISSION_FRAMEWORK = "arches_default_allow.ArchesDefaultAllowPermissionFramework"

PERMISSION_DEFAULTS = {}
# PERMISSION_DEFAULTS = {
#     "graphid": [{"id": "1", "type": "user", "permissions": ["no_access_to_resourceinstance"]}]
# }

##########################################
### END RUN TIME CONFIGURABLE SETTINGS ###
##########################################

try:
    from .settings_local import *
except ImportError:
    try:
        from arches.settings_local import *
    except ImportError:
        pass
