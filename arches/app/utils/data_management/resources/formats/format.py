from django.conf import settings
from arches.app.models.concept import Concept
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import GeometryCollection
from arches.app.utils.betterJSONSerializer import JSONSerializer

class Writer(object):

    def __init__(self):
        self.resource_type_configs = settings.RESOURCE_TYPE_CONFIGS()
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
        domains = resource['_source']['domains']
        child_entities = resource['_source']['child_entities']
        for mapping in field_map:
            mapping = mapping[0]
            conceptid = ''
            if 'value_type' in mapping:
                conceptid = mapping['value_type']
            entitytypeid = mapping['entitytypeid']
            alternates = False
            alternate_entitytypeid = None
            alternate_values = None

            if 'alternate_entitytypeid' in mapping:
                alternates = True
                alternate_entitytypeid = mapping['alternate_entitytypeid']
                alternate_values = []

            if entitytypeid.endswith('E55') != True:
                for entity in child_entities:
                    if alternate_entitytypeid == entity['entitytypeid']:
                        alternate_values.append(entity['value'])
                    if entitytypeid == entity['entitytypeid'] and conceptid == '':
                        template_record[mapping['field_name']].append(entity['value'])
                    elif entitytypeid == entity['entitytypeid'] and conceptid != '':
                        for domain in domains:
                            if conceptid == domain['conceptid']:
                                if entity['entityid'] == domain['parentid']:
                                    template_record[mapping['field_name']].append(entity['value'])
            else:
                for domain in domains:
                    if entitytypeid == domain['entitytypeid']:
                        template_record[mapping['field_name']].append(domain['label'])
                    if alternate_entitytypeid == domain['entitytypeid']:
                        alternate_values.append(entity['value'])

            if alternates == True and len(template_record[mapping['field_name']]) == 0:
                if len(alternate_values) > 0:
                    template_record[mapping['field_name']] = alternate_values

        return template_record

    def concatenate_value_lists(self, template_record):
        """
        If multiple values are found for a column, joins them into a semi-colon concatenated string.
        """
        for k, v in template_record.iteritems():
            if type(v) == list:
                template_record[k] = ("; ").join(v)
        return template_record

    def process_feature_geoms(self, properties, resource):
        geoms = []
        for g in resource['_source']['geometries']:
            geom = GEOSGeometry(JSONSerializer().serialize(g['value'], ensure_ascii=False))
            geoms.append(geom)
        geometry = GeometryCollection(geoms)
        feature = {'type':'Feature','geometry': geometry,'properties': properties}
        return feature