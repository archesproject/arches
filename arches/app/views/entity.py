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

from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from arches.app.models.entity import Entity
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

@csrf_exempt
def Entities(request, entityid):
    entity = []

    if request.method == 'GET':
        if entityid == '':
            pass
        else:
            entity = Entity().get(entityid)
    else:
        if 'edit' not in request.user.user_groups:
            raise Exception('User must be logged in to insert, update, or delete entities')
        if request.method == 'POST':
            if len(request.FILES) > 0:
                jsondata = JSONDeserializer().deserialize(request.POST.get('json'))  
            else:
                jsondata = JSONDeserializer().deserialize(request.body)            
            if not isinstance(jsondata, list):
                jsondata = [jsondata]
            for entityjson in jsondata:
                entity = Entity(entityjson)      
                if entity.entityid != '':
                    entity.delete_index() 
                entity.save(username=request.user.username, uploadedfile=request.FILES.get('file', None))
                entity.index()
        elif request.method == 'DELETE':
            jsondata = JSONDeserializer().deserialize(request.body)
            if not isinstance(jsondata, list):
                jsondata = [jsondata]
            for entityjson in jsondata:
                entity = Entity(entityjson)
                entity.delete_index()                
                entity.delete(delete_root=entity.get_rank()==0)
    return HttpResponse(JSONSerializer().serialize(entity, ensure_ascii=True, indent=4))

@csrf_exempt
def EntityTypes(request, entitytypeid):
    entityschema = []
    if entitytypeid == '':
        return HttpResponse(JSONSerializer().serialize({}, ensure_ascii=True, indent=4))
    else:
        if request.GET.get('f') is None:
            return render(request, 'graph.htm', {})
        else:
            entityschema = {entitytypeid: Entity.get_mapping_schema(entitytypeid)}            
            if request.GET.get('f') == 'json':
                return HttpResponse(JSONSerializer().serialize(entityschema, ensure_ascii=True, indent=4), content_type='application/json')
            
            if request.GET.get('f') == 'd3':
                d3Schema = d3Obj()
                d3Schema.name = entitytypeid

                for assestAttr in entityschema[entitytypeid]:
                    d3ObjAssestAttr = d3Obj()
                    d3ObjAssestAttr.name = assestAttr

                    for step in entityschema[entitytypeid][assestAttr]['steps']:
                        d3ObjStep = d3Obj()
                        d3ObjStep.name = step['entitytypedomain'] + ' ' + step['propertyid'] + ' ' + step['entitytyperange'] 
                        d3ObjAssestAttr.children.append(d3ObjStep)
                    d3Schema.children.append(d3ObjAssestAttr)        
                return HttpResponse(JSONSerializer().serialize(d3Schema, ensure_ascii=True, indent=4))

class d3Obj(object):
    def __init__(self):
        self.name = ''
        self.children = []
