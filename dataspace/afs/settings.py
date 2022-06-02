"""
Django settings for afs project.
"""

import os
import arches
import inspect

try:
    from arches.settings import *
except ImportError:
    pass

APP_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
STATICFILES_DIRS = (os.path.join(APP_ROOT, "media"),) + STATICFILES_DIRS
STATIC_ROOT = ""

DATATYPE_LOCATIONS.append("afs.datatypes")
FUNCTION_LOCATIONS.append("afs.functions")
SEARCH_COMPONENT_LOCATIONS.append("afs.search_components")
TEMPLATES[0]["DIRS"].append(os.path.join(APP_ROOT, "functions", "templates"))
TEMPLATES[0]["DIRS"].append(os.path.join(APP_ROOT, "widgets", "templates"))
TEMPLATES[0]["DIRS"].insert(0, os.path.join(APP_ROOT, "templates"))

APP_PATHNAME = ""

BYPASS_CARDINALITY_TILE_VALIDATION = False

CANTALOUPE_DIR = os.path.join(APP_ROOT, "uploadedfiles")
CANTALOUPE_HTTP_ENDPOINT = "http://localhost:8182/"

LOCALE_PATHS.append(os.path.join(APP_ROOT, "locale"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "(hdj_k6s^6*+ve_y9i(&$jo4cj4&jb=ryedo$2jh56bi82ye%*"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ROOT_URLCONF = "afs.urls"
FILE_UPLOAD_PERMISSIONS = 0o644
# a prefix to append to all elasticsearch indexes, note: must be lower case
ELASTICSEARCH_PREFIX = "afs"

ELASTICSEARCH_CUSTOM_INDEXES = []
# [{
#     'module': 'afs.search_indexes.sample_index.SampleIndex',
#     'name': 'my_new_custom_index' <-- follow ES index naming rules
# }]

DATABASES = {
    "default": {
        "ATOMIC_REQUESTS": False,
        "AUTOCOMMIT": True,
        "CONN_MAX_AGE": 0,
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": "localhost",
        "NAME": "afs",
        "OPTIONS": {},
        "PASSWORD": "postgis",
        "PORT": "5432",
        "POSTGIS_TEMPLATE": "template_postgis",
        "TEST": {"CHARSET": None, "COLLATION": None, "MIRROR": None, "NAME": None},
        "TIME_ZONE": None,
        "USER": "postgres",
    }
}

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
    "django_celery_results",
    "afs",
    "compressor",
    "autotranslate",
    # "debug_toolbar"
)


MIDDLEWARE = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
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

ALLOWED_HOSTS = ["10.0.2.2", "localhost"]

SYSTEM_SETTINGS_LOCAL_PATH = os.path.join(APP_ROOT, "system_settings", "System_Settings.json")
WSGI_APPLICATION = "afs.wsgi.application"

RESOURCE_IMPORT_LOG = os.path.join(APP_ROOT, "logs", "resource_import.log")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"console": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",},},
    "handlers": {
        "file": {
            "level": "WARNING",  # DEBUG, INFO, WARNING, ERROR
            "class": "logging.FileHandler",
            "filename": os.path.join(APP_ROOT, "arches.log"),
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

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(APP_ROOT)

# Sets default max upload size to 15MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 15728640

# Unique session cookie ensures that logins are treated separately for each app
SESSION_COOKIE_NAME = "afs"

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "unique-snowflake"},
    "user_permission": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "user_permission_cache",
    },
}

# Identify the usernames and duration (seconds) for which you want to cache the time wheel
CACHE_BY_USER = {"anonymous": 3600 * 24}

TILE_CACHE_TIMEOUT = 600  # seconds
GRAPH_MODEL_CACHE_TIMEOUT = 3600 * 24 * 30  # seconds * hours * days = ~1mo
USER_GRAPH_PERMITTED_CARDS_TIMEOUT = 3600 * 24 * 30  # seconds * hours * days = ~1mo
USER_GRAPH_CARDWIDGETS_TIMEOUT = 3600 * 24 * 30  # seconds * hours * days = ~1mo

