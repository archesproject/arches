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

import uuid
from arches.app.models import models
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.decorators import group_required
from django.http import HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.db import transaction


@method_decorator(group_required('edit'), name='dispatch')
class TileData(View):
    action = 'update_tile'

    def post(self, request):
        json = request.POST.get('data', None)
        if json != None:
            data = JSONDeserializer().deserialize(json)

            if self.action == 'update_tile':
                def saveTile(data, parenttile_id=None):
                    data['tileid'], created = uuid.get_or_create(data['tileid'])

                    # TODO: move this datatype ('file-list') specific code into
                    # a function meant to handle this datatype during tile save
                    try:
                        tile_model = models.Tile.objects.get(pk=data['tileid'])
                    except models.Tile.DoesNotExist:
                        tile_model = None

                    nodegroup = models.NodeGroup.objects.get(pk=data['nodegroup_id'])
                    for node in nodegroup.node_set.all():
                        if node.datatype == 'file-list':
                            if tile_model is not None:
                                model_files = tile_model.data[str(node.pk)]
                                for model_file in model_files:
                                    incoming_file = None
                                    for file_json in data['data'][str(node.pk)]:
                                        if file_json["file_id"] == model_file["file_id"]:
                                            incoming_file = file_json
                                    if incoming_file == None:
                                        deleted_file = models.File.objects.get(pk=model_file["file_id"])
                                        deleted_file.delete()
                            files = request.FILES.getlist('file-list_' + str(node.pk), [])
                            for file_data in files:
                                file_model = models.File()
                                file_model.path = file_data
                                file_model.save()
                                for file_json in data['data'][str(node.pk)]:
                                    if file_json["name"] == file_data.name and file_json["url"] is None:
                                        file_json["file_id"] = str(file_model.pk)
                                        file_json["url"] = str(file_model.path.url)
                                        file_json["status"] = 'uploaded'
                    # END 'file-list' SPECIFIC CODE

                    tile, created = models.Tile.objects.update_or_create(
                        tileid = data['tileid'],
                        defaults = {
                            'nodegroup_id': data['nodegroup_id'],
                            'data': data['data'],
                            'resourceinstance_id': data['resourceinstance_id'],
                            'parenttile_id': data['parenttile_id']
                        }
                    )
                    return data

                with transaction.atomic():
                    if 'tiles' in data and len(data['tiles']) > 0:
                        parenttile = saveTile(data)

                        for tiles in data['tiles'].itervalues():
                            for tile in tiles:
                                tile['parenttile_id'] = parenttile['tileid']
                                saveTile(tile)
                    else:
                        saveTile(data)

                return JSONResponse(data)

            if self.action == 'reorder_tiles':
                if 'tiles' in data and len(data['tiles']) > 0:
                    sortorder = 0
                    for tile in data['tiles']:
                        t = models.Tile(tileid=tile['tileid'], sortorder=sortorder)
                        sortorder = sortorder + 1
                        t.save(update_fields=['sortorder'])

                    return JSONResponse(data)

        return HttpResponseNotFound()

    def delete(self, request):
        json = request.body
        if json != None:
            data = JSONDeserializer().deserialize(json)
            tile = models.Tile.objects.get(tileid = data['tileid'])
            tile.delete()
            tile.tileid = data['tileid']
            return JSONResponse(tile)

        return HttpResponseNotFound()

# Move to util function
def get(id):
    try:
        uuid.UUID(id)
        return uuid.UUID(id), False
    except(ValueError, TypeError):
        return uuid.uuid4(), True


uuid.get_or_create = get
