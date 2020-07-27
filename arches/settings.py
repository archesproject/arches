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
import inspect


try:
    from corsheaders.defaults import default_headers
except ImportError:  # unable to import corsheaders prior to installing requirements.txt in setup.py
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

PG_SUPERUSER = ""
PG_SUPERUSER_PW = ""

COUCHDB_URL = "http://admin:admin@localhost:5984"  # defaults to localhost:5984

# from http://django-guardian.readthedocs.io/en/stable/configuration.html#anonymous-user-name
ANONYMOUS_USER_NAME = None

ELASTICSEARCH_HTTP_PORT = 9200  # this should be in increments of 200, eg: 9400, 9600, 9800
ELASTICSEARCH_TEMP_HTTP_ENDPOINT = "http://localhost:9800"
SEARCH_BACKEND = "arches.app.search.search.SearchEngine"
# see http://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch
ELASTICSEARCH_HOSTS = [{"host": "localhost", "port": ELASTICSEARCH_HTTP_PORT}]
ELASTICSEARCH_CONNECTION_OPTIONS = {"timeout": 30}
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
#     'name': 'my_new_custom_index'
# }]

USE_SEMANTIC_RESOURCE_RELATIONSHIPS = True
ROOT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PACKAGE_ROOT = ROOT_DIR
PACKAGE_NAME = PACKAGE_ROOT.split(os.sep)[-1]
RESOURCE_IMPORT_LOG = "arches/logs/resource_import.log"

RESOURCE_FORMATTERS = {
    "csv": "arches.app.utils.data_management.resources.formats.csvfile.CsvWriter",
    "json": "arches.app.utils.data_management.resources.formats.archesfile.ArchesFileWriter",
    "tilecsv": "arches.app.utils.data_management.resources.formats.csvfile.TileCsvWriter",
    "shp": "arches.app.utils.data_management.resources.formats.shpfile.ShpWriter",
    "xml": "arches.app.utils.data_management.resources.formats.rdffile.RdfWriter",
    "pretty-xml": "arches.app.utils.data_management.resources.formats.rdffile.RdfWriter",
    "json-ld": "arches.app.utils.data_management.resources.formats.rdffile.JsonLdWriter",
    "n3": "arches.app.utils.data_management.resources.formats.rdffile.RdfWriter",
    "nt": "arches.app.utils.data_management.resources.formats.rdffile.RdfWriter",
    "trix": "arches.app.utils.data_management.resources.formats.rdffile.RdfWriter",
}

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
PREFERRED_CONCEPT_SCHEMES = ["http://vocab.getty.edu/aat/", "http://www.cidoc-crm.org/cidoc-crm/"]
JSONLD_CONTEXT_CACHE_TIMEOUT = 43800  # in minutes (43800 minutes ~= 1 month)

# This is the namespace to use for export of data (for RDF/XML for example)
# Ideally this should point to the url where you host your site
# Make sure to use a trailing slash
ARCHES_NAMESPACE_FOR_DATA_EXPORT = "http://localhost:8000/"

RDM_JSONLD_CONTEXT = {"arches": ARCHES_NAMESPACE_FOR_DATA_EXPORT}

