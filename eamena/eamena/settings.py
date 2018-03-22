import os
import inspect
from arches.settings import *
from django.utils.translation import ugettext as _


PACKAGE_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PACKAGE_NAME = PACKAGE_ROOT.split(os.sep)[-1]

ROOT_URLCONF = '%s.urls' % (PACKAGE_NAME)
INSTALLED_APPS = INSTALLED_APPS + (PACKAGE_NAME, 'south', 'storages')
STATICFILES_DIRS = (os.path.join(PACKAGE_ROOT, 'media'),) + STATICFILES_DIRS
TEMPLATE_DIRS = (os.path.join(PACKAGE_ROOT, 'templates'),os.path.join(PACKAGE_ROOT, 'templatetags')) + TEMPLATE_DIRS
LOCALE_PATHS = (os.path.join(PACKAGE_ROOT, '../locale'),)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# MEDIA_ROOT =  os.path.join(PACKAGE_ROOT, 'uploadedfiles')

ugettext = lambda s: s
LANGUAGES = (
    ('en-US', ugettext('English')),
    ('ar', ugettext('Arabic')), #Your second language

)
LANGUAGE_CODE = 'en-US' #Your default language
USE_L10N = True

RESOURCE_MODEL = {'default': 'eamena.models.resource.Resource'}



EAMENA_RESOURCES = ['HERITAGE_RESOURCE_GROUP.E27'] #Specify which resource types should take on the identifier EAMENA-. All other resource types will take on an identifier beginning with their truncated EntityType, e.g. ACTOR for ACTOR.E39, INFORMATION for INFORMATION_RESOURCE.E73
ID_LENGTH = 7 #Indicates the length of the Unique Resource IDs after the set tag, e.g. 7 -> EAMENA-0000001. MUST BE GIVEN, AND BE 2 OR OVER.

# DATE_SEARCH_ENTITY_TYPES = ['BEGINNING_OF_EXISTENCE_TYPE.E55', 'END_OF_EXISTENCE_TYPE.E55', 'DISTURBANCE_DATE_TYPE.E55']




#The list of resource types which should have their geometries indexed into the maplayers index for restriction by geo area.
MAPLAYERS_INDEX_RESOURCE_TYPES = [
    "HERITAGE_RESOURCE_GROUP.E27",
    "INFORMATION_RESOURCE.E73"
]
#Limit number of items per Search page
SEARCH_ITEMS_PER_PAGE= 20
#GEOCODING_PROVIDER = ''

RESOURCE_GRAPH_LOCATIONS = (
#     # Put strings here, like "/home/data/resource_graphs" or "C:/data/resource_graphs".
#     # Always use forward slashes, even on Windows.
#     # Don't forget to use absolute paths, not relative paths.
     os.path.join(PACKAGE_ROOT, 'resource_graphs'),
)

ADDITIONAL_RESOURCE_GRAPH_LOCATIONS = (
     os.path.join(PACKAGE_ROOT, 'additional_resource_graphs'),
)

CONCEPT_SCHEME_LOCATIONS = (
    # Put strings here, like "/home/data/authority_files" or "C:/data/authority_files".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    
    #'absolute/path/to/authority_files',
    os.path.normpath(os.path.join(PACKAGE_ROOT, 'source_data', 'concepts', 'authority_files')),
)

BUSISNESS_DATA_FILES = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.normpath(os.path.join(PACKAGE_ROOT, 'source_data', 'business_data', 'sample.arches')),
)

EXTEND_ONTOLOGY_SQL = (
    os.path.join(ROOT_DIR, 'management', 'commands', 'package_utils', 'add_classes.sql')
)

ADD_ACTOR_TO = {
    'FUNCTION_AND_INTERPRETATION.I5': 'FUNCTION_AND_INTERPRETATION_ACTOR.E39',    
}
# Map new actor nodes to the pre-existing nodes to search for edits to the affected resource
# ( actor node entityid, parent node entityid of actor node, node entityid to check in edit log )
ACTOR_NODES = [
    ('FUNCTION_AND_INTERPRETATION_ACTOR.E39', 'FUNCTION_AND_INTERPRETATION.I5', 'FEATURE_EVIDENCE_INTERPRETATION_TYPE.E55')
]


APP_NAME = 'eamena'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(PACKAGE_ROOT, 'logs', 'application.txt'),
        },
    },
    'loggers': {
        'arches': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'eamena': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}

#Dictionary of nodes to sort data in the report sections. Keys of dict are the top nodes to which the nodes used for sorting are attached
ORDER_REPORT_SECTIONS_BY= {
    'CONDITION_ASSESSMENT.E14': ['DISTURBANCE_DATE_END.E49', 'THREAT_CAUSE_TYPE.E55'],
    'PRODUCTION.E12': ['FEATURE_EVIDENCE_INTERPRETATION_TYPE.E55', 'FEATURE_EVIDENCE_TYPE.E55']
}


SEARCH_GROUP_ROOTS= [
    ('NAME.E41', _('Resource Names')),
    ('SITE_FUNCTION_TYPE.E55', _('Site function')),
    ('CULTURAL_PERIOD.E55', _('Cultural period')),
    ('ASSESSMENT_TYPE.E55', _('Assessment')),
    ('FEATURE_EVIDENCE_ASSIGNMENT.E17', _('Feature form')),
    ('FEATURE_EVIDENCE_INTERPRETATION_ASSIGNMENT.E17', _('Feature interpretation')),
    ('DISTURBANCE_STATE.E3', _('Disturbance assessment')),
    ('THREAT_STATE.E3', _('Threat assessment')),
    ('PROTECTION_EVENT.E65', _('Designation')),
    ('MEASUREMENT_TYPE.E55', _('Measurements')),
    ('PLACE_ADDRESS.E45', _('Addresses'))
]

EXPORT_CONFIG = os.path.normpath(os.path.join(PACKAGE_ROOT, 'source_data', 'business_data', 'resource_export_mappings.json'))

try:
    from settings_local import *
except ImportError:
    pass
