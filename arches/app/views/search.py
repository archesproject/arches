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
    boolquery.should(Match(field='value', query=searchString.lower(), type='phrase_prefix', fuzziness='AUTO'))
    boolquery.should(Match(field='value.folded', query=searchString.lower(), type='phrase_prefix', fuzziness='AUTO'))
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
    results = query.search(index='strings') or {'hits': {'hits':[]}}

    i = 0;
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

def select_geoms_for_results(features, geojson_nodes, user_is_reviewer):
    res = []
    for feature in features:
        if 'provisional' in feature:
            if feature['provisional'] == False or (user_is_reviewer is True and feature['provisional'] is True):
                if feature['nodegroup_id'] in geojson_nodes:
                    res.append(feature)
        else:
            if feature['nodegroup_id'] in geojson_nodes:
                res.append(feature)

    return res

def search_results(request):
    try:
        search_results_dsl = build_search_results_dsl(request)
    except Exception as err:
        return JSONResponse(err.message, status=500)

    dsl = search_results_dsl['query']
    search_buffer = search_results_dsl['search_buffer']
    dsl.include('graph_id')
    dsl.include('root_ontology_class')
    dsl.include('resourceinstanceid')
    dsl.include('points')
    dsl.include('geometries')
    dsl.include('displayname')
    dsl.include('displaydescription')
    dsl.include('map_popup')
    dsl.include('provisional_resource')

    results = dsl.search(index='resource', doc_type=get_doc_type(request))

    if results is not None:
        user_is_reviewer = request.user.groups.filter(name='Resource Reviewer').exists()
        total = results['hits']['total']
        page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))

        paginator, pages = get_paginator(request, results, total, page, settings.SEARCH_ITEMS_PER_PAGE)
        page = paginator.page(page)

        # only reuturn points and geometries a user is allowed to view
        geojson_nodes = get_nodegroups_by_datatype_and_perm(request, 'geojson-feature-collection', 'read_nodegroup')

        for result in results['hits']['hits']:
            result['_source']['points'] = select_geoms_for_results(result['_source']['points'], geojson_nodes, user_is_reviewer)
            result['_source']['geometries'] = select_geoms_for_results(result['_source']['geometries'], geojson_nodes, user_is_reviewer)

        ret = {}
        ret['results'] = results
        ret['search_buffer'] = JSONSerializer().serialize(search_buffer) if search_buffer != None else None
        ret['paginator'] = {}
        ret['paginator']['current_page'] = page.number
        ret['paginator']['has_next'] = page.has_next()
        ret['paginator']['has_previous'] = page.has_previous()
        ret['paginator']['has_other_pages'] = page.has_other_pages()
        ret['paginator']['next_page_number'] = page.next_page_number() if page.has_next() else None
        ret['paginator']['previous_page_number'] = page.previous_page_number() if page.has_previous() else None
        ret['paginator']['start_index'] = page.start_index()
        ret['paginator']['end_index'] = page.end_index()
        ret['paginator']['pages'] = pages
        ret['reviewer'] = user_is_reviewer

        return JSONResponse(ret)
    else:
        return HttpResponseNotFound(_("There was an error retrieving the search results"))

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

