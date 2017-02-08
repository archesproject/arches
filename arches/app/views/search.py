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


from dateutil import parser
from django.conf import settings
from django.shortcuts import render
from django.core.paginator import Paginator
from django.apps import apps
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Max, Min
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.views.concept import get_preflabel_from_conceptid
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range, MinAgg, MaxAgg, DateRangeAgg
from arches.app.utils.data_management.resources.exporter import ResourceExporter
from django.utils.module_loading import import_string
from arches.app.views.base import BaseManagerView

import csv

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class SearchView(BaseManagerView):
    def get(self, request):
        map_layers = models.MapLayers.objects.all()
        map_sources = models.MapSources.objects.all()
        date_nodes = models.Node.objects.filter(datatype='date', graph__isresource=True, graph__isactive=True)

        context = self.get_context_data(
            date_nodes=date_nodes,
            map_layers=map_layers,
            map_sources=map_sources,
            main_script='views/search',
        )

        context['nav']['title'] = 'Search'
        context['nav']['icon'] = 'fa-search'
        context['nav']['search'] = False
        context['nav']['help'] = ('Searching the Arches Database','')

        return render(request, 'views/search.htm', context)

def home_page(request):
    return render(request, 'views/search.htm', {
        'main_script': 'views/search',
    })

def search_terms(request):
    lang = request.GET.get('lang', settings.LANGUAGE_CODE)

    query = build_search_terms_dsl(request)
    results = query.search(index='term', doc_type='value') or {'hits': {'hits':[]}}

    for result in results['hits']['hits']:
        prefLabel = get_preflabel_from_conceptid(result['_source']['context'], lang)
        result['_source']['options']['context_label'] = prefLabel['value']

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
    results = dsl.search(index='resource', doc_type=get_doc_type(request))
    total = results['hits']['total']
    page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))
    all_result_ids = []
    if request.GET.get('include_ids', 'false') == 'false':
        all_result_ids = ['_none']
    full_results = dsl.search(index='resource', doc_type='', start=0, limit=10000, fields=[])
    all_result_ids = [hit['_id'] for hit in full_results['hits']['hits']]

    paginator, pages = get_paginator(request, results, total, page, settings.SEARCH_ITEMS_PER_PAGE, all_result_ids)
    page = paginator.page(page)

    ret = {}
    ret['results'] = results
    ret['all_result_ids'] = all_result_ids

    ret['paginator'] = JSONSerializer().serializeToPython(page)
    ret['paginator']['has_next'] = page.has_next()
    ret['paginator']['has_previous'] = page.has_previous()
    ret['paginator']['has_other_pages'] = page.has_other_pages()
    ret['paginator']['next_page_number'] = page.next_page_number() if page.has_next() else None
    ret['paginator']['previous_page_number'] = page.previous_page_number() if page.has_previous() else None
    ret['paginator']['start_index'] = page.start_index()
    ret['paginator']['end_index'] = page.end_index()
    ret['paginator']['pages'] = pages
    return JSONResponse(ret)

def get_doc_type(request):
    doc_type = set()
    type_filter = request.GET.get('typeFilter', '')
    if type_filter != '':
        resource_model_ids = set(str(graphid) for graphid in models.GraphModel.objects.filter(isresource=True).values_list('graphid', flat=True))
        for resouceTypeFilter in JSONDeserializer().deserialize(type_filter):
            if resouceTypeFilter['inverted'] == True:
                inverted_resource_model_ids = resource_model_ids - set([str(resouceTypeFilter['graphid'])])
                if len(doc_type) > 0:
                    doc_type = doc_type.intersection(inverted_resource_model_ids)
                else:
                    doc_type = inverted_resource_model_ids
            else:
                doc_type.add(str(resouceTypeFilter['graphid']))

    return list(doc_type)

