from arches.settings import *

RESOURCE_IMPORT_LOG = 'logs/resource_import_imi.log'

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
            'filename': os.path.join(ROOT_DIR, 'arches_imi.log'),
        },
    },
    'loggers': {
        'arches': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

#Filtre espaial per al grup imi
DATA_SPATIAL_FILTER = {
    "type": "FeatureCollection",
    "features": [{
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [2.05245125523825,41.3169235933913],
                    [2.05245125523825,41.4682511768069],
                    [2.22920292690723,41.4682511768069],
                    [2.22920292690723,41.3169235933913],
                    [2.05245125523825,41.3169235933913]
                ]
            ]
        },
        "type": "Feature",
        "properties": {}
    }]
}

#AMB PERMISOS D'ADMINISTRADOR
ADMIN_ACCES=False

#DIFFERENT SESSION FOR APPS
SESSION_COOKIE_NAME = 'imi_cookie'

#PLANTILLA A AGAFAR PER LA PAGINA D'INICI
INDEX_TEMPLATE='index_imi.htm'
CONTEXT = 'imi'
