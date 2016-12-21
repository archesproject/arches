import os
import uuid
import importlib
import csv
import datetime
from time import time
from django.conf import settings
from django.db import connection, transaction
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.core.management.base import BaseCommand, CommandError
from arches.app.models.entity import Entity
from arches.app.models.resource import Resource
from arches.app.models.models import Concept
from arches.app.models.models import Value
from arches.app.models.models import ResourceXResource
from arches.app.models.concept import Concept
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.management.commands import utils
from optparse import make_option
from formats.archesfile import ArchesReader
from formats.archesjson import JsonReader
from formats.shpfile import ShapeReader
from arches.app.models.tile import Tile
from arches.app.models.models import ResourceInstance
from arches.app.models.models import FunctionXGraph
from arches.app.models.models import ResourceXResource
from arches.app.models.models import NodeGroup
from django.core.exceptions import ValidationError

def pre_import(tile, graph_id):
    for function in get_function_class_instances(tile, graph_id):
        try:
            function.on_import(tile)
        except NotImplementedError:
            pass
    return tile

def get_function_class_instances(tile, graph_id):
    ret = []
    functions = FunctionXGraph.objects.filter(graph_id=graph_id, config__triggering_nodegroups__contains=[tile['nodegroup_id']])
    for function in functions:
        mod_path = function.function.modulename.replace('.py', '')
        module = importlib.import_module('arches.app.functions.%s' % mod_path)
        func = getattr(module, function.function.classname)(function.config, tile['nodegroup_id'])
        ret.append(func)
    return ret

def validate_business_data(business_data):
    errors = []
    if type(business_data) == dict and business_data['resources']:
        for resource in business_data['resources']:
            graph_id = resource['resourceinstance']['graph_id']
            for tile in resource['tiles']:
                try:
                    pre_import(tile, graph_id)
                except ValidationError as e:
                    errors.append(e.args)
    return errors


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
        print '{0} of {1} resources saved'.format(self.resources_saved, self.resources)

    def update_tiles(self, count=1):
        self.total_tiles += count

    def update_tiles_saved(self, count=1):
        self.tiles_saved += count

    def update_relations_saved(self, count=1):
        self.relations_saved += count
        print self.tiles_saved

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

def import_business_data(business_data):
    reporter = ResourceImportReporter(business_data)
    try:
        for resource in business_data['resources']:
            if resource['resourceinstance'] != None:
                resource['resourceinstance']['resourceinstanceid'] = uuid.UUID(str(resource['resourceinstance']['resourceinstanceid']))
                resource['resourceinstance']['graphid'] = uuid.UUID(str(resource['resourceinstance']['graph_id']))

                resourceinstance, created = ResourceInstance.objects.update_or_create(
                    resourceinstanceid = resource['resourceinstance']['resourceinstanceid'],
                    graph_id = resource['resourceinstance']['graphid'],
                    resourceinstancesecurity = resource['resourceinstance']['resourceinstancesecurity']
                )
                if len(ResourceInstance.objects.filter(resourceinstanceid=resource['resourceinstance']['resourceinstanceid'])) == 1:
                    reporter.update_resources_saved()

            if resource['tiles'] != []:
                reporter.update_tiles(len(resource['tiles']))
                for tile in resource['tiles']:
                    Tile.objects.update_or_create(
                        resourceinstance = resourceinstance,
                        parenttile = Tile(uuid.UUID(str(tile['parenttile_id']))) if tile['parenttile_id'] else None,
                        nodegroup = NodeGroup(uuid.UUID(str(tile['nodegroup_id']))) if tile['nodegroup_id'] else None,
                        tileid = uuid.UUID(str(tile['tileid'])),
                        data = tile['data']
                    )
                    if len(Tile.objects.filter(tileid=tile['tileid'])) == 1:
                        reporter.update_tiles_saved()

    except (KeyError, TypeError) as e:
        print e

    try:
        for relation in business_data['relations']:
            relation['resourcexid'] = uuid.UUID(str(relation['resourcexid']))
            relation['resourceinstanceidfrom'] = ResourceInstance(uuid.UUID(str(relation['resourceinstanceidfrom'])))
            relation['resourceinstanceidto'] = ResourceInstance(uuid.UUID(str(relation['resourceinstanceidto'])))
            relation['relationshiptype'] = uuid.UUID(str(relation['relationshiptype']))

            relation = ResourceXResource.objects.update_or_create(
                resourcexid = relation['resourcexid'],
                resourceinstanceidfrom = relation['resourceinstanceidfrom'],
                resourceinstanceidto = relation['resourceinstanceidto'],
                notes = relation['notes'],
                relationshiptype = relation['relationshiptype'],
                datestarted = relation['datestarted'],
                dateended = relation['dateended']
            )
            # print vars(relation)
            relation.update_or_create()
            if len(ResourceXResource.objects.filter(resourcexid=relation['resourcexid'])) == 1:
                reporter.update_relations_saved()

    except (KeyError, TypeError) as e:
        print e

    reporter.report_results()

