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
# Django settings for Arches project.

MODE = 'PROD' #options are either "PROD" or "DEV" (installing with Dev mode set, get's you extra dependencies)
DEBUG = True
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1',)

#########################################
###  START PACKAGE SPECIFIC SETTINGS  ###
#########################################

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'arches',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'postgis',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
        'SCHEMAS': 'public,data,ontology,concepts', # syncdb will put the admin tables in the first listed schema,
        'POSTGIS_TEMPLATE': 'template_postgis_20',
    }
}

ENTITY_MODEL = {
    # override this setting in your packages settings.py file
    # to set the default model for the system to use
    # Your model needs to inherit from 'arches.app.models.entity.Entity' to work
    'default': 'arches.app.models.entity.Entity'
}


ELASTICSEARCH_HTTP_PORT = 9200 # this should be in increments of 200, eg: 9400, 9600, 9800
SEARCH_BACKEND = 'arches.app.search.search.SearchEngine'
# see http://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.Elasticsearch
ELASTICSEARCH_HOSTS = [
    {'host': 'localhost', 'port': ELASTICSEARCH_HTTP_PORT}
]
ELASTICSEARCH_CONNECTION_OPTIONS = {'timeout': 30}


SEARCH_ITEMS_PER_PAGE = 5
SEARCH_DROPDOWN_LENGTH = 100
WORDS_PER_SEARCH_TERM = 10 # set to None for unlimited number of words allowed for search terms

DISPLAY_NAME_FOR_UNNAMED_ENTITIES = 'Unnamed Resource' # override this setting in your packages settings.py file

# override this setting in your packages settings.py file
# entity type that holds the spatial coordinates of resources
ENTITY_TYPE_FOR_MAP_DISPLAY = ''

LIMIT_ENTITY_TYPES_TO_LOAD = None #(
    # override this setting in your packages settings.py file
#    'ARCHAEOLOGICAL HERITAGE (ARTIFACT).E18',
#)

DATA_CONCEPT_SCHEME = ''

ETL_USERNAME = 'ETL' # override this setting in your packages settings.py file

LIVERELOAD_PORT = 35729 # usually only used in development, 35729 is default for livereload browser extensions

DEFAULT_MAP_X = 0
DEFAULT_MAP_Y = 0
DEFAULT_MAP_ZOOM = 0
MAP_MIN_ZOOM = 0.0005831682455839253
MAP_MAX_ZOOM = 156543.03392804097
MAP_LAYER_FEATURE_LIMIT = 100000

BING_KEY = 'Ak-dzM4wZjSqTlzveKz5u0d4IQ4bRzVI309GxmkgSVr1ewS6iPSrOvOKhA-CJlm3'

RESOURCE_TYPE_CONFIGS = {
    # override this setting in your packages settings.py file
    #
    # 'HERITAGE_RESOURCE.E18': {
    #     'resourcetypeid': 'HERITAGE_RESOURCE.E18',
    #     'name': _('Heritage Resource'),
    #     'icon_class': 'fa fa-trophy',
    #     'default_page': 'summary',
    #     'description': _('INSERT RESOURCE DESCRIPTION HERE'),
    #     'categories': [_('Resource')],
    #     'has_layer': True,
    #     'on_map': True,
    #     'marker_color': '#3366FF',
    #     'stroke_color': '#3366FF',
    #     'fill_color': '#3366FF',
    #     'primary_name_lookups': {
    #         'entity_type': 'NAME.E41',
    #         'lookup_value': 'Primary'
    #     },
    #     'sort_order': 1
    # },
}

GEOCODING_PROVIDER = 'arches.app.utils.bing_geocoder'

EXPORT_CONFIG = ''

APP_NAME = 'Arches v3.0'

#######################################
###  END PACKAGE SPECIFIC SETTINGS  ###
#######################################

ROOT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

POSTGIS_VERSION = (2, 0, 0)

SITE_ID = 1

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

# see https://docs.djangoproject.com/en/1.6/topics/i18n/translation/#how-django-discovers-language-preference 
# to see how LocaleMiddleware tries to determine the user's language preference 
# (make sure to check your accept headers as they will override the LANGUAGE_CODE setting!)
# also see get_language_from_request in django.utils.translation.trans_real.py
# to see how the language code is derived in the actual code
LANGUAGE_CODE = 'en-us'

# the path where your translation strings are stored
LOCALE_PATHS = (
    os.path.join(ROOT_DIR, 'locale'),
)

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT =  os.path.join(ROOT_DIR, 'uploadedfiles')

# URL that handles the media served from MEDIA_ROOT, used for managing stored files. 
# It must end in a slash if set to a non-empty value.
MEDIA_URL = 'http://localhost:8000/media/'

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
    MEDIA_ROOT
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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)


# Application definition

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
    'arches.management'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'arches.urls'

WSGI_APPLICATION = 'arches.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT_DIR, 'app', 'templates'),

    # Adding a reference to error page templates because of issues we were seeing in amazon aws instances
    # http://stackoverflow.com/questions/13284443/django-template-error-500-html-on-amazon-ec2?rq=1
    # os.path.join(ROOT_DIR, 'virtualenv/ENV/Lib/site-packages/django/contrib/admin/templates/admin'),
    # os.path.join(ROOT_DIR, 'virtualenv/ENV/lib/python2.7/site-packages/django/contrib/admin/templates/admin'),
)

# List of processors used by RequestContext to populate the context.
# Each one should be a callable that takes the request object as its
# only parameter and returns a dictionary to add to the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'arches.app.utils.context_processors.livereload',
    'arches.app.utils.context_processors.resource_types',
    'arches.app.utils.context_processors.map_info',
    'arches.app.utils.context_processors.app_name',
    'arches.app.utils.context_processors.user_can_edit',
)


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
        },
    },
}

LOGIN_URL = 'auth'

# Package specific validation.
# Should be over-written in the package settings file.
PACKAGE_VALIDATOR = 'arches.app.utils.mock_package_validator'

# Bounding box for geometry data validation. By default set to coordinate system bounding box.
# NOTE: This is not used by the front end of the application.
DATA_VALIDATION_BBOX = [(-180,-90), (-180,90), (180,90), (180,-90), (-180,-90)]

try:
    from settings_local import *
except ImportError:
    pass
