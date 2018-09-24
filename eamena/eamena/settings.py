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

# Absolute filesystem path to the directory holds bulk upload data
BULK_UPLOAD_DIR =  os.path.join(PACKAGE_ROOT, 'bulk_upload')

ugettext = lambda s: s
LANGUAGES = (
    ('en-US', ugettext('English')),
    ('ar', ugettext('Arabic')), #Your second language

)
LANGUAGE_CODE = 'en-US' #Your default language
USE_L10N = True

RESOURCE_MODEL = {'default': 'eamena.models.resource.Resource'}


#Specify which ridentifiers should be taken on by which resource types. All other resource types will take on an identifier beginning with their truncated EntityType, e.g. ACTOR for ACTOR.E39, INFORMATION for INFORMATION_RESOURCE.E73
EAMENA_RESOURCES = {

'HERITAGE_RESOURCE_GROUP.E27' : 'IDIHA',
'HERITAGE_FEATURE.E24': 'IDIHA-F',
'HERITAGE_COMPONENT.B2': 'IDIHA-C'

}


ID_LENGTH = 7 #Indicates the length of the Unique Resource IDs after the set tag, e.g. 7 -> EAMENA-0000001. MUST BE GIVEN, AND BE 2 OR OVER.

# DATE_SEARCH_ENTITY_TYPES = ['BEGINNING_OF_EXISTENCE_TYPE.E55', 'END_OF_EXISTENCE_TYPE.E55', 'DISTURBANCE_DATE_TYPE.E55']

def RESOURCE_TYPE_CONFIGS():
    return {
        'HERITAGE_RESOURCE_GROUP.E27': {
            'resourcetypeid': 'HERITAGE_RESOURCE_GROUP.E27',
            'name': _('Heritage Place'),
            'icon_class': 'fa fa-stop',
            'default_page': 'assessment-summary',
            'default_description': _('No name available'),
            'description_node': _('NAME.E41'),
            'categories': [_('Resource')],
            'has_layer': True,
            'on_map': True,
            'marker_color': '#e53d20',
            'stroke_color': '#d9b562',
            'fill_color': '#eedbad',
            'primary_name_lookup': {
                'entity_type': 'EAMENA_ID.E42',
                'lookup_value': 'Primary'
            },
            'sort_order': 1
        },
        'HERITAGE_FEATURE.E24': {
            'resourcetypeid': 'HERITAGE_FEATURE.E24',
            'name': _('Heritage Feature'),
            'icon_class': 'fa fa-th-large',
            'default_page': 'assessment-summary',
            'default_description': _('No name available'),
            'description_node': _('NAME.E41'),
            'categories': [_('Resource')],
            'has_layer': True,
            'on_map': True,
            'marker_color': '#42b472',
            'stroke_color': '#d9b562',
            'fill_color': '#eedbad',
            'primary_name_lookup': {
                'entity_type': 'EAMENA_ID.E42',
                'lookup_value': 'Primary'
            },
            'sort_order': 2
        },
        'HERITAGE_COMPONENT.B2': {
            'resourcetypeid': 'HERITAGE_COMPONENT.B2',
            'name': _('Heritage Component'),
            'icon_class': 'fa fa-th',
            'default_page': 'component-assessment',
            'default_description': _('No name available'),
            'description_node': _('NAME.E41'),
            'categories': [_('Resource')],
            'has_layer': True,
            'on_map': True,
            'marker_color': '#FFC53D',
            'stroke_color': '#d9b562',
            'fill_color': '#eedbad',
            'primary_name_lookup': {
                'entity_type': 'HERITAGE_COMPONENT_ID.E42',
                'lookup_value': 'Primary'
            },
            'sort_order': 3
        },
        'ACTOR.E39': {
            'resourcetypeid': 'ACTOR.E39',
            'name': _('Person/Organization'),
            'icon_class': 'fa fa-group',
            'default_page': 'actor-summary',
            'default_description': _('No description available'),
            'description_node': _('ACTOR_APPELLATION.E82'),
            'categories': [_('Resource')],
            'has_layer': True,
            'on_map': False,
            'marker_color': '#a44b0f',
            'stroke_color': '#a7673d',
            'fill_color': '#c8b2a3',
            'primary_name_lookup': {
                'entity_type': 'EAMENA_ID.E42',
                'lookup_value': 'Primary'
            },
            'sort_order': 4
        },
        'INFORMATION_RESOURCE.E73': {
            'resourcetypeid': 'INFORMATION_RESOURCE.E73',
            'name': _('Information Resource'),
            'icon_class': 'fa fa-file-text-o',
            'default_page': 'information-resource-summary',
            'default_description': _('No description available'),
            'description_node': _('TITLE.E41,CATALOGUE_ID.E42,IMAGERY_CREATOR_APPELLATION.E82,TILE_SQUARE_DETAILS.E44,CONTRIBUTOR_APPELLATION.E82,SHARED_DATA_SOURCE_APPELLATION.E82,SHARED_DATA_SOURCE_AFFILIATION.E82,SHARED_DATA_SOURCE_CREATOR_APPELLATION.E82'),
            'categories': [_('Resource')],
            'has_layer': True,
            'on_map': True,
            'marker_color': '#8D45F8',
            'stroke_color': '#9367d5',
            'fill_color': '#c3b5d8',
            'primary_name_lookup': {
                'entity_type': 'EAMENA_ID.E42',
                'lookup_value': 'Primary'
            },
            'sort_order': 5
        }
    }


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
    ('DATE_INFERENCE_MAKING_ACTOR_NAME.E41', 'DATE_INFERENCE_MAKING.I5', 'CULTURAL_PERIOD.E55'),
    ('FEATURE_ASSIGNMENT_INVESTIGATOR_NAME.E41', 'FEATURE_ASSIGNMENT.E13', 'FEATURE_EVIDENCE_TYPE.E55'),
    ('FUNCTION_INTERPRETATION_INFERENCE_MAKING_ACTOR_NAME.E41', 'FUNCTION_INTERPRETATION_INFERENCE_MAKING.I5', 'FEATURE_EVIDENCE_INTERPRETATION_TYPE.E55'),
    ('DISTURBANCE_CAUSE_ASSIGNMENT_ASSESSOR_NAME.E41', 'DAMAGE_STATE.E3', 'DISTURBANCE_CAUSE_TYPE.E55'),
    ('THREAT_INFERENCE_MAKING_ASSESSOR_NAME.E41', 'THREAT_INFERENCE_MAKING.I5', 'THREAT_TYPE.E55'),
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
    
#Radius in metres to be used to calculate the existence of pre-existing resources in the database. If, upon resource creation, other pre-existing resources fall within this radius, an alert is returned before save.
METER_RADIUS = 1000 


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format':'%(levelname)s|%(message)s',
        },
        'simple': {
            'format':'%(message)s',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(ROOT_DIR, 'arches.log'),
            'formatter':'simple'
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