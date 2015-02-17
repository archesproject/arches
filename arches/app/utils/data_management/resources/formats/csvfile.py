from django.conf import settings
import csv
import os
import datetime
from arches.app.models.concept import Concept
import codecs

class CsvWriter:

    def __init__(self):
        self.resource_type_configs = settings.RESOURCE_TYPE_CONFIGS()
        self.legacy_concept_id_mapping = {}
        self.default_mapping = {
            "NAME": "ArchesResourceExport",
            "SCHEMA": [
                {"field_name":"PRIMARY NAME", "source":"primaryname"},
                {"field_name":"ARCHES ID", "source":"entityid"},
                {"field_name":"ARCHES RESOURCE TYPE", "source":"resource_name"},
            ],
            "RESOURCE_TYPES" : {},
            "RECORDS":[]
        }  

    def write_resources(self, resources, resource_export_configs, export_temp_directory):
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
        csv_header = self.get_column_header(schema)
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

        iso_date = datetime.datetime.now().isoformat().replace('T', '_')[0:-7].replace(':','-')
        csv_name = os.path.join(settings.PACKAGE_ROOT, export_temp_directory, '{0} {1}'.format(csv_name_prefix, iso_date))
        with open(csv_name + '.csv', 'w') as dest:
            csvwriter = csv.DictWriter(dest, delimiter=',', fieldnames=csv_header)
            csvwriter.writeheader()
            csvs_for_export.append(csv_name)
            for csv_record in csv_records:
                csvwriter.writerow({k:v.encode('utf8') for k,v in csv_record.items()})
        return csvs_for_export

    def get_column_header(self, schema):
        """
        Create the column header from the export mapping schema
        """
        header = []
        for column in schema:
            header.append(column['field_name'])
        return header

    def create_template_record(self, schema, resource, resource_type):
        """
        Creates an empty record from the export mapping schema and populates its values
        with resource data that does not require the export field mapping - these include
        entityid, primaryname and entitytypeid.
        """
        record = {}
        for column in schema:
            if column['source'] == 'resource_name':
                if resource_type != None:
                    record[column['field_name']] = self.resource_type_configs[resource_type]['name']
                else:
                    record[column['field_name']] = resource['_source']['entitytypeid']
            elif column['source'] in ('primaryname', 'entitytypeid', 'entityid'):
                record[column['field_name']] = resource['_source'][column['source']]
            elif column['source'] == 'alternatename':
                record[column['field_name']] = []
                for entity in resource['_source']['child_entities']:
                    primaryname_type = self.resource_type_configs[resource_type]['primary_name_lookup']['entity_type']
                    if entity['entitytypeid'] == primaryname_type and entity['label'] != resource['_source']['primaryname']:
                        record[column['field_name']].append(entity['label'])
            else:
                record[column['field_name']] = []
        return record

    def get_field_map_values(self, resource, template_record, field_map):
        """
        For a given resource, loops over its field map in the export mappings and
        collects values that correspond each entitytypeid in the field map.  Inserts those
        values into the template record's corresponding list of values.
        """
        for mapping in field_map:
            mapping = mapping[0]
            conceptid = ''
            if 'value_type' in mapping:
                if mapping['value_type'] in self.legacy_concept_id_mapping:
                    conceptid = self.legacy_concept_id_mapping[mapping['value_type']]
                else:
                    conceptid = Concept().get(legacyoid=mapping['value_type']).id
                    self.legacy_concept_id_mapping[mapping['value_type']] = conceptid
            entitytypeid = mapping['entitytypeid']
            for entity in resource['_source']['child_entities']:
                if entitytypeid == entity['entitytypeid'] and conceptid == '':
                    template_record[mapping['field_name']].append(entity['value'])
                elif entitytypeid == entity['entitytypeid'] and conceptid != '':
                    for domain in resource['_source']['domains']:
                        if entity['entityid'] == domain['parentid'] and conceptid == domain['conceptid']:
                            template_record[mapping['field_name']].append(entity['value'])
                if len(template_record[mapping['field_name']]) == 0:
                    for domain in resource['_source']['domains']:
                        if domain['entitytypeid'] == entitytypeid:
                            template_record[mapping['field_name']].append(domain['label'])

        return template_record

    def concatenate_value_lists(self, template_record):
        """
        If multiple values are found for a column, joins them into a semi-colon concatenated string.
        """
        for k, v in template_record.iteritems():
            if type(v) == list:
                template_record[k] = ("; ").join(v)
        return template_record