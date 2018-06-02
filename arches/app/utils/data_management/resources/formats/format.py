import os
import uuid
import shutil
import datetime
from arches.app.models.concept import Concept
from arches.app.models import models
from arches.app.models.models import ResourceXResource
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import GeometryCollection
from django.contrib.gis.geos import MultiPoint
from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.geos import MultiLineString
from django.db import connection, transaction
from django.utils.translation import ugettext as _


class MissingGraphException(Exception):
     def __init__(self, value=None):
         self.value = value
     def __str__(self):
         return repr(self.value)


class ResourceImportReporter:
    def __init__(self, business_data):
        self.resources = 0
        self.total_tiles = 0
        self.resources_saved = 0
        self.tiles_saved = 0
        self.relations_saved = 0
        self.relations = 0

        if 'resources' in business_data:
            self.resources = len(business_data['resources'])

        if 'relations' in business_data:
            self.relations = len(business_data['relations'])

    def update_resources_saved(self, count=1):
        self.resources_saved += count
        print _('{0} of {1} resources saved'.format(self.resources_saved, self.resources))

    def update_tiles(self, count=1):
        self.total_tiles += count

    def update_tiles_saved(self, count=1):
        self.tiles_saved += count

    def update_relations_saved(self, count=1):
        self.relations_saved += count
        print _('{0} of {1} relations saved'.format(self.relations_saved, self.relations))

    def report_results(self):
        if self.resources > 0:
            result = "Resources for Import: {0}, Resources Saved: {1}, Tiles for Import: {2}, Tiles Saved: {3}, Relations for Import: {4}, Relations Saved: {5}"
            print result.format(
                    self.resources,
                    self.resources_saved,
                    self.total_tiles,
                    self.tiles_saved,
                    self.relations,
                    self.relations_saved
                    )

