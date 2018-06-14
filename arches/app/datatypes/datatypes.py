import uuid
import json
import decimal
import importlib
import distutils
from datetime import datetime
from mimetypes import MimeTypes
from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.date_utils import ExtendedDateFormat
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Range, Term, Exists, RangeDSLException
from arches.app.search.search_engine_factory import SearchEngineFactory
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import GeometryCollection
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from elasticsearch import Elasticsearch
from edtf import parse_edtf

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
            mod_path = d_datatype.modulename.replace('.py', '')
            module = None
            import_success = False
            import_error = None
            for datatype_dir in settings.DATATYPE_LOCATIONS:
                try:
                    module = importlib.import_module(datatype_dir + '.%s' % mod_path)
                    import_success = True
                except ImportError as e:
                    import_error = e
                if module != None:
                    break
            if import_success == False:
                print 'Failed to import ' + mod_path
                print import_error
            datatype_instance = getattr(module, d_datatype.classname)(d_datatype)
            self.datatype_instances[d_datatype.classname] = datatype_instance
        return datatype_instance


class StringDataType(BaseDataType):

    def validate(self, value, row_number=None, source=None):
        errors = []
        try:
            value.upper()
        except:
            errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} {3} - {4}. {5}'.format(self.datatype_model.datatype, value, source, row_number, 'this is not a string', 'This data was not imported.')})
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


class NumberDataType(BaseDataType):

    def validate(self, value, row_number=None, source=''):
        errors = []

        try:
            decimal.Decimal(value)
        except:
            errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} {3}- {4}. {5}'.format(self.datatype_model.datatype, value, source, row_number, 'not a properly formatted number', 'This data was not imported.')})
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
                    search_query = Match(field='tiles.data.%s' % (str(node.pk)), query=value['val'], type='phrase_prefix', fuzziness=0)
                query.must(search_query)
        except KeyError, e:
            pass


class BooleanDataType(BaseDataType):

    def validate(self, value, row_number=None, source=''):
        errors = []

        try:
            type(bool(distutils.util.strtobool(str(value)))) == True
        except:
            errors.append({'type': 'ERROR', 'message': '{0} is not of type boolean. This data was not imported.'.format(value)})

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


class DateDataType(BaseDataType):

    def validate(self, value, row_number=None, source=''):
        errors = []

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
            if value['val'] != '':
                date_value = datetime.strptime(value['val'], '%Y-%m-%d').isoformat()
                if value['op'] != 'eq':
                    operators = {'gte': None, 'lte': None, 'lt': None, 'gt': None}
                    operators[value['op']] = date_value
                    search_query = Range(field='tiles.data.%s' % (str(node.pk)), **operators)
                else:
                    search_query = Match(field='tiles.data.%s' % (str(node.pk)), query=date_value, type='phrase_prefix', fuzziness=0)
                query.must(search_query)
        except KeyError, e:
            pass

    def after_update_all(self):
        config = cache.get('time_wheel_config_anonymous')
        if config is not None:
            cache.delete('time_wheel_config_anonymous')

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
                query.should(Match(field='tiles.data.%s.dates.date' % (str(node.pk)), query=edtf.lower, type='phrase_prefix', fuzziness=0))
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
        document['geometries'].append({'geom':nodevalue, 'nodegroup_id': tile.nodegroup_id, 'provisional': provisional})
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
        node_data = tile.data[str(node.pk)]
        return self.get_bounds_from_value(node_data)

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
                        (row_number() over ())::text as __id__,
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
                        "line-width": %(outlineWeight)s,
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
                        "line-width": %(haloWeight)s,
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
                        "line-width": %(weight)s,
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
                        "circle-radius": %(haloRadius)s,
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
                        "circle-radius": %(radius)s,
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
            "addtomap": node.config['addToMap'],
        }

    def after_update_all(self):
        cursor = connection.cursor()
        sql = """
            REFRESH MATERIALIZED VIEW mv_geojson_geoms;
        """
        cursor.execute(sql)


class FileListDataType(BaseDataType):
    def handle_request(self, current_tile, request, node):
        previously_saved_tile = models.TileModel.objects.filter(pk=current_tile.tileid)
        if previously_saved_tile.count() == 1:
            if previously_saved_tile[0].data[str(node.pk)] != None:
                for previously_saved_file in previously_saved_tile[0].data[str(node.pk)]:
                    previously_saved_file_has_been_removed = True
                    for incoming_file in current_tile.data[str(node.pk)]:
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
            file_model.save()
            if current_tile.data[str(node.pk)] != None:
                for file_json in current_tile.data[str(node.pk)]:
                    if file_json["name"] == file_data.name and file_json["url"] is None:
                        file_json["file_id"] = str(file_model.pk)
                        file_json["url"] = str(file_model.path.url)
                        file_json["status"] = 'uploaded'

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

class CSVChartJsonDataType(FileListDataType):
    def __init__(self, model=None):
        super(CSVChartJsonDataType, self).__init__(model=model)

    def handle_request(self, current_tile, request, node):
        try:
            previously_saved_tile = models.TileModel.objects.filter(pk=current_tile.tileid)
            if previously_saved_tile.count() == 1:
                for previously_saved_file in previously_saved_tile[0].data[str(node.pk)]['files']:
                    previously_saved_file_has_been_removed = True
                    for incoming_file in current_tile.data[str(node.pk)]['files']:
                        if previously_saved_file['file_id'] == incoming_file['file_id']:
                            previously_saved_file_has_been_removed = False
                    if previously_saved_file_has_been_removed:
                        deleted_file = models.File.objects.get(pk=previously_saved_file["file_id"])
                        deleted_file.delete()

            files = request.FILES.getlist('file-list_' + str(node.pk), [])
            for file_data in files:
                file_model = models.File()
                file_model.path = file_data
                file_model.save()
                for file_json in current_tile.data[str(node.pk)]['files']:
                    if file_json["name"] == file_data.name and file_json["url"] is None:
                        file_json["file_id"] = str(file_model.pk)
                        file_json["url"] = str(file_model.path.url)
                        file_json["status"] = 'uploaded'
        except Exception as e:
            print e


