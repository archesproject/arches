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

def search_results(request, as_text=False):
    dsl = build_search_results_dsl(request)
    results = dsl.search(index='entity', doc_type='') 
    total = results['hits']['total']
    page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))
    all_entity_ids = ['_all']
    if request.GET.get('include_ids', 'false') == 'false':
        all_entity_ids = ['_none']
    elif request.GET.get('no_filters', '') == '':
        full_dsl = build_search_results_dsl(request)
        full_results = full_dsl.search(index='entity', doc_type='', start=0, limit=1000000, fields=[])
        all_entity_ids = [hit['_id'] for hit in full_results['hits']['hits']]

    return _get_pagination(results, total, page, settings.SEARCH_ITEMS_PER_PAGE, all_entity_ids)

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
            start_date = start_date.strftime('%Y-%m-%d')
        if end_date:
            end_date = end_date.strftime('%Y-%m-%d')
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

def _get_pagination(results, total_count, page, count_per_page, all_ids):
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



import xml.etree.ElementTree as ET
from django.http import StreamingHttpResponse
from django.http import HttpResponse
import json
import os
import zipfile
from datetime import datetime
import glob
import csv
import shapefile
import arches.app.utils.geos_to_pyshp as geos_to_pyshp
import codecs

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import GeometryCollection

def export_results(request):
    '''
    Takes a search request with an export format parameter and returns the respective format.

    '''

    #search_results = search_resources(request, district_number) 
    dsl = build_search_results_dsl(request)
    search_results = dsl.search(index='entity', doc_type='') 
    response = None
    format = request.GET.get('export', 'csv')

    if len(search_results['hits']['hits']) > 0:

        if format == 'geojson':
            geo_json = format_search_as_geojson(search_results, geojson=True)
            return JSONResponse(geo_json, indent=4)  

        elif format == 'shp':
            shp_prepped = format_search_as_geojson(search_results)
            shapefiles = create_shapefiles(shp_prepped)
            return shapefiles

        elif format == 'kml':
            kml_prepped = format_search_as_geojson(search_results)
            kml = create_kml(kml_prepped)
            response = HttpResponse(kml, content_type='text/xml')
            response['Content-Disposition'] = 'attachment; filename="search_result_export.kml"'

        elif format == 'csv':
            csv_prepped = format_search_as_geojson(search_results)
            csvs = create_csvs(csv_prepped)
            return csvs

            # Leave this here for now - in case we want to return a single csv file rather than a zip file

            # feature_collection = format_search_as_geojson(search_results)
            # prepare_caltrans_csv(feature_collection)
            # fieldnames = feature_collection['features'][0]['properties'].keys()
            # csvfile = StringIO()
            # csvwriter = csv.DictWriter(csvfile, delimiter='|', fieldnames=fieldnames)

            # def read_and_flush():
            #     csvfile.seek(0)
            #     data = csvfile.read()
            #     csvfile.seek(0)
            #     csvfile.truncate()
            #     return data

            # def stream():
            #     csvwriter.writeheader()
            #     for feature in feature_collection['features']:
            #         csvwriter.writerow(feature['properties'])
            #     data = read_and_flush()
            #     yield data

            # response = StreamingHttpResponse(stream(), content_type='text/csv')
            # response['Content-Disposition'] = 'attachment; filename="search_result_export.csv"'
            # return response

    else:
        response = HttpResponse('no search results available', content_type='text')
        response['Content-Disposition'] = 'attachment; filename="search_result_export.txt"'

    return response

