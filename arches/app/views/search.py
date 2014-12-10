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

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range

def home(request):
    lang = request.GET.get('lang', 'en-us')

    return render_to_response('search.htm', {
            'main_script': 'search',
            'active_page': 'Search'
        }, context_instance=RequestContext(request))

def search(request):
    se = SearchEngineFactory().create()
    searchString = request.GET['q']
    search_results = _normalize_spatial_results_to_wkt(se.search(searchString.lower(), index='entity', type='', search_field='strings', use_phrase=True))
    return HttpResponse(JSONSerializer().serialize(search_results, ensure_ascii=False))

def search_terms(request):
    se = SearchEngineFactory().create()
    searchString = request.GET.get('q', '')
    
    query = Query(se, start=0, limit=settings.SEARCH_ITEMS_PER_PAGE)
    phrase = Match(field='term', query=searchString.lower(), type='phrase_prefix', fuzziness='AUTO')
    #boolfilter = Bool(should=phrase)
    query.add_query(phrase)

    return JSONResponse(query.search(index='term', type='value'))

def _normalize_spatial_results_to_wkt(search_results):
	for search_result in search_results['hits']['hits']:
		if settings.ENTITY_TYPE_FOR_MAP_DISPLAY in search_result['_source']:
			wkts = []
			for geom in search_result['_source'][settings.ENTITY_TYPE_FOR_MAP_DISPLAY]:
				wkts.append(GEOSGeometry(JSONSerializer().serialize(geom, ensure_ascii=False)).wkt)
			search_result['_source'][settings.ENTITY_TYPE_FOR_MAP_DISPLAY] = wkts

		wkts = []
		for geom in search_result['_source']['geometries']:
			wkts.append(GEOSGeometry(geom).wkt)
		search_result['_source']['geometries'] = wkts
	return search_results

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