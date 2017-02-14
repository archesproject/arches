import csv
import os
import datetime
import json
import codecs
from format import Writer
from arches.app.models.concept import Concept
from arches.app.models.models import Node, Value
from arches.app.datatypes.datatypes import DataTypeFactory
from django.db.models import Q
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class CsvWriter(Writer):

    def __init__(self):
        super(CsvWriter, self).__init__()
        self.datatype_factory = DataTypeFactory()
        self.node_datatypes = {str(nodeid): datatype for nodeid, datatype in  Node.objects.values_list('nodeid', 'datatype').filter(~Q(datatype='semantic'), graph__isresource=True)}

    def transform_value_for_export(self, datatype, value, concept_export_value_type):
        datatype_instance = self.datatype_factory.get_instance(datatype)
        value = datatype_instance.transform_export_values(value)
        return value

    def write_resources(self, resources, resource_export_configs=None):
        csv_records = []
        other_group_records = []
        mapping = {}
        concept_export_value_lookup = {}
        for resource_export_config in resource_export_configs:
            for node in resource_export_config['nodes']:
                if node['file_field_name'] != '':
                    mapping[node['arches_nodeid']] = node['file_field_name']
                if 'concept_export_value' in node:
                    concept_export_value_lookup[node['arches_nodeid']] = node['concept_export_value']
        csv_header = ['ResourceID'] + mapping.values()
        csvs_for_export = []

        for resource in resources:
            csv_record = {}
            other_group_record = {}
            resourceid = resource['_source']['resourceinstanceid']
            resource_graphid = resource['_source']['graph_id']
            resource_security = resource['_source']['resourceinstancesecurity']
            csv_record['ResourceID'] = resourceid
            other_group_record['ResourceID'] = resourceid

            for tile in resource['_source']['tiles']:
                if tile['data'] != {}:
                    for k in tile['data'].keys():
                            if tile['data'][k] != '' and k in mapping:
                                if mapping[k] not in csv_record:
                                    concept_export_value_type = None
                                    if k in concept_export_value_lookup:
                                        concept_export_value_type = concept_export_value_lookup[k]
                                    value = self.transform_value_for_export(self.node_datatypes[k], tile['data'][k], concept_export_value_type)
                                    csv_record[mapping[k]] = value
                                    del tile['data'][k]
                                else:
                                    value = self.transform_value_for_export(self.node_datatypes[k], tile['data'][k], concept_export_value_type)
                                    other_group_record[mapping[k]] = value
                            else:
                                del tile['data'][k]

            csv_records.append(csv_record)
            if other_group_record != {}:
                other_group_records.append(other_group_record)


        csv_name_prefix = resource_export_configs[0]['resource_model_name']
        iso_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        csv_name = os.path.join('{0}_{1}.{2}'.format(csv_name_prefix, iso_date, 'csv'))
        dest = StringIO()
        csvwriter = csv.DictWriter(dest, delimiter=',', fieldnames=csv_header)
        csvwriter.writeheader()
        csvs_for_export.append({'name':csv_name, 'outputfile': dest})
        for csv_record in csv_records:
            csvwriter.writerow({k:str(v) for k,v in csv_record.items()})

        dest = StringIO()
        csvwriter = csv.DictWriter(dest, delimiter=',', fieldnames=csv_header)
        csvwriter.writeheader()
        csvs_for_export.append({'name':csv_name + '_groups', 'outputfile': dest})
        for csv_record in other_group_records:
            csvwriter.writerow({k:str(v) for k,v in csv_record.items()})

        return csvs_for_export
