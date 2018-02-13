from arches.settings import *

RESOURCE_IMPORT_LOG = 'logs/resource_import_coac.log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(ROOT_DIR, 'arches_coac.log'),
        }
    },
    'loggers': {
        'arches': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}


#Filtre espaial per al grup imi
DATA_SPATIAL_FILTER = {
    "type": "Polygon",
    "coordinates": [
            [
                [0.159413237942827,40.5230250165038], 
                [0.159413237942827,42.8614503135853],
                [3.33254231638153,42.8614503135853],
                [3.33254231638153,40.5230250165038],
                [0.159413237942827,40.5230250165038]
            ]
    ],
    "crs":{"type":"name","properties":{"name":"EPSG:4326"}}
}


#AMB PERMISOS D'ADMINISTRADOR
ADMIN_ACCES=True

#DIFFERENT SESSION FOR APPS
SESSION_COOKIE_NAME = 'coac_cookie'

#PLANTILLA A AGAFAR PER LA PAGINA D'INICI + CONTEXTE PER ESTILS
INDEX_TEMPLATE='index_coac.htm'
CONTEXT = 'coac'
