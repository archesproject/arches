import TileStache
from django.http import HttpResponse
import os, shutil, sys
from arches.app.models import models


def handle_request(request):
    layers = {}
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
            "name": "Test",
            "verbose": True
        },
        "layers": layers
    }
    config = TileStache.Config.buildConfiguration(config_dict)
    path_info = request.path.replace('/tileserver/', '')
    query_string = None
    script_name = None

    status_code, headers, content = TileStache.requestHandler2(config, path_info, query_string, script_name)

    response = HttpResponse()
    response.content = content
    response.status_code = status_code
    for header, value in headers.items():
        response[header] = value
    response['Content-length'] = str(len(content))
    return response
