import os
import csv
import zipfile
import datetime
import json
import glob
import uuid
from django.db.models import Q
from formats.csvfile import CsvWriter
from formats.archesjson import JsonWriter #Writes full resource instances rather than search results
from django.http import HttpResponse
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class ResourceExporter(object):

    def __init__(self, file_format):
        self.filetypes = {'csv': CsvWriter, 'json': JsonWriter}
        self.format = file_format
        self.writer = self.filetypes[file_format]()

    def export(self, data_dest=None, query=None, configs=None, graph=None, single_file=False):
        #business data export
        #resources should be changed to query
        configs = self.read_export_configs(configs)
        business_data = self.get_resources_for_export(query, configs, graph)
        resources = self.writer.write_resources(business_data, configs, single_file)

        #relation export
        if len(business_data) > 0:
            if isinstance(business_data[0], dict):
                resourceids = []
                for resource in business_data:
                    resourceids.append(uuid.UUID(resource['_source']['resourceinstanceid']))
            elif isinstance(business_data[0], str):
                resourceids = [uuid.UUID(r) for r in business_data]
        if graph != settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID:
            relations = self.get_relations_for_export(resourceids)
            relations_file_name = resources[0]['name'].split('.')[0]
            relations_file = self.write_relations(relations, relations_file_name)
            resources.extend(relations_file)

        return resources

    def read_export_configs(self, configs):
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

    def get_resources_for_export(self, query=None, configs=None, graph=None):
        if query == None and graph == None and configs != []:
            results = {}
            results['hits']= {}
            results['hits']['hits'] = []
            resource_model_id = configs[0]['resource_model_id']

            resource_instances = models.ResourceInstance.objects.filter(graph_id=resource_model_id)
            for resource_instance in resource_instances:
                resource_instance_dict = {}
                resource_instance_dict['_source'] = JSONSerializer().serializeToPython(resource_instance)
                resource_instance_dict['_source']['tiles'] = JSONSerializer().serializeToPython(models.TileModel.objects.filter(resourceinstance_id=resource_instance_dict['_source']['resourceinstanceid']))
                results['hits']['hits'].append(resource_instance_dict)
            resources = results['hits']['hits']
        elif graph != None and query == None:
            resources = [str(resourceid) for resourceid in models.ResourceInstance.objects.filter(graph_id=graph).values_list('resourceinstanceid', flat=True)]
        else:
            se = SearchEngineFactory().create()
            query = query
            results = query.search(index='resource', doc_type='')
            resources = results['hits']['hits']

        return resources

    def get_relations_for_export(self, resourceids):
        relations = []

        for relation in models.ResourceXResource.objects.filter(Q(resourceinstanceidfrom__in=resourceids)|Q(resourceinstanceidto__in=resourceids)):
            if any(r.resourcexid == relation.resourcexid for r in relations) == False:
                relation.__dict__['relationshiptype'] = relation.__dict__.pop('relationshiptype_id')
                relation.__dict__['resourceinstanceidfrom'] = relation.__dict__.pop('resourceinstanceidfrom_id')
                relation.__dict__['resourceinstanceidto'] = relation.__dict__.pop('resourceinstanceidto_id')
                relation.__dict__['datestarted'] = relation.__dict__['datestarted'] if relation.__dict__['datestarted'] != None else ''
                relation.__dict__['dateended'] = relation.__dict__['dateended'] if relation.__dict__['dateended'] != None else ''
                relation.__dict__.pop('_state')
                relations.append(relation)

        return relations

    def write_relations(self, relations, file_name):
        relations_for_export = []
        csv_header = ['resourcexid','resourceinstanceidfrom','resourceinstanceidto','relationshiptype','datestarted','dateended','notes']
        csv_name_prefix = file_name
        csv_name = os.path.join('{0}.{1}'.format(csv_name_prefix, 'relations'))
        dest = StringIO()
        csvwriter = csv.DictWriter(dest, delimiter=',', fieldnames=csv_header)
        csvwriter.writeheader()
        relations_for_export.append({'name':csv_name, 'outputfile': dest})
        for relation in relations:
            csvwriter.writerow({k:str(v) for k,v in relation.__dict__.items()})

        return relations_for_export
