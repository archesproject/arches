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

import json
from arches import __version__
from arches.app.models.system_settings import settings
from arches.app.utils.geo_utils import GeoUtils
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


def livereload(request):
    return {
        'livereload_port': settings.LIVERELOAD_PORT,
        'use_livereload': settings.USE_LIVERELOAD
    }


def map_info(request):
    geo_utils = GeoUtils()
    if settings.DEFAULT_BOUNDS is not None:
        hex_bin_bounds = geo_utils.get_bounds_from_geojson(settings.DEFAULT_BOUNDS)
        default_center = geo_utils.get_centroid(settings.DEFAULT_BOUNDS)
    else:
        hex_bin_bounds = None
        default_center = None
    return {
        'map_info': {
            'x': default_center['coordinates'][0],
            'y': default_center['coordinates'][1],
            'zoom': settings.DEFAULT_MAP_ZOOM,
            'map_min_zoom': settings.MAP_MIN_ZOOM,
            'map_max_zoom': settings.MAP_MAX_ZOOM,
            'mapbox_api_key': settings.MAPBOX_API_KEY,
            'hex_bin_size': settings.HEX_BIN_SIZE if settings.HEX_BIN_SIZE != None else 100,
            'mapbox_sprites': settings.MAPBOX_SPRITES,
            'mapbox_glyphs': settings.MAPBOX_GLYPHS,
            'hex_bin_bounds': json.dumps(hex_bin_bounds),
            'geocoder_default': settings.DEFAULT_GEOCODER,
            'preferred_coordinate_systems': JSONSerializer().serialize(settings.PREFERRED_COORDINATE_SYSTEMS)
        }
    }

def app_settings(request):
    return {
        'app_settings':{
            'VERSION': __version__,
            'APP_NAME': settings.APP_NAME,
            'GOOGLE_ANALYTICS_TRACKING_ID': settings.GOOGLE_ANALYTICS_TRACKING_ID,
            'USE_SEMANTIC_RESOURCE_RELATIONSHIPS': settings.USE_SEMANTIC_RESOURCE_RELATIONSHIPS
        }
    }
