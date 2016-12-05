import TileStache
from django.http import HttpResponse
import os
import shutil
import sys
from arches.app.models import models


def handle_request(request):
    # TODO: the resource queries here perhaps should be moved to a separate view
    # and url.  We may want to consider parameterizing it to support filtering
    # on graphid and we will need to support filtering data based on user
    # permissions, which are defined at the node level; ie only show geometries
    # for nodes which the authenticated user has read permissions
    layers = {
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
                            FROM vw_getgeoms"""
                    ]
                },
            },
            "allowed origin": "*",
            "compress": True,
            "write cache": False
        },
        "resource-outlines": {
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
    layer_models = models.TileserverLayers.objects.all()
    for layer_model in layer_models:
        layers[layer_model.name] = {
            "provider": {
                "name": "mapnik",
                "mapfile": layer_model.path
            }
        }

    config_dict = {
        "cache": {
            "name": "Disk",
            "path": os.path.join('arches', 'tileserver', 'cache')
        },
        "layers": layers
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
