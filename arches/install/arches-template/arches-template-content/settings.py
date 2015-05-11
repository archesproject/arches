import os
import inspect
from {{ source_app }}.settings import *

PACKAGE_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PACKAGE_NAME = PACKAGE_ROOT.split(os.sep)[-1]
DATABASES['default']['NAME'] = 'arches_%s' % (PACKAGE_NAME)
ROOT_URLCONF = '%s.urls' % (PACKAGE_NAME)

INSTALLED_APPS = INSTALLED_APPS + (PACKAGE_NAME,)
STATICFILES_DIRS = (os.path.join(PACKAGE_ROOT, 'media'),) + STATICFILES_DIRS
TEMPLATE_DIRS = (os.path.join(PACKAGE_ROOT, 'templates'),os.path.join(PACKAGE_ROOT, 'templatetags')) + TEMPLATE_DIRS

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT =  os.path.join(PACKAGE_ROOT, 'uploadedfiles')

{% if source_app == 'arches' %}
RESOURCE_MODEL = {'default': 'arches.app.models.resource.Resource'}
{% else %}
#RESOURCE_MODEL = {'default': '{{ app_name }}.models.resource.Resource'}
{% endif %}

# DEFAULT_MAP_X = -13179347.3099
# DEFAULT_MAP_Y = 4031285.8349
DEFAULT_MAP_ZOOM = 1
# MAP_MIN_ZOOM = 9
# MAP_MAX_ZOOM = 19
# MAP_EXTENT = '-13228037.69691764,3981296.0184014924,-13123624.71628009,4080358.407059081'

{% if source_app == 'arches' %}
def RESOURCE_TYPE_CONFIGS():
    return {
        # 'HERITAGE_RESOURCE.E18': {
        #     'resourcetypeid': 'HERITAGE_RESOURCE.E18',
        #     'name': _('Historic Resource'),
        #     'icon_class': 'fa fa-university',
        #     'default_page': 'summary',
        #     'default_description': 'No description available',
        #     'description_node': _('DESCRIPTION.E62'),
        #     'categories': [_('Resource')],
        #     'has_layer': True,
        #     'on_map': False,
        #     'marker_color': '#fa6003',
        #     'stroke_color': '#fb8c49',
        #     'fill_color': '#ffc29e',
        #     'primary_name_lookup': {
        #         'entity_type': 'NAME.E41',
        #         'lookup_value': 'Primary'
        #     },
        #     'sort_order': 1
        # },
        # 'HERITAGE_RESOURCE_GROUP.E27': {
        #     'resourcetypeid': 'HERITAGE_RESOURCE_GROUP.E27',
        #     'name': _('Historic District'),
        #     'icon_class': 'fa fa-th',
        #     'default_page': 'summary',
        #     'default_description': 'No description available',
        #     'description_node': _('REASONS.E62'),
        #     'categories': [_('Resource')],
        #     'has_layer': True,
        #     'on_map': False,
        #     'marker_color': '#FFC53D',
        #     'stroke_color': '#d9b562',
        #     'fill_color': '#eedbad',
        #     'primary_name_lookup': {
        #         'entity_type': 'NAME.E41',
        #         'lookup_value': 'Primary'
        #     },
        #     'sort_order': 2
        # }
    }

{% else %}
# def RESOURCE_TYPE_CONFIGS():
#     return { 
#         'HERITAGE_RESOURCE.E18': {
#             'resourcetypeid': 'HERITAGE_RESOURCE.E18',
#             'name': _('Historic Resource'),
#             'icon_class': 'fa fa-university',
#             'default_page': 'summary',
#             'default_description': 'No description available',
#             'description_node': _('DESCRIPTION.E62'),
#             'categories': [_('Resource')],
#             'has_layer': True,
#             'on_map': False,
#             'marker_color': '#fa6003',
#             'stroke_color': '#fb8c49',
#             'fill_color': '#ffc29e',
#             'primary_name_lookup': {
#                 'entity_type': 'NAME.E41',
#                 'lookup_value': 'Primary'
#             },
#             'sort_order': 1
#         },
#         'HERITAGE_RESOURCE_GROUP.E27': {
#             'resourcetypeid': 'HERITAGE_RESOURCE_GROUP.E27',
#             'name': _('Historic District'),
#             'icon_class': 'fa fa-th',
#             'default_page': 'summary',
#             'default_description': 'No description available',
#             'description_node': _('REASONS.E62'),
#             'categories': [_('Resource')],
#             'has_layer': True,
#             'on_map': False,
#             'marker_color': '#FFC53D',
#             'stroke_color': '#d9b562',
#             'fill_color': '#eedbad',
#             'primary_name_lookup': {
#                 'entity_type': 'NAME.E41',
#                 'lookup_value': 'Primary'
#             },
#             'sort_order': 2
#         }
#     }
{% endif %}

#GEOCODING_PROVIDER = ''
{% if source_app == 'arches' %}
RESOURCE_GRAPH_LOCATIONS = (
    # Put strings here, like "/home/data/resource_graphs" or "C:/data/resource_graphs".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PACKAGE_ROOT, 'source_data', 'resource_graphs'),
)
{% else %}
# RESOURCE_GRAPH_LOCATIONS = (
#     # Put strings here, like "/home/data/resource_graphs" or "C:/data/resource_graphs".
#     # Always use forward slashes, even on Windows.
#     # Don't forget to use absolute paths, not relative paths.
#     os.path.join(PACKAGE_ROOT, 'source_data', 'resource_graphs'),
# )
{% endif %}


CONCEPT_SCHEME_LOCATIONS = (
    # Put strings here, like "/home/data/authority_files" or "C:/data/authority_files".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    
    #'absolute/path/to/authority_files',
    # os.path.normpath(os.path.join(PACKAGE_ROOT, 'source_data', 'concepts', 'authority_files')),
)

BUSISNESS_DATA_FILES = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # os.path.normpath(os.path.join(PACKAGE_ROOT, 'source_data', 'business_data', 'sample.arches')),
)

APP_NAME = '{{ app_name }}'

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
        '{{ app_name }}': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}

#EXPORT_CONFIG = os.path.normpath(os.path.join(PACKAGE_ROOT, 'source_data', 'business_data', 'resource_export_mappings.json'))

try:
    from settings_local import *
except ImportError:
    pass
