import uuid
import json
import decimal
import distutils
import base64
import re
from datetime import datetime
from mimetypes import MimeTypes
from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.date_utils import ExtendedDateFormat
from arches.app.utils.module_importer import get_class_from_modulename
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Range, Term, Exists, RangeDSLException
from arches.app.search.search_engine_factory import SearchEngineFactory
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import GeometryCollection
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from elasticsearch import Elasticsearch
from edtf import parse_edtf

# One benefit of shifting to python3.x would be to use
# importlib.util.LazyLoader to load rdflib (and other lesser
# used but memory soaking libs)
from rdflib import Namespace, URIRef, Literal, BNode
from rdflib import ConjunctiveGraph as Graph
from rdflib.namespace import RDF, RDFS, XSD, DC, DCTERMS
archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
cidoc_nm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")

EARTHCIRCUM = 40075016.6856
PIXELSPERTILE = 256


class DataTypeFactory(object):
    def __init__(self):
        self.datatypes = {datatype.datatype:datatype for datatype in models.DDataType.objects.all()}
        self.datatype_instances = {}

    def get_instance(self, datatype):
        d_datatype = self.datatypes[datatype]
        try:
            datatype_instance = self.datatype_instances[d_datatype.classname]
        except:
            class_method = get_class_from_modulename(d_datatype.modulename, d_datatype.classname, settings.DATATYPE_LOCATIONS)
            datatype_instance = class_method(d_datatype)
            self.datatype_instances[d_datatype.classname] = datatype_instance
        return datatype_instance