MOBILE_OAUTH_CLIENT_ID = ""  #'9JCibwrWQ4hwuGn5fu2u1oRZSs9V6gK8Vu8hpRC4'
MOBILE_DEFAULT_ONLINE_BASEMAP = {"default": "mapbox://styles/mapbox/streets-v9"}

APP_TITLE = "Arches for Science"
COPYRIGHT_TEXT = "All Rights Reserved."
COPYRIGHT_YEAR = "2019"

CELERY_BROKER_URL = "amqp://guest:guest@localhost"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_BACKEND = "django-db"  # Use 'django-cache' if you want to use your cache as your backend
CELERY_TASK_SERIALIZER = "json"

ONTOLOGY_NAMESPACES = {
    "http://purl.org/dc/terms/": "dcterms",
    "http://purl.org/dc/elements/1.1/": "dc",
    "http://schema.org/": "schema",
    "http://www.w3.org/2004/02/skos/core#": "skos",
    "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
    "http://xmlns.com/foaf/0.1/": "foaf",
    "http://www.w3.org/2001/XMLSchema#": "xsd",
    "https://linked.art/ns/terms/": "la",
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
    "http://www.cidoc-crm.org/cidoc-crm/": "",
    "http://www.ics.forth.gr/isl/CRMdig/": "",
    "http://www.ics.forth.gr/isl/CRMgeo/": "geo",
    "http://www.ics.forth.gr/isl/CRMsci/": "sci",
}


RENDERERS += [
    {
        "name": "fors-reader",
        "title": "ASD Hi Res FieldSpec4",
        "description": "Use for exports from all our ASD High Resolution Field Spectroscopy",
        "id": "88dccb59-14e3-4445-8f1b-07f0470b38bb",
        "iconclass": "fa fa-bar-chart-o",
        "component": "views/components/cards/file-renderers/fors-reader",
        "ext": "txt",
        "type": "text/plain",
        "exclude": "",
    },
    {
        "name": "xrf-reader",
        "title": "HP Spectrometer XRF ASCII Output",
        "description": "Use for exports from all our HP XRF outputs",
        "id": "31be40ae-dbe6-4f41-9c13-1964d7d17042",
        "iconclass": "fa fa-bar-chart-o",
        "component": "views/components/cards/file-renderers/xrf-reader",
        "ext": "txt",
        "type": "text/plain",
        "exclude": "",
    },
    {
        "name": "raman-reader",
        "title": "Raman File Reader",
        "description": "Use for exports from all our HP raman and gas chromatograph spectrometers",
        "id": "94fa1720-6773-4f99-b49b-4ea0926b3933",
        "iconclass": "fa fa-bolt",
        "component": "views/components/cards/file-renderers/raman-reader",
        "ext": "txt",
        "type": "text/plain",
        "exclude": "",
    },
    {
        "name": "pdbreader",
        "title": "PDB File Reader",
        "description": "",
        "id": "3744d5ec-c3f1-45a1-ab79-a4a141ee4197",
        "iconclass": "fa fa-object-ungroup",
        "component": "views/components/cards/file-renderers/pdbreader",
        "ext": "pdb",
        "type": "",
        "exclude": "",
    },
    {
        "name": "pcdreader",
        "title": "Point Cloud Reader",
        "description": "",
        "id": "e96e84f2-bcb2-4ca4-8793-7568b09d7374",
        "iconclass": "fa fa-cloud",
        "component": "views/components/cards/file-renderers/pcdreader",
        "ext": "pcd",
        "type": "",
        "exclude": "",
    },
    # {
    #     "name": "colladareader",
    #     "id": "3732bdf0-74b1-412f-955a-9ca038e7db31",
    #     "iconclass": "fa fa-spoon",
    #     "component": "views/components/cards/file-renderers/colladareader",
    #     "ext": "dae",
    #     "type": "",
    #    "exclude": [],
    # },
]

DOCKER = False

try:
    from .package_settings import *
except ImportError:
    pass

try:
    from .settings_local import *
except ImportError:
    pass

if DOCKER:
    try:
        from .settings_docker import *
    except ImportError:
        pass
