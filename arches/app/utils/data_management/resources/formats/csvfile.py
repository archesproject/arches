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

    def write_resources(self, resources, resource_export_configs):
        """Using resource_export_configs from either a resource_export_mappings.json
        or the default mapping (which includes only resource type, primaryname and entityid)
        writes a csv file to a temporary directory for export.
        """
        using_default_mapping = False
        if resource_export_configs == '':
            resource_export_configs = self.default_mapping
            using_default_mapping = True
        for resource in resources:
            if resource['_type'] in resource_export_configs['RESOURCE_TYPES']:
                resource_export_configs['RESOURCE_TYPES'][resource['_type']]['records'].append(resource)
            if using_default_mapping:
                resource_export_configs['RECORDS'].append(resource)

        schema = resource_export_configs['SCHEMA']
        resource_types = resource_export_configs['RESOURCE_TYPES']
        csv_name_prefix = resource_export_configs['NAME']
        csv_header = [column['field_name'] for column in schema]
        csvs_for_export = []

        csv_records = []
        for resource_type, data in resource_types.iteritems():
            field_map = data['FIELD_MAP']
            for resource in data['records']:
                template_record = self.create_template_record(schema, resource, resource_type)
                complete_record = self.get_field_map_values(resource, template_record, field_map)
                csv_record = self.concatenate_value_lists(complete_record)
                csv_records.append(csv_record)
        if using_default_mapping:
            for resource in resource_export_configs['RECORDS']:
                complete_record = self.create_template_record(schema, resource, resource_type=None)
                csv_record = self.concatenate_value_lists(complete_record)
                csv_records.append(csv_record)

        iso_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        csv_name = os.path.join('{0}_{1}.{2}'.format(csv_name_prefix, iso_date, 'csv'))
        dest = StringIO()
        csvwriter = csv.DictWriter(dest, delimiter=',', fieldnames=csv_header)
        csvwriter.writeheader()
        csvs_for_export.append({'name':csv_name, 'outputfile': dest})
        for csv_record in csv_records:
            csvwriter.writerow({k:v.encode('utf8') for k,v in csv_record.items()})
        return csvs_for_export
