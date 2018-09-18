import TileStache
import os
import shutil
import sys
import math
import json
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from ModestMaps.Core import Coordinate
from ModestMaps.Geo import Location
from arches.app.datatypes import datatypes
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.geo_utils import GeoUtils


def get_tileserver_config(layer_id, request=None):
    database = settings.DATABASES['default']
    datatype_factory = DataTypeFactory()

    try:
        node = models.Node.objects.get(pk=layer_id)
        datatype = datatype_factory.get_instance(node.datatype)
        if request == None or request.user.has_perm('read_nodegroup', node.nodegroup):
            layer_config = datatype.get_layer_config(node)
        else:
            layer_config = datatype.get_layer_config(None)
    except Exception:
        layer_model = models.TileserverLayer.objects.get(name=layer_id)
        layer_config = layer_model.config

    tile_cache_config = settings.TILE_CACHE_CONFIG

    config_dict = {
        "cache": tile_cache_config,
        "layers": {}
    }
    config_dict["layers"][str(layer_id)] = layer_config
    return config_dict


def handle_request(request):
    path_info = request.path.replace(reverse('tileserver') + '/', '')
    layer_id = path_info.split('/')[0]
    config_dict = get_tileserver_config(layer_id, request=request)
    config = TileStache.Config.buildConfiguration(config_dict)
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
    # get the tile model's bounds
    datatype_factory = DataTypeFactory()
    nodegroup = models.NodeGroup.objects.get(pk=tile.nodegroup_id)
    for node in nodegroup.node_set.all():
        datatype = datatype_factory.get_instance(node.datatype)
        if datatype.should_cache(node) and datatype.should_manage_cache(node):
            bounds = datatype.get_bounds(tile, node)
            if bounds is not None:
                zooms = range(20)
                config = TileStache.parseConfig(
                    get_tileserver_config(node.nodeid))
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
    for tile in tile.tiles:
        clean_resource_cache(tile)

def seed_resource_cache():
    datatype_factory = DataTypeFactory()
    zooms = range(settings.CACHE_SEED_MAX_ZOOM + 1)
    extension = 'pbf'
    try:
        lat1, lon1, lat2, lon2 = settings.CACHE_SEED_BOUNDS
    except:
        lat1, lon1, lat2, lon2 = GeoUtils().get_bounds_from_geojson(settings.CACHE_SEED_BOUNDS)

    south, west = min(lat1, lat2), min(lon1, lon2)
    north, east = max(lat1, lat2), max(lon1, lon2)

    northwest = Location(north, west)
    southeast = Location(south, east)

    padding = 0

    datatypes = [
        d.pk for d in models.DDataType.objects.filter(isgeometric=True)]
    nodes = models.Node.objects.filter(
        graph__isresource=True, datatype__in=datatypes)
    for node in nodes:
        datatype = datatype_factory.get_instance(node.datatype)
        count = models.TileModel.objects.filter(
            data__has_key=str(node.nodeid)).count()
        if datatype.should_cache(node) and count > 0:
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
