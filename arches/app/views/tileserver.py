import TileStache
from django.http import HttpResponse
import os
import shutil
import sys
from arches.app.models import models
from TileStache import parseConfig, getTile
from TileStache.Core import KnownUnknown
from TileStache.Caches import Disk, Multi
from sys import stderr, path
from json import dump as json_dump
from ModestMaps.Core import Coordinate
from ModestMaps.Geo import Location

def get_tileserver_config():
    # TODO: the resource queries here perhaps should be moved to a separate view
    # and url.  We may want to consider parameterizing it to support filtering
    # on graphid and we will need to support filtering data based on user
    # permissions, which are defined at the node level; ie only show geometries
    # for nodes which the authenticated user has read permissions
    return {
        "cache": {
            "name": "Disk",
            "path": os.path.join('arches', 'tileserver', 'cache')
        },
        "layers": {
            "resources": {
                "provider": {
                    "class": "TileStache.Goodies.VecTiles:Provider",
                    "kwargs": {
                        "dbinfo": {
                            "host": "localhost",
                            "user": "postgres",
                            "password": "postgis",
                            "database": "arches"
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
                "write cache": False
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

def generate_coordinates(ul, lr, zooms, padding):
    """ Generate a stream of (offset, count, coordinate) tuples for seeding.
        Flood-fill coordinates based on two corners, a list of zooms and padding.
    """
    # start with a simple total of all the coordinates we will need.
    count = 0

    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container().left(padding).up(padding)
        lr_ = lr.zoomTo(zoom).container().right(padding).down(padding)

        rows = lr_.row + 1 - ul_.row
        cols = lr_.column + 1 - ul_.column

        count += int(rows * cols)

    # now generate the actual coordinates.
    # offset starts at zero
    offset = 0

    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container().left(padding).up(padding)
        lr_ = lr.zoomTo(zoom).container().right(padding).down(padding)

        for row in range(int(ul_.row), int(lr_.row + 1)):
            for column in range(int(ul_.column), int(lr_.column + 1)):
                coord = Coordinate(row, column, zoom)

                yield (offset, count, coord)

                offset += 1


def clean_resource_cache(bbox):
    # bbox = (37.777, -122.352, 37.839, -122.226)
    zooms = range(20)

    config = parseConfig(get_tileserver_config())
    layer = config.layers['resources']

    extension = 'pbf'
    mimetype, format = layer.getTypeByExtension(extension)

    lat1, lon1, lat2, lon2 = bbox
    south, west = min(lat1, lat2), min(lon1, lon2)
    north, east = max(lat1, lat2), max(lon1, lon2)

    northwest = Location(north, west)
    southeast = Location(south, east)

    ul = layer.projection.locationCoordinate(northwest)
    lr = layer.projection.locationCoordinate(southeast)

    coordinates = generate_coordinates(ul, lr, zooms, 0)

    for (offset, count, coord) in coordinates:
        path = '%s/%d/%d/%d.%s' % (layer.name(), coord.zoom, coord.column, coord.row, extension)
        config.cache.remove(layer, coord, format)
