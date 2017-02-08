import TileStache
from django.http import HttpResponse
import os
import shutil
import sys
import math
from arches.app.models import models
from TileStache import parseConfig
from ModestMaps.Core import Coordinate
from ModestMaps.Geo import Location
from django.conf import settings
from arches.app.models import models
from shapely.geometry import asShape



EARTHRADIUS = 6378137
EARTHCIRCUM = EARTHRADIUS * 2.0 * math.pi
PIXELSPERTILE = 512

def get_tileserver_config():
    # TODO: the resource queries here perhaps should be moved to a separate view
    # and url.  We may want to consider parameterizing it to support filtering
    # on graphid and we will need to support filtering data based on user
    # permissions, which are defined at the node level; ie only show geometries
    # for nodes which the authenticated user has read permissions
    database = settings.DATABASES['default']

    cluster_sql = """
        WITH clusters(tileid, resourceinstanceid, nodeid, geom, node_name, graphid, graph_name, cid) AS
        	(SELECT m.*, ST_ClusterDBSCAN(geom, eps := %s, minpoints := %s) over () AS cid
        	FROM mv_geojson_geoms m)

        SELECT tileid::text,
        		resourceinstanceid::text,
        		nodeid::text,
        		graphid::text,
        		node_name,
        		graph_name,
        		false AS poly_outline,
        		row_number() over () as __id__,
        		1 as total,
        		0 AS radius,
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
        		sqrt(ST_Area(ST_MinimumBoundingCircle(ST_Collect(geom))) / pi()) AS radius,
        		ST_Centroid(ST_Envelope(ST_Collect(geom))) AS __geometry__,
                ST_AsGeoJSON(ST_Envelope(ST_Collect(geom))) AS extent
        	FROM clusters
        	WHERE cid IS NOT NULL
        	GROUP BY cid
    """

    sql_list = []

    for i in range(settings.CLUSTER_MAX_ZOOM + 1):
        arc = EARTHCIRCUM / ((1 << (i)) * PIXELSPERTILE)
        distance = arc * settings.CLUSTER_DISTANCE
        sql_string = cluster_sql % (distance, settings.CLUSTER_MIN_POINTS)
        sql_list.append(sql_string)

    sql_list.append("""
        SELECT tileid::text,
                resourceinstanceid::text,
                nodeid::text,
                graphid::text,
                node_name,
                graph_name,
                false AS poly_outline,
                geom AS __geometry__,
                row_number() over () as __id__,
                1 as total
            FROM mv_geojson_geoms
        UNION
        SELECT tileid::text,
                resourceinstanceid::text,
                nodeid::text,
                graphid::text,
                node_name,
                graph_name,
                true AS poly_outline,
                ST_ExteriorRing(geom) AS __geometry__,
                row_number() over () as __id__,
                1 as total
            FROM mv_geojson_geoms
            where ST_GeometryType(geom) = 'ST_Polygon'
    """)

    return {
        "cache": settings.TILE_CACHE_CONFIG,
        "layers": {
            "resources": {
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
        }
    }

def handle_request(request):
    config_dict = get_tileserver_config()
    print settings.CACHE_RESOURCE_TILES
    layer_models = models.TileserverLayers.objects.all()
    for layer_model in layer_models:
        config_dict['layers'][layer_model.name] = {
            "provider": {
                "name": "mapnik",
                "mapfile": layer_model.path
            }
        }

    config = TileStache.Config.buildConfiguration(config_dict)
    path_info = request.path.replace('/tileserver/', '')
    query_string = ""
    script_name = ""
    response = HttpResponse()

    try:
        status_code, headers, content = TileStache.requestHandler2(
            config, path_info, query_string, script_name)

        response.content = content
        response.status_code = status_code
        for header, value in headers.items():
            response[header] = value

        response['Content-length'] = str(len(content))

    except Exception as e:
        print 'No tile data', e, response

    return response


def clean_resource_cache(tile):
    if not settings.CACHE_RESOURCE_TILES:
        return

    # get the tile model's bounds
    bounds = None
    nodegroup = models.NodeGroup.objects.get(pk=tile.nodegroup_id)
    for node in nodegroup.node_set.all():
        if node.datatype == 'geojson-feature-collection':
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
    if bounds is None:
        return

    zooms = range(20)
    config = parseConfig(get_tileserver_config())
    layer = config.layers['resources']
    mimetype, format = layer.getTypeByExtension('pbf')

    lon1, lat1, lon2, lat2 = bounds
    south, west = min(lat1, lat2), min(lon1, lon2)
    north, east = max(lat1, lat2), max(lon1, lon2)

    northwest = Location(north, west)
    southeast = Location(south, east)

    ul = layer.projection.locationCoordinate(northwest)
    lr = layer.projection.locationCoordinate(southeast)

    # start with a simple total of all the coordinates we will need.
    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container()
        lr_ = lr.zoomTo(zoom).container()

        rows = lr_.row + 1 - ul_.row
        cols = lr_.column + 1 - ul_.column

    # now generate the actual coordinates.
    coordinates = []
    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container()
        lr_ = lr.zoomTo(zoom).container()

        for row in range(int(ul_.row), int(lr_.row + 1)):
            for column in range(int(ul_.column), int(lr_.column + 1)):
                coord = Coordinate(row, column, zoom)
                coordinates.append(coord)

    for coord in coordinates:
        config.cache.remove(layer, coord, format)