class ResourceLoader(object):

    def __init__(self):
        self.user = User()
        self.user.first_name = settings.ETL_USERNAME
        self.resources = []
        self.se = SearchEngineFactory().create()

    option_list = BaseCommand.option_list + (
        make_option('--source',
            action='store',
            dest='source',
            default='',
            help='.arches file containing resource records'),
         make_option('--format',
            action='store_true',
            default='arches',
            help='format extension that you would like to load: arches or shp'),
        )

    def load(self, source):
        file_name, file_format = os.path.splitext(source)
        archesjson = False
        if file_format == '.shp':
            reader = ShapeReader()
        elif file_format == '.arches':
            reader = ArchesReader()
            print '\nVALIDATING ARCHES FILE ({0})'.format(source)
            reader.validate_file(source)
        elif file_format == '.json':
            archesjson = True
            reader = JsonReader()

        start = time()
        resources = reader.load_file(source)

        print '\nLOADING RESOURCES ({0})'.format(source)
        relationships = None
        related_resource_records = []
        relationships_file = file_name + '.relations'
        elapsed = (time() - start)
        print 'time to parse {0} resources = {1}'.format(file_name, elapsed)
        results = self.resource_list_to_entities(resources, archesjson)
        if os.path.exists(relationships_file):
            relationships = csv.DictReader(open(relationships_file, 'r'), delimiter='|')
            for relationship in relationships:
                related_resource_records.append(self.relate_resources(relationship, results['legacyid_to_entityid'], archesjson))
        else:
            print 'No relationship file'

        #self.se.bulk_index(self.resources)


    def resource_list_to_entities(self, resource_list, archesjson=False):
        '''Takes a collection of imported resource records and saves them as arches entities'''

        start = time()
        d = datetime.datetime.now()
        load_id = 'LOADID:{0}-{1}-{2}-{3}-{4}-{5}'.format(d.year, d.month, d.day, d.hour, d.minute, d.microsecond) #Should we append the timestamp to the exported filename?

        ret = {'successfully_saved':0, 'failed_to_save':[]}
        schema = None
        current_entitiy_type = None
        legacyid_to_entityid = {}
        errors = []
        progress_interval = 250
        for count, resource in enumerate(resource_list):

            if count >= progress_interval and count % progress_interval == 0:
                print count, 'of', len(resource_list), 'loaded'


            if archesjson == False:
                masterGraph = None
                if current_entitiy_type != resource.entitytypeid:
                    schema = Resource.get_mapping_schema(resource.entitytypeid)

                master_graph = self.build_master_graph(resource, schema)
                self.pre_save(master_graph)

                try:
                    uuid.UUID(resource.resource_id)
                    entityid = resource.resource_id
                except(ValueError):
                    entityid = ''

                master_graph.save(user=self.user, note=load_id, resource_uuid=entityid)
                master_graph.index()
                resource.entityid = master_graph.entityid
                legacyid_to_entityid[resource.resource_id] = master_graph.entityid

            else:
                new_resource = Resource(resource)
                new_resource.save(user=self.user, note=load_id, resource_uuid=new_resource.entityid)
                try:
                    new_resource.index()
                except:
                    print 'Could not index resource. This may be because the valueid of a concept is not in the database.'
                legacyid_to_entityid[new_resource.entityid] = new_resource.entityid

            ret['successfully_saved'] += 1


        ret['legacyid_to_entityid'] = legacyid_to_entityid
        elapsed = (time() - start)
        print len(resource_list), 'resources loaded'
        if len(resource_list) > 0:
            print 'total time to etl = %s' % (elapsed)
            print 'average time per entity = %s' % (elapsed/len(resource_list))
            print 'Load Identifier =', load_id
            print '***You can reverse this load with the following command:'
            print 'python manage.py packages -o remove_resources --load_id', load_id
        return ret

    def build_master_graph(self, resource, schema):
        master_graph = None
        entity_data = []

        if len(entity_data) > 0:
            master_graph = entity_data[0]
            for mapping in entity_data[1:]:
                master_graph.merge(mapping)

        for group in resource.groups:
            entity_data2 = []
            for row in group.rows:
                entity = Resource()
                entity.create_from_mapping(row.resourcetype, schema[row.attributename]['steps'], row.attributename, row.attributevalue)
                entity_data2.append(entity)

            mapping_graph = entity_data2[0]
            for mapping in entity_data2[1:]:
                mapping_graph.merge(mapping)

            if master_graph == None:
                master_graph = mapping_graph
            else:
                node_type_to_merge_at = schema[row.attributename]['mergenodeid']
                master_graph.merge_at(mapping_graph, node_type_to_merge_at)

        return master_graph

    def pre_save(self, master_graph):
        pass

    def relate_resources(self, relationship, legacyid_to_entityid, archesjson):
        start_date = None if relationship['START_DATE'] in ('', 'None') else relationship['START_DATE']
        end_date = None if relationship['END_DATE'] in ('', 'None') else relationship['END_DATE']

        if archesjson == False:
            relationshiptype_concept = Concept.objects.get(legacyoid = relationship['RELATION_TYPE'])
            concept_value = Value.objects.filter(concept = relationshiptype_concept.conceptid).filter(valuetype = 'prefLabel')
            entityid1 = legacyid_to_entityid[relationship['RESOURCEID_FROM']]
            entityid2 = legacyid_to_entityid[relationship['RESOURCEID_TO']]

        else:
            concept_value = Value.objects.filter(valueid = relationship['RELATION_TYPE'])
            entityid1 = relationship['RESOURCEID_FROM']
            entityid2 = relationship['RESOURCEID_TO']

        related_resource_record = ResourceXResource(
            entityid1 = entityid1,
            entityid2 = entityid2,
            notes = relationship['NOTES'],
            relationshiptype = concept_value[0].valueid,
            datestarted = start_date,
            dateended = end_date,
            )

        related_resource_record.save()
        self.se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(related_resource_record), idfield='resourcexid')
