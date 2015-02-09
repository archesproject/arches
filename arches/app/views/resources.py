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

import re
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.models.entity import Entity
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Terms
from arches.app.views.concept import get_preflabel_from_valueid

@login_required
@csrf_exempt
def resource_manager(request, resourcetypeid='', form_id='', resourceid=''):

    if resourceid != '':
        resource = Resource(resourceid)
    elif resourcetypeid != '':
        resource = Resource({'entitytypeid': resourcetypeid})

    form = resource.get_form(form_id)

    if request.method == 'POST':
        # get the values from the form and pass to the resource
        data = JSONDeserializer().deserialize(request.POST.get('formdata', {}))
        form.update(data)

        with transaction.atomic():
            if resourceid != '':
                resource.delete_index()
            resource.save(user=request.user)
            resource.index()
            resourceid = resource.entityid

            return redirect('resource_manager', resourcetypeid=resourcetypeid, form_id=form_id, resourceid=resourceid)

    return render_to_response('resource-manager.htm', {
            'form': form,
            'formdata': JSONSerializer().serialize(form.data),
            'form_template': 'views/forms/' + form_id + '.htm',
            'form_id': form_id,
            'resourcetypeid': resourcetypeid,
            'resourceid': resourceid,
            'main_script': 'resource-manager',
            'active_page': 'ResourceManger',
            'resource': resource,
            'resource_name': resource.get_primary_name(),
            'resource_type_name': resource.get_type_name(),
            'form_groups': resource.form_groups
        },
        context_instance=RequestContext(request))
    
def related_resources(request, resourceid):
    lang = request.GET.get('lang', settings.LANGUAGE_CODE)
    start = request.GET.get('start', 0)
    return JSONResponse(get_related_resources(resourceid, lang, start=start, limit=15), indent=4)

def get_related_resources(resourceid, lang, limit=1000, start=0):
    ret = {
        'resource_relationships': [],
        'related_resources': []
    }
    se = SearchEngineFactory().create()

    query = Query(se, limit=limit, start=start)
    query.add_filter(Terms(field='entityid1', terms=resourceid).dsl, operator='or')
    query.add_filter(Terms(field='entityid2', terms=resourceid).dsl, operator='or')
    resource_relations = query.search(index='resource_relations', doc_type='all')
    ret['total'] = resource_relations['hits']['total']

    entityids = set()
    for relation in resource_relations['hits']['hits']:
        relation['_source']['preflabel'] = get_preflabel_from_valueid(relation['_source']['relationshiptype'], lang)
        ret['resource_relationships'].append(relation['_source'])
        entityids.add(relation['_source']['entityid1'])
        entityids.add(relation['_source']['entityid2'])
    if len(entityids) > 0:
        entityids.remove(resourceid)   

    related_resources = se.search(index='entity', doc_type='_all', id=list(entityids))
    if related_resources:
        for resource in related_resources['docs']:
            ret['related_resources'].append(resource['_source'])

    return ret

def map_layers(request, entitytypeid='all', get_centroids=False):
    data = []
    bbox = request.GET.get('bbox', '')
    limit = request.GET.get('limit', settings.MAP_LAYER_FEATURE_LIMIT)
    entityids = request.GET.get('entityid', '')
    geojson_collection = {
      "type": "FeatureCollection",
      "features": []
    }
    
    se = SearchEngineFactory().create()
    query = Query(se, limit=limit)

    args = { 'index': 'maplayers' }
    if entitytypeid != 'all':
        args['doc_type'] = entitytypeid
    if entityids != '':
        for entityid in entityids.split(','):
            geojson_collection['features'].append(se.search(index='maplayers', id=entityid)['_source'])
        return JSONResponse(geojson_collection)

    data = query.search(**args)

    for item in data['hits']['hits']:
        if get_centroids:
            item['_source']['geometry'] = item['_source']['properties']['centroid']
            item['_source'].pop('properties', None)
        else:
            item['_source']['properties'].pop('extent', None)
            item['_source']['properties'].pop('centroid', None)
        geojson_collection['features'].append(item['_source'])

    return JSONResponse(geojson_collection)

