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

from datetime import datetime, date
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.paginator import Paginator
from django.utils.importlib import import_module
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Max, Min
from arches.app.models import models
from arches.app.models.entity import Entity
from arches.app.models.models import EntityTypes, Mappings
from arches.app.models.concept import Concept, ConceptValue
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.views.concept import get_preflabel_from_conceptid
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range
from arches.app.utils.data_management.resources.exporter import ResourceExporter


import csv
import logging
import json

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

geocoder = import_module(settings.GEOCODING_PROVIDER)

def home_page(request):
    lang = request.GET.get('lang', settings.LANGUAGE_CODE)
    min_max_dates = models.Dates.objects.aggregate(Min('val'), Max('val'))
    return render_to_response('search.htm', {
            'main_script': 'search',
            'active_page': 'Search',
            'min_date': min_max_dates['val__min'].year if min_max_dates['val__min'] != None else 0,
            'max_date': min_max_dates['val__max'].year if min_max_dates['val__min'] != None else 1,
            'timefilterdata': JSONSerializer().serialize(Concept.get_time_filter_data()),
        }, 
        context_instance=RequestContext(request))
        
def search_terms(request):
    lang = request.GET.get('lang', settings.LANGUAGE_CODE)
    query = build_search_terms_dsl(request)
    results = query.search(index='term', doc_type='value')

    group_root_node = request.GET.get('group_root_node', '')
    delete_results = []
    for result in results['hits']['hits']:
        prefLabel = get_preflabel_from_conceptid(result['_source']['context'], lang)
        result['_source']['options']['context_label'] = prefLabel['value']
        
        entity_type = None
        
        # if a group is selected we have to filter out the results that don't belong to the selected group
        if group_root_node != 'No group':
            if 'conceptid' in result['_source']['options']:
                # concept: find the entity_type to check if it is connected to the selected group
                valueid = result['_source']['options']["conceptid"]
                
                value_relations_to = models.ConceptRelations.objects.filter(conceptidto=valueid, relationtype='member')
                
                if len(value_relations_to):
                    value_parent_concept = models.Concepts.objects.filter(conceptid=value_relations_to[0].conceptidfrom)
                    parent_relations_to = models.ConceptRelations.objects.filter(conceptidto=value_parent_concept[0].conceptid, relationtype='member')
                    
                    if value_parent_concept[0].nodetype.nodetype == 'Concept':
                        # need to get at the parent until we reach the root collection. concepts are arranged hierarchically
                        grandparent = models.Concepts.objects.filter(conceptid=parent_relations_to[0].conceptidfrom)
                        entity_type = grandparent[0].legacyoid
                        
                    elif value_parent_concept[0].nodetype.nodetype == 'Collection':
                        entity_type = value_parent_concept[0].legacyoid
                    else:
                        logging.warning("Not a concept or collection")

            else:
                # not a concept - possibly a name field or similar. Use the context
                entity_type = models.EntityTypes.objects.filter(conceptid=result['_source']['context'])

            delete_result = True
            # check the if the entity_type is under the selected root group node
            # so that it can be deleted later
            if entity_type:
                res = Entity().get_mapping_schema_to(entity_type)

                # search parents for group_root_node
                if 'HERITAGE_RESOURCE_GROUP.E27' in res:
                    for parent in res['HERITAGE_RESOURCE_GROUP.E27']['steps']:
                        if parent['entitytyperange'] == group_root_node:
                            delete_result = False
                            break
                
            if delete_result:
                delete_results.append(result)

    # deleted the flagged results
    for result in delete_results:
        results['hits']['hits'].remove(result);

    results['hits']['total'] = len(results['hits']['hits'])
        
    return JSONResponse(results)

def build_search_terms_dsl(request):
    se = SearchEngineFactory().create()
    searchString = request.GET.get('q', '')
    query = Query(se, start=0, limit=settings.SEARCH_DROPDOWN_LENGTH)
    boolquery = Bool()
    boolquery.should(Match(field='term', query=searchString.lower(), type='phrase_prefix', fuzziness='AUTO'))
    boolquery.should(Match(field='term.folded', query=searchString.lower(), type='phrase_prefix', fuzziness='AUTO'))
    boolquery.should(Match(field='term.folded', query=searchString.lower(), fuzziness='AUTO'))
    query.add_query(boolquery)
    return query

