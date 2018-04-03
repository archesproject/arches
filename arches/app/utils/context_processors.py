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

from django.conf import settings
from arches.app.models.resource import Resource
from arches.app.models.models import DLanguages
from arches.app.utils.decorators import deprecated

def livereload(request):
    return {
        'livereload_port': settings.LIVERELOAD_PORT
    }

def map_info(request):
    minzoom = settings.MAP_MIN_ZOOM
    maxzoom = settings.MAP_MAX_ZOOM
    if 'edit' not in request.user.user_groups:
      maxzoom =  settings.MAP_MAX_UNLOGGED_ZOOM
      if request.path.split('/')[1] == 'reports':
        minzoom = settings.REPORT_MIN_UNLOGGED_ZOOM
        maxzoom = settings.MAP_MAX_ZOOM
    return {
        'map_info': {
            'x': settings.DEFAULT_MAP_X,
            'y': settings.DEFAULT_MAP_Y,
            'zoom': settings.DEFAULT_MAP_ZOOM,
            'bing_key': settings.BING_KEY,
            'map_min_zoom': minzoom,
            'map_max_zoom': maxzoom,
            'extent': settings.MAP_EXTENT,
            'resource_marker_icon': settings.RESOURCE_MARKER_ICON_UNICODE,
            'resource_marker_font': settings.RESOURCE_MARKER_ICON_FONT,
            'resource_marker_color': settings.RESOURCE_MARKER_DEFAULT_COLOR
        }
    }

def resource_types(request):
    sorted_resource_types = sorted(settings.RESOURCE_TYPE_CONFIGS().items(), key=lambda v: v[1]['sort_order'])
    return {
        'resource_types': sorted_resource_types
    }

def app_settings(request):
    return {
        'APP_NAME': settings.APP_NAME,
        'GOOGLE_ANALYTICS_TRACKING_ID': settings.GOOGLE_ANALYTICS_TRACKING_ID
    }

@deprecated
def user_can_edit(request):
    # need to implement proper permissions check here...
    # for now allowing all logged in users to be 'editors'
    return {
        'user_can_edit': 'edit' in request.user.user_groups
    }

def header(request):
    languages = DLanguages.objects.all()
    return {
        'language_list': languages
    }
