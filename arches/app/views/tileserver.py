import TileStache
from django.http import HttpResponse
import os
import shutil
import sys
import math
from arches.app.models import models
from ModestMaps.Core import Coordinate
from ModestMaps.Geo import Location
from django.conf import settings
from arches.app.datatypes import datatypes
from arches.app.datatypes.datatypes import DataTypeFactory

def get_tileserver_config(node_id=None):
    database = settings.DATABASES['default']
    datatype_factory = DataTypeFactory()

    config_dict = {
        "cache": settings.TILE_CACHE_CONFIG,
        "layers": {}
    }

    if node_id is not None:
        node = models.Node.objects.get(pk=node_id)
        datatype = datatype_factory.get_instance(node.datatype)
        layer_config = datatype.get_layer_config(node)
        if layer_config is not None:
            config_dict["layers"][str(node_id)] = layer_config

    layer_models = models.TileserverLayers.objects.all()
    for layer_model in layer_models:
        config_dict['layers'][layer_model.name] = {
            "provider": {
                "name": "mapnik",
                "mapfile": layer_model.path
            }
        }

    return config_dict


def handle_request(request, node_id=None):
    # TODO: check user node permissions here, if node_id is not None and user
    # does not have read access to that node, fire an exception
    config_dict = get_tileserver_config(node_id)

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


def generateCoordinates(ul, lr, zooms, padding):
    count = 0

    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container().left(padding).up(padding)
        lr_ = lr.zoomTo(zoom).container().right(padding).down(padding)

        rows = lr_.row + 1 - ul_.row
        cols = lr_.column + 1 - ul_.column

        count += int(rows * cols)

    offset = 0
    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container().left(padding).up(padding)
        lr_ = lr.zoomTo(zoom).container().right(padding).down(padding)

        for row in range(int(ul_.row), int(lr_.row + 1)):
            for column in range(int(ul_.column), int(lr_.column + 1)):
                coord = Coordinate(row, column, zoom)

                yield (offset, count, coord)

                offset += 1


def clean_resource_cache(tile):
    if not settings.CACHE_RESOURCE_TILES or not settings.AUTO_MANAGE_TILE_CACHE:
        return

    # get the tile model's bounds
    datatype_factory = DataTypeFactory()
    nodegroup = models.NodeGroup.objects.get(pk=tile.nodegroup_id)
    for node in nodegroup.node_set.all():
        datatype = datatype_factory.get_instance(node.datatype)
        bounds = datatype.get_bounds(tile, node)

        if bounds is not None:
            zooms = range(20)
            config = TileStache.parseConfig(get_tileserver_config(node.nodeid))
            layer = config.layers[str(node.nodeid)]
            mimetype, format = layer.getTypeByExtension('pbf')

            lon1, lat1, lon2, lat2 = bounds
            south, west = min(lat1, lat2), min(lon1, lon2)
            north, east = max(lat1, lat2), max(lon1, lon2)

            northwest = Location(north, west)
            southeast = Location(south, east)

            ul = layer.projection.locationCoordinate(northwest)
            lr = layer.projection.locationCoordinate(southeast)

            padding = 0
            coordinates = generateCoordinates(ul, lr, zooms, padding)

            for (offset, count, coord) in coordinates:
                config.cache.remove(layer, coord, format)


def seed_resource_cache():
    if not settings.CACHE_RESOURCE_TILES:
        print 'set "CACHE_RESOURCE_TILES" to true in settings before seeding cache'
        return

    zooms = range(settings.CACHE_SEED_MAX_ZOOM + 1)
    extension = 'pbf'

    lat1, lon1, lat2, lon2 = settings.CACHE_SEED_BOUNDS
    south, west = min(lat1, lat2), min(lon1, lon2)
    north, east = max(lat1, lat2), max(lon1, lon2)

    northwest = Location(north, west)
    southeast = Location(south, east)

    padding = 0

    datatypes = [d.pk for d in models.DDataType.objects.filter(isgeometric=True)]
    nodes = models.Node.objects.filter(graph__isresource=True, datatype__in=datatypes)
    for node in nodes:
        count = models.TileModel.objects.filter(data__has_key=str(node.nodeid)).count()
        if count > 0:
            config = TileStache.parseConfig(get_tileserver_config(node.nodeid))
            layer = config.layers[str(node.nodeid)]
            ul = layer.projection.locationCoordinate(northwest)
            lr = layer.projection.locationCoordinate(southeast)
            coordinates = generateCoordinates(ul, lr, zooms, padding)
            for (offset, count, coord) in coordinates:
                path = '%s/%d/%d/%d.%s' % (layer.name(), coord.zoom,
                                           coord.column, coord.row, extension)

                progress = {"tile": path,
                            "offset": offset + 1,
                            "total": count}

                attempts = 3
                rendered = False

                while not rendered:
                    print '%(offset)d of %(total)d...' % progress,

                    try:
                        mimetype, content = TileStache.getTile(
                            layer, coord, extension, True)

                    except:
                        attempts -= 1
                        print 'Failed %s, will try %s more.' % (progress['tile'], ['no', 'once', 'twice'][attempts])

                        if attempts == 0:
                            print 'Failed %(zoom)d/%(column)d/%(row)d, trying next tile.\n' % coord.__dict__
                            break

                    else:
                        rendered = True
                        progress['size'] = '%dKB' % (len(content) / 1024)

                        print '%(tile)s (%(size)s)' % progress
