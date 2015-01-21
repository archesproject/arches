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

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import transaction
from django.db import connection
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.concept import Concept
from django.utils.translation import ugettext as _
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.models.entity import Entity
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Terms, Bool

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


def related_resoures(request, resourceid):
    ret = {
        'resource_relationships': [],
        'related_resources': []
    }
    terms = []    
    se = SearchEngineFactory().create()

    query = Query(se)
    terms.append(Terms(field='entityid1', terms=resourceid).dsl)
    terms.append(Terms(field='entityid2', terms=resourceid).dsl)
    query.add_filter(terms, operator='or')
    resource_relations = query.search(index='resource_relations', doc_type='all') 

    entityids = set()
    for relation in resource_relations['hits']['hits']:
        ret['resource_relationships'].append(relation['_source'])
        entityids.add(relation['_source']['entityid1'])
        entityids.add(relation['_source']['entityid2'])
    if len(entityids) > 0:
        entityids.remove(resourceid)   

    related_resources = se.search(index='entity', doc_type='_all', id=list(entityids))
    if related_resources:
        for resource in related_resources['docs']:
            ret['related_resources'].append(resource['_source'])

    return JSONResponse(ret)

def report(request, resourceid):
    report_info = Resource().get_report(resourceid)

    report_info = {
        # 'id':'00000000-0000-0000-0000-000000000000',
        'id':'heritage-resource',
        'ADDRESS_TYPE_E55':'ADDRESS_TYPE:1',
        'ADMINISTRATIVE_SUBDIVISION_TYPE_E55':'ADMINISTRATIVE_SUBDIVISION:1',
        'ADMINISTRATIVE_SUBDIVISION_E48':'San Francisco',
        'ANCILLARY_FEATURE_TYPE_E55':'RELATED_FEATURE:1',
        'BEGINNING_OF_EXISTENCE_TYPE_E55':'BEGIN_EXIST:1',
        'COMPONENT_TYPE_E55':'COMPONENT_TYPE:1',
        'CONDITION_DESCRIPTION_IMAGE_E62':'',
        'CONDITION_DESCRIPTION_E62':'Example image description.',
        'CONDITION_TYPE_E55':'CONDITION:1',
        'CONSTRUCTION_TECHNIQUE_E55':'CONSTRUCTION_TECHNIQUE:1',
        'CULTURAL_PERIOD_E55':'PERIOD_UID:52',
        'DATE_CONDITION_ASSESSED_E49':'12/8/14',
        'DESCRIPTION_OF_LOCATION_E62':'Example location description.',
        'DESCRIPTION_TYPE_E55':'DESCRIPTION_TYPE:1',
        'DESCRIPTION_E62':'Example resource description',
        'PROTECTION_EVENT_E65':[
            {
            'TYPE_OF_DESIGNATION_OR_PROTECTION_E55':'DESIGNATION:1',
            'DESIGNATION_OR_PROTECTION_FROM_DATE_E49':'12/8/10',
            'DESIGNATION_OR_PROTECTION_TO_DATE_E49':'12/8/11'
            },
            {
            'TYPE_OF_DESIGNATION_OR_PROTECTION_E55':'DESIGNATION:2',
            'DESIGNATION_OR_PROTECTION_FROM_DATE_E49':'12/8/13',
            'DESIGNATION_OR_PROTECTION_TO_DATE_E49':'12/8/14'
            },
        ],
        'DISTURBANCE_TYPE_E55':'DISTURBANCE_TYPE:1',
        'END_DATE_OF_EXISTENCE_E49':'12/10/14',
        'END_OF_EXISTENCE_TYPE_E55':'END_EXIST:1',
        'EVALUATION_CRITERIA_ASSIGNMENT_E13':[
            {'EVALUATION_CRITERIA_TYPE_E55':'CTP:1'},
            {'EVALUATION_CRITERIA_TYPE_E55':'CTP:1'}],# 'ELIGIBILITY_REQUIREMENT_TYPE_E55':'Eligibility Type:1' belongs to EVALUATION_CRITERIA_ASSIGNMENT_E13
        'EXTERNAL_XREF_TYPE_E55':'XREF_TYPE:1',
        'EXTERNAL_XREF_E42':'xxxxxxxxxxxxxxxxxxx',
        'FROM_DATE_E49':'11/8/13',
        'GEOMETRY_QUALIFIER_E55':'GEOMETRY_QUALIFIER:1',
        'HERITAGE_RESOURCE_TYPE_E55':['First example resource type', 'Second example resource type', 'Third example resource type'],
        'HERITAGE_RESOURCE_USE_TYPE_E55':'USE_TYPE:1',
        'INTEGRITY_TYPE_E55':'INTEGRITY:1',
        'KEYWORD_E55':'SUBJECT:1',
        'MATERIAL_E57':'MATERIAL:1',
        'MEASUREMENT_TYPE_E55':'MEASUREMENT_TYPE:1',
        'MODIFICATION_EVENT_E11':[{'MODIFICATION_DESCRIPTION_E62':'Example modification description.','MODIFICATION_TYPE_E55':'MODIFICATION_TYPE:1'},
            {'MODIFICATION_DESCRIPTION_E62':'Example modification description.','MODIFICATION_TYPE_E55':'MODIFICATION_TYPE:2'},
            {'MODIFICATION_DESCRIPTION_E62':'Example modification description.','MODIFICATION_TYPE_E55':'MODIFICATION_TYPE:3'}],
        'NAME_E41':[{'NAME_E41':'Primary name example.','NAME_TYPE_E55':'NAME_TYPE:1'}, {'NAME_E41':'Alternate name example 1', 'NAME_TYPE_E55':'Alternate Name'}, {'NAME_E41':'Alternate name example 2', 'NAME_TYPE_E55':'Alternate Name'}],
        'PHASE_TYPE_ASSIGNMENT_E17':[
            {'ANCILLARY_FEATURE_TYPE_E55':'RELATED_FEATURE:1'}, 
            {'ANCILLARY_FEATURE_TYPE_E55':'RELATED_FEATURE:2'}],
        'PLACE_ADDRESS_E45':'601 Montgomery Street. San Francisco, CA. 94111',
        'PLACE_APPELLATION_CADASTRAL_REFERENCE_E44':'Example cadastral reference.',
        'REASONS_E62':'Example reasons.',
        'RECOMMENDATION_TYPE_E55':'RECOMMENDATION_TYPE:1',
        'RESOURCE_TYPE_CLASSIFICATION_E55':'RESOURCE_CLASSIFICATION:1',
        'SETTING_TYPE_E55':'SETTING_TYPE:1',
        'START_DATE_OF_EXISTENCE_E49':'11/8/13',
        'STATUS_E55':'STATUS_CODE:65',
        'STYLE_E55':'STYLE:1',
        'THREAT_TYPE_E55':'THREAT_TYPE:1',
        'TO_DATE_E49':'11/8/14',
        'UNIT_OF_MEASUREMENT_E55':'UNIT_OF_MEASUREMENT:1',
        'VALUE_OF_MEASUREMENT_E60':'43',
        'SPATIAL_COORDINATES_GEOMETRY_E47':'POLYGON ((-118.37156 34.13212,-118.37162 34.13168,-118.372 34.13149,-118.37211 34.13169,-118.37226 34.13174,-118.37237 34.13173,-118.37303 34.13149,-118.37309 34.13149,-118.37316 34.1315,-118.37405 34.13178,-118.37449 34.13174,-118.37478 34.13165,-118.37486 34.13155,-118.37478 34.13108,-118.37483 34.13102,-118.37492 34.131,-118.37498 34.13104,-118.37499 34.13152,-118.37481 34.13181,-118.37464 34.13194,-118.37453 34.13183,-118.37394 34.13198,-118.37341 34.13184,-118.37335 34.13202,-118.37298 34.13181,-118.37263 34.13206,-118.37255 34.1319,-118.3722 34.13196,-118.37204 34.1321,-118.37156 34.13212))'
        }

    return render_to_response('resource-report.htm', {
            'report_template': 'views/reports/' + report_info['id'] + '.htm',
            'report_info': report_info,
            'main_script': 'resource-report',
            'active_page': 'ResourceReport'
        },
        context_instance=RequestContext(request))        

def map_layers(request, entitytypeid, get_centroids=False):
    data = []
    bbox = request.GET.get('bbox', '')
    limit = request.GET.get('limit', settings.MAP_LAYER_FEATURE_LIMIT)
    
    se = SearchEngineFactory().create()
    query = Query(se, limit=limit)

    if entitytypeid == 'all':
        data = query.search(index='maplayers') 
    else:
        data = query.search(index='maplayers', doc_type=entitytypeid) 

    geojson_collection = {
      "type": "FeatureCollection",
      "features": []
    }

    for item in data['hits']['hits']:
        if get_centroids:
            item['_source']['properties']['geometry_collection'] = item['_source']['geometry']
            item['_source']['geometry'] = item['_source']['properties']['centroid']
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
