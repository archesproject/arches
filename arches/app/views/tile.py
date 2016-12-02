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
        if self.action == 'update_tile':
            json = request.POST.get('data', None)
            if json != None:
                data = JSONDeserializer().deserialize(json)

                def saveTile(data, parenttile_id=None):
                    data['tileid'], created = uuid.get_or_create(data['tileid'])

                    data = preSave(data, request)
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
            json = request.body
            if json != None:
                data = JSONDeserializer().deserialize(json)
                
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
            data = preDelete(data, request)
            tile = models.Tile.objects.get(tileid = data['tileid'])
            tile.delete()
            tile.tileid = data['tileid']
            return JSONResponse(tile)

        return HttpResponseNotFound()


def preSave(tile, request):
    for function in getFunctionClassInstances(tile):
        try:
            function.save(tile, request)
        except NotImplementedError:
            pass
    return tile


def preDelete(tile, request):
    for function in getFunctionClassInstances(tile):
        try:
            function.delete(tile, request)
            print 'deleting'
        except NotImplementedError:
            pass
    return tile

def getFunctionClassInstances(tile):
    ret = []
    resource = models.ResourceInstance.objects.get(pk=tile['resourceinstance_id'])
    functions = models.FunctionXGraph.objects.filter(graph_id=resource.graph_id, config__triggering_nodegroups__contains=[tile['nodegroup_id']])
    for function in functions:
        print function.function.modulename.replace('.py', '')
        mod_path = function.function.modulename.replace('.py', '')
        module = importlib.import_module('arches.app.functions.%s' % mod_path)
        func = getattr(module, function.function.classname)()
        ret.append(func)
    return ret

# Move to util function
def get(id):
    try:
        uuid.UUID(id)
        return uuid.UUID(id), False
    except(ValueError, TypeError):
        return uuid.uuid4(), True


uuid.get_or_create = get
