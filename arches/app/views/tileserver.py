import TileStache
from django.http import HttpResponse
import os
import shutil
import sys
from arches.app.models import models
from TileStache import parseConfig
from ModestMaps.Core import Coordinate
from ModestMaps.Geo import Location
from django.conf import settings

def get_tileserver_config():
    # TODO: the resource queries here perhaps should be moved to a separate view
    # and url.  We may want to consider parameterizing it to support filtering
    # on graphid and we will need to support filtering data based on user
    # permissions, which are defined at the node level; ie only show geometries
    # for nodes which the authenticated user has read permissions
    database = settings.DATABASES['default']
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
                        "queries": [
                            """SELECT tileid::text,
                                        resourceinstanceid::text,
                                        nodeid::text,
                                        graphid::text,
                                        node_name,
                                        graph_name,
                                        geom AS __geometry__,
                                        row_number() over () as __id__
                                    FROM vw_getgeoms
                                UNION
                                SELECT tileid::text,
                                        resourceinstanceid::text,
                                        nodeid::text,
                                        graphid::text,
                                        node_name,
                                        graph_name,
                                        ST_ExteriorRing(geom) AS __geometry__,
                                        row_number() over () as __id__
                                    FROM vw_getgeoms
                                    where ST_GeometryType(geom) = 'ST_Polygon'"""
                        ]
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
    query_string = None
    script_name = None

    status_code, headers, content = TileStache.requestHandler2(
        config, path_info, query_string, script_name)

    response = HttpResponse()
    response.content = content
    response.status_code = status_code
    for header, value in headers.items():
        response[header] = value
    response['Content-length'] = str(len(content))
    return response

def clean_resource_cache(bbox):
    # bbox = (-122.592289978711, 37.70856070649707, -122.23798089667974, 37.85779759136601)
    zooms = range(20)

    config = parseConfig(get_tileserver_config())
    layer = config.layers['resources']

    extension = 'pbf'
    mimetype, format = layer.getTypeByExtension(extension)

    lon1, lat1, lon2, lat2 = bbox
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