class Reader(object):

    def __init__(self):
        self.errors = []

    def validate_datatypes(self, record):
        pass

    def import_business_data(self):
        pass

    def import_relations(self, relations=None):

        def get_resourceid_from_legacyid(legacyid):
            ret = Resource.objects.filter(legacyid=legacyid)

            if len(ret) > 1 or len(ret) == 0:
                return None
            else:
                return ret[0].resourceinstanceid

        for relation_count, relation in enumerate(relations):
            relation_count = relation_count + 2
            if relation_count % 500 == 0:
                print '{0} relations saved'.format(str(relation_count))


            def validate_resourceinstanceid(resourceinstanceid, key):
                # Test if resourceinstancefrom is a uuid it is for a resource or if it is not a uuid that get_resourceid_from_legacyid found a resourceid.
                try:
                    # Test if resourceinstanceid from relations file is a UUID.
                    newresourceinstanceid = uuid.UUID(resourceinstanceid)
                    try:
                        # If resourceinstanceid is a UUID then test that it is assoicated with a resource instance
                        Resource.objects.get(resourceinstanceid=resourceinstanceid)
                    except:
                        # If resourceinstanceid is not associated with a resource instance then set resourceinstanceid to None
                        newresourceinstanceid = None
                except:
                    # If resourceinstanceid is not UUID then assume it's a legacyid and pass it into get_resourceid_from_legacyid function
                    newresourceinstanceid = get_resourceid_from_legacyid(resourceinstanceid)

                # If resourceinstancefrom is None then either:
                # 1.) a legacyid was passed in and get_resourceid_from_legacyid could not find a resource or found multiple resources with the indicated legacyid or
                # 2.) a uuid was passed in and it is not associated with a resource instance
                if newresourceinstanceid == None:
                    errors = []
                    # self.errors.append({'datatype':'legacyid', 'value':relation[key], 'source':'', 'message':'either multiple resources or no resource have this legacyid\n'})
                    errors.append({'type':'ERROR', 'message': 'Relation not created, either zero or multiple resources found with legacyid: {0}'.format(relation[key])})
                    if len(errors) > 0:
                        self.errors += errors

                return newresourceinstanceid

            resourceinstancefrom = validate_resourceinstanceid(relation['resourceinstanceidfrom'], 'resourceinstanceidfrom')
            resourceinstanceto = validate_resourceinstanceid(relation['resourceinstanceidto'], 'resourceinstanceidto')
            if relation['datestarted'] == '' or relation['datestarted'] == 'None':
                relation['datestarted'] = None
            if relation['dateended'] == '' or relation['dateended'] == 'None':
                relation['dateended'] = None

            if resourceinstancefrom != None and resourceinstanceto != None:
                relation = ResourceXResource(
                    resourceinstanceidfrom = Resource(resourceinstancefrom),
                    resourceinstanceidto = Resource(resourceinstanceto),
                    relationshiptype = unicode(relation['relationshiptype']),
                    datestarted = relation['datestarted'],
                    dateended = relation['dateended'],
                    notes = relation['notes']
                )
                relation.save()

        self.report_errors()

    def report_errors(self):
        if len(self.errors) == 0:
            print _("No import errors")
        else:
            print _("***** Errors occured during import. Some data may not have been imported. For more information, check resource import error log: ") + settings.RESOURCE_IMPORT_LOG
            log_nums = [0]
            if os.path.isfile(settings.RESOURCE_IMPORT_LOG):
                if os.path.getsize(settings.RESOURCE_IMPORT_LOG)/1000000 > 5:
                    for file in os.listdir(os.path.dirname(settings.RESOURCE_IMPORT_LOG)):
                        try:
                            log_nums.append(int(file.split('.')[-1]))
                        except:
                            pass

                    archive_log_num = str(max(log_nums) + 1)
                    shutil.copy2(settings.RESOURCE_IMPORT_LOG , settings.RESOURCE_IMPORT_LOG.split('.')[0] + '_' + archive_log_num + '.' + settings.RESOURCE_IMPORT_LOG.split('.')[-1])
                    f = open(settings.RESOURCE_IMPORT_LOG, 'w')
                else:
                    f = open(settings.RESOURCE_IMPORT_LOG, 'a')
            else:
                f = open(settings.RESOURCE_IMPORT_LOG, 'w')

            for error in self.errors:
                timestamp = (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime('%a %b %d %H:%M:%S %Y')
                try:
                    f.write(_(timestamp + ' ' + '{0}: {1}\n'.format(error['type'], error['message'])))
                except TypeError as e:
                    f.write(timestamp + ' ' + e + unicode(error))


class Writer(object):

    def __init__(self, **kwargs):
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
        self.resourceinstances = {}
        self.file_prefix = ''
        self.file_name = ''
        self.tiles = []
        self.graph_id = None
        self.graph_model = None

    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        """
        Returns a list of dictionaries with the following format:

        {'name':file name, 'outputfile': a SringIO buffer of resource instance data in the specified format}

        """

        self.get_tiles(graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs)

    def write_resource_relations(self):
        """
        Returns a list of dictionaries with the following format:

        {'name':file name, 'outputfile': a SringIO buffer of resource relations data in the specified format}

        """

        pass

    def get_tiles(self, graph_id=None, resourceinstanceids=None, **kwargs):
        """
        Returns a dictionary of tiles keyed by their resourceinstanceid

        {
            'resourcs instance UUID': [tile list],
            ...
        }

        """

        user = kwargs.get('user', None)
        permitted_nodegroups = []
        if user:
            permitted_nodegroups = [str(nodegroup.pk) for nodegroup in get_nodegroups_by_perm(user, 'models.read_nodegroup')]

        if (graph_id is None or graph_id is False) and resourceinstanceids is None:
            raise MissingGraphException(_("Must supply either a graph id or a list of resource instance ids to export"))
        
        if graph_id:
            filters = {'resourceinstance__graph_id':graph_id}
            if user:
                filters['nodegroup_id__in'] = permitted_nodegroups
            self.tiles = models.TileModel.objects.filter(**filters)
            self.graph_id = graph_id
        else:
            filters = {'resourceinstance_id__in':resourceinstanceids}
            if user:
                filters['nodegroup_id__in'] = permitted_nodegroups
            self.tiles = models.TileModel.objects.filter(**filters)
            try:
                self.graph_id = self.tiles[0].resourceinstance.graph_id
            except:
                self.graph_id = models.ResourceInstance.objects.get(resourceinstanceid=resourceinstanceids[0]).graph_id


        iso_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.graph_model = models.GraphModel.objects.get(graphid=self.graph_id)
        self.file_prefix = self.graph_model.name.replace(' ', '_')
        self.file_name = '{0}_{1}'.format(self.file_prefix, iso_date)
        
        for tile in self.tiles:
            try:
                self.resourceinstances[tile.resourceinstance_id].append(tile)
            except:
                self.resourceinstances[tile.resourceinstance_id] = []
                self.resourceinstances[tile.resourceinstance_id].append(tile)

        return self.resourceinstances

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