def format_search_as_geojson(search_results, geojson=False):
    """
    Takes a 2d list of search results, groups them in to dictionaries by their resourceid, 
    and returns a geojson-like dictionary. If geojson is set to True, the returned object 
    is a valid geojson dictionary. 

    """

    resource_mappings = read_export_configs()
    features = []
    resources = search_results['hits']['hits']

    for resource in resources:
        if resource['_type'] in resource_mappings:
            source = resource['_source']
            field_mapping = resource_mappings[source['entitytypeid']]['fieldmap']
            
            properties = {}
            for entitytypeid, field_name in field_mapping.iteritems():
                print field_name
                properties[field_name] = None #A shapefile needs every possible field whether a resource has a matching related entity or not. ...So we add each field with None for every record.

            properties['type'] = source['entitytypeid']
            properties['id'] = resource['_id']

            #raise Exception()

            for entity in source['dates']:
                if entity['entitytypeid'] in field_mapping:
                    field_name = field_mapping[entity['entitytypeid']]
                    properties[field_name] = entity['value']

            geoms = []

            if len(source['geometries']) > 0:
                for g in source['geometries']:
                    geom = GEOSGeometry(JSONSerializer().serialize(g['value'], ensure_ascii=False))
                    geoms.append(geom)

            geometry = GeometryCollection(geoms)

            if geojson == True:
                geometry = json.loads(geometry.geojson)

            feature = {
                'type':'Feature',
                'geometry': geometry,
                'properties': properties
                }

            features.append(feature)

    feature_collection = {'type':'FeatureCollection', 'features': features}

    return feature_collection

def create_kml(feature_collection):
    """
    Takes a list of geojson dictionaries - with geometry still as a geos object and converts them to an ElementTree object with KML tags
    and attributes. Returns a kml version of the object.

    """

    root = ET.Element("kml", attrib={'xmlns':'http://earth.google.com/kml/2.0'})
    folder = ET.SubElement(root, "Folder")
    name = ET.SubElement(folder, "name")
    name.text = 'search-result-export'
    description = ET.SubElement(folder, 'description')
    description.text = 'Search Export Results'
    style = ET.SubElement(folder, 'Style', attrib={'id':'resource_style'})
    linestyle = ET.SubElement(style, 'LineStyle')
    width = ET.SubElement(linestyle, 'width')
    width.text = '2.0'
    line_color = ET.SubElement(linestyle, 'color')
    line_color.text = '7d0000ff'
    polystyle = ET.SubElement(style, 'PolyStyle')
    color = ET.SubElement(polystyle, 'color')
    color.text = '7d0000ff'
    colormode = ET.SubElement(polystyle, 'colorMode')
    colormode.text = 'normal'
    
    for feature in feature_collection['features']:
        placemark = ET.SubElement(folder,'Placemark')
        placemark_name = ET.SubElement(placemark, 'name')
        placemark_name.text = feature['properties']['type']
        placemark_description = ET.SubElement(placemark, 'description')
        visibility = ET.SubElement(placemark, 'visibility')
        visibility.text = '1'
        style_url = ET.SubElement(placemark, 'styleUrl')
        style_url.text = '#resource_style'

        extended_data = ET.SubElement(placemark, 'ExtendedData')
        for k, v in feature['properties'].iteritems():
            data = ET.SubElement(extended_data, 'Data', attrib={'name':k})
            value = ET.SubElement(data, 'value')
            value.text = v
        geometry_element = ET.fromstring(feature['geometry'].kml)
        placemark.append(geometry_element)

    return ET.tostring(root, encoding='UTF-8', method='xml')


def create_shapefiles(feature_collection):
    '''
    Takes a geojson-like (geojson-like because it has a geos geometry rather than a geojson geometry, allowing us to modify the 
    geometry to be a centroid or hull if necessary.) feature collection, groups the data by resource type and creates a shapefile
    for each resource. Returns a .zip file with each of the shapefiles. An arches export configuration file is needed to map shapefile
    fields to resorce entitytypeids and specify the shapefile column datatypes (fiona schema). 

    '''

    resource_export_groups = read_export_configs()

    for feature in feature_collection['features']:
        feature['geometry'] = feature['geometry'].centroid
        resource_export_groups[feature['properties']['type']]['records'].append(feature)      

    shapefiles_for_export = []
    for feature_class, data in resource_export_groups.iteritems():
        geom_type = data['schema']['geometry']

        if len(data['records']) > 0:
            if geom_type == 'Point':
                writer = shapefile.Writer(shapeType=shapefile.MULTIPOINT)
            elif geom_type == 'LineString':
                writer = shapefile.Writer(shapeType=shapefile.POLYLINE)
            elif geom_type == 'Polygon':
                writer = shapefile.Writer(shapeType=shapefile.POLYGON)

            geos_datatypes_to_pyshp_types = {'str':'C', 'datetime':'D', 'float':'F'}

            for k, v in data["schema"]["properties"].iteritems():
                writer.field(codecs.encode(k), geos_datatypes_to_pyshp_types[v])

            for r in data['records']:
                shp_geom = geos_to_pyshp.convert_geom(r['geometry'])
                if geom_type in ['Point','LineString']:
                    writer.line(parts=shp_geom)
                elif geom_type == 'Polygon':
                    writer.poly(parts=shp_geom)
                writer.record(**r['properties'])

            export_file_name = os.path.join(settings.PACKAGE_ROOT, 'tmp', data['export_file_name'], data['export_file_name'])
            writer.save(export_file_name)
            shapefiles_for_export.append(export_file_name)

    resp = zip_response(shapefiles_for_export, zip_file_name='search_result_shapefile_export.zip')
    return resp


