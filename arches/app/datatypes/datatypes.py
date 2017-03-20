import uuid
import json
import decimal
import importlib
from django.conf import settings
from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.betterJSONSerializer import JSONSerializer
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from shapely.geometry import asShape
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection

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
            module = importlib.import_module('arches.app.datatypes.%s' % mod_path)
            datatype_instance = getattr(module, d_datatype.classname)(d_datatype)
            self.datatype_instances[d_datatype.classname] = datatype_instance
        return datatype_instance


class StringDataType(BaseDataType):

    def validate(self, value, source=None):
        errors = []
        try:
            value.upper()
        except:
            errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}'.format(self.datatype_model.datatype, value, source, 'this is not a string')})
        return errors

    def append_to_document(self, document, nodevalue):
        document['strings'].append(nodevalue)

    def transform_export_values(self, value, *args, **kwargs):
        return value.encode('utf8')

    def get_search_term(self, nodevalue):
        term = None
        if nodevalue is not None:
            if settings.WORDS_PER_SEARCH_TERM == None or (len(nodevalue.split(' ')) < settings.WORDS_PER_SEARCH_TERM):
                term = nodevalue
        return term


class NumberDataType(BaseDataType):

    def validate(self, value, source=''):
        'validating a number'
        errors = []

        try:
            decimal.Decimal(value)
        except:
            errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}'.format(self.datatype_model.datatype, value, source, 'not a properly formatted number')})
        return errors

    def transform_import_values(self, value):
        return float(value)

    def append_to_document(self, document, nodevalue):
        document['numbers'].append(nodevalue)


class BooleanDataType(BaseDataType):

    def transform_import_values(self, value):
        return bool(distutils.util.strtobool(value))


class DateDataType(BaseDataType):

    def append_to_document(self, document, nodevalue):
        document['dates'].append(nodevalue)


