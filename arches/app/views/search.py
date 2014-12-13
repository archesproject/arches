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
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.contrib.gis.geos import GEOSGeometry
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range

def home(request):
    lang = request.GET.get('lang', 'en-us')

    return render_to_response('search.htm', {
            'main_script': 'search',
            'active_page': 'Search',
            'content': 'views/saved-searches.htm'
        }, context_instance=RequestContext(request))

def search_terms(request):
    se = SearchEngineFactory().create()
    searchString = request.GET.get('q', '')
    
    query = Query(se, start=0, limit=settings.SEARCH_ITEMS_PER_PAGE)
    phrase = Match(field='term', query=searchString.lower(), type='phrase_prefix', fuzziness='AUTO')
    query.add_query(phrase)

    return JSONResponse(query.search(index='term', type='value'))

def search_resources(request, as_text=False):
    searchString = request.GET.get('q', '')
    extent = request.GET.get('extent', None)    
    f = request.GET.get('f', None)
    export = request.GET.get('export', None)
    page = int(request.GET.get('page', 1))
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    groups = [group.name for group in request.user.groups.all()] 
    
    se = SearchEngineFactory().create()
    if export != None:
        query = Query(se, start=settings.SEARCH_EXPORT_ITEMS_PER_PAGE*int(page-1), limit=settings.SEARCH_EXPORT_ITEMS_PER_PAGE)
    else:
        query = Query(se, start=settings.SEARCH_ITEMS_PER_PAGE*int(page-1), limit=settings.SEARCH_ITEMS_PER_PAGE)
    boolquery = Bool()
    
    if searchString != '':
        q = JSONDeserializer().deserialize(searchString)
        strings = q['strings']
        strings_inverted = q['strings_inverted']
        concepts = q['concepts']
        concepts_inverted = q['concepts_inverted']      

        if len(strings) != 0 or len(strings_inverted) != 0 or len(concepts) != 0 or len(concepts_inverted) != 0:
            
            for string in strings:
                phrase = Match(field='relatedentities.value', query=string['value'], type='phrase')
                nested = Nested(path='relatedentities', query=phrase)
                boolquery.must(nested)

            for string in strings_inverted:
                phrase = Match(field='relatedentities.value', query=string['value'], type='phrase')
                nested = Nested(path='relatedentities', query=phrase)
                boolquery.must_not(nested)

            for concept in concepts:
                concept_lables = search_view._get_child_concepts(concept['value'])
                terms = Terms(field='relatedentities.value.raw', terms=concept_lables)
                nested = Nested(path='relatedentities', query=terms)
                boolfilter.must(nested)

            for concept in concepts_inverted:
                concept_lables = search_view._get_child_concepts(concept['value'])
                terms = Terms(field='relatedentities.value.raw', terms=concept_lables)
                nested = Nested(path='relatedentities', query=terms)
                boolfilter.must_not(nested)

    if extent:
        extent = extent.split(',')
        coordinates = [[extent[0],extent[3]], [extent[2],extent[1]]]
        geoshape = GeoShape(field='geometries.value', type='envelope', coordinates=coordinates)
        nested = Nested(path='geometries', query=geoshape)
        boolquery.must(nested)

    if start_date or end_date:
        if start_date:
            start_date = time.strptime(start_date, "%m/%d/%Y")
            start_date = time.strftime('%Y-%m-%d', start_date)
        if end_date:
            end_date = time.strptime(end_date, "%m/%d/%Y")
            end_date = time.strftime('%Y-%m-%d', end_date)
        range = Range(field='dates.value', gte=start_date, lte=end_date)
        nested = Nested(path='dates', query=range)
        boolquery.must(nested)
        
    if not boolquery.empty:
        query.add_query(boolquery)

    search_results = query.search(index='entity', type='') 

    if export in ['kml','shp','csv','geojson']:
        return search_results 

    if f == 'json' or f == 'pretty-json':
        indent = 4 if f == 'pretty-json' else None
        return JSONResponse(search_results, indent=indent)  

    total = search_results['hits']['total']

    # remove leading underscores from results dictionary becuase django templates don't like them
    for result in search_results['hits']['hits']:
        result['source'] = result.pop('_source')

    pagination = _get_pagination(total, page, settings.SEARCH_ITEMS_PER_PAGE)
    renderer = render_to_string if as_text==True else render_to_response

    return renderer('search.htm', {'content': 'views/search-results.htm', 'pagination': pagination, 'count': total, 'results': search_results['hits']['hits'], 'user_groups': groups}, context_instance=RequestContext(request))

def _get_child_concepts(conceptid):
	se = SearchEngineFactory().create()
	ret = se.search(conceptid, index='concept', type='all', search_field='conceptid', use_phrase=True)
	left = ret['hits']['hits'][0]['_source']['left']
	right = ret['hits']['hits'][0]['_source']['right']

	concepts = se.search({'from':left, 'to':right}, index='concept', type='all', search_field='left', use_range=True)

	ret = []
	for concept in concepts['hits']['hits']:
		for label in concept['_source']['labels']:
			ret.append(label['labelid'])

	return ret

def _get_pagination(total_count, page, count_per_page):
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
    return render_to_string('pagination.htm', {'pages': pages, 'page_obj': paginator.page(page)})