def create_csvs(feature_collection):
    '''
    Groups data by resource type as defined in the arches_export_file and creates a csv file for each resource type. 
    Returns a .zip file with each of the csv files. An arches export configuration file is needed to map shapefile
    fields to resorce entitytypeids. 

    '''

    resource_export_groups = read_export_configs()

    for feature in feature_collection['features']:
        resource_export_groups[feature['properties']['type']]['records'].append(feature)   

    csvs_for_export = []
    for feature_class, data in resource_export_groups.iteritems():
        if len(data['records']) > 0:
            if not os.path.exists(os.path.join(settings.PACKAGE_ROOT, 'tmp')):
                os.makedirs(os.path.join(settings.PACKAGE_ROOT, 'tmp'))
            csv_name = os.path.join(settings.PACKAGE_ROOT, 'tmp', data['export_file_name'])
            csvs_for_export.append(csv_name)
            with open(csv_name + '.csv', 'w') as dest:
                fieldnames = data['schema']['properties'].keys()
                csvwriter = csv.DictWriter(dest, delimiter='|', fieldnames=fieldnames)
                csvwriter.writeheader()
                for record in data['records']:
                    csvwriter.writerow(record['properties'])

    response = zip_response(csvs_for_export, zip_file_name='search_result_csv_export.zip', file_type='.csv')
    return response

    #Do not delete for now - This was written to support building flat records from search results
    # for project in projects:
    #     project_record = {'id': project['properties']['projectid'], 'project':project, 'documents': []}
    #     for document in documents:
    #         if document['properties']['projectid'] == project_record['id']:
    #             document_record = {'id': document['properties']['documentid'], 'document':document, 'mitigations': []}
    #             for mitigation in mitigations:
    #                 if mitigation['properties']['documentid'] == document_record['id']:
    #                     document_record['mitigations'].append(mitigation)
    #             project_record['documents'].append(document_record)
    #     project_records.append(project_record)
    
def read_export_configs():
    '''
    Reads the export configuration file and adds an array for records to store property data

    '''

    resource_export_groups = json.load(open(settings.EXPORT_CONFIG, 'r'))
    for key, val in resource_export_groups.iteritems():
        resource_export_groups[key]['records'] = []

    return resource_export_groups


def zip_response(files_for_export, zip_file_name=None, file_type=None):
    '''
    Given a list of export file names, zips up all the files with those names and returns and http response.

    '''

    d = datetime.now()
    timestamp = '{0}{1}{2}_{3}{4}'.format(d.year, d.month, d.day, d.hour, d.minute) #Should we append the timestamp to the exported filename?

    buffer = StringIO()
    zip = zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED)

    for filename in files_for_export:
        if file_type:
            for f in glob.glob(filename + '*' + file_type):
                zip.write(f, os.path.basename(f))
        else:
            for f in glob.glob(filename + '*'):
                zip.write(f, os.path.basename(f))

    zip.close()
    buffer.flush()
    zip_stream = buffer.getvalue()
    buffer.close()

    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=' + zip_file_name
    response['Content-length'] = str(len(zip_stream))
    response['Content-Type'] = 'application/zip'
    response.write(zip_stream)
    return response
