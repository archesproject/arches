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


import csv
from datetime import datetime
from django.shortcuts import render
from django.apps import apps
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.core.cache import cache
from django.db import connection
from django.db.models import Q, Max, Min
from django.http import HttpResponseNotFound
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.models.graph import Graph
from arches.app.models.system_settings import settings
from arches.app.utils.pagination import get_paginator
from arches.app.utils.response import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.date_utils import ExtendedDateFormat
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Term, Terms, GeoShape, Range, MinAgg, MaxAgg, RangeAgg, Aggregation, GeoHashGridAgg, GeoBoundsAgg, FiltersAgg, NestedAgg
from arches.app.search.time_wheel import TimeWheel
from arches.app.search.components.base import SearchFilterFactory
from arches.app.utils.data_management.resources.exporter import ResourceExporter
from arches.app.views.base import BaseManagerView, MapBaseManagerView
from arches.app.views.concept import get_preflabel_from_conceptid
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.permission_backend import get_nodegroups_by_perm



try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class SearchView(MapBaseManagerView):

    def get(self, request):
        saved_searches = JSONSerializer().serialize(settings.SAVED_SEARCHES)
        map_layers = models.MapLayer.objects.all()
        map_markers = models.MapMarker.objects.all()
        map_sources = models.MapSource.objects.all()
        date_nodes = models.Node.objects.filter(Q(datatype='date') | Q(datatype='edtf'), graph__isresource=True, graph__isactive=True)
        resource_graphs = models.GraphModel.objects.exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).exclude(isresource=False).exclude(isactive=False)
        searchable_datatypes = [d.pk for d in models.DDataType.objects.filter(issearchable=True)]
        searchable_nodes = models.Node.objects.filter(graph__isresource=True, graph__isactive=True, datatype__in=searchable_datatypes, issearchable=True)
        resource_cards = models.CardModel.objects.filter(graph__isresource=True, graph__isactive=True)
        datatypes = models.DDataType.objects.all()
        geocoding_providers = models.Geocoder.objects.all()
        search_components = models.SearchComponent.objects.all()
        # only allow cards that the user has permission to read
        searchable_cards = []
        for card in resource_cards:
            if request.user.has_perm('read_nodegroup', card.nodegroup):
                searchable_cards.append(card)

        # only allow date nodes that the user has permission to read
        searchable_date_nodes = []
        for node in date_nodes:
            if request.user.has_perm('read_nodegroup', node.nodegroup):
                searchable_date_nodes.append(node)

        context = self.get_context_data(
            resource_cards=JSONSerializer().serialize(searchable_cards),
            searchable_nodes=JSONSerializer().serialize(searchable_nodes),
            saved_searches=saved_searches,
            date_nodes=searchable_date_nodes,
            map_layers=map_layers,
            map_markers=map_markers,
            map_sources=map_sources,
            geocoding_providers=geocoding_providers,
            search_components=search_components,
            main_script='views/search',
            resource_graphs=resource_graphs,
            datatypes=datatypes,
            datatypes_json=JSONSerializer().serialize(datatypes),
            user_is_reviewer=request.user.groups.filter(name='Resource Reviewer').exists()
        )

        graphs = JSONSerializer().serialize(
            context['resource_graphs'],
            exclude=['functions',
                     'author',
                     'deploymentdate',
                     'deploymentfile',
                     'version',
                     'subtitle',
                     'description',
                     'disable_instance_creation',
                     'ontology_id'])
        context['graphs'] = graphs
        context['graph_models'] = models.GraphModel.objects.all().exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        context['nav']['title'] = _('Search')
        context['nav']['icon'] = 'fa-search'
        context['nav']['search'] = False
        context['nav']['help'] = {
            'title': _('Searching the Database'),
            'template': 'search-help',
        }

        return render(request, 'views/search.htm', context)


def home_page(request):
    return render(request, 'views/search.htm', {
        'main_script': 'views/search',
    })


def search_terms(request):
    lang = request.GET.get('lang', settings.LANGUAGE_CODE)
    se = SearchEngineFactory().create()
    searchString = request.GET.get('q', '')
    query = Query(se, start=0, limit=0)
    user_is_reviewer = request.user.groups.filter(name='Resource Reviewer').exists()

    boolquery = Bool()
    boolquery.should(Match(field='value', query=searchString.lower(), type='phrase_prefix'))
    boolquery.should(Match(field='value.folded', query=searchString.lower(), type='phrase_prefix'))
    boolquery.should(Match(field='value.folded', query=searchString.lower(), fuzziness='AUTO'))

    if user_is_reviewer is False:
        boolquery.filter(Terms(field='provisional', terms=['false']))

    query.add_query(boolquery)
    base_agg = Aggregation(name='value_agg', type='terms', field='value.raw', size=settings.SEARCH_DROPDOWN_LENGTH, order={"max_score": "desc"})
    nodegroupid_agg = Aggregation(name='nodegroupid', type='terms', field='nodegroupid')
    top_concept_agg = Aggregation(name='top_concept', type='terms', field='top_concept')
    conceptid_agg = Aggregation(name='conceptid', type='terms', field='conceptid')
    max_score_agg = MaxAgg(name='max_score', script='_score')

    top_concept_agg.add_aggregation(conceptid_agg)
    base_agg.add_aggregation(max_score_agg)
    base_agg.add_aggregation(top_concept_agg)
    base_agg.add_aggregation(nodegroupid_agg)
    query.add_aggregation(base_agg)
    results = query.search(index='terms,concepts') or {'hits': {'hits':[]}}

    i = 0
    ret = []
    for result in results['aggregations']['value_agg']['buckets']:
        if len(result['top_concept']['buckets']) > 0:
            for top_concept in result['top_concept']['buckets']:
                top_concept_id = top_concept['key']
                top_concept_label = get_preflabel_from_conceptid(top_concept['key'], lang)['value']
                for concept in top_concept['conceptid']['buckets']:
                    ret.append({
                        'type': 'concept',
                        'context': top_concept_id,
                        'context_label': top_concept_label,
                        'id': i,
                        'text': result['key'],
                        'value': concept['key']
                    })
                i = i + 1
        else:
            ret.append({
                'type': 'term',
                'context': '',
                'context_label': get_resource_model_label(result),
                'id': i,
                'text': result['key'],
                'value': result['key']
            })
            i = i + 1

    return JSONResponse(ret)


