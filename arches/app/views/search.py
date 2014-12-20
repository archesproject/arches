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
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Max, Min, Count
from django.utils.importlib import import_module
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range
geocoder = import_module(settings.GEOCODING_PROVIDER)

def home_page(request):
    se = SearchEngineFactory().create()

    lang = request.GET.get('lang', 'en-us')
    min_max_dates = models.Dates.objects.aggregate(Min('val'), Max('val'))
    resource_count = se.search(index='resource', search_type='_count')['count']

    date_types = Concept().get_e55_domain('BEGINNING_OF_EXISTENCE_TYPE.E55')+ Concept().get_e55_domain('END_OF_EXISTENCE_TYPE.E55')
    data = {'domains' :{'date_types': date_types}}
    data['domains']['date_operators'] = [{
        "conceptid": "0",
        "entitytypeid": "DATE_COMPARISON_OPERATOR.E55",
        "id": "0",
        "language,id": "en-us",
        "value": "Before",
        "valuetype": "prefLabel"
    },{
        "conceptid": "1",
        "entitytypeid": "DATE_COMPARISON_OPERATOR.E55",
        "id": "1",
        "language,id": "en-us",
        "value": "On",
        "valuetype": "prefLabel"
    },{
        "conceptid": "2",
        "entitytypeid": "DATE_COMPARISON_OPERATOR.E55",
        "id": "2",
        "language,id": "en-us",
        "value": "After",
        "valuetype": "prefLabel"
    }]

    return render_to_response('search.htm', {
            'main_script': 'search',
            'active_page': 'Search',
            'user_can_edit': False,
            'min_date': min_max_dates['val__min'].year,
            'max_date': min_max_dates['val__max'].year,
            #'date_types': date_types,
            'formdata': JSONSerializer().serialize(data),
            'resource_count': resource_count
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
    results = search_resources(request)
    total = results['hits']['total']
    page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))

    return _get_pagination(results, total, page, settings.SEARCH_ITEMS_PER_PAGE)

def search_resources(request):
    searchString = request.GET.get('q', '')
    spatial_filter = JSONDeserializer().deserialize(request.GET.get('spatialFilter', {'type': ''})) 
    f = request.GET.get('f', None)
    export = request.GET.get('export', None)
    page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))
    year_min_max = JSONDeserializer().deserialize(request.GET.get('year_min_max', []))

    groups = [group.name for group in request.user.groups.all()] 
    
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

    if spatial_filter['type'] != '':
        if spatial_filter['type'] == 'bbox':
            coordinates = [[spatial_filter['coordinates'][0],spatial_filter['coordinates'][3]], [spatial_filter['coordinates'][2],spatial_filter['coordinates'][1]]]
            geoshape = GeoShape(field='geometries.value', type='envelope', coordinates=coordinates )
            nested = Nested(path='geometries', query=geoshape)
            boolquery.must(nested)
        else:
            geoshape = GeoShape(field='geometries.value', type=spatial_filter['type'], coordinates=spatial_filter['coordinates'] )
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

    print query

    search_results = query.search(index='entity', type='') 

    return search_results

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
    searchString = request.GET.get('q', '')    
    return JSONResponse({ 'results': geocoder.findCandidates(searchString) })
