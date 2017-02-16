import importlib
import uuid
import json
import decimal
from django.conf import settings
from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import Polygon
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.betterJSONSerializer import JSONSerializer
from shapely.geometry import asShape
from django.core.exceptions import ValidationError

EARTHCIRCUM = 40075016.6856
PIXELSPERTILE = 256

class DataTypeFactory(object):
    def __init__(self):
        self.datatypes = {datatype.datatype:datatype for datatype in models.DDataType.objects.all()}
        self.datatype_instances = {}

    def get_instance(self, datatype):
        d_datatype = self.datatypes[datatype]
        mod_path = d_datatype.modulename.replace('.py', '')
        module = importlib.import_module('arches.app.datatypes.%s' % mod_path)
        try:
            datatype_instance = self.datatype_instances[d_datatype.classname]
        except:
            datatype_instance = getattr(module, d_datatype.classname)(d_datatype)
            self.datatype_instances[d_datatype.classname] = datatype_instance
        return datatype_instance


class StringDataType(BaseDataType):

    def validate(self, value, source=None):
        errors = []
        try:
            value.upper()
        except:
            errors.append({'source': source, 'value': value, 'message': 'this is not a string', 'datatype': self.datatype_model.datatype})
        return errors

    def append_to_document(self, document, nodevalue):
        document['strings'].append(nodevalue)

    def transform_export_values(self, value):
        return value.encode('utf8')

    def get_search_term(self, nodevalue):
        term = None
        if nodevalue is not None:
            if settings.WORDS_PER_SEARCH_TERM == None or (len(nodevalue.split(' ')) < settings.WORDS_PER_SEARCH_TERM):
                term = nodevalue
        return term


class NumberDataType(BaseDataType):

    def validate(self, value, source=''):
        errors = []

        try:
            decimal.Decimal(value)
        except:
            errors.append({'source': source, 'value': value, 'message': 'not a properly formatted number', 'datatype': self.datatype_model.datatype})
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
                    errors.append({'source': source, 'value': value, 'message': message, 'datatype': self.datatype_model.datatype})

                if bbox.contains(geom) == False:
                    message = 'Geometry does not fall within the bounding box of the selected coordinate system. Adjust your coordinates or your settings.DATA_EXTENT_VALIDATION property.'
            except:
                message = 'Not a properly formatted geometry'
                errors.append({'source': source, 'value': value, 'message': message, 'datatype': self.datatype_model.datatype})

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

    def transform_export_values(self, value):
        wkt_geoms = []
        for feature in value['features']:
            wkt_geoms.append(GEOSGeometry(json.dumps(feature['geometry'])))
        return GeometryCollection(wkt_geoms)

    def append_to_document(self, document, nodevalue):
        document['geometries'].append(nodevalue)

    def get_bounds(self, tile, node):
        bounds = None
        node_data = tile.data[str(node.pk)]
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
        database = settings.DATABASES['default']
        where_clause = ''
        and_where_clause = ''
        if node is not None:
            where_clause = "WHERE nodeid = '%s'" % node.pk
            and_where_clause = "AND nodeid = '%s'" % node.pk

        cluster_sql = """
            WITH clusters(tileid, resourceinstanceid, nodeid, geom, node_name, graphid, graph_name, cid) AS (
                SELECT m.*, ST_ClusterDBSCAN(geom, eps := %s, minpoints := %s) over () AS cid
            	FROM mv_geojson_geoms m
                %s
            )

            SELECT tileid::text,
            		resourceinstanceid::text,
            		nodeid::text,
            		graphid::text,
            		node_name,
            		graph_name,
            		false AS poly_outline,
            		row_number() over () as __id__,
            		1 as total,
            		ST_Centroid(geom) AS __geometry__,
                    '' AS extent
            	FROM clusters
            	WHERE cid is NULL

            UNION

            SELECT '' as tileid,
            		'' as resourceinstanceid,
            		'' as nodeid,
            		'' as graphid,
            		'' as node_name,
            		'' as graph_name,
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
        for i in range(settings.CLUSTER_MAX_ZOOM + 1):
            arc = EARTHCIRCUM / ((1 << i) * PIXELSPERTILE)
            distance = arc * settings.CLUSTER_DISTANCE
            sql_string = cluster_sql % (distance, settings.CLUSTER_MIN_POINTS, where_clause)
            sql_list.append(sql_string)

        sql_list.append("""
            SELECT tileid::text,
                    resourceinstanceid::text,
                    nodeid::text,
                    graphid::text,
                    node_name,
                    graph_name,
                    false AS poly_outline,
                    row_number() over () as __id__,
                    1 as total,
                    geom AS __geometry__,
                    '' AS extent
                FROM mv_geojson_geoms
                %s
            UNION
            SELECT tileid::text,
                    resourceinstanceid::text,
                    nodeid::text,
                    graphid::text,
                    node_name,
                    graph_name,
                    true AS poly_outline,
                    row_number() over () as __id__,
                    1 as total,
                    ST_ExteriorRing(geom) AS __geometry__,
                    '' AS extent
                FROM mv_geojson_geoms
                where ST_GeometryType(geom) = 'ST_Polygon'
                %s
        """ % (where_clause, and_where_clause))

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
            "write cache": settings.CACHE_RESOURCE_TILES
        }

    def get_map_layer(self, node=None):

        if node is None:
            return None
        elif node.config is None or not node.config["layerActivated"]:
            return None
        source_name = "resources-%s" % node.nodeid
        return {
            "nodeid": node.nodeid,
            "name": "%s - %s" % (node.graph.name, node.name),
            "layer_definitions": """[
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
                        "fill-color": "%(mainColor)s"
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
                        "line-width": 3,
                        "line-color": "%(haloColor)s"
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
                        "line-width": 1,
                        "line-color": "%(mainColor)s"
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
                        "line-width": 1.5,
                        "line-color": "%(haloColor)s"
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
                        "circle-radius": 5,
                        "circle-color": "%(haloColor)s"
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
                        "circle-radius": 3,
                        "circle-color": "%(mainColor)s"
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
                        "circle-color": "%(haloColor)s"
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
                        "circle-color": "%(mainColor)s"
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
                         "text-size": 12
                     },
                     "filter": ["all", [">", "total", 1]]
                 }
            ]""" % {
                "source_name": source_name,
                "nodeid": node.nodeid,
                "mainColor": node.config["mainColor"],
                "haloColor": node.config["haloColor"],
            },
            "icon": node.graph.iconclass,
        }

    def get_map_source(self, node=None):
        if node is None:
            return None
        return {
            "name": "resources-%s" % node.nodeid,
            "source": json.dumps({
                "type": "vector",
                "tiles": ["/tileserver/%s/{z}/{x}/{y}.pbf" % node.nodeid]
            })
        }

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