class StringDataType(BaseDataType):

    def validate(self, value, row_number=None, source=None):
        errors = []
        try:
            if value is not None:
                value.upper()
        except:
            errors.append({
                'type': 'ERROR',
                'message': 'datatype: {0} value: {1} {2} {3} - {4}. {5}'.format(
                    self.datatype_model.datatype,
                    value,
                    source,
                    row_number,
                    'this is not a string',
                    'This data was not imported.'
                )
            })
        return errors

    def clean(self, tile, nodeid):
        if tile.data[nodeid] in ['', "''"]:
            tile.data[nodeid] = None

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        val = {'string': nodevalue, 'nodegroup_id': tile.nodegroup_id, 'provisional': provisional}
        document['strings'].append(val)

    def transform_export_values(self, value, *args, **kwargs):
        if value != None:
            return value.encode('utf8')

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        if nodevalue is not None:
            if settings.WORDS_PER_SEARCH_TERM == None or (len(nodevalue.split(' ')) < settings.WORDS_PER_SEARCH_TERM):
                terms.append(nodevalue)
        return terms

    def append_search_filters(self, value, node, query, request):
        try:
            if value['val'] != '':
                match_type = 'phrase_prefix' if '~' in value['op'] else 'phrase'
                match_query = Match(field='tiles.data.%s' % (str(node.pk)), query=value['val'], type=match_type)
                if '!' in value['op']:
                    query.must_not(match_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(match_query)
        except KeyError, e:
            pass

    def is_a_literal_in_rdf(self):
        return True

    def to_rdf(self, edge_info, edge):
        # returns an in-memory graph object, containing the domain resource, its
        # type and the string as a string literal
        g = Graph()
        if edge_info['range_tile_data'] is not None:
            g.add((edge_info['d_uri'], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add((edge_info['d_uri'], URIRef(edge.ontologyproperty), Literal(edge_info['range_tile_data'])))
        return g

    def from_rdf(self, json_ld_node):
        # returns the string value only
        # FIXME: Language?
        value = get_value_from_jsonld(json_ld_node)
        try:
            return value[0]
        except (AttributeError, KeyError) as e:
            pass


class NumberDataType(BaseDataType):

    def validate(self, value, row_number=None, source=''):
        errors = []

        try:
            if value is not None:
                decimal.Decimal(value)
        except Exception as e:
            dt = self.datatype_model.datatype
            errors.append({
                'type': 'ERROR',
                'message': 'datatype: {0}, value: {1} {2} {3} - {4}. {5}'.format(
                                                                                dt,
                                                                                value,
                                                                                source,
                                                                                row_number,
                                                                                'not a properly formatted number',
                                                                                'This data was not saved.')
                                                                                })
        return errors

    def transform_import_values(self, value, nodeid):
        return float(value)

    def clean(self, tile, nodeid):
        try:
            tile.data[nodeid].upper()
            tile.data[nodeid] = float(tile.data[nodeid])
        except:
            pass

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        document['numbers'].append({'number': nodevalue, 'nodegroup_id': tile.nodegroup_id, 'provisional': provisional})

    def append_search_filters(self, value, node, query, request):
        try:
            if value['val'] != '':
                if value['op'] != 'eq':
                    operators = {'gte': None, 'lte': None, 'lt': None, 'gt': None}
                    operators[value['op']] = value['val']
                    search_query = Range(field='tiles.data.%s' % (str(node.pk)), **operators)
                else:
                    search_query = Match(field='tiles.data.%s' % (str(node.pk)), query=value['val'], type='phrase_prefix')
                query.must(search_query)
        except KeyError, e:
            pass

    def is_a_literal_in_rdf(self):
        return True

    def to_rdf(self, edge_info, edge):
        # returns an in-memory graph object, containing the domain resource, its
        # type and the number as a numeric literal (as this is how it is in the JSON)
        g = Graph()
        rtd = int(edge_info['range_tile_data']) if type(edge_info['range_tile_data']) == float and edge_info['range_tile_data'].is_integer() else edge_info['range_tile_data']
        if rtd is not None:
            g.add((edge_info['d_uri'], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add((edge_info['d_uri'], URIRef(edge.ontologyproperty), Literal(rtd)))
        return g

    def from_rdf(self, json_ld_node):
        # expects a node taken from an expanded json-ld graph
        # returns the value, or None if no "@value" key is found
        value = get_value_from_jsonld(json_ld_node)
        try:
            return value[0]  # should already be cast as a number in the JSON
        except (AttributeError, KeyError) as e:
            pass


class BooleanDataType(BaseDataType):

    def validate(self, value, row_number=None, source=''):
        errors = []

        try:
            type(bool(distutils.util.strtobool(str(value)))) is True
        except:
            errors.append({
                'type': 'ERROR',
                'message': '{0} is not of type boolean. This data was not imported.'.format(value)
            })

        return errors

    def transform_import_values(self, value, nodeid):
        return bool(distutils.util.strtobool(str(value)))

    def append_search_filters(self, value, node, query, request):
        try:
            if value['val'] != '':
                term = True if value['val'] == 't' else False
                query.must(Term(field='tiles.data.%s' % (str(node.pk)), term=term))
        except KeyError, e:
            pass

    def to_rdf(self, edge_info, edge):
        # returns an in-memory graph object, containing the domain resource, its
        # type and the number as a numeric literal (as this is how it is in the JSON)
        g = Graph()
        if edge_info['range_tile_data'] is not None:
            g.add((edge_info['d_uri'], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add((edge_info['d_uri'], URIRef(edge.ontologyproperty),
                   Literal(edge_info['range_tile_data'])))
        return g

    def is_a_literal_in_rdf(self):
        return True

    def from_rdf(self, json_ld_node):
        # expects a node taken from an expanded json-ld graph
        # returns the value, or None if no "@value" key is found
        value = get_value_from_jsonld(json_ld_node)
        try:
            return value[0]
        except (AttributeError, KeyError) as e:
            pass

class DateDataType(BaseDataType):

    def validate(self, value, row_number=None, source=''):
        errors = []
        if value is not None:
            date_formats = ['-%Y','%Y','%Y-%m-%d','%B-%m-%d','%Y-%m-%d %H:%M:%S']
            valid = False
            for mat in date_formats:
                if valid == False:
                    try:
                        if datetime.strptime(value, mat):
                            valid = True
                    except:
                        valid = False
            if valid == False:
                if hasattr(settings, 'DATE_IMPORT_EXPORT_FORMAT'):
                    date_format = settings.DATE_IMPORT_EXPORT_FORMAT
                else:
                    date_format = date_formats

                errors.append({'type': 'ERROR', 'message': '{0} {1} is not in the correct format, make sure it is in this format: {2} or set the date format in settings.DATE_IMPORT_EXPORT_FORMAT. This data was not imported.'.format(value, row_number, date_format)})

        return errors

    def transform_import_values(self, value, nodeid):
        if type(value) == list:
            value = value[0]

        try:
            if hasattr(settings, 'DATE_IMPORT_EXPORT_FORMAT'):
                v = datetime.strptime(str(value), settings.DATE_IMPORT_EXPORT_FORMAT)
                value = str(datetime.strftime(v, '%Y-%m-%d'))
            else:
                value = str(datetime(value).date())
        except:
            pass

        return value

    def transform_export_values(self, value, *args, **kwargs):
        if hasattr(settings, 'DATE_IMPORT_EXPORT_FORMAT'):
            v = datetime.strptime(value, '%Y-%m-%d')
            value = datetime.strftime(v, settings.DATE_IMPORT_EXPORT_FORMAT)
        return value

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        document['dates'].append({'date': ExtendedDateFormat(nodevalue).lower, 'nodegroup_id': tile.nodegroup_id, 'nodeid': nodeid, 'provisional': provisional})

    def append_search_filters(self, value, node, query, request):
        try:
            if value['val'] != '' and value['val'] is not None:
                date_value = datetime.strptime(value['val'], '%Y-%m-%d').isoformat()
                if value['op'] != 'eq':
                    operators = {'gte': None, 'lte': None, 'lt': None, 'gt': None}
                    operators[value['op']] = date_value
                    search_query = Range(field='tiles.data.%s' % (str(node.pk)), **operators)
                else:
                    search_query = Match(field='tiles.data.%s' % (str(node.pk)), query=date_value, type='phrase_prefix')
                query.must(search_query)
        except KeyError, e:
            pass

    def after_update_all(self):
        config = cache.get('time_wheel_config_anonymous')
        if config is not None:
            cache.delete('time_wheel_config_anonymous')

    def is_a_literal_in_rdf(self):
        return True

    def to_rdf(self, edge_info, edge):
        # returns an in-memory graph object, containing the domain resource, its
        # type and the number as a numeric literal (as this is how it is in the JSON)
        g = Graph()
        if edge_info['range_tile_data'] is not None:
            g.add((edge_info['d_uri'], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add((edge_info['d_uri'], URIRef(edge.ontologyproperty),
                   Literal(edge_info['range_tile_data'], datatype=XSD.dateTime)))
        return g

    def from_rdf(self, json_ld_node):
        # expects a node taken from an expanded json-ld graph
        # returns the value, or None if no "@value" key is found
        value = get_value_from_jsonld(json_ld_node)
        try:
            return value[0]
        except (AttributeError, KeyError) as e:
            pass


class EDTFDataType(BaseDataType):

    def validate(self, value, row_number=None, source=''):
        errors = []
        if not ExtendedDateFormat(value).is_valid():
            errors.append({'type': 'ERROR', 'message': '{0} {1} is not in the correct Extended Date Time Format, see http://www.loc.gov/standards/datetime/ for supported formats. This data was not imported.'.format(value, row_number)})

        return errors

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        def add_date_to_doc(document, edtf):
            if edtf.lower == edtf.upper:
                if edtf.lower is not None:
                    document['dates'].append({'date': edtf.lower, 'nodegroup_id': tile.nodegroup_id, 'nodeid': nodeid, 'provisional': provisional})
            else:
                dr = {}
                if edtf.lower_fuzzy is not None:
                    dr['gte'] = edtf.lower_fuzzy
                    document['dates'].append({'date': edtf.lower_fuzzy, 'nodegroup_id': tile.nodegroup_id, 'nodeid': nodeid, 'provisional': provisional})
                if edtf.upper_fuzzy is not None:
                    dr['lte'] = edtf.upper_fuzzy
                    document['dates'].append({'date': edtf.upper_fuzzy, 'nodegroup_id': tile.nodegroup_id, 'nodeid': nodeid, 'provisional': provisional})
                document['date_ranges'].append({'date_range': dr, 'nodegroup_id': tile.nodegroup_id, 'nodeid': nodeid, 'provisional': provisional})

        # update the indexed tile value to support adv. search
        tile.data[nodeid] = {
            'value': nodevalue,
            'dates': [],
            'date_ranges': []
        }

        node = models.Node.objects.get(nodeid=nodeid)
        edtf = ExtendedDateFormat(nodevalue, **node.config)
        if edtf.result_set:
            for result in edtf.result_set:
                add_date_to_doc(document, result)
                add_date_to_doc(tile.data[nodeid], result)
        else:
            add_date_to_doc(document, edtf)
            add_date_to_doc(tile.data[nodeid], edtf)

    def append_search_filters(self, value, node, query, request):
        def add_date_to_doc(query, edtf):
            if value['op'] == 'eq':
                if edtf.lower != edtf.upper:
                    raise Exception(_('Only dates that specify an exact year, month, and day can be used with the "=" operator'))
                query.should(Match(field='tiles.data.%s.dates.date' % (str(node.pk)), query=edtf.lower, type='phrase_prefix'))
            else:
                if value['op'] == 'overlaps':
                    operators = {'gte': edtf.lower, 'lte': edtf.upper}
                else:
                    if edtf.lower != edtf.upper:
                        raise Exception(_('Only dates that specify an exact year, month, and day can be used with the ">", "<", ">=", and "<=" operators'))

                    operators = {
                        value['op']: edtf.lower or edtf.upper
                    }

                try:
                    query.should(Range(field='tiles.data.%s.dates.date' % (str(node.pk)), **operators))
                    query.should(Range(field='tiles.data.%s.date_ranges.date_range' % (str(node.pk)), relation='intersects', **operators))
                except RangeDSLException:
                    if edtf.lower == None and edtf.upper == None:
                        raise Exception(_('Invalid date specified.'))

        edtf = ExtendedDateFormat(value['val'])
        if edtf.result_set:
            for result in edtf.result_set:
                add_date_to_doc(query, result)
        else:
            add_date_to_doc(query, edtf)


class GeojsonFeatureCollectionDataType(BaseDataType):

    def validate(self, value, row_number=None, source=None):
        errors = []
        coord_limit = 1500
        coordinate_count = 0
        def validate_geom(geom, coordinate_count=0):
            try:
                coordinate_count += geom.num_coords
                bbox = Polygon(settings.DATA_VALIDATION_BBOX)
                if coordinate_count > coord_limit:
                    message = 'Geometry has too many coordinates for Elasticsearch ({0}), Please limit to less then {1} coordinates of 5 digits of precision or less.'.format(coordinate_count, coord_limit)
                    errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}. {4}'.format(self.datatype_model.datatype, value, source, message, 'This data was not imported.')})

                if bbox.contains(geom) == False:
                    message = 'Geometry does not fall within the bounding box of the selected coordinate system. Adjust your coordinates or your settings.DATA_EXTENT_VALIDATION property.'
                    errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}. {4}'.format(self.datatype_model.datatype, value, source, message, 'This data was not imported.')})
            except:
                message = 'Not a properly formatted geometry'
                errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}. {4}.'.format(self.datatype_model.datatype, value, source, message, 'This data was not imported.')})

        if value is not None:
            for feature in value['features']:
                try:
                    geom = GEOSGeometry(JSONSerializer().serialize(feature['geometry']))
                    validate_geom(geom, coordinate_count)
                except:
                    message = 'It was not possible to serialize some feaures in your geometry.'
                    errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}. {4}'.format(self.datatype_model.datatype, value, source, message, 'This data was not imported.')})

        return errors

    def clean(self, tile, nodeid):
        if tile.data[nodeid] is not None and 'features' in tile.data[nodeid]:
            if len(tile.data[nodeid]['features']) == 0:
                tile.data[nodeid] = None

    def transform_import_values(self, value, nodeid):
        arches_geojson = {}
        arches_geojson['type'] = "FeatureCollection"
        arches_geojson['features'] = []
        geometry = GEOSGeometry(value, srid=4326)
        if geometry.geom_type == 'GeometryCollection':
            for geom in geometry:
                arches_json_geometry = {}
                arches_json_geometry['geometry'] = JSONDeserializer().deserialize(GEOSGeometry(geom, srid=4326).json)
                arches_json_geometry['type'] = "Feature"
                arches_json_geometry['id'] = str(uuid.uuid4())
                arches_json_geometry['properties'] = {}
                arches_geojson['features'].append(arches_json_geometry)
        else:
            arches_json_geometry = {}
            arches_json_geometry['geometry'] = JSONDeserializer().deserialize(geometry.json)
            arches_json_geometry['type'] = "Feature"
            arches_json_geometry['id'] = str(uuid.uuid4())
            arches_json_geometry['properties'] = {}
            arches_geojson['features'].append(arches_json_geometry)

        return arches_geojson

    def transform_export_values(self, value, *args, **kwargs):
        wkt_geoms = []
        for feature in value['features']:
            wkt_geoms.append(GEOSGeometry(json.dumps(feature['geometry'])))
        return GeometryCollection(wkt_geoms)

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        document['geometries'].append({
            'geom': nodevalue,
            'nodegroup_id': tile.nodegroup_id,
            'provisional': provisional,
            'tileid': tile.pk
        })
        bounds = self.get_bounds_from_value(nodevalue)
        if bounds is not None:
            minx, miny, maxx, maxy = bounds
            centerx = maxx - (maxx - minx) / 2
            centery = maxy - (maxy - miny) / 2
            document['points'].append({
                'point': {
                    "lon": centerx,
                    "lat": centery
                },
                'nodegroup_id': tile.nodegroup_id,
                'provisional': provisional
            })

    def get_bounds(self, tile, node):
        bounds = None
        try:
            node_data = tile.data[str(node.pk)]
            bounds = self.get_bounds_from_value(node_data)
        except KeyError as e:
            print e
        return bounds

    def get_bounds_from_value(self, node_data):
        bounds = None
        for feature in node_data['features']:
            geom_collection = GEOSGeometry(JSONSerializer().serialize(feature['geometry']))

            if bounds is None:
                bounds = geom_collection.extent
            else:
                minx, miny, maxx, maxy = bounds
                if geom_collection.extent[0] < minx:
                    minx = geom_collection.extent[0]
                if geom_collection.extent[1] < miny:
                    miny = geom_collection.extent[1]
                if geom_collection.extent[2] > maxx:
                    maxx = geom_collection.extent[2]
                if geom_collection.extent[3] > maxy:
                    maxy = geom_collection.extent[3]

                bounds = (minx, miny, maxx, maxy)

        return bounds

    def get_layer_config(self, node=None):
        sql_list = []
        database = settings.DATABASES['default']
        if node is not None and node.config is not None:
            config = node.config

            cluster_sql = """
                WITH clusters(tileid, resourceinstanceid, nodeid, geom, cid) AS (
                    SELECT m.*, ST_ClusterDBSCAN(geom, eps := %s, minpoints := %s) over () AS cid
                	FROM mv_geojson_geoms m
                    WHERE nodeid = '%s'
                )

                SELECT resourceinstanceid::text,
                		row_number() over () as __id__,
                		1 as total,
                		ST_Centroid(geom) AS __geometry__,
                        '' AS extent
                	FROM clusters
                	WHERE cid is NULL

                UNION

                SELECT NULL as resourceinstanceid,
                		row_number() over () as __id__,
                		count(*) as total,
                		ST_Centroid(
                            ST_Collect(geom)
                        ) AS __geometry__,
                        ST_AsGeoJSON(
                            ST_Transform(
                                ST_SetSRID(
                                    ST_Extent(geom), 900913
                                ), 4326
                            )
                        ) AS extent
                	FROM clusters
                	WHERE cid IS NOT NULL
                	GROUP BY cid
            """

            for i in range(int(config['clusterMaxZoom']) + 1):
                arc = EARTHCIRCUM / ((1 << i) * PIXELSPERTILE)
                distance = arc * int(config['clusterDistance'])
                sql_string = cluster_sql % (distance, int(config['clusterMinPoints']), node.pk)
                sql_list.append(sql_string)

            sql_list.append("""
                SELECT resourceinstanceid::text,
                        tileid::text,
                        (row_number() over ()) as __id__,
                        1 as total,
                        geom AS __geometry__,
                        '' AS extent
                    FROM mv_geojson_geoms
                    WHERE nodeid = '%s'
            """ % node.pk)

        else:
            config = {"cacheTiles": False}
            for i in range(23):
                sql_list.append(None)

        try:
            simplification = config['simplification']
        except KeyError, e:
            simplification = 0.3

        return {
            "provider": {
                "class": "TileStache.Goodies.VecTiles:Provider",
                "kwargs": {
                    "dbinfo": {
                        "host": database["HOST"],
                        "user": database["USER"],
                        "password": database["PASSWORD"],
                        "database": database["NAME"],
                        "port": database["PORT"]
                    },
                    "simplify": simplification,
                    "clip": False,
                    "queries": sql_list
                },
            },
            "allowed origin": "*",
            "compress": True,
            "write cache": config["cacheTiles"]
        }

    def should_cache(self, node=None):
        if node is None:
            return False
        elif node.config is None:
            return False
        return node.config["cacheTiles"]

    def should_manage_cache(self, node=None):
        if node is None:
            return False
        elif node.config is None:
            return False
        return node.config["autoManageCache"]

    def get_map_layer(self, node=None, preview=False):
        if node is None:
            return None
        elif node.config is None:
            return None
        count = models.TileModel.objects.filter(data__has_key=str(node.nodeid)).count()
        if not preview and (count < 1 or not node.config["layerActivated"]):
            return None

        source_name = "resources-%s" % node.nodeid
        layer_name = "%s - %s" % (node.graph.name, node.name)
        if not preview and node.config["layerName"] != "":
            layer_name = node.config["layerName"]
        layer_icon = node.graph.iconclass
        if not preview and node.config["layerIcon"] != "":
            layer_icon = node.config["layerIcon"]

        layer_legend = node.config["layerLegend"]

        if not preview and node.config["advancedStyling"]:
            try:
                style = json.loads(node.config["advancedStyle"])
                for layer in style:
                    layer["source-layer"] = str(node.pk)
                layer_def = json.dumps(style)
            except ValueError:
                layer_def = "[]"
        else:
            layer_def = """[
                {
                    "id": "resources-fill-%(nodeid)s",
                    "type": "fill",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Polygon"],["==", "total", 1]],
                    "paint": {
                        "fill-color": "%(fillColor)s"
                    }
                },
                {
                    "id": "resources-fill-%(nodeid)s-click",
                    "type": "fill",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Polygon"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "fill-color": "%(fillColor)s"
                    }
                },
                {
                    "id": "resources-fill-%(nodeid)s-hover",
                    "type": "fill",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Polygon"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "fill-color": "%(fillColor)s"
                    }
                },
                {
                    "id": "resources-poly-outline-%(nodeid)s",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all",["==", "$type", "Polygon"],["==", "total", 1]],
                    "paint": {
                        "line-width": ["case",
                            ["boolean", ["feature-state", "hover"], false],
                            %(expanded_outlineWeight)s,
                            %(outlineWeight)s
                        ],
                        "line-color": "%(outlineColor)s"
                    }
                },
                {
                    "id": "resources-poly-outline-%(nodeid)s-hover",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all",["==", "$type", "Polygon"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "line-width": %(expanded_outlineWeight)s,
                        "line-color": "%(outlineColor)s"
                    }
                },
                {
                    "id": "resources-poly-outline-%(nodeid)s-click",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all",["==", "$type", "Polygon"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "line-width": %(expanded_outlineWeight)s,
                        "line-color": "%(outlineColor)s"
                    }
                },
                {
                    "id": "resources-line-halo-%(nodeid)s",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "LineString"],["==", "total", 1]],
                    "paint": {
                        "line-width": ["case",
                            ["boolean", ["feature-state", "hover"], false],
                            %(expanded_haloWeight)s,
                            %(haloWeight)s
                        ],
                        "line-color": "%(lineHaloColor)s"
                    }
                },
                {
                    "id": "resources-line-%(nodeid)s",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all",["==", "$type", "LineString"],["==", "total", 1]],
                    "paint": {
                        "line-width": ["case",
                            ["boolean", ["feature-state", "hover"], false],
                            %(expanded_weight)s,
                            %(weight)s
                        ],
                        "line-color": "%(lineColor)s"
                    }
                },
                {
                    "id": "resources-line-halo-%(nodeid)s-hover",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all",["==", "$type", "LineString"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "line-width": %(expanded_haloWeight)s,
                        "line-color": "%(lineHaloColor)s"
                    }
                },
                {
                    "id": "resources-line-%(nodeid)s-hover",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all",["==", "$type", "LineString"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "line-width": %(expanded_weight)s,
                        "line-color": "%(lineColor)s"
                    }
                },
                {
                    "id": "resources-line-halo-%(nodeid)s-click",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "LineString"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "line-width": %(expanded_haloWeight)s,
                        "line-color": "%(lineHaloColor)s"
                    }
                },
                {
                    "id": "resources-line-%(nodeid)s-click",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "LineString"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "line-width": %(expanded_weight)s,
                        "line-color": "%(lineColor)s"
                    }
                },

                {
                    "id": "resources-point-halo-%(nodeid)s-hover",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "circle-radius": %(expanded_haloRadius)s,
                        "circle-color": "%(pointHaloColor)s"
                    }
                },
                {
                    "id": "resources-point-%(nodeid)s-hover",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "circle-radius": %(expanded_radius)s,
                        "circle-color": "%(pointColor)s"
                    }
                },

                {
                    "id": "resources-point-halo-%(nodeid)s",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],["==", "total", 1]],
                    "paint": {
                        "circle-radius": ["case",
                            ["boolean", ["feature-state", "hover"], false],
                            %(expanded_haloRadius)s,
                            %(haloRadius)s
                        ],
                        "circle-color": "%(pointHaloColor)s"
                    }
                },
                {
                    "id": "resources-point-%(nodeid)s",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],["==", "total", 1]],
                    "paint": {
                        "circle-radius": ["case",
                            ["boolean", ["feature-state", "hover"], false],
                            %(expanded_radius)s,
                            %(radius)s
                        ],
                        "circle-color": "%(pointColor)s"
                    }
                },

                {
                    "id": "resources-point-halo-%(nodeid)s-click",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "circle-radius": %(expanded_haloRadius)s,
                        "circle-color": "%(pointHaloColor)s"
                    }
                },
                {
                    "id": "resources-point-%(nodeid)s-click",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],["==", "total", 1],["==", "resourceinstanceid", ""]],
                    "paint": {
                        "circle-radius": %(expanded_radius)s,
                        "circle-color": "%(pointColor)s"
                    }
                },
                {
                    "id": "resources-cluster-point-halo-%(nodeid)s",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],[">", "total", 1]],
                    "paint": {
                        "circle-radius": {
                            "property": "total",
                            "stops": [
                                [0,   22],
                                [50, 24],
                                [100, 26],
                                [200, 28],
                                [400, 30],
                                [800, 32],
                                [1200, 34],
                                [1600, 36],
                                [2000, 38],
                                [2500, 40],
                                [3000, 42],
                                [4000, 44],
                                [5000, 46]
                            ]
                        },
                        "circle-color": "%(pointHaloColor)s"
                    }
                },
                {
                    "id": "resources-cluster-point-%(nodeid)s",
                    "type": "circle",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "Point"],[">", "total", 1]],
                    "paint": {
                         "circle-radius": {
                             "property": "total",
                             "type": "exponential",
                             "stops": [
                                 [0,   12],
                                 [50, 14],
                                 [100, 16],
                                 [200, 18],
                                 [400, 20],
                                 [800, 22],
                                 [1200, 24],
                                 [1600, 26],
                                 [2000, 28],
                                 [2500, 30],
                                 [3000, 32],
                                 [4000, 34],
                                 [5000, 36]
                             ]
                         },
                        "circle-color": "%(pointColor)s"
                    }
                },
                {
                     "id": "resources-cluster-count-%(nodeid)s",
                     "type": "symbol",
                     "source": "%(source_name)s",
                     "source-layer": "%(nodeid)s",
                     "layout": {
                         "text-field": "{total}",
                         "text-size": 10
                     },
                     "paint": {
                        "text-color": "#fff"
                    },
                     "filter": ["all", [">", "total", 1]]
                 }
            ]""" % {
                "source_name": source_name,
                "nodeid": node.nodeid,
                "pointColor": node.config["pointColor"],
                "pointHaloColor": node.config["pointHaloColor"],
                "radius": node.config["radius"],
                "expanded_radius": int(node.config["radius"])*2,
                "haloRadius": node.config["haloRadius"],
                "expanded_haloRadius": int(node.config["haloRadius"])*2,
                "lineColor": node.config["lineColor"],
                "lineHaloColor": node.config["lineHaloColor"],
                "weight": node.config["weight"],
                "haloWeight": node.config["haloWeight"],
                "expanded_weight": int(node.config["weight"])*2,
                "expanded_haloWeight": int(node.config["haloWeight"])*2,
                "fillColor": node.config["fillColor"],
                "outlineColor": node.config["outlineColor"],
                "outlineWeight": node.config["outlineWeight"],
                "expanded_outlineWeight": int(node.config["outlineWeight"])*2,
            }
        return {
            "nodeid": node.nodeid,
            "name": layer_name,
            "layer_definitions": layer_def,
            "icon": layer_icon,
            "legend": layer_legend,
            "addtomap": node.config['addToMap'],
        }

    def after_update_all(self):
        cursor = connection.cursor()
        sql = """
            REFRESH MATERIALIZED VIEW mv_geojson_geoms;
        """
        cursor.execute(sql)


class FileListDataType(BaseDataType):

    def get_tile_data(self, user_is_reviewer, user_id, tile):
        if user_is_reviewer is False and tile.provisionaledits is not None and user_id in tile.provisionaledits:
            data = tile.provisionaledits[user_id]['value']
        else:
            data = tile.data
        return data

    def handle_request(self, current_tile, request, node):
        previously_saved_tile = models.TileModel.objects.filter(pk=current_tile.tileid)
        user = request.user
        if hasattr(request.user, 'userprofile') is not True:
            models.UserProfile.objects.create(user=request.user)
        user_is_reviewer = request.user.userprofile.is_reviewer()
        current_tile_data = self.get_tile_data(user_is_reviewer, str(user.id), current_tile)
        if previously_saved_tile.count() == 1:
            previously_saved_tile_data = self.get_tile_data(user_is_reviewer, str(user.id), previously_saved_tile[0])
            if previously_saved_tile_data[str(node.pk)] is not None:
                for previously_saved_file in previously_saved_tile_data[str(node.pk)]:
                    previously_saved_file_has_been_removed = True
                    for incoming_file in current_tile_data[str(node.pk)]:
                        if previously_saved_file['file_id'] == incoming_file['file_id']:
                            previously_saved_file_has_been_removed = False
                    if previously_saved_file_has_been_removed:
                        try:
                            deleted_file = models.File.objects.get(pk=previously_saved_file["file_id"])
                            deleted_file.delete()
                        except models.File.DoesNotExist:
                            print 'file does not exist'

        files = request.FILES.getlist('file-list_' + str(node.pk), [])

        for file_data in files:
            file_model = models.File()
            file_model.path = file_data
            file_model.tile = current_tile
            if models.TileModel.objects.filter(pk=current_tile.tileid).count() > 0:
                file_model.save()
            if current_tile_data[str(node.pk)] is not None:
                resave_tile = False
                updated_file_records = []
                for file_json in current_tile_data[str(node.pk)]:
                    if file_json["name"] == file_data.name and file_json["url"] is None:
                        file_json["file_id"] = str(file_model.pk)
                        file_json["url"] = str(file_model.path.url)
                        file_json["status"] = 'uploaded'
                        resave_tile = True
                    updated_file_records.append(file_json)
                if resave_tile is True:
                    # resaving model to assign url from file_model
                    # importing proxy model errors, so cannot use super on the proxy model to save
                    if previously_saved_tile.count() == 1:
                        tile_to_update = previously_saved_tile[0]
                        if user_is_reviewer:
                            tile_to_update.data[str(node.pk)] = updated_file_records
                        else:
                            tile_to_update.provisionaledits[str(user.id)]['value'][str(node.pk)] = updated_file_records
                        tile_to_update.save()

    def transform_import_values(self, value, nodeid):
        '''
        # TODO: Following commented code can be used if user does not already have file in final location using django ORM:

        request = HttpRequest()
        # request.FILES['file-list_' + str(nodeid)] = None
        files = []
        # request_list = []

        for val in value.split(','):
            val_dict = {}
            val_dict['content'] = val
            val_dict['name'] = val.split('/')[-1].split('.')[0]
            val_dict['url'] = None
            # val_dict['size'] = None
            # val_dict['width'] = None
            # val_dict['height'] = None
            files.append(val_dict)
            f = open(val, 'rb')
            django_file = InMemoryUploadedFile(f,'file',val.split('/')[-1].split('.')[0],None,None,None)
            request.FILES.appendlist('file-list_' + str(nodeid), django_file)
        print request.FILES
        value = files
        '''

        mime = MimeTypes()
        tile_data = []
        for file_path in value.split(','):
            try:
                file_stats = os.stat(file_path)
                tile_file['lastModified'] = file_stats.st_mtime
                tile_file['size'] =  file_stats.st_size
            except:
                pass
            tile_file = {}
            tile_file['file_id'] =  str(uuid.uuid4())
            tile_file['status'] = ""
            tile_file['name'] =  file_path.split('/')[-1]
            tile_file['url'] =  settings.MEDIA_URL + 'uploadedfiles/' + str(tile_file['name'])
            # tile_file['index'] =  0
            # tile_file['height'] =  960
            # tile_file['content'] =  None
            # tile_file['width'] =  1280
            # tile_file['accepted'] =  True
            tile_file['type'] =  mime.guess_type(file_path)[0]
            tile_file['type'] = '' if tile_file['type'] == None else tile_file['type']
            tile_data.append(tile_file)
            file_path = 'uploadedfiles/' + str(tile_file['name'])
            fileid = tile_file['file_id']
            models.File.objects.get_or_create(fileid=fileid, path=file_path)

        result = json.loads(json.dumps(tile_data))
        return result

    def to_rdf(self, edge_info, edge):
        # outputs a graph holding an RDF representation of the file stored in the Arches instance

        g = Graph()

        unit_nt = """
        <http://vocab.getty.edu/aat/300055644> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.cidoc-crm.org/cidoc-crm/E55_Type> .
        <http://vocab.getty.edu/aat/300055644> <http://www.w3.org/2000/01/rdf-schema#label> "height" .
        <http://vocab.getty.edu/aat/300055647> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.cidoc-crm.org/cidoc-crm/E55_Type> .
        <http://vocab.getty.edu/aat/300055647> <http://www.w3.org/2000/01/rdf-schema#label> "width" .
        <http://vocab.getty.edu/aat/300265863> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.cidoc-crm.org/cidoc-crm/E55_Type> .
        <http://vocab.getty.edu/aat/300265863> <http://www.w3.org/2000/01/rdf-schema#label> "file size" .
        <http://vocab.getty.edu/aat/300265869> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.cidoc-crm.org/cidoc-crm/E58_Measurement_Unit> .
        <http://vocab.getty.edu/aat/300265869> <http://www.w3.org/2000/01/rdf-schema#label> "bytes" .
        <http://vocab.getty.edu/aat/300266190> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.cidoc-crm.org/cidoc-crm/E58_Measurement_Unit> .
        <http://vocab.getty.edu/aat/300266190> <http://www.w3.org/2000/01/rdf-schema#label> "pixels" .
        """

        g.parse(data=unit_nt, format="nt")

        aatrefs = {'pixels': URIRef("http://vocab.getty.edu/aat/300266190"),
                   'bytes': URIRef("http://vocab.getty.edu/aat/300265869"),
                   'height': URIRef("http://vocab.getty.edu/aat/300055644"),
                   'width': URIRef("http://vocab.getty.edu/aat/300055647"),
                   'file size': URIRef("http://vocab.getty.edu/aat/300265863"), }

        def add_dimension(graphobj, domain_uri, unittype, unit, value):
            dim_node = BNode()
            graphobj.add((domain_uri, cidoc["P43_has_dimension"], dim_node))
            graphobj.add((dim_node, RDF.type, cidoc["E54_Dimension"]))
            graphobj.add((dim_node, cidoc["P2_has_type"], aatrefs[unittype]))
            graphobj.add((dim_node, cidoc["P91_has_unit"], aatrefs[unit]))
            graphobj.add((dim_node, RDF.value, Literal(value)))

        for f_data in edge_info['range_tile_data']:
            # f_data will be something like:
            # "{\"accepted\": true, \"content\": \"blob:http://localhost/cccadfd0-64fc-104a-8157-3c96aca0b9bd\",
            # \"file_id\": \"f4cd6596-cd75-11e8-85e0-0242ac1b0003\", \"height\": 307, \"index\": 0,
            # \"lastModified\": 1535067185606, \"name\": \"FUjJqP6.jpg\", \"size\": 19350,
            # \"status\": \"uploaded\", \"type\": \"image/jpeg\", \"url\": \"/files/uploadedfiles/FUjJqP6.jpg\",
            # \"width\": 503}"

            # range URI should be the file URL/URI, and the rest of the details should hang off that
            # FIXME - (Poor) assumption that file is on same host as Arches instance host config.
            if f_data['url'].startswith("/"):
                f_uri = URIRef(archesproject[f_data['url'][1:]])
            else:
                f_uri = URIRef(archesproject[f_data['url']])
            g.add((edge_info['d_uri'], URIRef(edge.ontologyproperty), f_uri))
            g.add((f_uri, RDF.type, URIRef(edge.rangenode.ontologyclass)))
            g.add((f_uri, DC['format'], Literal(f_data['type'])))
            g.add((f_uri, RDFS.label, Literal(f_data['name'])))

            # FIXME - improve this ms in timestamp handling code in case of odd OS environments
            # FIXME - Use the timezone settings for export?
            if f_data['lastModified']:
                lm = f_data['lastModified']
                if lm > 9999999999:   # not a straight timestamp, but includes milliseconds
                    lm = f_data['lastModified'] / 1000
                graph.add((f_uri, DCTERMS.modified, Literal(datetime.utcfromtimestamp(lm).isoformat())))

            if 'size' in f_data:
                add_dimension(graph, f_uri, "file size", "bytes", f_data['size'])
            if 'height' in f_data:
                add_dimension(graph, f_uri, "height", "pixels", f_data['height'])
            if 'width' in f_data:
                add_dimension(graph, f_uri, "width", "pixels", f_data['width'])

        return g

    def from_rdf(self, json_ld_node):
        # Currently up in the air about how best to do file imports via JSON-LD
        pass

    def process_mobile_data(self, tile, node, db, couch_doc, node_value):
        '''
        Takes a tile, couch db instance, couch record, and the node value from
        a provisional edit. Creates a django instance, saves the corresponding
        attachement as a file, updates the provisional edit value with the
        file location information and returns the revised provisional edit value
        '''

        try:
            for file in node_value:
                attachment = db.get_attachment(couch_doc['_id'], file['file_id'])
                if attachment is not None:
                    attachment_file = attachment.read()
                    file_data = ContentFile(attachment_file, name=file['name'])
                    file_model = models.File()
                    file_model.path = file_data
                    file_model.pk = file['file_id']
                    file_model.save()
                    if file["name"] == file_data.name and 'url' not in list(file.keys()):
                        file["file_id"] = str(file_model.pk)
                        file["url"] = str(file_model.path.url)
                        file["status"] = 'uploaded'
                        file["accepted"] = True
                        file["size"] = file_data.size
                    # db.delete_attachment(couch_doc, file['name'])

        except KeyError as e:
            pass
        return node_value


class BaseDomainDataType(BaseDataType):
    def get_option_text(self, node, option_id):
        for option in node.config['options']:
            if option['id'] == option_id:
                return option['text']
        return ''

    def get_option_id_from_text(self, value):
        # this could be better written with most of the logic in SQL tbh
        for dnode in models.Node.objects.filter(config__options__contains=[{"text": value}]):
            for option in dnode.config['options']:
                if option['text'] == value:
                    yield option['id'], dnode.node_id


class DomainDataType(BaseDomainDataType):

    def validate(self, value, row_number=None, source=''):
        errors = []
        if value is not None:
            if len(models.Node.objects.filter(config__options__contains=[{"id": value}])) < 1:
                errors.append({'type': 'ERROR', 'message': '{0} {1} is not a valid domain id. Please check the node this value is mapped to for a list of valid domain ids. This data was not imported.'.format(value, row_number)})
        return errors

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        node = models.Node.objects.get(nodeid=nodeid)
        domain_text = self.get_option_text(node, nodevalue)
        if domain_text is not None:
            if settings.WORDS_PER_SEARCH_TERM == None or (len(domain_text.split(' ')) < settings.WORDS_PER_SEARCH_TERM):
                terms.append(domain_text)
        return terms

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        domain_text = None
        for tile in document['tiles']:
            for k, v in tile.data.items():
                if v == nodevalue:
                    node = models.Node.objects.get(nodeid=k)
                    domain_text = self.get_option_text(node, v)

        if domain_text not in document['strings'] and domain_text != None:
            document['strings'].append({'string': domain_text, 'nodegroup_id': tile.nodegroup_id, 'provisional': provisional})

    def get_display_value(self, tile, node):
        data = self.get_tile_data(tile)
        return self.get_option_text(node, data[str(node.nodeid)])

    def transform_export_values(self, value, *args, **kwargs):
        ret = ''
        if kwargs['concept_export_value_type'] == None or kwargs['concept_export_value_type'] == '' or kwargs['concept_export_value_type'] == 'label':
            ret = self.get_option_text(models.Node.objects.get(nodeid=kwargs['node']), value)
        elif kwargs['concept_export_value_type'] == 'both':
            ret = value + '|' + self.get_option_text(models.Node.objects.get(nodeid=kwargs['node']), value)
        elif kwargs['concept_export_value_type'] == 'id':
            ret = value
        return ret

    def append_search_filters(self, value, node, query, request):
        try:
            if value['val'] != '':
                search_query = Match(field='tiles.data.%s' % (str(node.pk)), type="phrase", query=value['val'])
                # search_query = Term(field='tiles.data.%s' % (str(node.pk)), term=str(value['val']))
                if '!' in value['op']:
                    query.must_not(search_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(search_query)

        except KeyError, e:
            pass

    def to_rdf(self, edge_info, edge):
        # returns an in-memory graph object, containing the domain resource, its
        # type and the number as a numeric literal (as this is how it is in the JSON)
        g = Graph()
        if edge_info['range_tile_data'] is not None:
            g.add((edge_info['d_uri'], RDF.type, URIRef(edge.domainnode.ontologyclass)))
            g.add((edge_info['d_uri'], URIRef(edge.ontologyproperty),
                   Literal(self.get_option_text(edge.rangenode, edge_info['range_tile_data']))))
        return g

    def from_rdf(self, json_ld_node):
        # depends on how much is passed to the method
        # if just the 'leaf' node, then not much can be done aside from return the list of nodes it might be from
        # a string may be present in multiple domains for instance
        # via models.Node.objects.filter(config__options__contains=[{"text": value}])
        value = get_value_from_jsonld(json_ld_node)
        try:
            return [{'id': v_id, 'n_id': node_id} for v_id, n_id in self.get_option_id_from_text(value[0])]
        except (AttributeError, KeyError, TypeError) as e:
            print(e)


class DomainListDataType(BaseDomainDataType):
    def validate(self, value, row_number=None, source=''):
        errors = []
        if value is not None:
            for v in value:
                if len(models.Node.objects.filter(config__options__contains=[{"id": v}])) < 1:
                    errors.append({'type': 'ERROR', 'message': '{0} {1} is not a valid domain id. Please check the node this value is mapped to for a list of valid domain ids. This data was not imported.'.format(v, row_number)})
        return errors

    def transform_import_values(self, value, nodeid):
        return [v.strip() for v in value.split(',')]

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        node = models.Node.objects.get(nodeid=nodeid)
        for val in nodevalue:
            domain_text = self.get_option_text(node, val)
            if domain_text is not None:
                if settings.WORDS_PER_SEARCH_TERM == None or (len(domain_text.split(' ')) < settings.WORDS_PER_SEARCH_TERM):
                    terms.append(domain_text)

        return terms

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        domain_text_values = set([])
        for tile in document['tiles']:
            for k, v in tile.data.items():
                if v == nodevalue:
                    node = models.Node.objects.get(nodeid=k)
                    for value in nodevalue:
                        text_value = self.get_option_text(node, value)
                        domain_text_values.add(text_value)

        for value in domain_text_values:
            if value not in document['strings']:
                document['strings'].append({'string': value, 'nodegroup_id': tile.nodegroup_id, 'provisional': provisional})

    def get_display_value(self, tile, node):
        new_values = []
        data = self.get_tile_data(tile)
        if data[str(node.nodeid)] is not None:
            for val in data[str(node.nodeid)]:
                option = self.get_option_text(node, val)
                new_values.append(option)
        return ','.join(new_values)

    def transform_export_values(self, value, *args, **kwargs):
        ret = ''
        if kwargs['concept_export_value_type'] == None or kwargs['concept_export_value_type'] == '' or kwargs['concept_export_value_type'] == 'label':
            ret = self.get_option_text(models.Node.objects.get(nodeid=kwargs['node']), value)
        elif kwargs['concept_export_value_type'] == 'both':
            ret = value + '|' + self.get_option_text(models.Node.objects.get(nodeid=kwargs['node']), value)
        elif kwargs['concept_export_value_type'] == 'id':
            ret = value
        return ret

    def transform_export_values(self, value, *args, **kwargs):
        new_values = []
        for val in value:
            if kwargs['concept_export_value_type'] == None or kwargs['concept_export_value_type'] == '' or kwargs['concept_export_value_type'] == 'label':
                new_values.append(self.get_option_text(models.Node.objects.get(nodeid=kwargs['node']), val))
            elif kwargs['concept_export_value_type'] == 'both':
                new_values.append(val + '|' + self.get_option_text(models.Node.objects.get(nodeid=kwargs['node']), val))
            elif kwargs['concept_export_value_type'] == 'id':
                new_values.append(val)
        return ','.join(new_values)

    def append_search_filters(self, value, node, query, request):
        try:
            if value['val'] != '':
                search_query = Match(field='tiles.data.%s' % (str(node.pk)), type="phrase", query=value['val'])
                # search_query = Term(field='tiles.data.%s' % (str(node.pk)), term=str(value['val']))
                if '!' in value['op']:
                    query.must_not(search_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(search_query)

        except KeyError, e:
            pass

    def to_rdf(self, edge_info, edge):
        g = Graph()
        domtype = DomainDataType()

        for domain_id in edge_info['range_tile_data']:
            indiv_info = edge_info.copy()
            indiv_info['range_tile_data'] = domain_id
            g += domtype.to_rdf(indiv_info, edge)
        return g

    def from_rdf(self, json_ld_node):
        # returns a list of lists of {domain id, node id}
        domtype = DomainDataType()

        return [domtype.from_rdf(item) for item in json_ld_node]



class ResourceInstanceDataType(BaseDataType):
    def get_id_list(self, nodevalue):
        id_list = nodevalue
        if type(nodevalue) is unicode:
            id_list = [nodevalue]
        return id_list

    def get_resource_names(self, nodevalue):
        resource_names = set([])
        if nodevalue is not None:
            se = SearchEngineFactory().create()
            id_list = self.get_id_list(nodevalue)
            for resourceid in id_list:
                try:
                    resource_document = se.search(index='resources', id=resourceid)
                    resource_names.add(resource_document['_source']['displayname'])
                except:
                    print 'resource not available'
        else:
            print 'resource not avalable'
        return resource_names

    def validate(self, value, row_number=None, source=''):
        errors = []

        if value is not None:
            id_list = self.get_id_list(value)
            for resourceid in id_list:
                try:
                    models.ResourceInstance.objects.get(pk=resourceid)
                except:
                    errors.append({'type': 'WARNING', 'message': 'The resource id: {0} does not exist in the system. The data for this card will be available in the system once resource {0} is loaded.'.format(resourceid)})
        return errors

    def get_display_value(self, tile, node):
        data = self.get_tile_data(tile)
        nodevalue = data[str(node.nodeid)]
        resource_names = self.get_resource_names(nodevalue)
        return ', '.join(resource_names)

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        resource_names = self.get_resource_names(nodevalue)
        for value in resource_names:
            document['ids'].append({'id': nodevalue, 'nodegroup_id': tile.nodegroup_id, 'provisional': provisional})
            if value not in document['strings']:
                document['strings'].append({'string': value, 'nodegroup_id': tile.nodegroup_id, 'provisional': provisional})

    def transform_import_values(self, value, nodeid):
        return [v.strip() for v in value.split(',')]

    def transform_export_values(self, value, *args, **kwargs):
        result = value
        try:
            if not isinstance(value, basestring): #change basestring to str in python3
                result = ",".join(value)
        except:
            pass

        return result

    def append_search_filters(self, value, node, query, request):
        try:
            if value['val'] != '':
                search_query = Match(field='tiles.data.%s' % (str(node.pk)), type="phrase", query=value['val'])
                # search_query = Term(field='tiles.data.%s' % (str(node.pk)), term=str(value['val']))
                if '!' in value['op']:
                    query.must_not(search_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(search_query)
        except KeyError, e:
            pass

    def to_rdf(self, edge_info, edge):
        g = Graph()

        def _add_resource(d, p, r, r_type):
            if r_type is not None:
                g.add((r, RDF.type, URIRef(r_type)))
            g.add((d, URIRef(p), r))

        if edge_info['range_tile_data'] is not None:
            res_insts = edge_info['range_tile_data']
            if not isinstance(res_insts, list):
                res_insts = [res_insts]

            for res_inst in res_insts:
                rangenode = URIRef(archesproject['resources/%s' % res_inst])
                # FIXME: should be the class of the Resource Instance, rather than the expected class
                # from the edge.
                _add_resource(edge_info['d_uri'], edge.ontologyproperty,
                              rangenode, edge.rangenode.ontologyclass)
        return g

    def from_rdf(self, json_ld_node):
        res_inst_uri = json_ld_node['@id']
        # `id` should be in the form schema:{...}/{UUID}
        # eg `urn:uuid:{UUID}`
        #    `http://arches_instance.getty.edu/resources/{UUID}`
        p = re.compile(r"(?P<r>[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12})/?$")
        m = p.search(res_inst_uri)
        if m is not None:
            return m.groupdict()['r']


class NodeValueDataType(BaseDataType):
    def validate(self, value, row_number=None, source=''):
        errors = []
        if value:
            try:
                models.TileModel.objects.get(tileid=value)
            except:
                errors.append({'type': 'ERROR', 'message': '{0} {1} is not a valid tile id. This data was not imported.'.format(value, row_number)})
        return errors

    def get_display_value(self, tile, node):
        datatype_factory = DataTypeFactory()
        value_node = models.Node.objects.get(nodeid=node.config['nodeid'])
        data = self.get_tile_data(tile)
        tileid = data[str(node.pk)]
        if tileid:
            value_tile = models.TileModel.objects.get(tileid=tileid)
            datatype = datatype_factory.get_instance(value_node.datatype)
            return datatype.get_display_value(value_tile, value_node)
        return ''

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        pass

    def append_search_filters(self, value, node, query, request):
        pass


def get_value_from_jsonld(json_ld_node):
    try:
        return (json_ld_node[0].get("@value"), json_ld_node[0].get("@language"))
    except KeyError as e:
        try:
            return (json_ld_node.get("@value"), json_ld_node.get("@language"))
        except AttributeError as e:
            return
    except IndexError as e:
        return