def get_paginator(request, results, total_count, page, count_per_page, all_ids):
    paginator = Paginator(range(total_count), count_per_page)
    pages = [page]
    if paginator.num_pages > 1:
        before = range(1, page)
        after = range(page+1, paginator.num_pages+1)
        default_ct = 2
        ct_before = default_ct if len(after) > default_ct else default_ct*2-len(after)
        ct_after = default_ct if len(before) > default_ct else default_ct*2-len(before)
        if len(before) > ct_before:
            before = [1,None]+before[-1*(ct_before-1):]
        if len(after) > ct_after:
            after = after[0:ct_after-1]+[None,paginator.num_pages]
        pages = before+pages+after
    return paginator, pages

    return render(request, 'pagination.htm', {
        'pages': pages,
        'page_obj': paginator.page(page),
        'results': JSONSerializer().serialize(results),
        'all_ids': JSONSerializer().serialize(all_ids)
    })

def build_search_results_dsl(request):
    term_filter = request.GET.get('termFilter', '')
    spatial_filter = JSONDeserializer().deserialize(request.GET.get('mapFilter', '{}'))
    export = request.GET.get('export', None)
    page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))
    temporal_filter = JSONDeserializer().deserialize(request.GET.get('temporalFilter', '{}'))

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
                term_filter = Bool()
                term_filter.must(Match(field='strings', query=term['value'], type='phrase'))
                if term['inverted']:
                    boolfilter.must_not(term_filter)
                else:
                    boolfilter.must(term_filter)
            elif term['type'] == 'concept':
                concept_ids = _get_child_concepts(term['value'])
                conceptid_filter = Terms(field='domains.conceptid', terms=concept_ids)
                if term['inverted']:
                    boolfilter.must_not(conceptid_filter)
                else:
                    boolfilter.must(conceptid_filter)
            elif term['type'] == 'string':
                string_filter = Bool()
                string_filter.should(Match(field='strings', query=term['value'], type='phrase_prefix'))
                string_filter.should(Match(field='strings.folded', query=term['value'], type='phrase_prefix'))
                if term['inverted']:
                    boolfilter.must_not(string_filter)
                else:
                    boolfilter.must(string_filter)

    if 'features' in spatial_filter:
        if len(spatial_filter['features']) > 0:
            feature_geom = spatial_filter['features'][0]['geometry']
            feature_properties = spatial_filter['features'][0]['properties']
            buffer = {'width':0,'unit':'ft'}
            if 'buffer' in feature_properties:
                buffer = feature_properties['buffer']
            feature_geom = JSONDeserializer().deserialize(_buffer(feature_geom,buffer['width'],buffer['unit']).json)
            geoshape = GeoShape(field='geometries.features.geometry', type=feature_geom['type'], coordinates=feature_geom['coordinates'] )

            invert_spatial_search = False
            if 'inverted' in feature_properties:
                invert_spatial_search = feature_properties['inverted']

            if invert_spatial_search == True:
                boolfilter.must_not(geoshape)
            else:
                boolfilter.must(geoshape)

    if 'fromDate' in temporal_filter and 'toDate' in temporal_filter:
        start_date = None
        end_date = None
        try:
            start_date = parser.parse(temporal_filter['fromDate'])
            start_date = start_date.isoformat()
        except:
            pass
        try:
            end_date = parser.parse(temporal_filter['toDate'])
            end_date = end_date.isoformat()
        except:
            pass

        if 'dateNodeId' in temporal_filter and temporal_filter['dateNodeId'] != '':
            range = Range(field='tiles.data.%s' % (temporal_filter['dateNodeId']), gte=start_date, lte=end_date)
            time_query_dsl = Nested(path='tiles', query=range)
        else:
            time_query_dsl = Range(field='dates', gte=start_date, lte=end_date)

        if 'inverted' not in temporal_filter:
            temporal_filter['inverted'] = False

        if temporal_filter['inverted']:
            boolfilter.must_not(time_query_dsl)
        else:
            boolfilter.must(time_query_dsl)

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
    for row in Concept().get_child_concepts(conceptid, ['narrower'], ['prefLabel'], 'prefLabel'):
        ret.add(row[0])
        ret.add(row[1])
    return list(ret)