def get_resource_model_label(result):
    if len(result['nodegroupid']['buckets']) > 0:
        for nodegroup in result['nodegroupid']['buckets']:
            nodegroup_id = nodegroup['key']
            node = models.Node.objects.get(nodeid = nodegroup_id)
            graph = node.graph
        return "{0} - {1}".format(graph.name, node.name)
    else:
        return ''

def search_results(request):    
    se = SearchEngineFactory().create()
    search_results_object = {
        'query': Query(se)
    }

    include_provisional = get_provisional_type(request)
    permitted_nodegroups = get_permitted_nodegroups(request.user)

    search_filter_factory = SearchFilterFactory(request)
    try:
        for filter_type, querystring in request.GET.items() + [('search-results', '')]:
            search_filter = search_filter_factory.get_filter(filter_type)
            if search_filter:
                search_filter.append_dsl(search_results_object, permitted_nodegroups, include_provisional)
    except Exception as err:
        return JSONResponse(err.message, status=500)

    dsl = search_results_object.pop('query', None)
    dsl.include('graph_id')
    dsl.include('root_ontology_class')
    dsl.include('resourceinstanceid')
    dsl.include('points')
    dsl.include('geometries')
    dsl.include('displayname')
    dsl.include('displaydescription')
    dsl.include('map_popup')
    dsl.include('provisional_resource')
    if request.GET.get('tiles', None) is not None:
        dsl.include('tiles')

    results = dsl.search(index='resources')

    if results is not None:
        # allow filters to modify the results
        for filter_type, querystring in request.GET.items() + [('search-results', '')]:
            search_filter = search_filter_factory.get_filter(filter_type)
            if search_filter:
                search_filter.post_search_hook(search_results_object, results, permitted_nodegroups)

        ret = {}
        ret['results'] = results

        for key, value in search_results_object.items():
            ret[key] = value
            
        ret['reviewer'] = request.user.groups.filter(name='Resource Reviewer').exists()
        ret['timestamp'] = datetime.now()

        return JSONResponse(ret)
    else:
        return HttpResponseNotFound(_("There was an error retrieving the search results"))

def get_provisional_type(request):
    """
    Parses the provisional filter data to determine if a search results will
    include provisional (True) exclude provisional (False) or inlude only
    provisional 'only provisional'
    """

    result = False
    provisional_filter = JSONDeserializer().deserialize(request.GET.get('provisionalFilter', '[]'))
    user_is_reviewer = request.user.groups.filter(name='Resource Reviewer').exists()
    if user_is_reviewer != False:
        if len(provisional_filter) == 0:
            result = True
        else:
            inverted = provisional_filter[0]['inverted']
            if provisional_filter[0]['provisionaltype'] == 'Provisional':
                if inverted == False:
                    result = 'only provisional'
                else:
                    result = False
            if provisional_filter[0]['provisionaltype'] == 'Authoritative':
                if inverted == False:
                    result = False
                else:
                    result = 'only provisional'

    return result

def get_permitted_nodegroups(user):
    return [str(nodegroup.pk) for nodegroup in get_nodegroups_by_perm(user, 'models.read_nodegroup')]

def buffer(request):
    spatial_filter = JSONDeserializer().deserialize(request.GET.get('filter', {'geometry':{'type':'','coordinates':[]},'buffer':{'width':'0','unit':'ft'}}))

    if spatial_filter['geometry']['coordinates'] != '' and spatial_filter['geometry']['type'] != '':
        return JSONResponse(_buffer(spatial_filter['geometry'],spatial_filter['buffer']['width'],spatial_filter['buffer']['unit']), geom_format='json')

    return JSONResponse()

def _buffer(geojson, width=0, unit='ft'):
    geojson = JSONSerializer().serialize(geojson)
    geom = GEOSGeometry(geojson, srid=4326)

    try:
        width = float(width)
    except:
        width = 0

    if width > 0:
        if unit == 'ft':
            width = width/3.28084

        geom.transform(settings.ANALYSIS_COORDINATE_SYSTEM_SRID)
        geom = geom.buffer(width)
        geom.transform(4326)

    return geom

def _get_child_concepts(conceptid):
    ret = set([conceptid])
    for row in Concept().get_child_concepts(conceptid, ['prefLabel']):
        ret.add(row[0])
    return list(ret)

def time_wheel_config(request):
    time_wheel = TimeWheel()
    key = 'time_wheel_config_{0}'.format(request.user.username)
    config = cache.get(key)
    if config is None:
        config = time_wheel.time_wheel_config(request.user)
    return JSONResponse(config, indent=4)