def build_search_results_dsl(request):
    term_filter = request.GET.get('termFilter', '')
    spatial_filter = JSONDeserializer().deserialize(request.GET.get('mapFilter', '{}'))
    include_provisional = get_provisional_type(request)

    export = request.GET.get('export', None)
    mobile_download = request.GET.get('mobiledownload', None)
    page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))
    temporal_filter = JSONDeserializer().deserialize(request.GET.get('temporalFilter', '{}'))
    advanced_filters = JSONDeserializer().deserialize(request.GET.get('advanced', '[]'))
    search_buffer = None
    se = SearchEngineFactory().create()

    if export != None:
        limit = settings.SEARCH_EXPORT_ITEMS_PER_PAGE
    elif mobile_download != None:
        limit = settings.MOBILE_DOWNLOAD_RESOURCE_LIMIT
    else:
        limit = settings.SEARCH_ITEMS_PER_PAGE

    query = Query(se, start=limit*int(page-1), limit=limit)
    search_query = Bool()

    nested_agg = NestedAgg(path='points', name='geo_aggs')
    nested_agg_filter = FiltersAgg(name='inner')

    permitted_nodegroups = get_permitted_nodegroups(request.user)
    geo_agg_filter = Bool()

    if include_provisional == True:
        geo_agg_filter.filter(Terms(field='points.provisional', terms=['false','true']))

    else:
        provisional_resource_filter = Bool()

        if include_provisional == False:
            provisional_resource_filter.filter(Terms(field='provisional_resource', terms=['false', 'partial']))
            geo_agg_filter.filter(Terms(field='points.provisional', terms=['false']))

        elif include_provisional == 'only provisional':
            provisional_resource_filter.filter(Terms(field='provisional_resource', terms=['true', 'partial']))
            geo_agg_filter.filter(Terms(field='points.provisional', terms=['true']))

        search_query.must(provisional_resource_filter)

    geo_agg_filter.filter(Terms(field='points.nodegroup_id', terms=permitted_nodegroups))
    nested_agg_filter.add_filter(geo_agg_filter)
    nested_agg_filter.add_aggregation(GeoHashGridAgg(field='points.point', name='grid', precision=settings.HEX_BIN_PRECISION))
    nested_agg_filter.add_aggregation(GeoBoundsAgg(field='points.point', name='bounds'))
    nested_agg.add_aggregation(nested_agg_filter)
    query.add_aggregation(nested_agg)

    if term_filter != '':
        for term in JSONDeserializer().deserialize(term_filter):
            term_query = Bool()
            provisional_term_filter = Bool()
            if term['type'] == 'term' or term['type'] == 'string':
                string_filter = Bool()
                if term['type'] == 'term':
                    string_filter.must(Match(field='strings.string', query=term['value'], type='phrase'))
                elif term['type'] == 'string':
                    string_filter.should(Match(field='strings.string', query=term['value'], type='phrase_prefix'))
                    string_filter.should(Match(field='strings.string.folded', query=term['value'], type='phrase_prefix'))

                if include_provisional == False:
                    string_filter.must_not(Match(field='strings.provisional', query='true', type='phrase'))
                elif include_provisional == 'only provisional':
                    string_filter.must_not(Match(field='strings.provisional', query='false', type='phrase'))

                string_filter.filter(Terms(field='strings.nodegroup_id', terms=permitted_nodegroups))
                nested_string_filter = Nested(path='strings', query=string_filter)
                if term['inverted']:
                    search_query.must_not(nested_string_filter)
                else:
                    search_query.must(nested_string_filter)
                    # need to set min_score because the query returns results with score 0 and those have to be removed, which I don't think it should be doing
                    query.min_score('0.01')
            elif term['type'] == 'concept':
                concept_ids = _get_child_concepts(term['value'])
                conceptid_filter = Bool()
                conceptid_filter.filter(Terms(field='domains.conceptid', terms=concept_ids))
                conceptid_filter.filter(Terms(field='domains.nodegroup_id', terms=permitted_nodegroups))

                if include_provisional == False:
                    conceptid_filter.must_not(Match(field='domains.provisional', query='true', type='phrase'))
                elif include_provisional == 'only provisional':
                    conceptid_filter.must_not(Match(field='domains.provisional', query='false', type='phrase'))

                nested_conceptid_filter = Nested(path='domains', query=conceptid_filter)
                if term['inverted']:
                    search_query.must_not(nested_conceptid_filter)
                else:
                    search_query.filter(nested_conceptid_filter)

    if 'features' in spatial_filter:

        if len(spatial_filter['features']) > 0:
            feature_geom = spatial_filter['features'][0]['geometry']
            feature_properties = {}
            if 'properties' in spatial_filter['features'][0]:
                feature_properties = spatial_filter['features'][0]['properties']
            buffer = {'width':0,'unit':'ft'}
            if 'buffer' in feature_properties:
                buffer = feature_properties['buffer']
            search_buffer = _buffer(feature_geom, buffer['width'], buffer['unit'])
            feature_geom = JSONDeserializer().deserialize(search_buffer.json)
            geoshape = GeoShape(field='geometries.geom.features.geometry', type=feature_geom['type'], coordinates=feature_geom['coordinates'] )


            invert_spatial_search = False
            if 'inverted' in feature_properties:
                invert_spatial_search = feature_properties['inverted']

            spatial_query = Bool()
            if invert_spatial_search == True:
                spatial_query.must_not(geoshape)
            else:
                spatial_query.filter(geoshape)

            # get the nodegroup_ids that the user has permission to search
            spatial_query.filter(Terms(field='geometries.nodegroup_id', terms=permitted_nodegroups))

            if include_provisional == False:
                spatial_query.filter(Terms(field='geometries.provisional', terms=['false']))

            elif include_provisional == 'only provisional':
                spatial_query.filter(Terms(field='geometries.provisional', terms=['true']))

            search_query.filter(Nested(path='geometries', query=spatial_query))

    if 'fromDate' in temporal_filter and 'toDate' in temporal_filter:
        now = str(datetime.utcnow())
        start_date = ExtendedDateFormat(temporal_filter['fromDate'])
        end_date = ExtendedDateFormat(temporal_filter['toDate'])
        date_nodeid = str(temporal_filter['dateNodeId']) if 'dateNodeId' in temporal_filter and temporal_filter['dateNodeId'] != '' else None
        query_inverted = False if 'inverted' not in temporal_filter else temporal_filter['inverted']

        temporal_query = Bool()

        if query_inverted:
            # inverted date searches need to use an OR clause and are generally more complicated to structure (can't use ES must_not)
            # eg: less than START_DATE OR greater than END_DATE
            inverted_date_query = Bool()
            inverted_date_ranges_query = Bool()

            if start_date.is_valid():
                inverted_date_query.should(Range(field='dates.date', lt=start_date.lower))
                inverted_date_ranges_query.should(Range(field='date_ranges.date_range', lt=start_date.lower))
            if end_date.is_valid():
                inverted_date_query.should(Range(field='dates.date', gt=end_date.upper))
                inverted_date_ranges_query.should(Range(field='date_ranges.date_range', gt=end_date.upper))

            date_query = Bool()
            date_query.filter(inverted_date_query)
            date_query.filter(Terms(field='dates.nodegroup_id', terms=permitted_nodegroups))

            if include_provisional == False:
                date_query.filter(Terms(field='dates.provisional', terms=['false']))

            elif include_provisional == 'only provisional':
                date_query.filter(Terms(field='dates.provisional', terms=['true']))

            if date_nodeid:
                date_query.filter(Term(field='dates.nodeid', term=date_nodeid))
            else:
                date_ranges_query = Bool()
                date_ranges_query.filter(inverted_date_ranges_query)
                date_ranges_query.filter(Terms(field='date_ranges.nodegroup_id', terms=permitted_nodegroups))

                if include_provisional == False:
                    date_ranges_query.filter(Terms(field='date_ranges.provisional', terms=['false']))

                elif include_provisional == 'only provisional':
                    date_ranges_query.filter(Terms(field='date_ranges.provisional', terms=['true']))

                temporal_query.should(Nested(path='date_ranges', query=date_ranges_query))
            temporal_query.should(Nested(path='dates', query=date_query))

        else:
            date_query = Bool()
            date_query.filter(Range(field='dates.date', gte=start_date.lower, lte=end_date.upper))
            date_query.filter(Terms(field='dates.nodegroup_id', terms=permitted_nodegroups))

            if include_provisional == False:
                date_query.filter(Terms(field='dates.provisional', terms=['false']))
            elif include_provisional == 'only provisional':
                date_query.filter(Terms(field='dates.provisional', terms=['true']))

            if date_nodeid:
                date_query.filter(Term(field='dates.nodeid', term=date_nodeid))
            else:
                date_ranges_query = Bool()
                date_ranges_query.filter(Range(field='date_ranges.date_range', gte=start_date.lower, lte=end_date.upper, relation='intersects'))
                date_ranges_query.filter(Terms(field='date_ranges.nodegroup_id', terms=permitted_nodegroups))

                if include_provisional == False:
                    date_ranges_query.filter(Terms(field='date_ranges.provisional', terms=['false']))
                if include_provisional == 'only provisional':
                    date_ranges_query.filter(Terms(field='date_ranges.provisional', terms=['true']))

                temporal_query.should(Nested(path='date_ranges', query=date_ranges_query))
            temporal_query.should(Nested(path='dates', query=date_query))

        search_query.filter(temporal_query)

    datatype_factory = DataTypeFactory()
    if len(advanced_filters) > 0:
        advanced_query = Bool()
        grouped_query = Bool()
        grouped_queries = [grouped_query]
        for index, advanced_filter in enumerate(advanced_filters):
            tile_query = Bool()
            for key, val in advanced_filter.iteritems():
                if key != 'op':
                    node = models.Node.objects.get(pk=key)
                    if request.user.has_perm('read_nodegroup', node.nodegroup):
                        datatype = datatype_factory.get_instance(node.datatype)
                        datatype.append_search_filters(val, node, tile_query, request)
            nested_query = Nested(path='tiles', query=tile_query)
            if advanced_filter['op'] == 'or' and index != 0:
                grouped_query = Bool()
                grouped_queries.append(grouped_query)
            grouped_query.must(nested_query)
        for grouped_query in grouped_queries:
            advanced_query.should(grouped_query)
        search_query.must(advanced_query)

    query.add_query(search_query)
    if search_buffer != None:
        search_buffer = search_buffer.geojson
    return {'query': query, 'search_buffer':search_buffer}

def get_permitted_nodegroups(user):
    return [str(nodegroup.pk) for nodegroup in get_nodegroups_by_perm(user, 'models.read_nodegroup')]

def get_nodegroups_by_datatype_and_perm(request, datatype, permission):
    nodes = []
    for node in models.Node.objects.filter(datatype=datatype):
        if request.user.has_perm(permission, node.nodegroup):
            nodes.append(str(node.nodegroup_id))
    return nodes

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

def export_results(request):
    search_results_dsl = build_search_results_dsl(request)
    dsl = search_results_dsl['query']
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

def time_wheel_config(request):
    time_wheel = TimeWheel()
    key = 'time_wheel_config_{0}'.format(request.user.username)
    config = cache.get(key)
    if config is None:
        config = time_wheel.time_wheel_config(request.user)
    return JSONResponse(config, indent=4)