def geocode(request):
    geocoding_provider_id = request.GET.get('geocoder', '')
    provider = next((provider for provider in settings.GEOCODING_PROVIDERS if provider['id'] == geocoding_provider_id), None)
    Geocoder = import_string('arches.app.utils.geocoders.' + provider['id'])
    search_string = request.GET.get('q', '')
    return JSONResponse({ 'results': Geocoder().find_candidates(search_string, provider['api_key']) })

def time_wheel_config(request):
    se = SearchEngineFactory().create()

    query = Query(se, limit=0)
    query.add_aggregation(MinAgg(field='dates', format='y'))
    query.add_aggregation(MaxAgg(field='dates', format='y'))
    results = query.search(index='resource')
    min_date = results['aggregations']['min_dates']['value_as_string']
    max_date = results['aggregations']['max_dates']['value_as_string']

    query = Query(se, limit=0)
    #date_range_agg = DateRangeAgg(field='dates', format='y', min_date=min_date, max_date=max_date)
    #date_range_agg.add(min_date='2000', max_date='4000')
    
    #date_range_agg.add_aggregation(DateRangeAgg(field='dates', format='y', min_date=min_date, max_date=max_date))

    # import ipdb
    # ipdb.set_trace()
    for millennium in range(0,3000,1000):
        min_millenium = millennium
        max_millenium = millennium + 1000
        millenium_agg = DateRangeAgg(name="%s-%s"%(min_millenium, max_millenium), field='dates', format='yyyy', min_date=str(min_millenium), max_date=str(max_millenium))
        
        for century in range(min_millenium,max_millenium,100):
            min_century = century
            max_century = century + 100
            century_aggregation = DateRangeAgg(name="%s-%s"%(min_century, max_century), field='dates', format='yyyy', min_date=str(min_century), max_date=str(max_century))
            millenium_agg.add_aggregation(century_aggregation)

        query.add_aggregation(millenium_agg)
    return JSONResponse(get_tw_config(), indent=4)
    return JSONResponse(query.search(index='resource'), indent=4)
    return JSONResponse(query.dsl, indent=4)

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


