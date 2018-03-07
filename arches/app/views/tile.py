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

import uuid, importlib, json as jsonparser
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.decorators import can_edit_resource_instance
from arches.app.views.tileserver import clean_resource_cache
from django.http import HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.views.generic import View
from django.db import transaction

@method_decorator(can_edit_resource_instance(), name='dispatch')
class TileData(View):
    action = 'update_tile'

    def delete_provisional_edit(self, data, request):
        tile = Tile.objects.get(tileid = data['tileid'])
        provisionaledits = None
        if tile.provisionaledits is not None:
            provisionaledits = jsonparser.loads(tile.provisionaledits)
            if data['user'] in provisionaledits:
                provisionaledits.pop(data['user'])
                if len(provisionaledits) == 0:
                    tile.provisionaledits = None
                else:
                    tile.provisionaledits = jsonparser.dumps(provisionaledits)

                if len(tile.data) == 0 and tile.provisionaledits == None:
                    tile.delete(request=request)
                else:
                    tile.save(log=False)

    def post(self, request):
        if self.action == 'update_tile':
            json = request.POST.get('data', None)
            if json != None:
                data = JSONDeserializer().deserialize(json)
                try:
                    models.ResourceInstance.objects.get(pk=data['resourceinstance_id'])
                except ObjectDoesNotExist:
                    resource = Resource()
                    resource.resourceinstanceid = data['resourceinstance_id']
                    graphid = models.Node.objects.filter(nodegroup=data['nodegroup_id'])[0].graph.graphid
                    resource.graph_id = graphid
                    resource.save(user=request.user)
                    resource.index()
                tile_id = data['tileid']
                if tile_id != None and tile_id != '':
                    old_tile = Tile.objects.get(pk=tile_id)
                    clean_resource_cache(old_tile)
                tile = Tile(data)
                if tile.filter_by_perm(request.user, 'write_nodegroup'):
                    with transaction.atomic():
                        try:
                            tile.save(request=request)
                            if tile_id == '4345f530-aa90-48cf-b4b3-92d1185ca439':
                                print 'saving tile'
                                import couchdb
                                import json as json_json
                                couch = couchdb.Server(settings.COUCHDB_URL)
                                for project in models.MobileSurveyModel.objects.all():
                                    db = couch['project_' + str(project.id)]
                                    #tile = models.TileModel.objects.get(pk='4345f530-aa90-48cf-b4b3-92d1185ca439')
                                    tile_json = json_json.loads(JSONSerializer().serialize(tile))
                                    tile_json['_id'] = tile_json['tileid']
                                    for row in db.view('_all_docs', include_docs=True):
                                        if 'tileid' in row.doc and tile_json['_id'] == row.doc['_id']:
                                            tile_json['_rev'] = row.doc['_rev']
                                            db.save(tile_json)

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

        if self.action == 'delete_provisional_tile':
            data = request.POST
            if 'tileid' in data:
                provisionaledits = self.delete_provisional_edit(data, request)
                return JSONResponse(provisionaledits)

            else:
                payload = data.get('payload', None)
                if payload is not None:
                    edits = jsonparser.loads(payload)
                    for edit in edits['edits']:
                        provisionaledits = self.delete_provisional_edit(edit, request)
                return JSONResponse({'result':'success'})

        return HttpResponseNotFound()

    def delete(self, request):
        json = request.body
        if json != None:
            ret = []
            data = JSONDeserializer().deserialize(json)

            with transaction.atomic():
                tile = Tile.objects.get(tileid = data['tileid'])
                user_is_reviewer = request.user.groups.filter(name='Resource Reviewer').exists()
                if user_is_reviewer or tile.is_provisional() == True:
                    if tile.filter_by_perm(request.user, 'delete_nodegroup'):
                        nodegroup = models.NodeGroup.objects.get(pk=tile.nodegroup_id)
                        clean_resource_cache(tile)
                        tile.delete(request=request)
                        tile.after_update_all()
                        update_system_settings_cache(tile)
                        return JSONResponse(tile)
                    else:
                        return JSONResponse({'status':'false','message': [_('Request Failed'), _('Permission Denied')]}, status=500)
                else:
                    return JSONResponse({'status':'false','message': [_('Request Failed'), _('You do not have permissions to delete a tile with authoritative data.')]}, status=500)

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
