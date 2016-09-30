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
from arches.app.models.card import Card
from django.utils.translation import ugettext as _
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

class Form(object):
    def __init__(self, resourceid=None, formid=None):
        self.forms = []
        self.widgets = []
        self.tiles = {}
        self.blanks = {}

        if resourceid or formid:
            self.load(resourceid, formid=formid)


    def load(self, resourceid, formid=None):
        self.widgets = models.Widget.objects.all()

        # self.forms = [{
        #     'id': '1',
        #     'title': _('Server Settings'),
        #     'subtitle': _('Check/Update settings for Arches'),
        #     'cardgroups': [
        #     {
        #         'id': '1-1',
        #         'title': _('Arches Server Settings'),
        #         'cardinality': '1',
        #         'nodegroup_id': '21111111-0000-0000-0000-000000000000',  # <-- virtual nodegroup because this cardgroup has a cardinality of 1
        #         'cards': [{
        #             'id': '30000000-0000-0000-0000-000000000000',
        #             'title': _('TEst'),
        #             'cardinality': '1',
        #             'nodegroup_id': '99999999-0000-0000-0000-000000000001',
        #             'description': _('Keys allow you to access external services (like Mapbox maps) from Arches. Add your user keys (optional):'),
        #             'widgets':[{
        #                 'name': 'text-widget',
        #                 'label': 'Service Name',
        #                 'placeholder': 'e.g. MapBox Base Maps',
        #                 'node_id': '20000000-0000-0000-0000-000000000002'
        #             },{
        #                 'name': 'text-widget',
        #                 'label': 'Key',
        #                 'placeholder': 'Enter key value',
        #                 'node_id': '20000000-0000-0000-0000-000000000004'
        #             }]
        #         },{
        #             'id': '30000000-0000-0000-0000-000000000000',
        #             'title': _('Keys'),
        #             'cardinality': 'n',
        #             'nodegroup_id': '99999999-0000-0000-0000-000000000000',
        #             'description': _('Keys allow you to access external services (like Mapbox maps) from Arches. Add your user keys (optional):'),
        #             'widgets':[{
        #                 'name': 'select-widget',
        #                 'label': 'Service Provider',
        #                 'placeholder': 'e.g.: MapBox',
        #                 'node_id': '20000000-0000-0000-0000-000000000003',
        #                 'options': [{'id':'1', 'text': 'Bing'},{'id': '2', 'text': 'Map Box'}]
        #             },{
        #                 'name': 'text-widget',
        #                 'label': 'Service Name',
        #                 'placeholder': 'e.g. MapBox Base Maps',
        #                 'node_id': '20000000-0000-0000-0000-000000000002'
        #             },{
        #                 'name': 'text-widget',
        #                 'label': 'Key',
        #                 'placeholder': 'Enter key value',
        #                 'node_id': '20000000-0000-0000-0000-000000000004'
        #             }]
        #         }],
        #         'widgets': []
        #     },
        #     {
        #         'id': '50000000-0000-0000-0000-000000000000',
        #         'title': _('Base Maps'),
        #         'cardinality': 'n',
        #         'nodegroup_id': '11111111-0000-0000-0000-000000000000',
        #         'cards': [{
        #             'id': '30000000-0000-0000-0000-000000000000',
        #             'title': _('Other Data'),
        #             'cardinality': 'n',
        #             'nodegroup_id': '32999999-0000-0000-0000-000000000000',
        #             'description': _('Do something awesome here'),
        #             'widgets':[{
        #                 'name': 'select-widget',
        #                 'label': 'Service Provider',
        #                 'placeholder': 'e.g.: MapBox',
        #                 'node_id': '20000000-0000-0000-0000-000000000003',
        #                 'options': [{'id':'1', 'text': 'Bing'},{'id': '2', 'text': 'Map Box'}]
        #             },{
        #                 'name': 'text-widget',
        #                 'label': 'Service Name',
        #                 'placeholder': 'e.g. MapBox Base Maps',
        #                 'node_id': '20000000-0000-0000-0000-000000000002'
        #             },{
        #                 'name': 'text-widget',
        #                 'label': 'Key',
        #                 'placeholder': 'Enter key value',
        #                 'node_id': '20000000-0000-0000-0000-000000000004'
        #             }]
        #         }
        #         ,{
        #             'id': '30000000-0000-0000-0000-000000000001',
        #             'title': _('TEST'),
        #             'cardinality': 'n',
        #             'nodegroup_id': '19999999-0000-0000-0000-000000000000',
        #             'description': _('TEAFASDF'),
        #             'widgets':[{
        #                 'name': 'text-widget',
        #                 'label': 'Service Name',
        #                 'placeholder': 'e.g. MapBox Base Maps',
        #                 'node_id': '20000000-0000-0000-0000-000000000002'
        #             },{
        #                 'name': 'text-widget',
        #                 'label': 'Key',
        #                 'placeholder': 'Enter key value',
        #                 'node_id': '20000000-0000-0000-0000-000000000004'
        #             }]
        #         }
        #         ],
        #         'widgets': []
        #     }]
        # }]

        #formid = '3d98910a-7f84-11e6-892b-14109fd34195'

        tiles = models.Tile.objects.filter(resourceinstance_id=resourceid)

        if formid is not None:
            form = models.Form.objects.get(pk=formid)
            formxcards = form.formxcard_set.all()
            form_obj = {
                'id': form.pk,
                'title': form.title,
                'subtitle': form.subtitle
            }
            form_obj['cardgroups'] = []
            for formxcard in formxcards:
                card_obj = JSONSerializer().serializeToPython(Card.objects.get(cardid=formxcard.card_id))
                card_obj['tiles'] = JSONSerializer().serializeToPython(tiles.filter(nodegroup_id=card_obj['nodegroup_id']))
                for child_card in card_obj['cards']:
                    child_card['tiles'] = JSONSerializer().serializeToPython(tiles.filter(nodegroup_id=child_card['nodegroup_id']))
                form_obj['cardgroups'].append(card_obj)
            self.forms = [form_obj]
        else:
            pass


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
                            print card['nodegroup_id']
                            parentTile['tiles'][card['nodegroup_id']] = []
                        for tile in JSONSerializer().serializeToPython(tiles.filter(parenttile_id=parentTile['tileid'])):
                            parentTile['tiles'][str(tile['nodegroup_id'])].append(tile)

                if len(self.tiles[cardgroup['nodegroup_id']]) == 0 and cardgroup['cardinality'] == '1':
                    # add blank parent tile
                    parentTile = JSONSerializer().serializeToPython(models.Tile())
                    parentTile['tileid'] = ''
                    parentTile['parenttile_id'] = None
                    parentTile['resourceinstance_id'] = resourceid
                    parentTile['nodegroup_id'] = cardgroup['nodegroup_id']
                    parentTile['tiles'] = {}
                    parentTile['data'] = {}
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
                            tile['data'][widget['node_id']] = ''

                        parentTile['tiles'][card['nodegroup_id']] = JSONSerializer().serializeToPython(tiles.filter(nodegroup_id=card['nodegroup_id']))

                        if len(parentTile['tiles'][card['nodegroup_id']]) == 0 and card['cardinality'] == '1':
                            parentTile['tiles'][card['nodegroup_id']] = [copy.deepcopy(tile)]



        for form in self.forms:
            for cardgroup in form['cardgroups']:
                # add blank parent tile
                parentTile = JSONSerializer().serializeToPython(models.Tile())
                parentTile['tileid'] = ''
                parentTile['parenttile_id'] = None
                parentTile['resourceinstance_id'] = resourceid
                parentTile['nodegroup_id'] = cardgroup['nodegroup_id']
                parentTile['tiles'] = {}
                parentTile['data'] = {}
                for widget in cardgroup['widgets']:
                    parentTile['data'][widget['node_id']] = ''

                # add a blank tile for the cardgroup
                self.blanks[parentTile['nodegroup_id']] = parentTile

                for card in cardgroup['cards']:
                    # make a blank tile
                    tile = JSONSerializer().serializeToPython(models.Tile())
                    tile['tileid'] = ''
                    tile['parenttile_id'] = None # parentTile
                    tile['resourceinstance_id'] = resourceid
                    tile['nodegroup_id'] = card['nodegroup_id']
                    tile['tiles'] = {}
                    tile['data'] = {}
                    for widget in card['widgets']:
                        tile['data'][widget['node_id']] = ''

                    if(card['cardinality'] == '1'):
                        parentTile['tiles'][card['nodegroup_id']] = [tile]
                    else:
                        parentTile['tiles'][card['nodegroup_id']] = []
                    
                    # add a blank tile for each card 
                    self.blanks[tile['nodegroup_id']] = tile