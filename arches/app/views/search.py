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

from datetime import date
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.paginator import Paginator
from django.utils.importlib import import_module
from django.contrib.gis.geos import GEOSGeometry
from arches.app.models.concept import Concept
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.views.concept import get_preflabel_from_conceptid
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range
from arches.app.utils.data_management.resources.exporter import ResourceExporter
geocoder = import_module(settings.GEOCODING_PROVIDER)

def home_page(request):
    lang = request.GET.get('lang', 'en-us')

    return render_to_response('search.htm', {
            'main_script': 'search',
            'active_page': 'Search'
        }, 
        context_instance=RequestContext(request))

def search_terms(request):
    lang = request.GET.get('lang', 'en-us')
    
    query = build_search_terms_dsl(request)
    results = query.search(index='term', doc_type='value')

    for result in results['hits']['hits']:
        prefLabel = get_preflabel_from_conceptid(result['_source']['context'], lang)
        result['_source']['context'] = prefLabel['value']

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
    term_filter = request.GET.get('termFilter', '')
    spatial_filter = JSONDeserializer().deserialize(request.GET.get('spatialFilter', None)) 
    export = request.GET.get('export', None)
    page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))
    temporal_filter = JSONDeserializer().deserialize(request.GET.get('temporalFilter', None))

    se = SearchEngineFactory().create()

    if export != None:
        limit = settings.SEARCH_EXPORT_ITEMS_PER_PAGE  
    else:
        limit = settings.SEARCH_ITEMS_PER_PAGE
    
    query = Query(se, start=limit*int(page-1), limit=limit)
    boolquery = Bool()
    boolfilter = Bool()
    
    if term_filter != '':
        for term in JSONDeserializer().deserialize(term_filter):
            if term['type'] == 'term':
                boolfilter_folded = Bool()
                boolfilter_folded.should(Match(field='child_entities.value', query=term['value'], type='phrase'))
                boolfilter_folded.should(Match(field='child_entities.value.folded', query=term['value'], type='phrase'))
                nested = Nested(path='child_entities', query=boolfilter_folded)
                if term['inverted']:
                    boolfilter.must_not(nested)
                else:    
                    boolfilter.must(nested)
            elif term['type'] == 'concept':
                concept_ids = _get_child_concepts(term['value'])
                terms = Terms(field='domains.conceptid', terms=concept_ids)
                nested = Nested(path='domains', query=terms)
                if term['inverted']:
                    boolfilter.must_not(nested)
                else:
                    boolfilter.must(nested)
            elif term['type'] == 'string':
                boolfilter_folded = Bool()
                boolfilter_folded.should(Match(field='child_entities.value', query=term['value'], type='phrase_prefix'))
                boolfilter_folded.should(Match(field='child_entities.value.folded', query=term['value'], type='phrase_prefix'))
                #phrase = Match(field='child_entities.value', query=term['value'], type='phrase_prefix')
                nested = Nested(path='child_entities', query=boolfilter_folded)
                if term['inverted']:
                    boolquery.must_not(nested)
                else:    
                    boolquery.must(nested)

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

    if 'year_min_max' in temporal_filter and len(temporal_filter['year_min_max']) == 2:
        start_date = date(temporal_filter['year_min_max'][0], 1, 1)
        end_date = date(temporal_filter['year_min_max'][1], 12, 31)
        if start_date:
            start_date = start_date.isoformat()
        if end_date:
            end_date = end_date.isoformat()
        range = Range(field='dates.value', gte=start_date, lte=end_date)
        nested = Nested(path='dates', query=range)
        
        if 'inverted' not in temporal_filter:
            temporal_filter['inverted'] = False

        if temporal_filter['inverted']:
            boolfilter.must_not(nested)
        else:
            boolfilter.must(nested)
        
    if not boolquery.empty:
        query.add_query(boolquery)

    if not boolfilter.empty:
        query.add_filter(boolfilter)

    return query

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

        if unit == 'ft':
            width = width/3.28084

        buffered_geom = geom.buffer(width)
        buffered_geom.transform(4326)
        return buffered_geom
    else:
        return GEOSGeometry(geojson)

def _get_child_concepts(conceptid):
    ret = set([conceptid])
    for row in Concept().get_child_concepts(conceptid, 'narrower', ['prefLabel'], 'prefLabel'):
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
    zipped_results = exporter.zip_response(results, '{0}_{1}_export.zip'.format(settings.PACKAGE_NAME, format))
    return zipped_results
