import uuid
from django.core.exceptions import ValidationError
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile
import json

details = {
    "name": "Sample Function",
    "type": "node",
    "description": "Just a sample demonstrating node group selection",
    "defaultconfig": {"triggering_nodegroups": []},
    "classname": "SampleFunction",
    "component": "views/components/functions/sample-function",
}


class SampleFunction(BaseFunction):
    def save(self, tile, request):
        print("running before tile save")

    def post_save(self, tile, request):
        print("running after tile save")

    def on_import(self, tile, request):
        print("calling on import")

    def get(self, tile, request):
        print("calling get")

    def delete(self, tile, request):
        print("calling delete")
