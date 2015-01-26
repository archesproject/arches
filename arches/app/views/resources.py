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
from arches.app.search.elasticsearch_dsl_builder import Query, Terms, Bool, Match

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
    
def related_resoures(request, resourceid):
    return JSONResponse(get_related_resources(resourceid))

def get_related_resources(resourceid):
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

    return ret

def report(request, resourceid):
    lang = request.GET.get('lang', settings.LANGUAGE_CODE)
    se = SearchEngineFactory().create()
    report_info = se.search(index='resource', id=resourceid)
    report_info['source'] = report_info['_source']
    report_info['type'] = report_info['_type']
    report_info['source']['graph'] = report_info['source']['graph'][0]
    del report_info['_source']
    del report_info['_type']

    related_resource_info = get_related_resources(resourceid)

    #return JSONResponse(report_info, indent=4)

    def get_evaluation_path(valueid):
        value = models.Values.objects.get(pk=valueid)
        concept_graph = Concept().get(id=value.conceptid_id, include_subconcepts=False, 
            include_parentconcepts=True, include_relatedconcepts=False, up_depth_limit=None, lang=lang)
        
        paths = []
        for path in concept_graph.get_paths(lang=lang)[0]:
            if path['label'] != 'Arches' and path['label'] != 'Evaluation Criteria Type':
                paths.append(path['label'])
        return '; '.join(paths)


    concept_label_ids = set()
    uuid_regex = re.compile('[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
    # gather together all uuid's referenced in the resource graph
    def crawl(items):
        for item in items:
            for key in item:
                if isinstance(item[key], list):
                    crawl(item[key])
                else:
                    if uuid_regex.match(item[key]):
                        if key == 'EVALUATION_CRITERIA_TYPE_E55__value':
                            item[key] = get_evaluation_path(item[key])
                        concept_label_ids.add(item[key])

    crawl([report_info['source']['graph']])

    # get all the concept labels from the uuid's
    concept_labels = se.search(index='concept_labels', id=list(concept_label_ids))
    
    #print concept_labels
    temp = {}

    # convert all labels to their localized prefLabel
    for concept_label in concept_labels['docs']:
        #temp[concept_label['_id']] = concept_label
        if concept_label['found']:
            # the resource graph already referenced the preferred label in the desired language
            if concept_label['_source']['type'] == 'prefLabel' and concept_label['_source']['language'] == lang:
                temp[concept_label['_id']] = concept_label['_source']
            else: 
                # the resource graph referenced a non-preferred label or a label not in our target language, so we need to get the right label
                query = Query(se)
                terms = Terms(field='conceptid', terms=[concept_label['_source']['conceptid']])
                match = Match(field='type', query='preflabel', type='phrase')
                query.add_filter(terms)
                query.add_query(match)
                preflabels = query.search(index='concept_labels')['hits']['hits'] 
                for preflabel in preflabels:
                    # get the label in the preferred language, otherwise get the label in the default language
                    if preflabel['_source']['language'] == lang:
                        temp[concept_label['_id']] = preflabel['_source']
                        break
                    if preflabel['_source']['language'] == settings.LANGUAGE_CODE:
                        temp[concept_label['_id']] = preflabel['_source']

    # replace the uuid's in the resource graph with their preferred and localized label                    
    def crawl_again(items):
        for item in items:
            for key in item:
                if isinstance(item[key], list):
                    crawl_again(item[key])
                else:
                    if uuid_regex.match(item[key]):
                        try:
                            item[key] = temp[item[key]]['value']
                        except:
                            pass

    crawl_again([report_info['source']['graph']])

    #return JSONResponse(report_info, indent=4)

    return render_to_response('resource-report.htm', {
            'resourceid': resourceid,
            'report_template': 'views/reports/' + report_info['type'] + '.htm',
            'report_info': report_info,
            'main_script': 'resource-report',
            'active_page': 'ResourceReport'
        },
        context_instance=RequestContext(request))        

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
