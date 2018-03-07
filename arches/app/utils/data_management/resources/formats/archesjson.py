
import os
import types
import sys
import datetime
from django.conf import settings
from django.db import connection
import arches.app.models.models as archesmodels
from arches.app.models.resource import Resource
import codecs
from format import Writer
import json
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer



try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class JsonWriter(Writer):

    def __init__(self):
        super(JsonWriter, self).__init__()

    def write_resources(self, resources, resource_export_configs):
        json_resources = []
        json_resources_for_export = []
        iso_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        json_file_name = os.path.join('{0}_{1}.{2}'.format('EAMENA', iso_date, 'json'))
        f = StringIO()


        for count, resource in enumerate(resources, 1):
            if count % 1000 == 0:
                print "%s Resources exported" % count            
            errors = []
            
            try:
                a_resource = Resource().get(resource['_id'])
                
                a_resource.form_groups = None
                json_resources.append(a_resource)
            except Exception as e:
                if e not in errors:
                    errors.append(e)
        if len(errors) > 0:
            print errors[0], ':', len(errors)
                   
                   
        f.write((JSONSerializer().serialize({'resources':json_resources}, indent = 4, separators=(',',':'))))
        json_resources_for_export.append({'name': json_file_name, 'outputfile': f})
        return json_resources_for_export
        
class JsonReader():

    def validate_file(self, archesjson, break_on_error=True):
        pass

    def load_file(self, archesjson):
        resources = []
        with open(archesjson, 'r') as f:
            resources = JSONDeserializer().deserialize(f.read())
        
        return resources['resources']