def search_results(request):
    dsl = build_search_results_dsl(request)
    results = dsl.search(index='entity', doc_type='')
    total = results['hits']['total']
    page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))
    all_entity_ids = ['_all']
    if request.GET.get('include_ids', 'false') == 'false':
        all_entity_ids = ['_none']
    elif request.GET.get('no_filters', '') == '':
        full_results = dsl.search(index='entity', doc_type='', start=0, limit=1000000, fields=[])
        all_entity_ids = [hit['_id'] for hit in full_results['hits']['hits']]
    return get_paginator(results, total, page, settings.SEARCH_ITEMS_PER_PAGE, all_entity_ids)

def build_search_results_dsl(request):
#    Results are sorted ascendingly by the value of SITE_ID.E42, which is displayed as primary name of Heritage Resources. 
#    Must go back to this method once new Automatic Resource ID has been fully developed (AZ 10/08/16) Update 06/09/16: EAMENA_ID.E42 now used as sorting criterion.

    sorting = {
		"child_entities.label":  {
			"order" : "asc",
			"nested_path": "child_entities",
			"nested_filter": {
				"term": {"child_entities.entitytypeid" : "EAMENA_ID.E42"}
			}
		}
	}
    
    term_filter = request.GET.get('termFilter', '')
    
    
    spatial_filter = JSONDeserializer().deserialize(request.GET.get('spatialFilter', None)) 
    export = request.GET.get('export', None)
    page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))
    temporal_filter = JSONDeserializer().deserialize(request.GET.get('temporalFilter', None))
    boolean_search = request.GET.get('booleanSearch', '')
    filter_and_or = JSONDeserializer().deserialize(request.GET.get('termFilterAndOr', ''))
    filter_grouping = JSONDeserializer().deserialize(request.GET.get('termFilterGroup', ''))
    
    filter_combine_flags = JSONDeserializer().deserialize(request.GET.get('termFilterCombineWithPrev', ''))
    #Ignore first entry as it is a dummy
    filter_combine_flags = filter_combine_flags[1:]
    # filter_combine_flags = [False, True, False, False, False]
    
    # filter_groups = JSONDeserializer().deserialize(request.GET.get('termFilterGroups', ''))
    # Not here yet, so put in some bogus data
    # filter_groups = [
    #     'NAME.E41',
    #     'NAME.E41',
    #     'DISTURBANCE_STATE.E3',
    #     'THREAT_STATE.E3'
    # ]
    
    se = SearchEngineFactory().create()

    if export != None:
        limit = settings.SEARCH_EXPORT_ITEMS_PER_PAGE  
    else:
        limit = settings.SEARCH_ITEMS_PER_PAGE
    
    query = Query(se, start=limit*int(page-1), limit=limit)
    boolquery = Bool()
    boolfilter = Bool()
    is_empty_temporal_filter = True

    # store each search term in an initially. These will be combined based on the global and/or and the optional groupings
    terms_queries = [];

    # logging.warning("-------QUERY-------")

    if term_filter != '' or not is_empty_temporal_filter:
        for index, select_box in enumerate(JSONDeserializer().deserialize(term_filter)):
            selectbox_boolfilter = Bool()
            
            groupid = filter_grouping[index]
            if not groupid == 'No group':
                # build a nested query against the nested_entities
                
                # trace the path from each term to the group root
                term_paths = []
                for term in select_box:

                    # trace path from group root to this term
                    if term['type'] == 'concept':
                        
                        # get the parent concept for this value i.e. the field
                        term_parent_concept = Concept.get_parent_concept(term['value'])
                        
                        # get the steps from the root to that concept
                        if term_parent_concept.nodetype.nodetype == "Collection":
                            term_schema = Entity.get_mapping_schema_to(term_parent_concept.legacyoid)
                        elif term_parent_concept.nodetype.nodetype == 'Concept':
                            # need to get at the parent until we reach the root collection. concepts are arranged hierarchically
                            parent_relations_to = models.ConceptRelations.objects.filter(conceptidto=term_parent_concept.conceptid, relationtype='member')
                            grandparent = models.Concepts.objects.filter(conceptid=parent_relations_to[0].conceptidfrom)
                            term_schema = Entity.get_mapping_schema_to(grandparent[0].legacyoid)
                        
                        #this path begins at the root, and ends up at the node in question
                        term_path = term_schema['HERITAGE_RESOURCE_GROUP.E27']['steps']
                        
                        term_paths.append({
                            'term': term,
                            'path': term_path
                        })
                        
                    elif term['type'] == 'term':

                        concept = models.Concepts.objects.get(conceptid=term['context'])
                        term_schema = Entity.get_mapping_schema_to(concept.legacyoid)
                        term_path = term_schema['HERITAGE_RESOURCE_GROUP.E27']['steps']
                        
                        term_paths.append({
                            'term': term,
                            'path': term_path
                        })

                    elif term['type'] == 'string':
                        term_schema = Entity.get_mapping_schema_to(groupid)
                        term_path = term_schema['HERITAGE_RESOURCE_GROUP.E27']['steps']
                        
                        term_paths.append({
                            'term': term,
                            'path': term_path
                        })
                        
                if 'year_min_max' in temporal_filter[index] and len(temporal_filter[index]['year_min_max']) == 2:
                    start_date = date(temporal_filter[index]['year_min_max'][0], 1, 1)
                    end_date = date(temporal_filter[index]['year_min_max'][1], 12, 31)
                    if start_date:
                        start_date = start_date.isoformat()
                    if end_date:
                        end_date = end_date.isoformat()

                    if 'inverted' not in temporal_filter[index]:
                        inverted_temporal_filter = False
                    else:
                        if temporal_filter[index]['inverted']:
                            inverted_temporal_filter = True
                        else:
                            inverted_temporal_filter = False
                    
                    term_paths.append({
                        'term': {
                            'date_operator': '3',
                            'start_date': start_date,
                            'end_date': end_date,
                            'type': 'date',
                            'inverted': inverted_temporal_filter
                        },
                        'path': term_path
                    })
                    
                    
                if 'filters' in temporal_filter[index]:
                    term_schema = Entity.get_mapping_schema_to(groupid)
                    term_path = term_schema['HERITAGE_RESOURCE_GROUP.E27']['steps']

                    for temporal_filter_item in temporal_filter[index]['filters']:
                        date_type = ''
                        searchdate = ''
                        date_operator = ''
                        for node in temporal_filter_item['nodes']:
                            if node['entitytypeid'] == 'DATE_COMPARISON_OPERATOR.E55':
                                date_operator = node['value']
                            elif node['entitytypeid'] == 'date':
                                searchdate = node['value']
                            else:
                                date_type = node['value']
                
                        date_value = datetime.strptime(searchdate, '%Y-%m-%d').isoformat()
                        if 'inverted' not in temporal_filter[index]:
                            inverted_temporal_filter = False
                        else:
                            if temporal_filter[index]['inverted']:
                                inverted_temporal_filter = True
                            else:
                                inverted_temporal_filter = False
                                
                        term_paths.append({
                            'term': {
                                'date_operator': date_operator,
                                'date_value': date_value,
                                'type': 'date',
                                'inverted': inverted_temporal_filter
                            },
                            'path': term_path
                        })

                # combine the traced path to build a nested query                
                group_query = nested_query_from_pathed_values(term_paths, 'nested_entity.child_entities')

                
                # add nested query to overall query
                selectbox_boolfilter.must(group_query)
                
                # logging.warning("BOX QUERY - %s", JSONSerializer().serialize(selectbox_boolfilter, indent=2))

            else:    
                for term in select_box:
                    
                    if term['type'] == 'term':
                        entitytype = models.EntityTypes.objects.get(conceptid_id=term['context'])
                        boolfilter_nested = Bool()
                        boolfilter_nested.must(Terms(field='child_entities.entitytypeid', terms=[entitytype.pk]))
                        boolfilter_nested.must(Match(field='child_entities.value', query=term['value'], type='phrase'))
                        nested = Nested(path='child_entities', query=boolfilter_nested)
                        if filter_and_or[index] == 'or':
                            if not term['inverted']:
                                selectbox_boolfilter.should(nested)
                        else:
                            if term['inverted']:
                                selectbox_boolfilter.must_not(nested)
                            else:    
                                selectbox_boolfilter.must(nested)
                                
                    elif term['type'] == 'concept':
                        concept_ids = _get_child_concepts(term['value'])
                        terms = Terms(field='domains.conceptid', terms=concept_ids)
                        nested = Nested(path='domains', query=terms)
                        if filter_and_or[index] == 'or':
                            if not term['inverted']:
                                    selectbox_boolfilter.should(nested)
                        else:
                            if term['inverted']:
                                selectbox_boolfilter.must_not(nested)
                            else:
                                selectbox_boolfilter.must(nested)
                                
                    elif term['type'] == 'string':
                        boolquery2 = Bool() #This bool contains the subset of nested string queries on both domains and child_entities paths
                        boolfilter_folded = Bool() #This bool searches by string in child_entities, where free text strings get indexed
                        boolfilter_folded2 = Bool() #This bool searches by string in the domains path,where controlled vocabulary concepts get indexed
                        boolfilter_folded.should(Match(field='child_entities.value', query=term['value'], type='phrase_prefix', fuzziness='AUTO', operator='and'))
                        boolfilter_folded.should(Match(field='child_entities.value.folded', query=term['value'], type='phrase_prefix', fuzziness='AUTO', operator='and'))
                        boolfilter_folded.should(Match(field='child_entities.value.folded', query=term['value'], fuzziness='AUTO', operator='and'))
                        nested = Nested(path='child_entities', query=boolfilter_folded)
                        boolfilter_folded2.should(Match(field='domains.label', query=term['value'], type='phrase_prefix', fuzziness='AUTO', operator='and'))
                        boolfilter_folded2.should(Match(field='domains.label.folded', query=term['value'], type='phrase_prefix', fuzziness='AUTO', operator='and'))
                        boolfilter_folded2.should(Match(field='domains.label.folded', query=term['value'], fuzziness='AUTO', operator='and'))
                        nested2 = Nested(path='domains', query=boolfilter_folded2)
                        boolquery2.should(nested)
                        boolquery2.should(nested2)
                        if filter_and_or[index] == 'or':
                            if not term['inverted']:
                                # use boolfilter here instead of boolquery because boolquery
                                # can't be combined with other boolfilters using boolean OR
                                selectbox_boolfilter.should(boolquery2)
                        else:
                            if term['inverted']:
                                selectbox_boolfilter.must_not(boolquery2)
                            else:    
                                selectbox_boolfilter.must(boolquery2)
                            
                if 'year_min_max' in temporal_filter[index] and len(temporal_filter[index]['year_min_max']) == 2:
                    start_date = date(temporal_filter[index]['year_min_max'][0], 1, 1)
                    end_date = date(temporal_filter[index]['year_min_max'][1], 12, 31)
                    if start_date:
                        start_date = start_date.isoformat()
                    if end_date:
                        end_date = end_date.isoformat()
                    range = Range(field='dates.value', gte=start_date, lte=end_date)
                    nested = Nested(path='dates', query=range)
            
                    if 'inverted' not in temporal_filter[index]:
                        temporal_filter[index]['inverted'] = False

                    if temporal_filter[index]['inverted']:
                        selectbox_boolfilter.must_not(nested)
                    else:
                        selectbox_boolfilter.must(nested)
                        
                if 'filters' in temporal_filter[index]:
                    for temporal_filter_item in temporal_filter[index]['filters']:
                        date_type = ''
                        searchdate = ''
                        date_operator = ''
                        for node in temporal_filter_item['nodes']:
                            if node['entitytypeid'] == 'DATE_COMPARISON_OPERATOR.E55':
                                date_operator = node['value']
                            elif node['entitytypeid'] == 'date':
                                searchdate = node['value']
                            else:
                                date_type = node['value']


                        date_value = datetime.strptime(searchdate, '%Y-%m-%d').isoformat()

                        if date_operator == '1': # equals query
                            range = Range(field='dates.value', gte=date_value, lte=date_value)
                        elif date_operator == '0': # greater than query 
                            range = Range(field='dates.value', lt=date_value)
                        elif date_operator == '2': # less than query
                            range = Range(field='dates.value', gt=date_value)
                        
                        nested = Nested(path='dates', query=range)
                        if 'inverted' not in temporal_filter[index]:
                            temporal_filter[index]['inverted'] = False

                        if temporal_filter[index]['inverted']:
                            selectbox_boolfilter.must_not(nested)
                        else:
                            selectbox_boolfilter.must(nested)


            terms_queries.append(selectbox_boolfilter)
            # if not selectbox_boolfilter.empty:
            #     if boolean_search == 'or':
            #         boolfilter.should(selectbox_boolfilter)
            #     else:
            #         boolfilter.must(selectbox_boolfilter)
        
        # We now have individual query terms for each of the search components. Combine into one group now
        # Start by building a an array of groups which will be combined according to the global And/Or
        # Queries within one of these groups will be combined by the complement of the global And/Or
        # We may end up with [ [A,B], [C], [D,E] ], which would translate to either:
        #    (A || B) && C && (D || E)
        #       or
        #    (A && B) || C || (D && E)
        # for global AND or OR respectively
        
        # logging.warning("TERMS QUERIES %s", terms_queries)
        
        bool_components = [];
        
        for i, term_query in enumerate(terms_queries):
            if i is 0:
                bool_components.append([term_query])
            else:
                should_group_with_previous = filter_combine_flags[i-1]
                if should_group_with_previous:
                    bool_components[-1].append(term_query)
                else:
                    bool_components.append([term_query])
            
        # logging.warning("BOOL COMPONENTS %s", bool_components)
        # Now build the ES queries
        for bool_component in bool_components:
            if len(bool_component) is 1:
                # just combine this on its own
                q = bool_component[0]
            else:
                q = Bool()
                for sub_component in bool_component:
                    if boolean_search == 'or':
                        #apply the OPPOSITE of the global boolean operator
                        q.must(sub_component)
                    else:
                        q.should(sub_component)
                        
            # combine to the overall query according to the global boolean operator
            if boolean_search == 'or':
                boolfilter.should(q)
            else:
                boolfilter.must(q)

    if 'geometry' in spatial_filter and 'type' in spatial_filter['geometry'] and spatial_filter['geometry']['type'] != '':
        geojson = spatial_filter['geometry']
        if geojson['type'] == 'bbox':
            coordinates = [[geojson['coordinates'][0],geojson['coordinates'][3]], [geojson['coordinates'][2],geojson['coordinates'][1]]]
            geoshape = GeoShape(field='geometries.value', type='envelope', coordinates=coordinates )
            nested = Nested(path='geometries', query=geoshape)
        else:
            buffer = spatial_filter['buffer']
            geojson = JSONDeserializer().deserialize(_buffer(geojson,buffer['width'],buffer['unit']).json)
            geoshape = GeoShape(field='geometries.value', type=geojson['type'], coordinates=geojson['coordinates'] )
            nested = Nested(path='geometries', query=geoshape)

        if 'inverted' not in spatial_filter:
            spatial_filter['inverted'] = False

        if spatial_filter['inverted']:
            boolfilter.must_not(nested)
        else:
            boolfilter.must(nested)

    if not boolquery.empty:
        query.add_query(boolquery)

    if not boolfilter.empty:
        query.add_filter(boolfilter)
    