class GeojsonFeatureCollectionDataType(BaseDataType):

    def validate(self, value, source=None):
        errors = []
        coord_limit = 1500
        coordinate_count = 0

        def validate_geom(geom, coordinate_count=0):
            try:
                coordinate_count += geom.num_coords
                bbox = Polygon(settings.DATA_VALIDATION_BBOX)
                if coordinate_count > coord_limit:
                    message = 'Geometry has too many coordinates for Elasticsearch ({0}), Please limit to less then {1} coordinates of 5 digits of precision or less.'.format(coordinate_count, coord_limit)
                    errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}'.format(self.datatype_model.datatype, value, source, message)})

                if bbox.contains(geom) == False:
                    message = 'Geometry does not fall within the bounding box of the selected coordinate system. Adjust your coordinates or your settings.DATA_EXTENT_VALIDATION property.'
            except:
                message = 'Not a properly formatted geometry'
                errors.append({'type': 'ERROR', 'message': 'datatype: {0} value: {1} {2} - {3}'.format(self.datatype_model.datatype, value, source, message)})

        for feature in value['features']:
            geom = GEOSGeometry(JSONSerializer().serialize(feature['geometry']))
            validate_geom(geom, coordinate_count)

        return errors

    def transform_import_values(self, value):
        arches_geojson = {}
        arches_geojson['type'] = "FeatureCollection"
        arches_geojson['features'] = []
        geometry = GEOSGeometry(value, srid=4326)
        if geometry.num_geom > 1:
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

    def append_to_document(self, document, nodevalue):
        document['geometries'].append(nodevalue)
        bounds = self.get_bounds_from_value(nodevalue)
        if bounds is not None:
            minx, miny, maxx, maxy = bounds
            centerx = maxx - (maxx - minx) / 2
            centery = maxy - (maxy - miny) / 2
            document['points'].append({
                "lon": centerx,
                "lat": centery
            })

    def get_bounds(self, tile, node):
        node_data = tile.data[str(node.pk)]
        return self.get_bounds_from_value(node_data)

    def get_bounds_from_value(self, node_data):
        bounds = None
        for feature in node_data['features']:
            shape = asShape(feature['geometry'])
            if bounds is None:
                bounds = shape.bounds
            else:
                minx, miny, maxx, maxy = bounds
                if shape.bounds[0] < minx:
                    minx = shape.bounds[0]
                if shape.bounds[1] < miny:
                    miny = shape.bounds[1]
                if shape.bounds[2] > maxx:
                    maxx = shape.bounds[2]
                if shape.bounds[3] > maxy:
                    maxy = shape.bounds[3]

                bounds = (minx, miny, maxx, maxy)
        return bounds

    def get_layer_config(self, node=None):
        if node is None:
            return None
        elif node.config is None:
            return None
        database = settings.DATABASES['default']
        config = node.config

        cluster_sql = """
            WITH clusters(tileid, resourceinstanceid, nodeid, geom, cid) AS (
                SELECT m.*, ST_ClusterDBSCAN(geom, eps := %s, minpoints := %s) over () AS cid
            	FROM mv_geojson_geoms m
                WHERE nodeid = '%s'
            )

            SELECT resourceinstanceid::text,
                    false AS poly_outline,
            		row_number() over () as __id__,
            		1 as total,
            		ST_Centroid(geom) AS __geometry__,
                    '' AS extent
            	FROM clusters
            	WHERE cid is NULL

            UNION

            SELECT '' as resourceinstanceid,
            		false AS poly_outline,
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

        sql_list = []
        for i in range(int(config['clusterMaxZoom']) + 1):
            arc = EARTHCIRCUM / ((1 << i) * PIXELSPERTILE)
            distance = arc * int(config['clusterDistance'])
            sql_string = cluster_sql % (distance, int(config['clusterMinPoints']), node.pk)
            sql_list.append(sql_string)

        sql_list.append("""
            SELECT resourceinstanceid::text,
                    false AS poly_outline,
                    row_number() over () as __id__,
                    1 as total,
                    geom AS __geometry__,
                    '' AS extent
                FROM mv_geojson_geoms
                WHERE nodeid = '%s'
            UNION
            SELECT resourceinstanceid::text,
                    true AS poly_outline,
                    row_number() over () as __id__,
                    1 as total,
                    ST_ExteriorRing(geom) AS __geometry__,
                    '' AS extent
                FROM mv_geojson_geoms
                WHERE ST_GeometryType(geom) = 'ST_Polygon'
                AND nodeid = '%s'
        """ % (node.pk, node.pk))

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
        if not preview and count < 1 or not node.config["layerActivated"]:
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
                    "id": "resources-line-halo-%(nodeid)s",
                    "type": "line",
                    "source": "%(source_name)s",
                    "source-layer": "%(nodeid)s",
                    "layout": {
                        "visibility": "visible"
                    },
                    "filter": ["all", ["==", "$type", "LineString"],["==", "poly_outline", false],["==", "total", 1]],
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
                    "filter": ["all", ["==", "$type", "LineString"],["==", "poly_outline", false],["==", "total", 1]],
                    "paint": {
                        "line-width": %(weight)s,
                        "line-color": "%(lineColor)s"
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
                    "filter": ["all", ["==", "$type", "LineString"],["==", "poly_outline", true],["==", "total", 1]],
                    "paint": {
                        "line-width": %(outlineWeight)s,
                        "line-color": "%(outlineColor)s"
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
                         "text-font": [
                             "DIN Offc Pro Medium",
                             "Arial Unicode MS Bold"
                         ],
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
                "haloRadius": node.config["haloRadius"],
                "lineColor": node.config["lineColor"],
                "lineHaloColor": node.config["lineHaloColor"],
                "weight": node.config["weight"],
                "haloWeight": node.config["haloWeight"],
                "fillColor": node.config["fillColor"],
                "outlineColor": node.config["outlineColor"],
                "outlineWeight": node.config["outlineWeight"],
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
    def manage_files(self, previously_saved_tile, current_tile, request, node):
        if previously_saved_tile.count() == 1:
            for previously_saved_file in previously_saved_tile[0].data[str(node.pk)]:
                previously_saved_file_has_been_removed = True
                for incoming_file in current_tile.data[str(node.pk)]:
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
            for file_json in current_tile.data[str(node.pk)]:
                if file_json["name"] == file_data.name and file_json["url"] is None:
                    file_json["file_id"] = str(file_model.pk)
                    file_json["url"] = str(file_model.path.url)
                    file_json["status"] = 'uploaded'

    def transform_import_values(self, value):
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
            tile_file['type'] = '' if tile_file['type'] == None else file_tile['type']
            tile_data.append(tile_file)
            file_path = 'uploadedfiles/' + str(tile_file['name'])
            fileid = tile_file['file_id']
            File.objects.get_or_create(fileid=fileid, path=file_path)

        result = json.loads(json.dumps(tile_data))
        return result
