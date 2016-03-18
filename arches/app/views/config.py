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
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from arches.app.models import models
from django.utils.translation import ugettext as _
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.models.app_settings import AppSettings

@csrf_exempt
def manager(request):
    resourceinstanceid = '40000000-0000-0000-0000-000000000000'
    resourceclassid = '20000000-0000-0000-0000-000000000000'

    if request.method == 'GET':

        widgets = models.Widget.objects.all()
        string_widget = widgets.get(name='string')
        select_widget = widgets.get(name='select')

        forms = [{
            'id': '1',
            'title': _('Server Settings'),
            'subtitle': _('Check/Update settings for Arches'),
            'cardgroups': [
            {
                'id': '1-1',
                'title': _('Arches Server Settings'),
                'cardinality': '1',
                'nodegroup_id': '21111111-0000-0000-0000-000000000000',  # <-- virtual nodegroup because this cardgroup has a cardinality of 1
                'cards': [{
                    'id': '30000000-0000-0000-0000-000000000000',
                    'title': _('TEst'),
                    'cardinality': '1',
                    'nodegroup_id': '99999999-0000-0000-0000-000000000001',
                    'description': _('Keys allow you to access external services (like Mapbox maps) from Arches. Add your user keys (optional):'),
                    'widgets':[{
                        'path': string_widget.template.path,
                        'label': 'Service Name',
                        'placeholder': 'e.g. MapBox Base Maps',
                        'nodeid': '20000000-0000-0000-0000-000000000002'
                    },{
                        'path': string_widget.template.path,
                        'label': 'Key',
                        'placeholder': 'Enter key value',
                        'nodeid': '20000000-0000-0000-0000-000000000004'
                    }]
                },{
                    'id': '30000000-0000-0000-0000-000000000000',
                    'title': _('Keys'),
                    'cardinality': 'n',
                    'nodegroup_id': '99999999-0000-0000-0000-000000000000',
                    'description': _('Keys allow you to access external services (like Mapbox maps) from Arches. Add your user keys (optional):'),
                    'widgets':[{
                        'path': select_widget.template.path,
                        'label': 'Service Provider',
                        'placeholder': 'e.g.: MapBox',
                        'nodeid': '20000000-0000-0000-0000-000000000003',
                        'select2Config': {'data': [{'id':'1', 'text': 'Bing'},{'id': '2', 'text': 'Map Box'}]}
                    },{
                        'path': string_widget.template.path,
                        'label': 'Service Name',
                        'placeholder': 'e.g. MapBox Base Maps',
                        'nodeid': '20000000-0000-0000-0000-000000000002'
                    },{
                        'path': string_widget.template.path,
                        'label': 'Key',
                        'placeholder': 'Enter key value',
                        'nodeid': '20000000-0000-0000-0000-000000000004'
                    }]
                }]
            },
            {
                'id': '50000000-0000-0000-0000-000000000000',
                'title': _('Base Maps'),
                'cardinality': 'n',
                'nodegroup_id': '11111111-0000-0000-0000-000000000000',
                'cards': [{
                    'id': '30000000-0000-0000-0000-000000000000',
                    'title': _('Other Data'),
                    'cardinality': 'n',
                    'nodegroup_id': '32999999-0000-0000-0000-000000000000',
                    'description': _('Do something awesome here'),
                    'widgets':[{
                        'path': select_widget.template.path,
                        'label': 'Service Provider',
                        'placeholder': 'e.g.: MapBox',
                        'nodeid': '20000000-0000-0000-0000-000000000003',
                        'select2Config': {'data': [{'id':'1', 'text': 'Bing'},{'id': '2', 'text': 'Map Box'}]}
                    },{
                        'path': string_widget.template.path,
                        'label': 'Service Name',
                        'placeholder': 'e.g. MapBox Base Maps',
                        'nodeid': '20000000-0000-0000-0000-000000000002'
                    },{
                        'path': string_widget.template.path,
                        'label': 'Key',
                        'placeholder': 'Enter key value',
                        'nodeid': '20000000-0000-0000-0000-000000000004'
                    }]
                }
                ,{
                    'id': '30000000-0000-0000-0000-000000000001',
                    'title': _('TEST'),
                    'cardinality': 'n',
                    'nodegroup_id': '19999999-0000-0000-0000-000000000000',
                    'description': _('TEAFASDF'),
                    'widgets':[{
                        'path': string_widget.template.path,
                        'label': 'Service Name',
                        'placeholder': 'e.g. MapBox Base Maps',
                        'nodeid': '20000000-0000-0000-0000-000000000002'
                    },{
                        'path': string_widget.template.path,
                        'label': 'Key',
                        'placeholder': 'Enter key value',
                        'nodeid': '20000000-0000-0000-0000-000000000004'
                    }]
                }
                ]
            }]
        }]

        
        tiles = models.Tile.objects.filter(resourceinstance_id=resourceinstanceid)

        t2 = []
        blanks = {}
        for form in forms:
            for cardgroup in form['cardgroups']:
                parentTiles = JSONSerializer().serializeToPython(tiles.filter(nodegroup_id=cardgroup['nodegroup_id']))

                if len(parentTiles) > 0:
                    for parentTile in parentTiles:
                        parentTile['tiles'] = {}
                        for card in cardgroup['cards']:
                            parentTile['tiles'][card['nodegroup_id']] = []
                        for tile in JSONSerializer().serializeToPython(tiles.filter(parenttile_id=parentTile['tileid'])):
                            parentTile['tiles'][str(tile['nodegroup_id'])].append(tile)

                if len(parentTiles) == 0 and cardgroup['cardinality'] == '1':
                    # add blank parent tile
                    parentTile = JSONSerializer().serializeToPython(models.Tile())
                    parentTile['tileid'] = ''
                    parentTile['tiles'] = {}
                    parentTile['nodegroup_id'] = cardgroup['nodegroup_id']
                    parentTile['resourceinstance_id'] = resourceinstanceid
                    parentTiles = [parentTile]

                    for card in cardgroup['cards']:
                        #print card
                        # make a blank tile
                        tile = JSONSerializer().serializeToPython(models.Tile())
                        tile['tileid'] = ''
                        tile['parenttile_id'] = None # parentTile
                        tile['resourceinstance_id'] = resourceinstanceid
                        tile['nodegroup_id'] = card['nodegroup_id']
                        tile['data'] = {}
                        for widget in card['widgets']:
                            tile['data'][widget['nodeid']] = ''

                        parentTile['tiles'][card['nodegroup_id']] = JSONSerializer().serializeToPython(tiles.filter(nodegroup_id=card['nodegroup_id']))

                        if len(parentTile['tiles'][card['nodegroup_id']]) == 0 and card['cardinality'] == '1':
                            parentTile['tiles'][card['nodegroup_id']] = [copy.deepcopy(tile)]

                t2 = t2 + parentTiles


        for form in forms:
            for cardgroup in form['cardgroups']:
                # add blank parent tile
                parentTile = JSONSerializer().serializeToPython(models.Tile())
                parentTile['tileid'] = ''
                parentTile['tiles'] = {}
                parentTile['nodegroup_id'] = cardgroup['nodegroup_id']
                parentTile['resourceinstance_id'] = resourceinstanceid

                # add a blank tile for the cardgroup
                blanks[parentTile['nodegroup_id']] = parentTile

                for card in cardgroup['cards']:
                    # make a blank tile
                    tile = JSONSerializer().serializeToPython(models.Tile())
                    tile['tileid'] = ''
                    tile['parenttile_id'] = None # parentTile
                    tile['resourceinstance_id'] = resourceinstanceid
                    tile['nodegroup_id'] = card['nodegroup_id']
                    tile['tiles'] = []
                    tile['data'] = {}
                    for widget in card['widgets']:
                        tile['data'][widget['nodeid']] = ''

                    parentTile['tiles'][card['nodegroup_id']] = []
                    
                    # add a blank tile for each card 
                    blanks[tile['nodegroup_id']] = tile
    


        return render(request, 'config-manager.htm', {
            'main_script': 'config-manager',
            'active_page': 'Home',
            'forms': forms,
            'blanks': JSONSerializer().serialize(blanks),
            'tiledata': JSONSerializer().serialize(t2)
        })


    if request.method == 'POST':
        json = request.body
        if json != None:
            data = JSONDeserializer().deserialize(json)
            #print data

            def saveTile(data, parenttile_id=None):
                data['tileid'], created = uuid.get_or_create(data['tileid'])
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
            tile = models.Tile.objects.get(tileid = data['tileid'])
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