#  Sorting criterion added to query (AZ 10/08/16)
    query.dsl.update({'sort': sorting})
    # logging.warning("-=-==-=-===-=--=-==-=-===-=- query: -=-==-=-===-=--=-==-=-===-=-> %s", query)

    return query

def nested_query_from_pathed_values(pathed_values, stem):
    """
    Given an array of pathed values to query terms from the root, return a nested query
    pathed_values: e.g. 
    [
        {
            val: '29430-4955-...'
            path: [a, b, c]
        }
    ]
    stem: the path into the index for the nested terms. This will be of the form 'nested_entity.child_entities.child_entities'
    """
    
    # f( [[A,B,C], [A,B,D] )
    # = Nested( AND( f( [[B,C],[B,D]] ))
    # = Nested( AND( Nested( AND( f([[C],[D]]) ))  ))
    # = Nested( AND( Nested( AND( valueC, valueD))))
    
    # f( [[A,B,C], [A,B,D], [A,B,D] )
    # = Nested( AND( f([[B,C],[B,D],[B,D]] ))
    # = Nested( AND( Nested( AND( f([[C],[D],[D]]) ))  ))
    # = Nested( AND( Nested( AND( valueB, valueD))))
    
    # group paths by their head of each paths list is the same, make a single nested query and recurse on the tails
    
    branch_groups = {}      # those groups with a continuing tail, where we will recursively build a nested query
    leaf_groups = []        # those groups without a continuing tail, where we will use an ordinary term query
    
    
    # build the groups
    for v in pathed_values:
        path = v['path']
        if len(path) == 1:
            # this goes in its own group
            leaf_groups.append(v)
        else:
            # see if there is already a group using this head
            head = v['path'][0]['entitytyperange']
            if head not in branch_groups:
                branch_groups[head] = []
            branch_groups[head].append(v)

    # We should now have a set of groups
    # create the bool query
    bool_term = Bool()
        
    # add terms for any leaf groups
    for leaf_group in leaf_groups:
        
        if leaf_group['term']['type'] == 'concept':
            if leaf_group['term']['inverted']:
                terms = Terms(field=stem+'.conceptid', terms=leaf_group['term']['value'])
                n_terms = Nested(path=stem, query=terms)
                bool_term.must_not(n_terms)
            else:
                terms = Terms(field=stem+'.conceptid', terms=leaf_group['term']['value'])
                n_terms = Nested(path=stem, query=terms)
                bool_term.must(n_terms)
                
        elif leaf_group['term']['type'] == 'term':
            
                # boolfilter_nested.must(Terms(field='child_entities.entitytypeid', terms=[entitytype.pk]))
                # boolfilter_nested.must(Match(field='child_entities.value', query=term['value'], type='phrase'))
            
            entitytype = models.EntityTypes.objects.get(conceptid_id=leaf_group['term']['context'])
            sub_bool = Bool()
            
            if leaf_group['term']['inverted']:
                sub_bool.must_not(Terms(field=stem+'.entitytypeid', terms=[entitytype.pk]))
                sub_bool.must_not(Match(field=stem+'.value', query=leaf_group['term']['value'], type='phrase'))
            else:
                sub_bool.must(Terms(field=stem+'.entitytypeid', terms=[entitytype.pk]))
                sub_bool.must(Match(field=stem+'.value', query=leaf_group['term']['value'], type='phrase'))
                
            nsub_bool = Nested(path=stem, query=sub_bool)
            bool_term.must(nsub_bool)
    
        elif leaf_group['term']['type'] == 'string':
            boolfilter_folded = Bool()
            boolfilter_folded.should(Match(field=stem+'.flat_child_entities.label', query=leaf_group['term']['value'], type='phrase_prefix', fuzziness='AUTO'))
            boolfilter_folded.should(Match(field=stem+'.flat_child_entities.label.folded', query=leaf_group['term']['value'], type='phrase_prefix', fuzziness='AUTO'))
            boolfilter_folded.should(Match(field=stem+'.flat_child_entities.label.folded', query=leaf_group['term']['value'], fuzziness='AUTO'))
            nested = Nested(path=stem+'.flat_child_entities', query=boolfilter_folded)
            if leaf_group['term']['inverted']:
                bool_term.must_not(nested)
            else:    
                bool_term.must(nested)
    
        elif leaf_group['term']['type'] == 'date':
            if leaf_group['term']['date_operator'] == '1': # equals query
                daterange = Range(field=stem+'.flat_child_entities.date', gte=leaf_group['term']['date_value'], lte=leaf_group['term']['date_value'])
            elif leaf_group['term']['date_operator'] == '0': # greater than query 
                daterange = Range(field=stem+'.flat_child_entities.date', lt=leaf_group['term']['date_value'])
            elif leaf_group['term']['date_operator'] == '2': # less than query
                daterange = Range(field=stem+'.flat_child_entities.date', gt=leaf_group['term']['date_value'])
            elif leaf_group['term']['date_operator'] == '3': # greater than and less than query
                daterange = Range(field=stem+'.flat_child_entities.date', gte=leaf_group['term']['start_date'], lte=leaf_group['term']['end_date'])
            
            nested_date = Nested(path=stem+'.flat_child_entities', query=daterange)
            if leaf_group['term']['inverted']:
                bool_term.must_not(nested_date)
            else:
                bool_term.must(nested_date)
    
    # add terms for any branch groups
    for key in branch_groups:
        # add a nested term for each group
        branch_group = branch_groups[key]
        
        #remove head from each path and recurse
        for value in branch_group:
            value['path'] = value['path'][1:]
        sub_query = nested_query_from_pathed_values(branch_group, stem+'.child_entities')
        
        nsub_query = Nested(path=stem, query=sub_query)
        
        bool_term.must(nsub_query)
    
    return bool_term;
    

