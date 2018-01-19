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

import uuid, importlib
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.decorators import can_edit_resource_instance
from arches.app.views.tileserver import clean_resource_cache
from django.http import HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.views.generic import View
from django.db import transaction

@method_decorator(can_edit_resource_instance(), name='dispatch')
class TileData(View):
    action = 'update_tile'

    def post(self, request):
        if self.action == 'update_tile':
            json = request.POST.get('data', None)
            if json != None:
                data = JSONDeserializer().deserialize(json)
                tile_id = data['tileid']
                if tile_id != None and tile_id != '':
                    old_tile = Tile.objects.get(pk=tile_id)
                    clean_resource_cache(old_tile)
                tile = Tile(data)
                if tile.filter_by_perm(request.user, 'write_nodegroup'):
                    with transaction.atomic():
                        try:
                            tile.save(request=request)
                        except ValidationError as e:
                            return JSONResponse({'status':'false','message':e.args}, status=500)
                        tile.after_update_all()
                        clean_resource_cache(tile)
                        update_system_settings_cache(tile)
                    return JSONResponse(tile)
                else:
                    return JSONResponse({'status':'false','message': [_('Request Failed'), _('Permission Denied')]}, status=500)

        if self.action == 'reorder_tiles':
            json = request.body
            if json != None:
                data = JSONDeserializer().deserialize(json)

                if 'tiles' in data and len(data['tiles']) > 0:
                    sortorder = 0
                    with transaction.atomic():
                        for tile in data['tiles']:
                            t = Tile(tile)
                            if t.filter_by_perm(request.user, 'write_nodegroup'):
                                t.sortorder = sortorder
                                t.save(update_fields=['sortorder'], request=request)
                                sortorder = sortorder + 1

                    return JSONResponse(data)

        return HttpResponseNotFound()

    def delete(self, request):
        json = request.body
        if json != None:
            ret = []
            data = JSONDeserializer().deserialize(json)

            with transaction.atomic():
                tile = Tile.objects.get(tileid = data['tileid'])
                if tile.filter_by_perm(request.user, 'delete_nodegroup'):
                    nodegroup = models.NodeGroup.objects.get(pk=tile.nodegroup_id)
                    clean_resource_cache(tile)
                    tile.delete(request=request)
                    tile.after_update_all()
                    update_system_settings_cache(tile)
                    return JSONResponse(tile)
                else:
                    return JSONResponse({'status':'false','message': [_('Request Failed'), _('Permission Denied')]}, status=500)

        return HttpResponseNotFound()

# Move to util function
def get(id):
    try:
        uuid.UUID(id)
        return uuid.UUID(id), False
    except(ValueError, TypeError):
        return uuid.uuid4(), True

uuid.get_or_create = get

def update_system_settings_cache(tile):
    if str(tile.resourceinstance_id) == settings.RESOURCE_INSTANCE_ID:
        settings.update_from_db()
