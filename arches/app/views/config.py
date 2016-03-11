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
                'nodegroupid': '21111111-0000-0000-0000-000000000000',  # <-- virtual nodegroup because this cardgroup has a cardinality of 1
                'cards': [{
                    'id': '30000000-0000-0000-0000-000000000000',
                    'title': _('Keys'),
                    'cardinality': 'n',
                    'nodegroupid': '99999999-0000-0000-0000-000000000000',
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
                },{
                    'id': '30000000-0000-0000-0000-000000000000',
                    'title': _('TEst'),
                    'cardinality': '1',
                    'nodegroupid': '99999999-0000-0000-0000-000000000001',
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
                }]
            },
            {
                'id': '50000000-0000-0000-0000-000000000000',
                'title': _('Base Maps'),
                'cardinality': 'n',
                'nodegroupid': '11111111-0000-0000-0000-000000000000',
                'cards': [{
                    'id': '30000000-0000-0000-0000-000000000000',
                    'title': _('Other Data'),
                    'cardinality': 'n',
                    'nodegroupid': '32999999-0000-0000-0000-000000000000',
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
                    'nodegroupid': '19999999-0000-0000-0000-000000000000',
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
        
        tiles = models.Tile.objects.filter(resourceinstanceid_id=resourceinstanceid)

        t = {}
        blanks = {}
        for form in forms:
            for cardgroup in form['cardgroups']:
                t[cardgroup['nodegroupid']] = tiles.filter(nodegroupid=cardgroup['nodegroupid'])

                if len(t[cardgroup['nodegroupid']]) == 0:
                    # add blank parent tile
                    parentTile = JSONSerializer().serializeToPython(models.Tile())
                    parentTile['tileid'] = ''
                    # parentTile.nodegroupid_id = cardgroup['nodegroupid']
                    # parentTile.resourceinstanceid_id = resourceinstanceid
                    if cardgroup['cardinality'] == 'n':
                        t[cardgroup['nodegroupid']+'-blank'] = [parentTile]
                    else:
                        t[cardgroup['nodegroupid']] = [parentTile]
                    
                    for card in cardgroup['cards']:
                        # make a blank tile
                        tile = models.Tile()
                        tile.tileid = ''
                        tile.parenttileid = None # parentTile
                        tile.resourceinstanceid_id = resourceinstanceid
                        tile.nodegroupid_id = card['nodegroupid']
                        tile.data = {}
                        for widget in card['widgets']:
                            tile.data[widget['nodeid']] = ''
                        
                        if cardgroup['cardinality'] == 'n':
                            t[cardgroup['nodegroupid']+'-blank'][0][card['nodegroupid'] + '-blank'] = [tile]
                        else:
                            t[cardgroup['nodegroupid']][0][card['nodegroupid'] + '-blank'] = [tile]

                            t[cardgroup['nodegroupid']][0][card['nodegroupid']] = tiles.filter(nodegroupid=card['nodegroupid'])
                            if len(t[cardgroup['nodegroupid']][0][card['nodegroupid']]) == 0:
                                if card['cardinality'] == '1':
                                    t[cardgroup['nodegroupid']][0][card['nodegroupid']] = [tile]

                # if cardgroup['cardinality'] == 'n':
                #     pass

        t2 = []
        blanks = {}
        for form in forms:
            for cardgroup in form['cardgroups']:
                parentTiles = JSONSerializer().serializeToPython(tiles.filter(nodegroupid=cardgroup['nodegroupid']))

                if len(parentTiles) == 0 and cardgroup['cardinality'] == '1':
                    # add blank parent tile
                    parentTile = JSONSerializer().serializeToPython(models.Tile())
                    parentTile['tileid'] = ''
                    parentTile['tiles'] = []
                    parentTile['nodegroupid'] = cardgroup['nodegroupid']
                    parentTile['resourceinstanceid'] = resourceinstanceid
                    parentTiles = [parentTile]

                    for card in cardgroup['cards']:
                        # make a blank tile
                        tile = JSONSerializer().serializeToPython(models.Tile())
                        tile['tileid'] = ''
                        tile['parenttileid'] = None # parentTile
                        tile['resourceinstanceid'] = resourceinstanceid
                        tile['nodegroupid'] = card['nodegroupid']
                        tile['data'] = {}
                        for widget in card['widgets']:
                            tile['data'][widget['nodeid']] = ''
                        #blanks[tile['nodegroupid']] = copy.deepcopy(tile)

                        tile['tiles'] = JSONSerializer().serializeToPython(tiles.filter(nodegroupid=card['nodegroupid']))

                        if len(tile['tiles']) == 0 and card['cardinality'] == '1':
                            tile['tiles'] = [copy.deepcopy(tile)]
                        
                        parentTile['tiles'].append(tile)

                t2 = t2 + parentTiles


        for form in forms:
            for cardgroup in form['cardgroups']:
                # add blank parent tile
                parentTile = JSONSerializer().serializeToPython(models.Tile())
                parentTile['tileid'] = ''
                parentTile['tiles'] = []
                parentTile['nodegroupid'] = cardgroup['nodegroupid']
                parentTile['resourceinstanceid'] = resourceinstanceid

                blanks[parentTile['nodegroupid']] = parentTile

                for card in cardgroup['cards']:
                    # make a blank tile
                    tile = JSONSerializer().serializeToPython(models.Tile())
                    tile['tileid'] = ''
                    tile['parenttileid'] = None # parentTile
                    tile['resourceinstanceid'] = resourceinstanceid
                    tile['nodegroupid'] = card['nodegroupid']
                    tile['tiles'] = []
                    tile['data'] = {}
                    for widget in card['widgets']:
                        tile['data'][widget['nodeid']] = ''

                    parentTile['tiles'].append(tile)
                    
                    blanks[tile['nodegroupid']] = tile
                 
        


        ##
        ##  path down through the nodegroups until you get to actual data
        ##

        # t = [{
        #     'tileid': '123',
        #     'parenttileid': '',
        #     'nodegroupid': '21111111-0000-0000-0000-000000000000',
        #     'data': {},
        #     'resourceclassid': '',
        #     'resourceinstanceid': resourceinstanceid,
        #     'tiles': [{
        #         'tileid': 'xyz',
        #         'parenttileid': '123',
        #         'nodegroupid': '99999999-0000-0000-0000-000000000000',
        #         'data': {
        #             "20000000-0000-0000-0000-000000000003": "1",
        #             "20000000-0000-0000-0000-000000000002": "Map Key",
        #             "20000000-0000-0000-0000-000000000004": "23984ll2399494",
        #         },
        #         'resourceclassid': '',
        #         'resourceinstanceid': resourceinstanceid,
        #         'tiles': [
        #             ....
        #         ]
        #     }]
        # }]

        # No need for a blank cardgroup if the cardgroup cardinality is 1
        # '21111111-0000-0000-0000-000000000000-blank': [{
        #     '99999999-0000-0000-0000-000000000000': [],
        #     "99999999-0000-0000-0000-000000000000-blank": [{
        #         'tileid': '',
        #         'parenttileid': '',
        #         'nodegroupid': '99999999-0000-0000-0000-000000000000',
        #         'data': {
        #             "20000000-0000-0000-0000-000000000003": "",
        #             "20000000-0000-0000-0000-000000000002": "",
        #             "20000000-0000-0000-0000-000000000004": "",
        #         },
        #         'resourceclassid': '',
        #         'resourceinstanceid': resourceinstanceid
        #     }]
        # }],

        ta = {
            '21111111-0000-0000-0000-000000000000': [{ # <-- this is a virtual node group 
                'tileid': '123',
                'parenttileid': '',
                'nodegroupid': '21111111-0000-0000-0000-000000000000',
                'data': {},
                'resourceclassid': '',
                'resourceinstanceid': resourceinstanceid,
                '99999999-0000-0000-0000-000000000000': [{
                    'tileid': '',
                    'parenttileid': '123',
                    'nodegroupid': '99999999-0000-0000-0000-000000000000',
                    'data': {
                        "20000000-0000-0000-0000-000000000003": "1",
                        "20000000-0000-0000-0000-000000000002": "Map Key",
                        "20000000-0000-0000-0000-000000000004": "23984ll2399494",
                    },
                    'resourceclassid': '',
                    'resourceinstanceid': resourceinstanceid
                },{
                    'tileid': '',
                    'parenttileid': '123',
                    'nodegroupid': '99999999-0000-0000-0000-000000000000',
                    'data': {
                        "20000000-0000-0000-0000-000000000003": "2",
                        "20000000-0000-0000-0000-000000000002": "MapBox Base Maps",
                        "20000000-0000-0000-0000-000000000004": "At53AAkpRmfAAU6uclyo7DDveGo_PHSJE5nT4PDJ9htfDRZwjGcxFTXnLJY2GBcd",
                    },
                    'resourceclassid': '',
                    'resourceinstanceid': resourceinstanceid
                }],
                '99999999-0000-0000-0000-000000000001': [{
                    'tileid': '',
                    'parenttileid': '123',
                    'nodegroupid': '99999999-0000-0000-0000-000000000001',
                    'data': {
                        "20000000-0000-0000-0000-000000000002": "Map Key",
                        "20000000-0000-0000-0000-000000000004": "23984ll2399494",
                    },
                    'resourceclassid': '',
                    'resourceinstanceid': resourceinstanceid
                }]
            }],
            '11111111-0000-0000-0000-000000000000': [{   # <-- this is a semantic node group 
                'tileid': '62345678-0000-0000-0000-000000000000',
                'parenttileid': '7777777-0000-0000-0000-000000000000',
                'nodegroupid': '11111111-0000-0000-0000-000000000000',
                'data': {},
                'resourceclassid': '',
                'resourceinstanceid': resourceinstanceid,
                '99999999-0000-0000-0000-000000000000': [{
                    'tileid': '',
                    'parenttileid': '62345678-0000-0000-0000-000000000000',
                    'data': {
                        "20000000-0000-0000-0000-000000000003": "1",
                        "20000000-0000-0000-0000-000000000002": "Map Key",
                        "20000000-0000-0000-0000-000000000004": "23984ll2399494",
                    },
                    'nodegroupid': '99999999-0000-0000-0000-000000000000',
                    'resourceclassid': '',
                    'resourceinstanceid': resourceinstanceid
                },{
                    'tileid': '',
                    'parenttileid': '62345678-0000-0000-0000-000000000000',
                    'data': {
                        "20000000-0000-0000-0000-000000000003": "2",
                        "20000000-0000-0000-0000-000000000002": "MapBox Base Maps",
                        "20000000-0000-0000-0000-000000000004": "At53AAkpRmfAAU6uclyo7DDveGo_PHSJE5nT4PDJ9htfDRZwjGcxFTXnLJY2GBcd",
                    },
                    'nodegroupid': '99999999-0000-0000-0000-000000000000',
                    'resourceclassid': '',
                    'resourceinstanceid': resourceinstanceid
                }]
            },{
                'tileid': '12345678-0000-0000-0000-000000000000',
                'parenttileid': '7777777-0000-0000-0000-000000000000',
                'nodegroupid': '11111111-0000-0000-0000-000000000000',
                'data': {},
                'resourceclassid': '',
                'resourceinstanceid': resourceinstanceid,
                '99999999-0000-0000-0000-000000000000': [{
                    'tileid': '',
                    'parenttileid': '12345678-0000-0000-0000-000000000000',
                    'data': {
                        "20000000-0000-0000-0000-000000000003": "1",
                        "20000000-0000-0000-0000-000000000002": "Map Key",
                        "20000000-0000-0000-0000-000000000004": "TESTING 123",
                    },
                    'nodegroupid': '99999999-0000-0000-0000-000000000000',
                    'resourceclassid': '',
                    'resourceinstanceid': resourceinstanceid
                },{
                    'tileid': '',
                    'parenttileid': '12345678-0000-0000-0000-000000000000',
                    'data': {
                        "20000000-0000-0000-0000-000000000003": "2",
                        "20000000-0000-0000-0000-000000000002": "MapBox Base Maps",
                        "20000000-0000-0000-0000-000000000004": "holy mackrel",
                    },
                    'nodegroupid': '99999999-0000-0000-0000-000000000000',
                    'resourceclassid': '',
                    'resourceinstanceid': resourceinstanceid
                }]
            }]
        }

        # blanks = {
        #     '99999999-0000-0000-0000-000000000000': [{
        #         'tileid': '',
        #         'parenttileid': '',
        #         'data': {
        #             "20000000-0000-0000-0000-000000000003": "",
        #             "20000000-0000-0000-0000-000000000002": "",
        #             "20000000-0000-0000-0000-000000000004": "",
        #         },
        #         'nodegroupid': '99999999-0000-0000-0000-000000000000',
        #         'resourceclassid': '',
        #         'resourceinstanceid': resourceinstanceid
        #     }],
        #     '99999999-0000-0000-0000-000000000001': [{
        #         'tileid': '',
        #         'parenttileid': '',
        #         'data': {
        #             "20000000-0000-0000-0000-000000000003": "",
        #             "20000000-0000-0000-0000-000000000002": "",
        #             "20000000-0000-0000-0000-000000000004": "",
        #         },
        #         'nodegroupid': '99999999-0000-0000-0000-000000000001',
        #         'resourceclassid': '',
        #         'resourceinstanceid': resourceinstanceid
        #     }],
        #     '19999999-0000-0000-0000-000000000000': [{
        #         'tileid': '',
        #         'parenttileid': '',
        #         'data': {
        #             "20000000-0000-0000-0000-000000000002": "",
        #             "20000000-0000-0000-0000-000000000004": "",
        #         },
        #         'nodegroupid': '99999999-0000-0000-0000-000000000001',
        #         'resourceclassid': '',
        #         'resourceinstanceid': resourceinstanceid
        #     }],
        #     '11111111-0000-0000-0000-000000000000': [{
        #         '99999999-0000-0000-0000-000000000000': [],
        #         "99999999-0000-0000-0000-000000000000": [{
        #             'tileid': '',
        #             'parenttileid': '',
        #             'nodegroupid': '99999999-0000-0000-0000-000000000000',
        #             'data': {
        #                 "20000000-0000-0000-0000-000000000003": "",
        #                 "20000000-0000-0000-0000-000000000002": "",
        #                 "20000000-0000-0000-0000-000000000004": "",
        #             },
        #             'resourceclassid': '',
        #             'resourceinstanceid': resourceinstanceid
        #         }]
        #     }],
        # }

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
            print data

            def saveTile(data, parenttileid=None):
                data['parenttileid'] = parenttileid
                data['tileid'], created = uuid.get_or_create(data['tileid'])
                tile, created = models.Tile.objects.update_or_create(
                    tileid = data['tileid'], 
                    defaults = {
                        'nodegroupid_id': data['nodegroupid'], 
                        'data': data['data'],
                        'resourceinstanceid_id': data['resourceinstanceid'],
                        'parenttileid_id': parenttileid
                    }
                )
                return data

            if 'tiles' in data and len(data['tiles']) > 0:                
                parenttile = saveTile(data)

                for tile in data['tiles']:
                    saveTile(tile, parenttileid=parenttile['tileid'])
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