def edit_history(request, resourceid=''):
    ret = []
    current = None
    index = -1
    start = request.GET.get('start', 0)
    limit = request.GET.get('limit', 10)
    if resourceid != '':
        dates = models.EditLog.objects.filter(resourceid = resourceid).values_list('timestamp', flat=True).order_by('-timestamp').distinct('timestamp')[start:limit]
        # dates = models.EditLog.objects.datetimes('timestamp', 'second', order='DESC')
        for date in dates:
            #ret[str(date)] = models.EditLog.objects.filter(resourceid = self.resource.entityid, timestamp = date)
            print str(date)

        for log in models.EditLog.objects.filter(resourceid = resourceid, timestamp__in = dates).values().order_by('-timestamp', 'attributeentitytypeid'):
            if str(log['timestamp']) != current:
                current = str(log['timestamp']) 
                ret.append({'date':str(log['timestamp'].date()), 'time': str(log['timestamp'].time().replace(microsecond=0).isoformat()), 'log': []})
                index = index + 1

            ret[index]['log'].append(log)
            
    return JSONResponse(ret, indent=4)


class ResourceForm(object):
    def __init__(self, resource):
        # here is where we can create the basic format for the form data
        info = self.get_info()
        self.id = info['id']
        self.name = info['name']
        self.icon = info['icon']
        self.resource = resource
        if self.resource == None:
            self.schema = None
        else:
            self.schema = Entity.get_mapping_schema(self.resource.entitytypeid)
        
        self.data = {
            "domains": {},
            "defaults": {}
        }
        self.load()
    
    @staticmethod
    def get_info():
        return {
            'id': '',
            'icon': '',
            'name': '',
            'class': ResourceForm
        }

	def update(self, data):
		# update resource w/ post data
		return 

    def load(self):
        # retrieves the data from the server
        return 

    def get_nodes(self, entitytypeid):
        ret = []
        entities = self.resource.find_entities_by_type_id(entitytypeid)
        for entity in entities:
            data = {}

            for entity in entity.flatten():
                #data[entity.entitytypeid] = self.encode_entity(entity)
                data = dict(data.items() + self.encode_entity(entity).items())
            ret.append(data)
        return ret

    def update_nodes(self, entitytypeid, data):
        for entity in self.resource.find_entities_by_type_id(entitytypeid):
            self.resource.child_entities.remove(entity)

        if self.schema == None:
            self.schema = Entity.get_mapping_schema(self.resource.entitytypeid)
        for value in data[entitytypeid.replace('.', '_')]:
            baseentity = None
            for newentity in self.decode_data_item(value):
                entity = Entity()
                entity.create_from_mapping(self.resource.entitytypeid, self.schema[newentity['entitytypeid']]['steps'], newentity['entitytypeid'], newentity['value'], newentity['entityid'])

                if baseentity == None:
                    baseentity = entity
                else:
                    baseentity.merge(entity)
            
            self.resource.merge_at(baseentity, self.resource.entitytypeid)

    def update_node(self, entitytypeid, data):
        if self.schema == None:
            self.schema = Entity.get_mapping_schema(self.resource.entitytypeid)
        nodes = self.resource.find_entities_by_type_id(entitytypeid)
        node_data = self.decode_data_item(data[entitytypeid.replace('.', '_')])[0]

        if len(nodes) == 0:
            entity = Entity()
            entity.create_from_mapping(self.resource.entitytypeid, self.schema[entitytypeid]['steps'], entitytypeid, node_data['value'], node_data['entityid'])
            self.resource.merge_at(entity, self.resource.entitytypeid)
        else:
            nodes[0].value = node_data['value']

    def encode_entity(self, entity):
        def enc(entity, attr):
            return '%s__%s' % (entity.entitytypeid.replace('.', '_'), attr)

        ret = {}
        for key, value in entity.__dict__.items():
            if not key.startswith("__"):
                ret[enc(entity, key)] = value
        return ret

    def decode_data_item(self, entity):
        def dec(item):
            # item = "NAME_E41__entitytypeid"
            val = item.split('__')
            if len(val) != 2:
                return False
            entitytypeid = val[0]
            propertyname = val[1]
            
            v = entitytypeid.split('_')
            entitytypeid = '%s.%s' % ('_'.join(v[:-1]), v[-1])
            return (entitytypeid, propertyname)

        ret = {}
        for key, value in entity.iteritems():
            r = dec(key)
            if r:
                if r[0] not in ret:
                    ret[r[0]] = {}
                ret[r[0]][r[1]] = value

        ret2 = []
        for key, value in ret.iteritems():
            value['entitytypeid'] = key
            ret2.append(value)
        return ret2
