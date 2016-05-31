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

import copy
from arches.app.models import models
from arches.app.models.tile import Tile
from django.utils.translation import ugettext as _
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

class Form(object):
    def __init__(self, resourceid=None):
        self.forms = []
        self.widgets = []
        self.tiles = {}
        self.blanks = {}

        if resourceid:
            self.load(resourceid)

    def load(self, resourceid):
        widgets = models.Widget.objects.all()
        string_widget = widgets.get(name='string')
        select_widget = widgets.get(name='select')
        self.widgets = ['widgets/text', 'widgets/select']

        self.forms = [{
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
                        'name': 'text-widget',
                        'nodeid': '20000000-0000-0000-0000-000000000002',
                        'config': {
                            'label': 'Service Name',
                            'placeholder': 'e.g. MapBox Base Maps',
                        }
                    },{
                        'name': 'text-widget',
                        'nodeid': '20000000-0000-0000-0000-000000000004',
                        'config': {
                            'label': 'Key',
                            'placeholder': 'Enter key value',
                        }
                    }]
                },{
                    'id': '30000000-0000-0000-0000-000000000000',
                    'title': _('Keys'),
                    'cardinality': 'n',
                    'nodegroup_id': '99999999-0000-0000-0000-000000000000',
                    'description': _('Keys allow you to access external services (like Mapbox maps) from Arches. Add your user keys (optional):'),
                    'widgets':[{
                        'name': 'select-widget',
                        'nodeid': '20000000-0000-0000-0000-000000000003',
                        'config': {
                            'label': 'Service Provider',
                            'placeholder': 'e.g.: MapBox',
                            'options': [{'id':'1', 'text': 'Bing'},{'id': '2', 'text': 'Map Box'}]
                        }
                    },{
                        'name': 'text-widget',
                        'nodeid': '20000000-0000-0000-0000-000000000002',
                        'config': {
                            'label': 'Service Name',
                            'placeholder': 'e.g. MapBox Base Maps',
                        }
                    },{
                        'name': 'text-widget',
                        'nodeid': '20000000-0000-0000-0000-000000000004',
                        'config': {
                            'label': 'Key',
                            'placeholder': 'Enter key value',
                        }
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
                        'name': 'select-widget',
                        'nodeid': '20000000-0000-0000-0000-000000000003',
                        'config': {
                            'label': 'Service Provider',
                            'placeholder': 'e.g.: MapBox',
                            'options': [{'id':'1', 'text': 'Bing'},{'id': '2', 'text': 'Map Box'}]
                        }
                    },{
                        'name': 'text-widget',
                        'nodeid': '20000000-0000-0000-0000-000000000002',
                        'config': {
                            'label': 'Service Name',
                            'placeholder': 'e.g. MapBox Base Maps',
                        }
                    },{
                        'name': 'text-widget',
                        'nodeid': '20000000-0000-0000-0000-000000000004',
                        'config': {
                            'label': 'Key',
                            'placeholder': 'Enter key value',
                        }
                    }]
                }
                ,{
                    'id': '30000000-0000-0000-0000-000000000001',
                    'title': _('TEST'),
                    'cardinality': 'n',
                    'nodegroup_id': '19999999-0000-0000-0000-000000000000',
                    'description': _('TEAFASDF'),
                    'widgets':[{
                        'name': 'text-widget',
                        'nodeid': '20000000-0000-0000-0000-000000000002',
                        'config': {
                            'label': 'Service Name',
                            'placeholder': 'e.g. MapBox Base Maps',
                        }
                    },{
                        'name': 'text-widget',
                        'nodeid': '20000000-0000-0000-0000-000000000004',
                        'config': {
                            'label': 'Key',
                            'placeholder': 'Enter key value',
                        }
                    }]
                }
                ]
            }]
        }]

        tiles = models.Tile.objects.filter(resourceinstance_id=resourceid)

        # def addTiles(parentObj, nodegroup_id, tiles):
        #     parentObj.tiles[nodegroup_id] = JSONSerializer().serializeToPython(tiles.filter(nodegroup_id=nodegroup_id))
        #     return parentObj.tiles[nodegroup_id]

        for form in self.forms:
            for cardgroup in form['cardgroups']:
                #addedTiles = addTiles(self, cardgroup['nodegroup_id'], tiles)
                self.tiles[cardgroup['nodegroup_id']] = JSONSerializer().serializeToPython(tiles.filter(nodegroup_id=cardgroup['nodegroup_id']))

                if len(self.tiles[cardgroup['nodegroup_id']]) > 0:
                    for parentTile in self.tiles[cardgroup['nodegroup_id']]:
                        parentTile['tiles'] = {}
                        for card in cardgroup['cards']:
                            parentTile['tiles'][card['nodegroup_id']] = []
                        for tile in JSONSerializer().serializeToPython(tiles.filter(parenttile_id=parentTile['tileid'])):
                            parentTile['tiles'][str(tile['nodegroup_id'])].append(tile)

                if len(self.tiles[cardgroup['nodegroup_id']]) == 0 and cardgroup['cardinality'] == '1':
                    # add blank parent tile
                    parentTile = JSONSerializer().serializeToPython(models.Tile())
                    parentTile['tileid'] = ''
                    parentTile['tiles'] = {}
                    parentTile['nodegroup_id'] = cardgroup['nodegroup_id']
                    parentTile['resourceinstance_id'] = resourceid
                    self.tiles[cardgroup['nodegroup_id']] = [parentTile]

                    for card in cardgroup['cards']:
                        #print card
                        # make a blank tile
                        tile = JSONSerializer().serializeToPython(models.Tile())
                        tile['tileid'] = ''
                        tile['parenttile_id'] = None # parentTile
                        tile['resourceinstance_id'] = resourceid
                        tile['nodegroup_id'] = card['nodegroup_id']
                        tile['data'] = {}
                        for widget in card['widgets']:
                            tile['data'][widget['nodeid']] = ''

                        parentTile['tiles'][card['nodegroup_id']] = JSONSerializer().serializeToPython(tiles.filter(nodegroup_id=card['nodegroup_id']))

                        if len(parentTile['tiles'][card['nodegroup_id']]) == 0 and card['cardinality'] == '1':
                            parentTile['tiles'][card['nodegroup_id']] = [copy.deepcopy(tile)]



        for form in self.forms:
            for cardgroup in form['cardgroups']:
                # add blank parent tile
                parentTile = JSONSerializer().serializeToPython(models.Tile())
                parentTile['tileid'] = ''
                parentTile['tiles'] = {}
                parentTile['nodegroup_id'] = cardgroup['nodegroup_id']
                parentTile['resourceinstance_id'] = resourceid

                # add a blank tile for the cardgroup
                self.blanks[parentTile['nodegroup_id']] = parentTile

                for card in cardgroup['cards']:
                    # make a blank tile
                    tile = JSONSerializer().serializeToPython(models.Tile())
                    tile['tileid'] = ''
                    tile['parenttile_id'] = None # parentTile
                    tile['resourceinstance_id'] = resourceid
                    tile['nodegroup_id'] = card['nodegroup_id']
                    tile['tiles'] = []
                    tile['data'] = {}
                    for widget in card['widgets']:
                        tile['data'][widget['nodeid']] = ''

                    parentTile['tiles'][card['nodegroup_id']] = []
                    
                    # add a blank tile for each card 
                    self.blanks[tile['nodegroup_id']] = tile