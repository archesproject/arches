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

import os
import inspect


#########################################
###          STATIC SETTINGS          ###
#########################################

MODE = 'PROD' #options are either "PROD" or "DEV" (installing with Dev mode set, gets you extra dependencies)
DEBUG = True
INTERNAL_IPS = ('127.0.0.1',)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'arches',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'postgis',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
        'POSTGIS_TEMPLATE': 'template_postgis_20',
    }
}

# from http://django-guardian.readthedocs.io/en/stable/configuration.html#anonymous-user-name
ANONYMOUS_USER_NAME = None

ELASTICSEARCH_HTTP_PORT = 9200 # this should be in increments of 200, eg: 9400, 9600, 9800
SEARCH_BACKEND = 'arches.app.search.search.SearchEngine'
# see http://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch
ELASTICSEARCH_HOSTS = [
    {'host': 'localhost', 'port': ELASTICSEARCH_HTTP_PORT}
]
ELASTICSEARCH_CONNECTION_OPTIONS = {'timeout': 30}
# a prefix to append to all elasticsearch indexes, note: must be lower case
ELASTICSEARCH_PREFIX = ''

USE_SEMANTIC_RESOURCE_RELATIONSHIPS = True
ROOT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PACKAGE_ROOT = ROOT_DIR
PACKAGE_NAME = PACKAGE_ROOT.split(os.sep)[-1]
RESOURCE_IMPORT_LOG = 'arches/logs/resource_import.log'

RESOURCE_FORMATERS = {
    'csv': 'arches.app.utils.data_management.resources.formats.csvfile.CsvWriter',
    'json': 'arches.app.utils.data_management.resources.formats.archesjson.JsonWriter',
    'xml': 'arches.app.utils.data_management.resources.formats.rdffile.RdfWriter',
    'pretty-xml': 'arches.app.utils.data_management.resources.formats.rdffile.RdfWriter',
    'json-ld': 'arches.app.utils.data_management.resources.formats.rdffile.JsonLdWriter',
    'n3': 'arches.app.utils.data_management.resources.formats.rdffile.RdfWriter',
    'nt': 'arches.app.utils.data_management.resources.formats.rdffile.RdfWriter',
    'trix': 'arches.app.utils.data_management.resources.formats.rdffile.RdfWriter',
    'rdfa': 'arches.app.utils.data_management.resources.formats.rdffile.RdfWriter'
}

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

# Set the ontolgoy namespace prefixes to use in the UI, set the namespace to '' omit a prefix
# Users can also override existing namespaces as well if you like
ONTOLOGY_NAMESPACES = {
    #'http://my_namespace_here/': 'some_ns',
    #'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'RDF' <-- note the all caps
    'http://www.cidoc-crm.org/cidoc-crm/': '',
    'http://www.ics.forth.gr/isl/CRMarchaeo/': '',
    'http://www.ics.forth.gr/isl/CRMdig/': '',
    'http://www.ics.forth.gr/isl/CRMgeo/': '',
    'http://www.ics.forth.gr/isl/CRMinf/': '',
    'http://www.ics.forth.gr/isl/CRMsci/': '',
}

# A context to supply for use in export of resource instances in JSON-LD format
JSON_LD_CONTEXT = {
    # "crm": "http://www.cidoc-crm.org/cidoc-crm/",
    # "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    # "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    # "dc": "http://purl.org/dc/elements/1.1/",
    # "dcterms": "http://purl.org/dc/terms/",
    # "schema": "http://schema.org/",
    # "skos": "http://www.w3.org/2004/02/skos/core#",
    # "foaf": "http://xmlns.com/foaf/0.1/",
    # "xsd": "http://www.w3.org/2001/XMLSchema#",
    # "pi": "http://linked.art/ns/prov/",
    # "aat": "http://vocab.getty.edu/aat/",
    # "ulan": "http://vocab.getty.edu/ulan/",
    # "tgn": "http://vocab.getty.edu/tgn/",
    # "id": "@id",
    # "type": "@type",
    # "Period": "crm:E4_Period",
    # "Event": "crm:E5_Event",
    # "Activity": "crm:E7_Activity",
    # "identified_by": {
    #     "@id": "crm:P1_is_identified_by",
    #     "@type": "@id",
    #     "@container": "@set"
    # },
    # "identifies": {
    #     "@id": "crm:P1i_identifies",
    #     "@type": "@id"
    # }
}

