
import os
import types
import sys
import uuid
import datetime
from django.conf import settings
from django.db import connection
import arches.app.models.models as archesmodels
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.models.graph import Graph
from arches.app.models import models
import codecs
from format import Writer
import json
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
import csv

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class JsonWriter(Writer):

    def __init__(self):
        super(JsonWriter, self).__init__()

    def get_tiles(self, resourceid):
        #insure parenttiles are ordered so they are imported before their respective child tiles
        tiles = Tile.objects.filter(resourceinstance_id=resourceid).order_by('-parenttile_id')
        return tiles

    def write_resources(self, resourceids, resource_export_configs=None):
        json_for_export = []
        resources = []
        relations = []
        export = {}
        export['business_data'] = {}

        for resourceid in resourceids:
            if resourceid != uuid.UUID(str('40000000-0000-0000-0000-000000000000')):
                resourceid = uuid.UUID(str(resourceid))
                resource = {}
                resource['tiles'] = self.get_tiles(resourceid)
                resource['resourceinstance'] = models.ResourceInstance.objects.get(resourceinstanceid=resourceid)
                resources.append(resource)

        for relation in models.ResourceXResource.objects.all():
            relations.append(relation)

        export['business_data']['resources'] = resources
        export['business_data']['relations'] = relations

        json_name_prefix = Graph.objects.get(graphid=export['business_data']['resources'][0]['resourceinstance'].graph_id).name

        export = JSONDeserializer().deserialize(JSONSerializer().serialize(JSONSerializer().serializeToPython(export)))
        iso_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        json_name = os.path.join('{0}_{1}.{2}'.format(json_name_prefix, iso_date, 'json'))
        dest = StringIO()
        json.dump(export, dest)
        json_for_export.append({'name':json_name, 'outputfile': dest})

        return json_for_export


class JsonReader():

    def validate_file(self, archesjson, break_on_error=True):
        pass

    def load_file(self, archesjson):
        resources = []
        with open(archesjson, 'r') as f:
            resources = JSONDeserializer().deserialize(f.read())
        return resources['resources']