def get_tw_config():
    return {
        "name": "root",
        "children": [{
                "name": "Historic",
                "children": [{
                        "name": "21st Century",
                        "size": 75,
                        "start": 2001,
                        "end": 2100
                    },
                    {
                        "name": "20th Century",
                        "start": 1901,
                        "end": 2000,
                        "children": [{
                                "name": "Late 20th Century",
                                "size": 230,
                                "start": 1965,
                                "end": 1999
                            },
                            {
                                "name": "Middle 20th Century",
                                "size": 190,
                                "start": 1945,
                                "end": 1965
                            },
                            {
                                "name": "WWII",
                                "size": 207,
                                "start": 1939,
                                "end": 1945
                            },
                            {
                                "name": "Early 20th Century",
                                "start": 1900,
                                "end": 1939,
                                "children": [{
                                        "name": "WWI",
                                        "size": 377,
                                        "start": 1914,
                                        "end": 1918
                                    },
                                    {
                                        "name": "Post WWI",
                                        "size": 632,
                                        "start": 1918,
                                        "end": 1939
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "name": "Enlightenment",
                        "start": 1600,
                        "end": 2000,
                        "children": [{
                                "name": "1900s",
                                "size": 1003,
                                "start": 1900,
                                "end": 2000
                            },
                            {
                                "name": "1800s",
                                "size": 2108,
                                "start": 1800,
                                "end": 1900
                            },
                            {
                                "name": "1700s",
                                "size": 1533,
                                "start": 1700,
                                "end": 1800
                            },
                            {
                                "name": "1600s",
                                "size": 2312,
                                "start": 1600,
                                "end": 1700
                            }
                        ]
                    },
                    {
                        "name": "Post Midieval",
                        "start": 1300,
                        "end": 1600,
                        "children": [{
                                "name": "Victorian",
                                "size": 3861,
                                "start": 1400,
                                "end": 1500
                            },
                            {
                                "name": "Hannoverian",
                                "start": 1380,
                                "end": 1380,
                                "children": [{
                                        "name": "George I",
                                        "size": 2877,
                                        "start": 1380,
                                        "end": 1380
                                    },
                                    {
                                        "name": "George Ib",
                                        "size": 1187,
                                        "start": 1380,
                                        "end": 1380
                                    }
                                ]
                            },
                            {
                                "name": "Stuart",
                                "start": 1340,
                                "end": 1380,
                                "children": [{
                                    "name": "Jacobean",
                                    "size": 961,
                                    "start": 1340,
                                    "end": 1380
                                }]
                            },
                            {
                                "name": "Tudor",
                                "start": 1300,
                                "end": 1340,
                                "children": [{
                                    "name": "Elizabethian",
                                    "size": 1900,
                                    "start": 1300,
                                    "end": 1340
                                }]
                            }
                        ]
                    },
                    {
                        "name": "Midieval",
                        "start": 900,
                        "end": 1300,
                        "children": [{
                                "name": "Late Midieval",
                                "size": 4134,
                                "start": 1100,
                                "end": 1300
                            },
                            {
                                "name": "Early Midieval",
                                "size": 7399,
                                "start": 900,
                                "end": 1100
                            }
                        ]
                    },
                    {
                        "name": "Roman",
                        "size": 18012,
                        "start": 43,
                        "end": 900
                    }
                ]
            },
            {
                "name": "Prehistoric",
                "start": -15000,
                "end": 43,
                "children": [{
                        "name": "Late Prehistoric",
                        "children": [{
                                "name": "Iron Age",
                                "start": -800,
                                "end": 43,
                                "children": [{
                                        "name": "Late Iron",
                                        "size": 2977,
                                        "start": 0,
                                        "end": 43
                                    },
                                    {
                                        "name": "Middle Iron",
                                        "size": 3866,
                                        "start": -400,
                                        "end": 0
                                    },
                                    {
                                        "name": "Early Iron",
                                        "size": 5219,
                                        "start": -800,
                                        "end": -400
                                    }
                                ]
                            },
                            {
                                "name": "Bronze Age",
                                "start": -1800,
                                "end": -800,
                                "children": [{
                                        "name": "Late Bronze",
                                        "size": 1883,
                                        "start": -1000,
                                        "end": -800
                                    },
                                    {
                                        "name": "Middle Bronze",
                                        "size": 2016,
                                        "start": -1200,
                                        "end": -1000
                                    },
                                    {
                                        "name": "Early Bronze",
                                        "size": 300,
                                        "start": -1800,
                                        "end": -1200
                                    }
                                ]
                            },
                            {
                                "name": "Neolithic",
                                "start": -4500,
                                "end": -1800,
                                "children": [{
                                        "name": "Late Neolithic",
                                        "size": 2196,
                                        "start": -2000,
                                        "end": -1800
                                    },
                                    {
                                        "name": "Middle Neolithic",
                                        "size": 2445,
                                        "start": -3000,
                                        "end": -2000
                                    },
                                    {
                                        "name": "Early Neolithic",
                                        "size": 988,
                                        "start": -4500,
                                        "end": -3000
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "name": "Early Prehistoric",
                        "start": -15000,
                        "end": -4500,
                        "children": [{
                                "name": "Mesolithic",
                                "children": [{
                                        "name": "Late Mesolithic",
                                        "size": 875,
                                        "start": -6000,
                                        "end": -4500
                                    },
                                    {
                                        "name": "Early Mesolithic",
                                        "size": 775,
                                        "start": -8000,
                                        "end": -6000
                                    }
                                ]
                            },
                            {
                                "name": "Paleolithic",
                                "start": -15000,
                                "end": -8000,
                                "children": [{
                                        "name": "Upper Paleolithic",
                                        "size": 3997,
                                        "start": -10000,
                                        "end": -8000
                                    },
                                    {
                                        "name": "Middle Paleolithic",
                                        "size": 1009,
                                        "start": -13000,
                                        "end": -10000
                                    },
                                    {
                                        "name": "Lower Paleolithic",
                                        "size": 8877,
                                        "start": -15000,
                                        "end": -13000
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    };