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
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.models.app_settings import AppSettings

@csrf_exempt
def manager(request):


    forms = [{
        'id': '1',
        'title': _('Server Settings'),
        'subtitle': _('Check/Update settings for Arches'),
        'cardgroups': [{
            'id': '1-1',
            'title': _('Arches Server Settings'),
            'cards': [{
                'id': 'DATABASE',
                'title': _('Database'),
                'cardinality': '1',
                'description': _('Update your PostgreSQL database access information'),
                'htmltemplate': '''<form>
                    <div class="row mar-btm">
                        <div class="form-group">
                            <label class="col-xs-12 control-label widget-input-label" for="">Database Name</label>
                            <div class="col-xs-12 col-md-9">
                                <input type="" data-bind="value: NAME" placeholder="template_postgis_20" class="form-control input-lg widget-input">
                            </div>
                        </div>
                    </div>
                    <div class="row mar-btm">
                        <div class="form-group">
                            <label class="col-xs-12 control-label widget-input-label" for="">User</label>
                            <div class="col-xs-12 col-md-9">
                                <input type="" data-bind="value: USER" placeholder="postgres" class="form-control input-lg widget-input">
                            </div>
                        </div>
                    </div>
                    <div class="row mar-btm">
                        <div class="form-group">
                            <label class="col-xs-12 control-label widget-input-label" for="">Password</label>
                            <div class="col-xs-12 col-md-9">
                                <input type="password" data-bind="value: PASSWORD" placeholder="password" class="form-control input-lg widget-input">
                            </div>
                        </div>
                    </div>
                    <div class="row mar-btm">
                        <div class="form-group">
                            <label class="col-xs-12 control-label widget-input-label" for="">Port</label>
                            <div class="col-xs-12 col-md-9">
                                <input type="" data-bind="value: PORT" placeholder="5432" class="form-control input-lg widget-input widget-input">
                            </div>
                        </div>
                    </div>
                </form>'''
            },{
                'id': 'cardid1-1-2',
                'title': _('Keys'),
                'cardinality': 'n',
                'description': _('Keys allow you to access external services (like Mapbox maps) from Arches. Add your user keys (optional):'),
                'htmltemplate': '''<form>
                    <div class="row mar-btm">
                        <div class="form-group">
                            <label class="col-xs-12 control-label widget-input-label" for="">Service Provider</label>
                            <div class="col-xs-12 col-md-9">
                                <input type="" data-bind="value: nodeid5" placeholder="e.g.: MapBox" class="form-control input-lg widget-input">
                            </div>
                        </div>
                    </div>
                    <div class="row mar-btm">
                        <div class="form-group">
                            <label class="col-xs-12 control-label widget-input-label" for="">Service Name</label>
                            <div class="col-xs-12 col-md-9">
                                <input type="" data-bind="value: nodeid6" placeholder="e.g. MapBox Base Maps" class="form-control input-lg widget-input">
                            </div>
                        </div>
                    </div>
                    <div class="row mar-btm">
                        <div class="form-group">
                            <label class="col-xs-12 widget-input-label" for="">Key</label>
                            <div class="col-xs-12 col-md-9">
                                <input type="" data-bind="value: nodeid7" placeholder="Enter key value" class="form-control input-lg widget-input widget-input-disabled">
                            </div>
                        </div>
                    </div>
                </form>'''
            }]
        }]
    }]

    app_settings = AppSettings()

    db = app_settings.get('DATABASES')['default']

    tiles = {
        "DATABASE": [{
            'tileinstanceid': '',
            'tilegroupid': '12',
            'tileinstancedata': {
                "USER": db['USER'],
                "PASSWORD": db['PASSWORD'],
                "PORT": db['PORT'],
                "NAME": db['NAME'],
            },
            'cardid': '5d28d9c0-db90-11e5-8719-ef7f5d2d967b',
            'parenttileinstanceid': '',
            'resourceclassid': 'b9157be4-db90-11e5-8aeb-b7c0a160df7a',
            'resourceinstanceid': '89f12728-db90-11e5-9016-5748aec58ad1'
        }],
        "cardid1-1-2": [{
            'tileinstanceid': '',
            'tilegroupid': '',
            'tileinstancedata': {
                "nodeid5": "Bing",
                "nodeid6": "Map Key",
                "nodeid7": "23984ll2399494",
            },
            'cardid': 'cardid1-1-2',
            'parenttileinstanceid': '',
            'resourceclassid': '',
            'resourceinstanceid': ''
        },{
            'tileinstanceid': '',
            'tilegroupid': '',
            'tileinstancedata': {
                "nodeid5": "MapBox",
                "nodeid6": "MapBox Base Maps",
                "nodeid7": "At53AAkpRmfAAU6uclyo7DDveGo_PHSJE5nT4PDJ9htfDRZwjGcxFTXnLJY2GBcd",
            },
            'cardid': 'cardid1-1-2',
            'parenttileinstanceid': '',
            'resourceclassid': '',
            'resourceinstanceid': ''
        }],
        "cardid1-1-2-blank": [{
            'tileinstanceid': '',
            'tilegroupid': '',
            'tileinstancedata': {
                "nodeid5": "",
                "nodeid6": "",
                "nodeid7": "",
            },
            'cardid': 'cardid1-1-2',
            'parenttileinstanceid': '',
            'resourceclassid': '',
            'resourceinstanceid': ''
        }]
    }

    
    if request.method == 'POST':
        json = request.body
        if json != None:
            data = JSONDeserializer().deserialize(json)
            print data
            # tile = models.Tileinstances()
            # tile.tileinstanceid = str(uuid.uuid4())
            # tile.cardid_id = data['cardid']
            # tile.tileinstancedata = data['tileinstancedata']
            # tile.tilegroupid = data['tilegroupid']
            # tile.resourceinstanceid_id = data['resourceinstanceid']
            # tile.resourceclassid_id = data['resourceclassid']
            # tile.save()
            #app_settings.update(data)

    return render(request, 'config-manager.htm', {
        'main_script': 'config-manager',
        'active_page': 'Home',
        'app_settings': app_settings,
        'forms': forms,
        'tiledata': JSONSerializer().serialize(tiles)
    })
