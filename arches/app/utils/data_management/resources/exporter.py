import os
import csv
import zipfile
import datetime
import json
import glob
import uuid
from django.conf import settings
from formats.csvfile import CsvWriter
from formats.kmlfile import KmlWriter
from formats.shpfile import ShpWriter
from formats.archesjson import JsonWriter #Writes full resource instances rather than search results
from django.http import HttpResponse
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class ResourceExporter(object):

    def __init__(self, file_format):
        self.filetypes = {'csv': CsvWriter, 'kml': KmlWriter, 'shp': ShpWriter, 'json': JsonWriter}
        self.format = file_format
        self.writer = self.filetypes[file_format]()

    def export(self, resources=None, zip=False, search_results=True, dest_dir=None):
        result=None
        if search_results == True and dest_dir is not None:
            result = self.writer.write_resources(resources, dest_dir)
        elif search_results == True:
            configs = self.read_export_configs()
            result = self.writer.write_resources(resources, configs)
        else:
            self.writer.write_resources(dest_dir)
        return result

    def read_export_configs(self):
        '''
        Reads the export configuration file and adds an array for records to store property data
        '''
        configs = settings.EXPORT_CONFIG
        if configs != '':
            resource_export_configs = json.load(open(settings.EXPORT_CONFIG, 'r'))
            if self.format in resource_export_configs:
                configs = resource_export_configs[self.format]
                for key, val in configs['RESOURCE_TYPES'].iteritems():
                    configs['RESOURCE_TYPES'][key]['records'] = []
            else:
                configs = ''

        return configs

    def zip_response(self, files_for_export, zip_file_name=None, file_type=None):
        '''
        Given a list of export file names, zips up all the files with those names and returns and http response.
        '''
        buffer = StringIO()

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip:
            for f in files_for_export:
                f['outputfile'].seek(0)
                zip.writestr(f['name'], f['outputfile'].read())

        zip.close()
        buffer.flush()
        zip_stream = buffer.getvalue()
        buffer.close()

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=' + zip_file_name
        response['Content-length'] = str(len(zip_stream))
        response['Content-Type'] = 'application/zip'
        response.write(zip_stream)
        return response

    def get_resources_for_export(self, resourceids):
        resources = []
        if resourceids == None or resourceids == []:
            for resourceinstance in models.ResourceInstance.objects.all():
                resourceids.append(resourceinstance.resourceinstanceid)
        for resourceid in resourceids:
            if resourceid != uuid.UUID(str('40000000-0000-0000-0000-000000000000')):
                resource = {}
                resource['resourceinstanceid'] = resourceid
                resource['tiles'] = models.Tile.objects.filter(resourceinstance_id=resourceid)
                resources.append(resource)
        return JSONSerializer().serialize(resources)