PREFERRED_COORDINATE_SYSTEMS = (
    {"name": "Geographic", "srid": "4326", "proj4": "+proj=longlat +datum=WGS84 +no_defs", "default": True},  # Required
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
# EMAIL_HOST_USER = 'xxxx@xxx.com'
# EMAIL_HOST_PASSWORD = 'xxxxxxx'
# EMAIL_PORT = 587

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

# Default Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html

# see https://docs.djangoproject.com/en/1.9/topics/i18n/translation/#how-django-discovers-language-preference
# to see how LocaleMiddleware tries to determine the user's language preference
# (make sure to check your accept headers as they will override the LANGUAGE_CODE setting!)
# also see get_language_from_request in django.utils.translation.trans_real.py
# to see how the language code is derived in the actual code
#
# make sure to uncomment the Middleware class 'LocaleMiddleware'
#
# https://docs.djangoproject.com/en/1.9/ref/django-admin/#makemessages
#
# run
# django-admin.py makemessages --ignore=virtualenv/* --local=en --extension=htm,py
# django-admin.py compilemessages
LANGUAGE_CODE = "en-US"

# the path where your translation strings are stored
LOCALE_PATHS = [
    os.path.join(ROOT_DIR, "locale"),
]

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(ROOT_DIR)

# Sets default max upload size to 15MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 15728640

# URL that handles the media served from MEDIA_ROOT, used for managing stored files.
# It must end in a slash if set to a non-empty value.
MEDIA_URL = "/files/"

# By setting RESTRICT_MEDIA_ACCESS to True, media file requests will be
# served by Django rather than your web server (e.g. Apache). This allows file requests to be checked against nodegroup permissions.
# However, this will adversely impact performace when serving large files or during periods of high traffic.
RESTRICT_MEDIA_ACCESS = False

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ""

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/media/"

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = "/media/admin/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT_DIR, "app", "media"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = "c7ky-mc6vdnv+avp0r@(a)8y^51ex=25nogq@+q5$fnc*mxwdi"
JWT_KEY = SECRET_KEY
JWT_TOKEN_EXPIRATION = 50  # days before the token becomes stale
JWT_ALGORITHM = "HS256"

# OAuth settings
# https://django-oauth-toolkit.readthedocs.io/en/latest/settings.html
OAUTH2_PROVIDER = {"ACCESS_TOKEN_EXPIRE_SECONDS": 36000}

# This is the client id you get when you register a new application
# see https://arches.readthedocs.io/en/stable/api/#authentication
MOBILE_OAUTH_CLIENT_ID = ""  #'9JCibwrWQ4hwuGn5fu2u1oRZSs9V6gK8Vu8hpRC4'
MOBILE_DEFAULT_ONLINE_BASEMAP = {"default": "mapbox://styles/mapbox/streets-v9"}
MOBILE_IMAGE_SIZE_LIMITS = {
    # These limits are meant to be approximates. Expect to see uploaded sizes range +/- 20%
    # Not to exceed the limit defined in DATA_UPLOAD_MAX_MEMORY_SIZE
    "full": min(1500000, DATA_UPLOAD_MAX_MEMORY_SIZE),  # ~1.5 Mb
    "thumb": 400,  # max width/height in pixels, this will maintain the aspect ratio of the original image
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # insert your TEMPLATE_DIRS here
            os.path.join(ROOT_DIR, "app", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "arches.app.utils.context_processors.livereload",
                "arches.app.utils.context_processors.map_info",
                "arches.app.utils.context_processors.app_settings",
            ],
            "debug": DEBUG,
        },
    },
]

AUTHENTICATION_BACKENDS = (
    "arches.app.utils.email_auth_backend.EmailAuthenticationBackend",
    "oauth2_provider.backends.OAuth2Backend",
    "django.contrib.auth.backends.ModelBackend",  # this is default
    "guardian.backends.ObjectPermissionBackend",
    "arches.app.utils.permission_backend.PermissionBackend",
)

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "arches",
    "arches.app.models",
    "arches.management",
    "guardian",
    "captcha",
    "revproxy",
    "corsheaders",
    "oauth2_provider",
    "django_celery_results"
    # 'debug_toolbar'
)

MIDDLEWARE = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    #'arches.app.utils.middleware.TokenMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "arches.app.utils.middleware.ModifyAuthorizationHeader",
    "oauth2_provider.middleware.OAuth2TokenMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "arches.app.utils.middleware.SetAnonymousUser",
]

ROOT_URLCONF = "arches.urls"

WSGI_APPLICATION = "arches.wsgi.application"

CORS_ORIGIN_ALLOW_ALL = True

try:
    CORS_ALLOW_HEADERS = list(default_headers) + [
        "x-authorization",
    ]
except Exception as e:
    print(e)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"console": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",},},
    "handlers": {
        "file": {
            "level": "WARNING",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
            "class": "logging.FileHandler",
            "filename": os.path.join(ROOT_DIR, "arches.log"),
            "formatter": "console",
        },
        "console": {"level": "WARNING", "class": "logging.StreamHandler", "formatter": "console"},
    },
    "loggers": {"arches": {"handlers": ["file", "console"], "level": "WARNING", "propagate": True}},
}

LOGIN_URL = "auth"

PROFILE_LOG_BASE = os.path.join(ROOT_DIR, "logs")

BULK_IMPORT_BATCH_SIZE = 2000

SYSTEM_SETTINGS_LOCAL_PATH = os.path.join(ROOT_DIR, "db", "system_settings", "Arches_System_Settings_Local.json")
SYSTEM_SETTINGS_RESOURCE_ID = "a106c400-260c-11e7-a604-14109fd34195"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "arches.app.utils.password_validation.NumericPasswordValidator"},  # Passwords cannot be entirely numeric
    {
        "NAME": "arches.app.utils.password_validation.SpecialCharacterValidator",  # Passwords must contain special characters
        "OPTIONS": {"special_characters": ("!", "@", "#", ")", "(", "*", "&", "^", "%", "$")},
    },
    {"NAME": "arches.app.utils.password_validation.HasNumericCharacterValidator"},  # Passwords must contain 1 or more numbers
    {"NAME": "arches.app.utils.password_validation.HasUpperAndLowerCaseValidator"},  # Passwords must contain upper and lower characters
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
if DEBUG is True:
    SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]

# group to assign users who self sign up via the web ui
USER_SIGNUP_GROUP = "Crowdsource Editor"

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "unique-snowflake"}}

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
CACHE_BY_USER = {"anonymous": 3600 * 24}

DATE_IMPORT_EXPORT_FORMAT = "%Y-%m-%d"  # Custom date format for dates imported from and exported to csv

