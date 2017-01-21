from django.conf import settings
import csv
import os
import datetime
from arches.app.models.concept import Concept
import codecs
from format import Writer

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class CsvWriter(Writer):

    def __init__(self):
        super(CsvWriter, self).__init__()

    # def old_write_resources(self, resources, resource_export_configs):
    #     """Using resource_export_configs from either a resource_export_mappings.json
    #     or the default mapping (which includes only resource type, primaryname and entityid)
    #     writes a csv file to a temporary directory for export.
    #     """
    #     using_default_mapping = False
    #     if resource_export_configs == '':
    #         resource_export_configs = self.default_mapping
    #         using_default_mapping = True
    #     for resource in resources:
    #         if resource['_type'] in resource_export_configs['RESOURCE_TYPES']:
    #             resource_export_configs['RESOURCE_TYPES'][resource['_type']]['records'].append(resource)
    #         if using_default_mapping:
    #             resource_export_configs['RECORDS'].append(resource)
    #
    #     schema = resource_export_configs['SCHEMA']
    #     resource_types = resource_export_configs['RESOURCE_TYPES']
    #     csv_name_prefix = resource_export_configs['NAME']
    #     csv_header = [column['field_name'] for column in schema]
    #     csvs_for_export = []
    #
    #     csv_records = []
    #     for resource_type, data in resource_types.iteritems():
    #         field_map = data['FIELD_MAP']
    #         for resource in data['records']:
    #             template_record = self.create_template_record(schema, resource, resource_type)
    #             complete_record = self.get_field_map_values(resource, template_record, field_map)
    #             csv_record = self.concatenate_value_lists(complete_record)
    #             csv_records.append(csv_record)
    #     if using_default_mapping:
    #         for resource in resource_export_configs['RECORDS']:
    #             complete_record = self.create_template_record(schema, resource, resource_type=None)
    #             csv_record = self.concatenate_value_lists(complete_record)
    #             csv_records.append(csv_record)
    #
    #     iso_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #     csv_name = os.path.join('{0}_{1}.{2}'.format(csv_name_prefix, iso_date, 'csv'))
    #     dest = StringIO()
    #     csvwriter = csv.DictWriter(dest, delimiter=',', fieldnames=csv_header)
    #     csvwriter.writeheader()
    #     csvs_for_export.append({'name':csv_name, 'outputfile': dest})
    #     for csv_record in csv_records:
    #         csvwriter.writerow({k:v.encode('utf8') for k,v in csv_record.items()})
    #     return csvs_for_export

    def write_resources(self, resources, resource_export_configs=None):
        csv_records = []
        other_group_records = []
        mapping = {}
        for node in resource_export_configs['nodes']:
            mapping[node['arches_nodeid']] = node['file_field_name']
        csv_header = mapping.values()
        csv_header.append('ResourceID')
        csvs_for_export = []

        for resource in resources['business_data']['resources']:
        # for resource in resources:
            csv_record = {}
            other_group_record = {}
            # resourceid = resource['_source']['resourceinstanceid']
            resourceid = resource['resourceinstance'].resourceinstanceid
        #     resource_graphid = resource['_source']['graph_id']
            resource_graphid = resource['resourceinstance'].graph_id
        #     resource_security = resource['_source']['resourceinstancesecurity']
            csv_record['ResourceID'] = resourceid
            other_group_record['ResourceID'] = resourceid

        #     for tile in resource['_source']['tiles']:
            for tile in resource['tiles']:
                # if tile['data'] != {}:
                if tile.data != {}:
                    # for k in tile['data'].keys():
                    for k in tile.data.keys():
                            # if tile['data'][k] != '' and k in mapping:
                            if tile.data[k] != '' and k in mapping:
                                if mapping[k] not in csv_record:
                                    # csv_record[mapping[k]] = tile['data'][k]
                                    csv_record[mapping[k]] = tile.data[k]
                                    # del tile['data'][k]
                                    del tile.data[k]
                                else:
                                    # other_group_record[mapping[k]] = tile['data'][k]
                                    other_group_record[mapping[k]] = tile.data[k]
                            else:
                                # del tile['data'][k]
                                del tile.data[k]
        #
            csv_records.append(csv_record)
            if other_group_record != {}:
                other_group_records.append(other_group_record)


        csv_name_prefix = 'taco'
        iso_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        csv_name = os.path.join('{0}_{1}.{2}'.format(csv_name_prefix, iso_date, 'csv'))
        dest = StringIO()
        csvwriter = csv.DictWriter(dest, delimiter=',', fieldnames=csv_header)
        csvwriter.writeheader()
        csvs_for_export.append({'name':csv_name, 'outputfile': dest})
        for csv_record in csv_records:
            csvwriter.writerow({k:str(v).encode('utf8') for k,v in csv_record.items()})

        dest = StringIO()
        csvwriter = csv.DictWriter(dest, delimiter=',', fieldnames=csv_header)
        csvwriter.writeheader()
        csvs_for_export.append({'name':csv_name, 'outputfile': dest})
        for csv_record in other_group_records:
            csvwriter.writerow({k:str(v).encode('utf8') for k,v in csv_record.items()})
