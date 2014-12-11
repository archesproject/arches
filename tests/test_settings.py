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

ROOT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
ROOT_DIR = os.path.normpath(os.path.join(ROOT_DIR, '..', 'arches'))
PACKAGE_ROOT = os.path.normpath(os.path.join(ROOT_DIR, '..', 'tests'))

RESOURCE_GRAPH_LOCATIONS = os.path.join(PACKAGE_ROOT, 'fixtures'),

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

