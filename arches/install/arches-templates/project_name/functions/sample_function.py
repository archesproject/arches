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
    "defaultconfig": {"selected_nodegroup": ""},
    "classname": "SampleFunction",
    "component": "views/components/functions/sample-function",
}


class SampleFunction(BaseFunction):
    def save(self):
        print("calling save")

    def on_import(self):
        print("calling on import")

    def get(self):
        print("calling get")

    def delete(self):
        print("calling delete")