class IIIFDrawingDataType(BaseDataType):
    def get_strings(self, nodevalue):
        string_list = [nodevalue['manifestLabel']]
        for feature in nodevalue['features']:
            if feature['properties']['name'] != '':
                string_list.append(feature['properties']['name'])
        return string_list

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        string_list = self.get_strings(nodevalue)
        for string_item in string_list:
            document['strings'].append({'string': string_item, 'nodegroup_id': tile.nodegroup_id})
        for feature in nodevalue['features']:
            if feature['properties']['type'] is not None:
                valueid = feature['properties']['type']
                value = models.Value.objects.get(pk=valueid)
                document['domains'].append({'label': value.value, 'conceptid': value.concept_id, 'valueid': valueid, 'nodegroup_id': tile.nodegroup_id, 'provisional': provisional})

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        string_list = self.get_strings(nodevalue)
        for string_item in string_list:
            if string_item is not None:
                if settings.WORDS_PER_SEARCH_TERM == None or (len(string_item.split(' ')) < settings.WORDS_PER_SEARCH_TERM):
                    terms.append(string_item)
        return terms

class BaseDomainDataType(BaseDataType):
    def get_option_text(self, node, option_id):
        for option in node.config['options']:
            if option['id'] == option_id:
                return option['text']
        return ''


class DomainDataType(BaseDomainDataType):

    def validate(self, value, row_number=None, source=''):
        errors = []
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
            for k, v in tile.data.iteritems():
                if v == nodevalue:
                    node = models.Node.objects.get(nodeid=k)
                    domain_text = self.get_option_text(node, v)

        if domain_text not in document['strings'] and domain_text != None:
            document['strings'].append({'string': domain_text, 'nodegroup_id': tile.nodegroup_id, 'provisional': provisional})

    def get_display_value(self, tile, node):
        return self.get_option_text(node, tile.data[str(node.nodeid)])

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
                search_query = Match(field='tiles.data.%s' % (str(node.pk)), type="phrase", query=value['val'], fuzziness=0)
                # search_query = Term(field='tiles.data.%s' % (str(node.pk)), term=str(value['val']))
                if '!' in value['op']:
                    query.must_not(search_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(search_query)

        except KeyError, e:
            pass


class DomainListDataType(BaseDomainDataType):
    def validate(self, value, row_number=None, source=''):
        errors = []

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
            for k, v in tile.data.iteritems():
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
        for val in tile.data[str(node.nodeid)]:
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
                search_query = Match(field='tiles.data.%s' % (str(node.pk)), type="phrase", query=value['val'], fuzziness=0)
                # search_query = Term(field='tiles.data.%s' % (str(node.pk)), term=str(value['val']))
                if '!' in value['op']:
                    query.must_not(search_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(search_query)

        except KeyError, e:
            pass


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
                    resource_document = se.search(index='resource', doc_type='_all', id=resourceid)
                    resource_names.add(resource_document['_source']['displayname'])
                except:
                    print 'resource not available'
        else:
            print 'resource not avalable'
        return resource_names

    def validate(self, value, row_number=None, source=''):
        errors = []
        id_list = self.get_id_list(value)

        for resourceid in id_list:
            try:
                models.ResourceInstance.objects.get(pk=resourceid)
            except:
                errors.append({'type': 'WARNING', 'message': 'The resource id: {0} does not exist in the system. The data for this card will be available in the system once resource {0} is loaded.'.format(resourceid)})
        return errors

    def get_display_value(self, tile, node):
        nodevalue = tile.data[str(node.nodeid)]
        resource_names = self.get_resource_names(nodevalue)
        return ', '.join(resource_names)

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        resource_names = self.get_resource_names(nodevalue)
        for value in resource_names:
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
                search_query = Match(field='tiles.data.%s' % (str(node.pk)), type="phrase", query=value['val'], fuzziness=0)
                # search_query = Term(field='tiles.data.%s' % (str(node.pk)), term=str(value['val']))
                if '!' in value['op']:
                    query.must_not(search_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(search_query)
        except KeyError, e:
            pass


class NodeValueDataType(BaseDataType):
    def validate(self, value, row_number=None, source=''):
        errors = []
        if value:
            try:
                models.TileModel.objects.get(tileid=value)
            except:
                errors.append({'type': 'ERROR', 'message': '{0} {1} is not a valid tile id. This data was not imported.'.format(v, row_number)})
        return errors

    def get_display_value(self, tile, node):
        datatype_factory = DataTypeFactory()
        value_node = models.Node.objects.get(nodeid=node.config['nodeid'])
        tileid = tile.data[str(node.pk)]
        if tileid:
            value_tile = models.TileModel.objects.get(tileid=tileid)
            datatype = datatype_factory.get_instance(value_node.datatype)
            return datatype.get_display_value(value_tile, value_node)
        return ''

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        pass

    def append_search_filters(self, value, node, query, request):
        pass
