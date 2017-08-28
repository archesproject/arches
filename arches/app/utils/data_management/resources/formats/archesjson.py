import os
import uuid
import json
import datetime
from arches.app.models.system_settings import settings
from arches.app.models import models
from format import Writer
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class JsonWriter(Writer):

    def __init__(self, **kwargs):
        super(JsonWriter, self).__init__(**kwargs)

    def write_resources(self, graph_id=None, resourceinstanceids=None):
        super(JsonWriter, self).write_resources(graph_id=graph_id, resourceinstanceids=resourceinstanceids)
        json_for_export = []
        resources = []
        relations = []
        export = {}
        export['business_data'] = {}

        for resourceinstanceid, tiles in self.resourceinstances.iteritems():
            resourceinstanceid = uuid.UUID(str(resourceinstanceid))
            resource = {}
            resource['tiles'] = tiles
            resource['resourceinstance'] = models.ResourceInstance.objects.get(resourceinstanceid=resourceinstanceid)
            resources.append(resource)

        export['business_data']['resources'] = resources
        graph_id = export['business_data']['resources'][0]['resourceinstance'].graph_id
        
        iso_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if str(graph_id) != settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID:
            json_name = os.path.join('{0}_{1}.{2}'.format(self.file_prefix, iso_date, 'json'))
        else:
            json_name = os.path.join('{0}'.format(os.path.basename(settings.SYSTEM_SETTINGS_LOCAL_PATH)))
        
        dest = StringIO()
        export = JSONDeserializer().deserialize(JSONSerializer().serialize(JSONSerializer().serializeToPython(export)))
        json.dump(export, dest, indent=4)
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
