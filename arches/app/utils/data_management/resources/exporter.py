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
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class ResourceExporter(object):

    def __init__(self, file_format):
        self.filetypes = {'csv': CsvWriter, 'kml': KmlWriter, 'shp': ShpWriter, 'json': JsonWriter}
        self.format = file_format
        self.writer = self.filetypes[file_format]()

    # def export(self, resources=None, zip=False, search_results=True, dest_dir=None):
    #     result=None
    #     if search_results == True and dest_dir is not None:
    #         result = self.writer.write_resources(resources, dest_dir)
    #     elif search_results == True:
    #         configs = self.read_export_configs()
    #         result = self.writer.write_resources(resources, configs)
    #     else:
    #         self.writer.write_resources(dest_dir)
    #     return result

    def export(self, data_dest=None, resources=None, configs=None):
        #resources should be changed to query
        configs = self.read_csv_export_configs(configs)
        business_data = self.get_search_results_for_export()
        csv_files = self.writer.write_resources(business_data, configs)

    def read_csv_export_configs(self, configs):
        '''
        Reads the export configuration file or object and adds an array for records to store property data
        '''
        if configs:
            resource_export_configs = json.load(open(configs, 'r'))
            resource_configs = [resource_export_configs]
            configs = resource_configs
        else:
            resource_configs = []
            configs = models.GraphXMapping.objects.values('mapping')
            for val in configs:
                resource_configs.append(val['mapping'])
            configs = resource_configs

        return configs

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
        relations = []
        business_data_dict = {}
        business_data_dict['business_data'] = {}

        if resourceids == None or resourceids == [] or resourceids == ['']:
            resourceids = []
            for resourceinstance in models.ResourceInstance.objects.all():
                resourceids.append(resourceinstance.resourceinstanceid)

        for resourceid in resourceids:
            if resourceid != uuid.UUID(str('40000000-0000-0000-0000-000000000000')):
                resourceid = uuid.UUID(str(resourceid))
                resource = {}
                resource['tiles'] = models.TileModel.objects.filter(resourceinstance_id=resourceid)
                resource['resourceinstance'] = models.ResourceInstance.objects.get(resourceinstanceid=resourceid)
                resources.append(resource)

        for relation in models.ResourceXResource.objects.all():
            relations.append(relation)

        business_data_dict['business_data']['resources'] = resources
        business_data_dict['business_data']['relations'] = relations

        return business_data_dict

    def get_search_results_for_export(self, query=None):
        se = SearchEngineFactory().create()
        query = Query(se, start=0, limit=10)
        results = query.search(index='resource', doc_type='')
        return results['hits']['hits']