def buffer(request):
    spatial_filter = JSONDeserializer().deserialize(request.GET.get('filter', {'geometry':{'type':'','coordinates':[]},'buffer':{'width':'0','unit':'ft'}})) 

    if spatial_filter['geometry']['coordinates'] != '' and spatial_filter['geometry']['type'] != '':
        return JSONResponse(_buffer(spatial_filter['geometry'],spatial_filter['buffer']['width'],spatial_filter['buffer']['unit']), geom_format='json')

    return JSONResponse()

def _buffer(geojson, width=0, unit='ft'):
    geojson = JSONSerializer().serialize(geojson)
    
    try:
        width = float(width)
    except:
        width = 0

    if width > 0:
        geom = GEOSGeometry(geojson, srid=4326)
        geom.transform(3857)
        
# Below 2 lines are deprecated in EAMENA's Arches as the unit of choice is EPSG3857's default metres
        if unit == 'ft':
            width = width/3.28084

        buffered_geom = geom.buffer(width)
        buffered_geom.transform(4326)
        return buffered_geom
    else:
        return GEOSGeometry(geojson)

def _get_child_concepts(conceptid):
    ret = set([conceptid])
    for row in Concept().get_child_concepts(conceptid, ['narrower'], ['prefLabel'], 'prefLabel'):
        ret.add(row[0])
        ret.add(row[1])
    return list(ret)

def get_paginator(results, total_count, page, count_per_page, all_ids):
    paginator = Paginator(range(total_count), count_per_page)
    pages = [page]
    if paginator.num_pages > 1:
        before = paginator.page_range[0:page-1]
        after = paginator.page_range[page:paginator.num_pages]
        default_ct = 3
        ct_before = default_ct if len(after) > default_ct else default_ct*2-len(after)
        ct_after = default_ct if len(before) > default_ct else default_ct*2-len(before)
        if len(before) > ct_before:
            before = [1,None]+before[-1*(ct_before-1):]
        if len(after) > ct_after:
            after = after[0:ct_after-1]+[None,paginator.num_pages]
        pages = before+pages+after
    return render_to_response('pagination.htm', {'pages': pages, 'page_obj': paginator.page(page), 'results': JSONSerializer().serialize(results), 'all_ids': JSONSerializer().serialize(all_ids)})

def geocode(request):
    search_string = request.GET.get('q', '')    
    return JSONResponse({ 'results': geocoder.find_candidates(search_string) })

def export_results(request):
    dsl = build_search_results_dsl(request)
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