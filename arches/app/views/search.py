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
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range
geocoder = import_module(settings.GEOCODING_PROVIDER)

def home_page(request):
    se = SearchEngineFactory().create()

    lang = request.GET.get('lang', 'en-us')
    resource_count = se.search(index='resource', search_type='_count')['count']

    return render_to_response('search.htm', {
            'main_script': 'search',
            'active_page': 'Search',
            'resource_count': resource_count,
            'user_can_edit': False
        }, 
        context_instance=RequestContext(request))


def search_terms(request):
    se = SearchEngineFactory().create()
    searchString = request.GET.get('q', '')
    
    query = Query(se, start=0, limit=settings.SEARCH_ITEMS_PER_PAGE)
    phrase = Match(field='term', query=searchString.lower(), type='phrase_prefix', fuzziness='AUTO')
    query.add_query(phrase)

    return JSONResponse(query.search(index='term', type='value'))

def search_results(request, as_text=False):
    dsl = build_query_dsl(request)
    results = dsl.search(index='entity', type='') 
    total = results['hits']['total']
    page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))

    return _get_pagination(results, total, page, settings.SEARCH_ITEMS_PER_PAGE)

def build_query_dsl(request):
    searchString = request.GET.get('q', '')
    spatial_filter = JSONDeserializer().deserialize(request.GET.get('spatialFilter', {'geometry':{'type':'','coordinates':[]},'buffer':{'width':'0','unit':'ft'}})) 
    export = request.GET.get('export', None)
    page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))
    year_min_max = JSONDeserializer().deserialize(request.GET.get('year_min_max', []))

    se = SearchEngineFactory().create()
    if export != None:
        query = Query(se, start=settings.SEARCH_EXPORT_ITEMS_PER_PAGE*int(page-1), limit=settings.SEARCH_EXPORT_ITEMS_PER_PAGE)
    else:
        query = Query(se, start=settings.SEARCH_ITEMS_PER_PAGE*int(page-1), limit=settings.SEARCH_ITEMS_PER_PAGE)
    boolquery = Bool()
    boolfilter = Bool()
    
    if searchString != '':
        qparam = JSONDeserializer().deserialize(searchString)
        for q in qparam:
            if q['type'] == 'term':
                phrase = Match(field='child_entities.value', query=q['value'], type='phrase')
                nested = Nested(path='child_entities', query=phrase)
                boolquery.must(nested)
            elif q['type'] == 'concept':
                concept_ids = _get_child_concepts(q['value'])
                terms = Terms(field='domains.conceptid', terms=concept_ids)
                nested = Nested(path='domains', query=terms)
                boolfilter.must(nested)
            elif q['type'] == 'string':
                phrase = Match(field='child_entities.value', query=q['value'], type='phrase_prefix')
                nested = Nested(path='child_entities', query=phrase)
                boolquery.must(nested)
            elif q['type'] == 'string_inverted':
                phrase = Match(field='child_entities.value', query=q['value'], type='phrase')
                nested = Nested(path='child_entities', query=phrase)
                boolquery.must_not(nested)
            elif q['type'] == 'concept_inverted':
                concept_lables = _get_child_concepts(q['value'])
                terms = Terms(field='domains.conceptid', terms=concept_lables)
                nested = Nested(path='domains', query=terms)
                boolfilter.must_not(nested)

    if spatial_filter['geometry']['type'] != '':
        geojson = spatial_filter['geometry']
        if geojson['type'] == 'bbox':
            coordinates = [[geojson['coordinates'][0],geojson['coordinates'][3]], [geojson['coordinates'][2],geojson['coordinates'][1]]]
            geoshape = GeoShape(field='geometries.value', type='envelope', coordinates=coordinates )
            nested = Nested(path='geometries', query=geoshape)
            boolquery.must(nested)
        else:
            buffer = spatial_filter['buffer']
            geojson = JSONDeserializer().deserialize(_buffer(geojson,buffer['width'],buffer['unit']).json)
            geoshape = GeoShape(field='geometries.value', type=geojson['type'], coordinates=geojson['coordinates'] )
            nested = Nested(path='geometries', query=geoshape)
            boolquery.must(nested)

    if len(year_min_max) == 2:
        start_date = date(year_min_max[0], 1, 1)
        end_date = date(year_min_max[1], 12, 31)
        if start_date:
            start_date = start_date.strftime('%Y-%m-%d')
        if end_date:
            end_date = end_date.strftime('%Y-%m-%d')
        range = Range(field='dates.value', gte=start_date, lte=end_date)
        nested = Nested(path='dates', query=range)
        boolquery.must(nested)
        
    if not boolquery.empty:
        query.add_query(boolquery)

    if not boolfilter.empty:
        query.add_query(boolfilter)

    return query

def buffer(request):
    spatial_filter = JSONDeserializer().deserialize(request.GET.get('spatialFilter', {'geometry':{'type':'','coordinates':[]},'buffer':{'width':'0','unit':'ft'}})) 

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

def _get_pagination(results, total_count, page, count_per_page):
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
    return render_to_response('pagination.htm', {'pages': pages, 'page_obj': paginator.page(page), 'results': JSONSerializer().serialize(results)})

def geocode(request):
    search_string = request.GET.get('q', '')    
    return JSONResponse({ 'results': geocoder.find_candidates(search_string) })