# This is the namespace to use for export of data (for RDF/XML for example)
# Ideally this should point to the url where you host your site
ARCHES_NAMESPACE_FOR_DATA_EXPORT = 'http://localhost/'

PREFERRED_COORDINATE_SYSTEMS = (
    {"name": "Geographic", "srid": "4326", "proj4": "+proj=longlat +datum=WGS84 +no_defs", "default": True}, #Required
)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  #<-- Only need to uncomment this for testing without an actual email server
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'xxxx@xxx.com'
# EMAIL_HOST_PASSWORD = 'xxxxxxx'
# EMAIL_PORT = 587

POSTGIS_VERSION = (2, 0, 0)

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
TIME_ZONE = 'America/Chicago'
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
LANGUAGE_CODE = 'en-US'

# the path where your translation strings are stored
LOCALE_PATHS = (
    os.path.join(ROOT_DIR, 'locale'),
)

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT =  os.path.join(ROOT_DIR)

# URL that handles the media served from MEDIA_ROOT, used for managing stored files.
# It must end in a slash if set to a non-empty value.
MEDIA_URL = '/files/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/media/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT_DIR, 'app', 'media'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'c7ky-mc6vdnv+avp0r@(a)8y^51ex=25nogq@+q5$fnc*mxwdi'
JWT_KEY = SECRET_KEY
JWT_TOKEN_EXPIRATION = 50 #days before the token becomes stale
JWT_ALGORITHM = 'HS256'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
            os.path.join(ROOT_DIR, 'app', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'arches.app.utils.context_processors.livereload',
                'arches.app.utils.context_processors.map_info',
                'arches.app.utils.context_processors.app_settings',
            ],
            'debug': DEBUG
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'guardian.backends.ObjectPermissionBackend',
    'arches.app.utils.permission_backend.PermissionBackend',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'arches',
    'arches.app.models',
    'arches.management',
    'guardian',
    'captcha'
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'arches.app.utils.middleware.TokenMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'arches.app.utils.middleware.JWTAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'arches.app.utils.middleware.SetAnonymousUser',
]

ROOT_URLCONF = 'arches.urls'

WSGI_APPLICATION = 'arches.wsgi.application'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(ROOT_DIR, 'arches.log'),
        },
    },
    'loggers': {
        'arches': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

LOGIN_URL = 'auth'

PROFILE_LOG_BASE = os.path.join(ROOT_DIR, 'logs')

BULK_IMPORT_BATCH_SIZE = 2000

SYSTEM_SETTINGS_LOCAL_PATH = os.path.join(ROOT_DIR, 'db', 'system_settings', 'Arches_System_Settings_Local.json')

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'arches.app.utils.password_validation.NumericPasswordValidator', #Passwords cannot be entirely numeric
    },
    {
        'NAME': 'arches.app.utils.password_validation.SpecialCharacterValidator', #Passwords must contain special characters
        'OPTIONS': {
            'special_characters': ('!','@','#',')','(','*','&','^','%','$'),
        }
    },
    {
        'NAME': 'arches.app.utils.password_validation.HasNumericCharacterValidator', #Passwords must contain 1 or more numbers
    },
    {
        'NAME': 'arches.app.utils.password_validation.HasUpperAndLowerCaseValidator', #Passwords must contain upper and lower characters
    },
    {
        'NAME': 'arches.app.utils.password_validation.MinLengthValidator', #Passwords must meet minimum length requirement
        'OPTIONS': {
            'min_length': 9,
        }
    },
]

USE_LIVERELOAD = False
LIVERELOAD_PORT = 35729 # usually only used in development, 35729 is default for livereload browser extensions

