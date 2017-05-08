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

from arches import __version__
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

def livereload(request):
    return {
        'livereload_port': settings.LIVERELOAD_PORT
    }

def map_info(request):
    return {
        'map_info': {
            'x': settings.DEFAULT_MAP_X,
            'y': settings.DEFAULT_MAP_Y,
            'zoom': settings.DEFAULT_MAP_ZOOM,
            'map_min_zoom': settings.MAP_MIN_ZOOM,
            'map_max_zoom': settings.MAP_MAX_ZOOM,
            'mapbox_api_key': settings.MAPBOX_API_KEY,
            'hex_bin_size': settings.HEX_BIN_SIZE,
            'mapbox_sprites': settings.MAPBOX_SPRITES,
            'mapbox_glyphs': settings.MAPBOX_GLYPHS,
            'hex_bin_bounds': JSONSerializer().serialize(settings.HEX_BIN_BOUNDS),
            'geocoder_default': settings.DEFAULT_SEARCH_GEOCODER
        }
    }

def app_settings(request):
    return {
        'VERSION': __version__,
        'APP_NAME': settings.APP_NAME,
        'GOOGLE_ANALYTICS_TRACKING_ID': settings.GOOGLE_ANALYTICS_TRACKING_ID
    }
