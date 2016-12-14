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
import copy
from django.shortcuts import render
from arches.app.models import models
from arches.app.models.forms import Form
from django.utils.translation import ugettext as _
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

def manager(request):
    resourceinstanceid = '40000000-0000-0000-0000-000000000000'

    if request.method == 'GET':

        form = Form(resourceinstanceid)

        return render(request, 'config-manager.htm', {
            'main_script': 'config-manager',
            'active_page': 'Home',
            'forms': form.forms,
            'widgets': form.widgets,
            'blanks': JSONSerializer().serialize(form.blanks),
            'tiledata': JSONSerializer().serialize(form.tiles)
        })


    if request.method == 'POST':
        json = request.body
        if json != None:
            data = JSONDeserializer().deserialize(json)
            #print data

            def saveTile(data, parenttile_id=None):
                data['tileid'], created = uuid.get_or_create(data['tileid'])
                tile, created = models.TileModel.objects.update_or_create(
                    tileid = data['tileid'], 
                    defaults = {
                        'nodegroup_id': data['nodegroup_id'], 
                        'data': data['data'],
                        'resourceinstance_id': data['resourceinstance_id'],
                        'parenttile_id': data['parenttile_id']
                    }
                )
                return data

            if 'tiles' in data and len(data['tiles']) > 0:                
                parenttile = saveTile(data)

                for key, tiles in data['tiles'].iteritems():
                    for tile in tiles:
                        tile['parenttile_id'] = parenttile['tileid']
                        saveTile(tile)
            else:
                saveTile(data)

        return JSONResponse(data)

    if request.method == 'DELETE':
        json = request.body
        if json != None:
            data = JSONDeserializer().deserialize(json)
            print data
            tile = models.TileModel.objects.get(tileid = data['tileid'])
            tile.delete()
            tile.tileid = data['tileid']
        return JSONResponse(tile)


# Move to util function
def get(id):
    try:
        uuid.UUID(id)
        return uuid.UUID(id), False
    except(ValueError, TypeError):
        return uuid.uuid4(), True


uuid.get_or_create = get