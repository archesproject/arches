from django.conf import settings
from arches.app.models.concept import Concept
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import GeometryCollection
from django.contrib.gis.geos import MultiPoint
from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.geos import MultiLineString
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
        child_entities += resource['_source']['dates']
        child_entities += resource['_source']['numbers']
        for mapping in field_map:
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
                    if entitytypeid == domain['entitytypeid'] and conceptid == '':
                        template_record[mapping['field_name']].append(domain['label'])
                    elif entitytypeid == domain['entitytypeid'] and conceptid != '':
                        for domain_type in domains:
                            if conceptid == domain_type['conceptid']:
                                if domain['entityid'] == domain_type['parentid']:
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
                v.sort()
                try:
                    template_record[k] = ("; ").join(v)
                except:
                    unicode_vals = [unicode(x) for x in v]
                    template_record[k] = ("; ").join(unicode_vals)
        return template_record

    def process_feature_geoms(self, properties, resource, geo_process='collection'):
        geoms = []
        result = None
        for g in resource['_source']['geometries']:
            geom = GEOSGeometry(JSONSerializer().serialize(g['value'], ensure_ascii=False))
            geoms.append(geom)
        if geo_process=='collection':
            geometry = GeometryCollection(geoms)
            result = {'type':'Feature','geometry': geometry,'properties': properties}
        elif geo_process == 'sorted':
            result = []
            sorted_geoms = {'points':[], 'lines':[], 'polys':[]}
            for geom in geoms:
                if geom.geom_typeid == 0:
                    sorted_geoms['points'].append(geom)
                if geom.geom_typeid == 1:
                    sorted_geoms['lines'].append(geom)
                if geom.geom_typeid == 3:
                    sorted_geoms['polys'].append(geom)
                if geom.geom_typeid == 4:
                    for feat in geom:
                        sorted_geoms['points'].append(feat)
                if geom.geom_typeid == 5:
                    for feat in geom:
                        sorted_geoms['lines'].append(feat)
                if geom.geom_typeid == 6:
                    for feat in geom:
                        sorted_geoms['polys'].append(feat)
            if len(sorted_geoms['points']) > 0:
                result.append({'type':'Feature','geometry': MultiPoint(sorted_geoms['points']),'properties': properties})
            if len(sorted_geoms['lines']) > 0:
                result.append({'type':'Feature','geometry': MultiLineString(sorted_geoms['lines']),'properties': properties})
            if len(sorted_geoms['polys']) > 0:
                result.append({'type':'Feature','geometry': MultiPolygon(sorted_geoms['polys']),'properties': properties})

        return result