ENABLE_CAPTCHA = True
# RECAPTCHA_PUBLIC_KEY = ''
# RECAPTCHA_PRIVATE_KEY = ''
# RECAPTCHA_USE_SSL = False
NOCAPTCHA = True
# RECAPTCHA_PROXY = 'http://127.0.0.1:8000'

# group to assign users who self sign up via the web ui
USER_SIGNUP_GROUP = 'Crowdsource Editor'

#######################################
###       END STATIC SETTINGS       ###
#######################################



##########################################
###   RUN TIME CONFIGURABLE SETTINGS   ###
##########################################

PHONE_REGEX = r'^\+\d{8,15}$'
SEARCH_ITEMS_PER_PAGE = 5
SEARCH_EXPORT_ITEMS_PER_PAGE = 100000
RELATED_RESOURCES_PER_PAGE = 15
RELATED_RESOURCES_EXPORT_LIMIT = 10000
SEARCH_DROPDOWN_LENGTH = 100
WORDS_PER_SEARCH_TERM = 10 # set to None for unlimited number of words allowed for search terms

ETL_USERNAME = 'ETL' # override this setting in your packages settings.py file

GOOGLE_ANALYTICS_TRACKING_ID = None

DEFAULT_GEOCODER = "10000000-0000-0000-0000-010000000000"

SPARQL_ENDPOINT_PROVIDERS = (
    {'SPARQL_ENDPOINT_PROVIDER':'arches.app.utils.data_management.sparql_providers.aat_provider.AAT_Provider'},
)

APP_NAME = 'Arches'

APP_TITLE = 'Arches | Heritage Data Management'
COPYRIGHT_TEXT = 'All Rights Reserved.'
COPYRIGHT_YEAR = '2016'

# Bounding box for geometry data validation. By default set to coordinate system bounding box.
# NOTE: This is not used by the front end of the application.
DATA_VALIDATION_BBOX = [(-180,-90), (-180,90), (180,90), (180,-90), (-180,-90)]

RESOURCE_GRAPH_LOCATIONS = (
    # Put strings here, like "/home/data/resource_graphs" or "C:/data/resource_graphs".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT_DIR, 'db', 'graphs', 'branches'),
    os.path.join(ROOT_DIR, 'db', 'graphs', 'resource_models'),
)

BUSINESS_DATA_FILES = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

DATATYPE_LOCATIONS = ['arches.app.datatypes',]
FUNCTION_LOCATIONS = ['arches.app.functions',]
# If you are manually managing your resource tile cache, you may want to "seed"
# the cache (or prerender some tiles) for low zoom levels.  You can do this by
# running:
# python manage.py packages -o seed_resource_tile_cache
#
# The following settings control the extent and max zoom level to which tiles
# will be seeded.  Be aware, seeding tiles at high zoom levels (more zoomed in)
# will take a long time
CACHE_SEED_BOUNDS = (-122.0, -52.0, 128.0, 69.0)
CACHE_SEED_MAX_ZOOM = 5

# configure where the tileserver should store its cache
TILE_CACHE_CONFIG = {
    "name": "Disk",
    "path": os.path.join(ROOT_DIR, 'tileserver', 'cache')

    # to reconfigure to use S3 (recommended for production), use the following
    # template:

    # "name": "S3",
    # "bucket": "<bucket name>",
    # "access": "<access key>",
    # "secret": "<secret key>"
}

MAPBOX_API_KEY = '' # Put your Mapbox key here!

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
    "features": [{
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-122, -52],
                    [128, -52],
                    [128, 69],
                    [-122, 69],
                    [-122, -52]
                ]
            ]
        },
        "type": "Feature",
        "properties": {}
    }]
}

# size to use for hex binning search results on map (in km)
HEX_BIN_SIZE = 100
# binning uses elasticsearch GeoHash grid aggregation.
# precision for binning is set based on GeoHash precision, see this table:
# https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-geohashgrid-aggregation.html#_cell_dimensions_at_the_equator
# high precision binning may result in performance issues.
HEX_BIN_PRECISION = 4

##########################################
### END RUN TIME CONFIGURABLE SETTINGS ###
##########################################


try:
    from settings_local import *
except ImportError:
    pass
