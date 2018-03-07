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

from datetime import datetime
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.db.models import Max, Min
from arches.app.models import models
from arches.app.views.search import get_paginator
from arches.app.views.search import build_search_results_dsl as build_base_search_results_dsl
from arches.app.models.concept import Concept
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range
from django.utils.translation import ugettext as _
from arches.app.utils.data_management.resources.exporter import ResourceExporter

from arches.app.views.resources import get_related_resources

import csv
import logging

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
    
def home_page(request):
    lang = request.GET.get('lang', settings.LANGUAGE_CODE)
    min_max_dates = models.Dates.objects.aggregate(Min('val'), Max('val'))

    return render_to_response('search.htm', {
            'main_script': 'search',
            'active_page': 'Search',
            'min_date': min_max_dates['val__min'].year if min_max_dates['val__min'] != None else 0,
            'max_date': min_max_dates['val__max'].year if min_max_dates['val__min'] != None else 1,
            'timefilterdata': JSONSerializer().serialize(Concept.get_time_filter_data()),
            'group_options': settings.SEARCH_GROUP_ROOTS
        }, 
        context_instance=RequestContext(request))

def get_related_resource_ids(resourceids, lang, limit=1000, start=0):
    se = SearchEngineFactory().create()
    query = Query(se, limit=limit, start=start)
    query.add_filter(Terms(field='entityid1', terms=resourceids).dsl, operator='or')
    query.add_filter(Terms(field='entityid2', terms=resourceids).dsl, operator='or')
    resource_relations = query.search(  index='resource_relations', doc_type='all')
    
    entityids = set()
    for relation in resource_relations['hits']['hits']: 
        # add the other halves add the relations which are not in the original list of ids
        from_is_original_result = relation['_source']['entityid1'] in resourceids
        to_is_original_result = relation['_source']['entityid2'] in resourceids
        
        if from_is_original_result:
            entityids.add(relation['_source']['entityid2'])
            
        if to_is_original_result:
            entityids.add(relation['_source']['entityid1'])
    
    return entityids

def search_results(request):

    lang = request.GET.get('lang', request.LANGUAGE_CODE)
    query = build_search_results_dsl(request)
    
    # logging.warning("\n\nQUERY: ----\n%s\n\n", query)
    
    search_related_resources = JSONDeserializer().deserialize(request.GET.get('searchRelatedResources'))
    
    if search_related_resources:
        results_from_prev_query = request.session['result-resource-ids']
        related_resources_from_prev_query = list(get_related_resource_ids(results_from_prev_query, lang, start=0, limit=1000000))
        
        ids_filter = Terms(field='entityid', terms=related_resources_from_prev_query)
        query.add_filter(ids_filter)
        
    results = query.search(index='entity', doc_type='')
    
    total = results['hits']['total']
    page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))

    all_entity_ids = ['_all']
    if request.GET.get('include_ids', 'false') == 'false':
        all_entity_ids = ['_none']
    elif request.GET.get('no_filters', '') == '':
        full_results = query.search(index='entity', doc_type='', start=0, limit=1000000, fields=[])
        all_entity_ids = [hit['_id'] for hit in full_results['hits']['hits']]
    
    start = request.GET.get('start', 0)
    
    if not search_related_resources:
        # Store in session for next related resources search
        request.session['result-resource-ids'] = all_entity_ids
    
    return get_paginator(results, total, page, settings.SEARCH_ITEMS_PER_PAGE, all_entity_ids)

def build_search_results_dsl(request):
    temporal_filters = JSONDeserializer().deserialize(request.GET.get('temporalFilter', None))
    sorting = {
		"child_entities.label":  {
			"order" : "asc",
			"nested_path": "child_entities",
			"nested_filter": {
				"term": {"child_entities.entitytypeid" : "EAMENA_ID.E42"}
			}			
		}
	}
    query = build_base_search_results_dsl(request)  
    boolfilter = Bool()

    query.dsl.update({'sort': sorting})

    return query

def export_results(request):
    dsl = build_search_results_dsl(request)
    
    search_related_resources = JSONDeserializer().deserialize(request.GET.get('searchRelatedResources'))
    
    if search_related_resources:
        results_from_prev_query = request.session['result-resource-ids']
        related_resources_from_prev_query = list(get_related_resource_ids(results_from_prev_query, lang, start=0, limit=1000000))

        ids_filter = Terms(field='entityid', terms=related_resources_from_prev_query)
        dsl.add_filter(ids_filter)
    
    
    search_results = dsl.search(index='entity', doc_type='')

    response = None
    format = request.GET.get('export', 'csv')
    exporter = ResourceExporter(format)
    results = exporter.export(search_results['hits']['hits'])
    
    related_resources = [{'id1':rr.entityid1, 'id2':rr.entityid2, 'type':rr.relationshiptype} for rr in models.RelatedResource.objects.all()] 
    csv_name = 'resource_relationships.csv'
    dest = StringIO()
    csvwriter = csv.DictWriter(dest, delimiter=',', fieldnames=['id1','id2','type'])
    csvwriter.writeheader()
    for csv_record in related_resources:
        csvwriter.writerow({k:v.encode('utf8') for k,v in csv_record.items()})
    results.append({'name':csv_name, 'outputfile': dest})
    zipped_results = exporter.zip_response(results, '{0}_{1}_export.zip'.format(settings.PACKAGE_NAME, format))
    return zipped_results