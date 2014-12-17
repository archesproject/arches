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
#import version
import inspect
from django.utils.importlib import import_module
# Django settings for Arches project.

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

PRIMARY_DISPLAY_NAME_LOOKUPS = {
    'default': {
        # override this setting in your packages settings.py file
        'entity_type': '',
        'lookup_value': ''
    }
}

ELASTICSEARCH_HTTP_PORT = 9200 # this should be in increments of 200, eg: 9400, 9600, 9800
SEARCH_CONNECTION = {
    # override this setting in your packages settings.py file
    'default': {
        'backend': 'arches.app.search.search.SearchEngine',
        'host': 'localhost',
        'timeout': 30,
        'connection_type': 'http'
    }
}

SEARCH_ITEMS_PER_PAGE = 5

SEARCHABLE_ENTITY_TYPES = (
    # override this setting in your packages settings.py file
    # entity types that are used to index terms for simple search
)

ADV_SEARCHABLE_ENTITY_TYPES = (
    # override this setting in your packages settings.py file
    # entity types to index for advanced search
)

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

BING_KEY = 'Ak-dzM4wZjSqTlzveKz5u0d4IQ4bRzVI309GxmkgSVr1ewS6iPSrOvOKhA-CJlm3'

#######################################
###  END PACKAGE SPECIFIC SETTINGS  ###
#######################################


# ARCHES_VERSION = version.__VERSION__
# BUILD = version.__BUILD__
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


try:
    from settings_local import *
except ImportError:
    pass

# def apply_package_settings(package_name):
#     print 'Loading package : %s' % package_name
#     if package_name == '':
#         if len(INSTALLED_PACKAGES) == 1:
#             package_name = INSTALLED_PACKAGES[0]
#         if len(INSTALLED_PACKAGES) > 1:
#             clear_package_setting()
#             raise Exception("""\n
#     ------------------------------------------------------------------------------------------------------
#         ERROR: You have more then 1 package enabled and you didn't specify which package to load
#         Either disable one of the packages by commenting out it's name in the INSTALLED_PACKAGES setting
#                                                 OR
#         Specify the package by adding the --package or -p flag and then the package name like so...
#         python manage.py packages -p <package_name>
#                                                 OR
#         Run the server from runserver.py specifying the package name and port to run on like so...
#         python runserver.py <my package name> <port>
#     ----------------------------------------------------------------------------------------------------\n""")


#     if package_name in INSTALLED_PACKAGES:
#         print 'Running package : %s' % package_name
#         settingsfile = os.path.join(ROOT_DIR, 'packages', package_name, 'settings.py')
#         if os.path.exists(settingsfile):
#             mod = import_module("arches.app.packages.%s.settings" % package_name)
#             package_settings = mod.get_settings(globals())
#             for member_name in package_settings: 
#                 globals()[member_name] = package_settings[member_name]
#     else:
#         clear_package_setting()
#         raise Exception("""\n
#         ------------------------------------------------------------------------------------------------------
#             ERROR: You specified a package "%s" that doesn't exist in your INSTALLED_PACKAGES setting
#         ----------------------------------------------------------------------------------------------------\n""" % package_name)

# def clear_package_setting():
#     from arches.app.build.management.commands import utils
#     utils.write_to_file(os.path.join(ROOT_DIR, 'package_setting.py'), 'PACKAGE=""')
#     #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arches.app.settings")


# apply_package_settings(PACKAGE)
# clear_package_setting()


