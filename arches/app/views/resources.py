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

import re
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from arches.app.utils.decorators import group_required
from django.conf import settings
from django.db import transaction
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Terms
from arches.app.models.concept import Concept, get_preflabel_from_valueid
from django.http import HttpResponseNotFound
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Max, Min

def report(request, resourceid):
    raise NotImplementedError('Reports are not yet implemented.')

@group_required('edit')
@csrf_exempt
def resource_manager(request, resourcetypeid='', form_id='default', resourceid=''):

    if resourceid != '':
        resource = Resource(resourceid)
    elif resourcetypeid != '':
        resource = Resource({'entitytypeid': resourcetypeid})

    if form_id == 'default':
        form_id = resource.form_groups[0]['forms'][0]['id']

    form = resource.get_form(form_id)

    if request.method == 'DELETE':
        resource.delete_index()
        se = SearchEngineFactory().create()
        realtionships = resource.get_related_resources(return_entities=False)
        for realtionship in realtionships:
            se.delete(index='resource_relations', doc_type='all', id=realtionship.resourcexid)
            realtionship.delete()
        resource.delete()
        return JSONResponse({ 'success': True })

    if request.method == 'POST':
        data = JSONDeserializer().deserialize(request.POST.get('formdata', {}))
        form.update(data, request.FILES)

        with transaction.atomic():
            if resourceid != '':
                resource.delete_index()
            resource.save(user=request.user)
            resource.index()
            resourceid = resource.entityid

            return redirect('resource_manager', resourcetypeid=resourcetypeid, form_id=form_id, resourceid=resourceid)

    min_max_dates = models.Dates.objects.aggregate(Min('val'), Max('val'))

    if request.method == 'GET':
        if form != None:
            lang = request.GET.get('lang', settings.LANGUAGE_CODE)
            form.load(lang)
            return render(request, 'resource-manager.htm', {
                'form': form,
                'formdata': JSONSerializer().serialize(form.data),
                'form_template': 'views/forms/' + form_id + '.htm',
                'form_id': form_id,
                'resourcetypeid': resourcetypeid,
                'resourceid': resourceid,
                'main_script': 'resource-manager',
                'active_page': 'ResourceManger',
                'resource': resource,
                'resource_name': resource.get_primary_name(),
                'resource_type_name': resource.get_type_name(),
                'form_groups': resource.form_groups,
                'min_date': min_max_dates['val__min'].year if min_max_dates['val__min'] != None else 0,
                'max_date': min_max_dates['val__max'].year if min_max_dates['val__min'] != None else 1,
                'timefilterdata': JSONSerializer().serialize(Concept.get_time_filter_data()),
            })
        else:
            return HttpResponseNotFound('<h1>Arches form not found.</h1>')

@csrf_exempt
def related_resources(request, resourceid):
    if request.method == 'GET':
        lang = request.GET.get('lang', settings.LANGUAGE_CODE)
        start = request.GET.get('start', 0)
        return JSONResponse(get_related_resources(resourceid, lang, start=start, limit=15), indent=4)

    if 'edit' in request.user.user_groups and request.method == 'DELETE':
        se = SearchEngineFactory().create()
        data = JSONDeserializer().deserialize(request.body)
        entityid1 = data.get('entityid1')
        entityid2 = data.get('entityid2')
        resourcexid = data.get('resourcexid')
        realtionshiptype = data.get('realtionshiptype')
        resource = Resource(entityid1)
        resource.delete_resource_relationship(entityid2, realtionshiptype)
        se.delete(index='resource_relations', doc_type='all', id=resourcexid)
        return JSONResponse({ 'success': True })

def get_related_resources(resourceid, lang, limit=1000, start=0):
    ret = {
        'resource_relationships': [],
        'related_resources': []
    }
    se = SearchEngineFactory().create()

    query = Query(se, limit=limit, start=start)
    query.add_filter(Terms(field='entityid1', terms=resourceid).dsl, operator='or')
    query.add_filter(Terms(field='entityid2', terms=resourceid).dsl, operator='or')
    resource_relations = query.search(index='resource_relations', doc_type='all')
    ret['total'] = resource_relations['hits']['total']

    entityids = set()
    for relation in resource_relations['hits']['hits']:
        relation['_source']['preflabel'] = get_preflabel_from_valueid(relation['_source']['relationshiptype'], lang)
        ret['resource_relationships'].append(relation['_source'])
        entityids.add(relation['_source']['entityid1'])
        entityids.add(relation['_source']['entityid2'])
    if len(entityids) > 0:
        entityids.remove(resourceid)

    related_resources = se.search(index='entity', doc_type='_all', id=list(entityids))
    if related_resources:
        for resource in related_resources['docs']:
            ret['related_resources'].append(resource['_source'])

    return ret

def map_layers(request, entitytypeid='all', get_centroids=False):
    data = []

    geom_param = request.GET.get('geom', None)

    bbox = request.GET.get('bbox', '')
    limit = request.GET.get('limit', settings.MAP_LAYER_FEATURE_LIMIT)
    entityids = request.GET.get('entityid', '')
    geojson_collection = {
      "type": "FeatureCollection",
      "features": []
    }

    se = SearchEngineFactory().create()
    query = Query(se, limit=limit)

    args = { 'index': 'maplayers' }
    if entitytypeid != 'all':
        args['doc_type'] = entitytypeid
    if entityids != '':
        for entityid in entityids.split(','):
            geojson_collection['features'].append(se.search(index='maplayers', id=entityid)['_source'])
        return JSONResponse(geojson_collection)

    data = query.search(**args)

    for item in data['hits']['hits']:
        if get_centroids:
            item['_source']['geometry'] = item['_source']['properties']['centroid']
            item['_source'].pop('properties', None)
        elif geom_param != None:
            item['_source']['geometry'] = item['_source']['properties'][geom_param]
            item['_source']['properties'].pop('extent', None)
            item['_source']['properties'].pop(geom_param, None)
        else:
            item['_source']['properties'].pop('extent', None)
            item['_source']['properties'].pop('centroid', None)
        geojson_collection['features'].append(item['_source'])

    return JSONResponse(geojson_collection)

def edit_history(request, resourceid=''):
    ret = []
    current = None
    index = -1
    start = request.GET.get('start', 0)
    limit = request.GET.get('limit', 10)
    if resourceid != '':
        dates = models.EditLog.objects.filter(resourceid = resourceid).values_list('timestamp', flat=True).order_by('-timestamp').distinct('timestamp')[start:limit]
        # dates = models.EditLog.objects.datetimes('timestamp', 'second', order='DESC')
        for date in dates:
            #ret[str(date)] = models.EditLog.objects.filter(resourceid = self.resource.entityid, timestamp = date)
            print str(date)

        for log in models.EditLog.objects.filter(resourceid = resourceid, timestamp__in = dates).values().order_by('-timestamp', 'attributeentitytypeid'):
            if str(log['timestamp']) != current:
                current = str(log['timestamp'])
                ret.append({'date':str(log['timestamp'].date()), 'time': str(log['timestamp'].time().replace(microsecond=0).isoformat()), 'log': []})
                index = index + 1

            ret[index]['log'].append(log)

    return JSONResponse(ret, indent=4)

def get_admin_areas(request):
    geomString = request.GET.get('geom', '')
    geom = GEOSGeometry(geomString)
    intersection = models.Overlay.objects.filter(geometry__intersects=geom)
    return JSONResponse({'results': intersection}, indent=4)