DATE_FORMATS = {
    "Python": ["-%Y", "%Y", "%Y-%m", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"],
    "JavaScript": ["-YYYY", "YYYY", "YYYY-MM", "YYYY-MM-DD", "YYYY-MM-DDTHH:mm:ssZ", "YYYY-MM-DDTHH:mm:ss.sssZ"],
    "Elasticsearch": [
        "-yyyy",
        "yyyy",
        "yyyy-MM",
        "yyyy-MM-dd",
        "yyyy-MM-dd'T'HH:mm:ssZ",
        "yyyy-MM-dd'T'HH:mm:ssZZZZZ",
        "yyyy-MM-dd'T'HH:mm:ss.SSSZ",
        "yyyy-MM-dd'T'HH:mm:ss.SSSZZZZZ",
    ],
}

API_MAX_PAGE_SIZE = 500

UUID_REGEX = "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"

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
RELATED_RESOURCES_PER_PAGE = 15
RELATED_RESOURCES_EXPORT_LIMIT = 10000
SEARCH_DROPDOWN_LENGTH = 100

# a lower number will give more "Fuzzy" matches, recomend between 0-4,
# see "prefix_length" at https://www.elastic.co/guide/en/elasticsearch/reference/6.7/query-dsl-fuzzy-query.html#_parameters_7
SEARCH_TERM_SENSITIVITY = 3

WORDS_PER_SEARCH_TERM = 10  # set to None for unlimited number of words allowed for search terms
SEARCH_RESULT_LIMIT = 10000  # should be less than or equal to elasticsearch configuration, index.max_result_window (default = 10,000)

ETL_USERNAME = "ETL"  # override this setting in your packages settings.py file

GOOGLE_ANALYTICS_TRACKING_ID = None

DEFAULT_GEOCODER = "10000000-0000-0000-0000-010000000000"

SPARQL_ENDPOINT_PROVIDERS = ({"SPARQL_ENDPOINT_PROVIDER": "arches.app.utils.data_management.sparql_providers.aat_provider.AAT_Provider"},)

APP_NAME = "Arches"

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

DATATYPE_LOCATIONS = [
    "arches.app.datatypes",
]
FUNCTION_LOCATIONS = [
    "arches.app.functions",
]
SEARCH_COMPONENT_LOCATIONS = [
    "arches.app.search.components",
]

MAPBOX_API_KEY = ""  # Put your Mapbox key here!

# links to sprites and glyphs for use on map
MAPBOX_SPRITES = "mapbox://sprites/mapbox/basic-v9"
MAPBOX_GLYPHS = "mapbox://fonts/mapbox/{fontstack}/{range}.pbf"

DEFAULT_MAP_ZOOM = 0
MAP_MIN_ZOOM = 0
MAP_MAX_ZOOM = 20

# If True, users can make edits to graphs that are locked
# (generally because they have resource intances saved against them)
# Changing this setting to True and making graph modifications may result in
# disagreement between your Resource Models and Resource Instances potentially
# causing your application to break.
OVERRIDE_RESOURCE_MODEL_LOCK = False

# bounds for search results hex binning fabric (search grid).
# a smaller bbox will give you less distortion in hexes and better performance
DEFAULT_BOUNDS = {
    "type": "FeatureCollection",
    "features": [
        {
            "geometry": {"type": "Polygon", "coordinates": [[[-122, -52], [128, -52], [128, 69], [-122, 69], [-122, -52]]]},
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

CELERY_BROKER_URL = "amqp://guest:guest@localhost"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_BACKEND = "django-db"  # Use 'django-cache' if you want to use your cache as your backend
CELERY_TASK_SERIALIZER = "json"
CELERY_SEARCH_EXPORT_EXPIRES = 24 * 3600  # seconds
CELERY_SEARCH_EXPORT_CHECK = 3600  # seconds

CELERY_BEAT_SCHEDULE = {
    "delete-expired-search-export": {"task": "arches.app.tasks.delete_file", "schedule": CELERY_SEARCH_EXPORT_CHECK},
    "notification": {"task": "arches.app.tasks.message", "schedule": CELERY_SEARCH_EXPORT_CHECK, "args": ("Celery Beat is Running",)},
}

AUTO_REFRESH_GEOM_VIEW = True
TILE_CACHE_TIMEOUT = 600  # seconds
GRAPH_MODEL_CACHE_TIMEOUT = None  # seconds * hours * days = ~1mo

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
    }
]

##########################################
### END RUN TIME CONFIGURABLE SETTINGS ###
##########################################

try:
    from .settings_local import *
except ImportError as e:
    print(e)
    print("Error attempting to load settings from relative '.settings_local'. Attempting 'arches.settings_local' import")
    try:
        from arches.settings_local import *
    except ImportError as e:
        print("Error attempting to load settings from 'arches.settings_local.py'.")
        print(e)
