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
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from arches.app.models import models
from django.utils.translation import ugettext as _
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.models.app_settings import AppSettings

@csrf_exempt
def manager(request):

    if request.method == 'GET':
        resourceinstanceid = '40000000-0000-0000-0000-000000000000'
        resourceclassid = '20000000-0000-0000-0000-000000000000'

        widgets = models.Widget.objects.all()
        string_widget = widgets.get(name='string')
        select_widget = widgets.get(name='select')

        forms = [{
            'id': '1',
            'title': _('Server Settings'),
            'subtitle': _('Check/Update settings for Arches'),
            'cardgroups': [{
                'id': '1-1',
                'title': _('Arches Server Settings'),
                'cards': [
                # {
                #     'id': 'DATABASE',
                #     'title': _('Database'),
                #     'cardinality': '1',
                #     'description': _('Update your PostgreSQL database access information'),
                #     'widgets':[{
                #         'path': string_widget.template.path,
                #         'label': 'Database Name',
                #         'placeholder': '',
                #         'nodeid': 'NAME'
                #     },{
                #         'path': string_widget.template.path,
                #         'label': 'User',
                #         'placeholder': '',
                #         'nodeid': 'USER'
                #     },{
                #         'path': string_widget.template.path,
                #         'label': 'Password',
                #         'placeholder': '',
                #         'nodeid': 'PASSWORD'
                #     },{
                #         'path': string_widget.template.path,
                #         'label': 'Port',
                #         'placeholder': '',
                #         'nodeid': 'PORT'
                #     }]
                # },
                {
                    'id': '30000000-0000-0000-0000-000000000000',
                    'title': _('Keys'),
                    'cardinality': 'n',
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
            }]
        }]

        # add placeholders for each card
        t = {}
        for form in forms:
            for cardgroup in form['cardgroups']:
                for card in cardgroup['cards']:
                    tile = models.Tile()
                    tile.tileid = ''
                    tile.resourceinstanceid_id = resourceinstanceid
                    #tile.resourceclassid_id = resourceclassid
                    tile.cardid_id = card['id']
                    tile.data = {}
                    for widget in card['widgets']:
                        tile.data[widget['nodeid']] = ''
                    t[card['id']+'-blank'] = [tile]
                    t[card['id']] = []
        
        # append actual data            
        for tile in models.Tile.objects.filter(resourceinstanceid=resourceinstanceid):
            t[str(tile.cardid_id)].append(tile)


        # t = {
        #     "DATABASE": [{
        #         'tileid': '',
        #         'tilegroupid': '12',
        #         'data': {
        #             "USER": db['USER'],
        #             "PASSWORD": db['PASSWORD'],
        #             "PORT": db['PORT'],
        #             "NAME": db['NAME'],
        #         },
        #         'cardid': '5d28d9c0-db90-11e5-8719-ef7f5d2d967b',
        #         'resourceclassid': 'b9157be4-db90-11e5-8aeb-b7c0a160df7a',
        #         'resourceinstanceid': '89f12728-db90-11e5-9016-5748aec58ad1'
        #     }],
        #     "30000000-0000-0000-0000-000000000000": [{
        #         'tileid': '',
        #         'tilegroupid': '',
        #         'data': {
        #             "20000000-0000-0000-0000-000000000003": "1",
        #             "20000000-0000-0000-0000-000000000002": "Map Key",
        #             "20000000-0000-0000-0000-000000000004": "23984ll2399494",
        #         },
        #         'cardid': '30000000-0000-0000-0000-000000000000',
        #         'resourceclassid': '',
        #         'resourceinstanceid': ''
        #     },{
        #         'tileid': '',
        #         'tilegroupid': '',
        #         'data': {
        #             "20000000-0000-0000-0000-000000000003": "2",
        #             "20000000-0000-0000-0000-000000000002": "MapBox Base Maps",
        #             "20000000-0000-0000-0000-000000000004": "At53AAkpRmfAAU6uclyo7DDveGo_PHSJE5nT4PDJ9htfDRZwjGcxFTXnLJY2GBcd",
        #         },
        #         'cardid': '30000000-0000-0000-0000-000000000000',
        #         'resourceclassid': '',
        #         'resourceinstanceid': ''
        #     }],
        #     "30000000-0000-0000-0000-000000000000-blank": [{
        #         'tileid': '',
        #         'tilegroupid': '',
        #         'data': {
        #             "20000000-0000-0000-0000-000000000003": "",
        #             "20000000-0000-0000-0000-000000000002": "",
        #             "20000000-0000-0000-0000-000000000004": "",
        #         },
        #         'cardid': '30000000-0000-0000-0000-000000000000',
        #         'resourceclassid': '',
        #         'resourceinstanceid': ''
        #     }]
        # }

        return render(request, 'config-manager.htm', {
            'main_script': 'config-manager',
            'active_page': 'Home',
            'forms': forms,
            'tiledata': JSONSerializer().serialize(t)
        })


    if request.method == 'POST':
        json = request.body
        if json != None:
            data = JSONDeserializer().deserialize(json)
            print data
            data['tileid'], created = uuid.get_or_create(data['tileid'])
            tile, created = models.Tile.objects.update_or_create(
                tileid = data['tileid'], 
                defaults = {
                    'tilegroupid': data['tilegroupid'], 
                    'cardid_id': data['cardid'],
                    'data': data['data'],
                    'resourceinstanceid_id': data['resourceinstanceid'],
                    #'resourceclassid_id': data['resourceclassid']
                }
            )
        return JSONResponse(tile)

# Move to util function
def get(id):
    try:
        uuid.UUID(id)
        return uuid.UUID(id), False
    except(ValueError):
        return uuid.uuid4(), True


uuid.get_or_create = get