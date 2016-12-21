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
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from copy import deepcopy

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
        func = getattr(module, function.function.classname)(function.config)
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

def import_business_data(business_data, mapping=None):
    if mapping == None or mapping == '':
        if type(business_data) == dict and business_data['resources']:
            for resource in business_data['resources']:
                if resource['resourceinstance'] != None:
                    resource['resourceinstance']['resourceinstanceid'] = uuid.UUID(str(resource['resourceinstance']['resourceinstanceid']))
                    resource['resourceinstance']['graphid'] = uuid.UUID(str(resource['resourceinstance']['graph_id']))

                    resourceinstance = ResourceInstance.objects.update_or_create(
                        resourceinstanceid = resource['resourceinstance']['resourceinstanceid'],
                        graph_id = resource['resourceinstance']['graphid'],
                        resourceinstancesecurity = resource['resourceinstance']['resourceinstancesecurity']
                    )

                if resource['tiles'] != []:
                    for tile in resource['tiles']:
                        tile['parenttile_id'] = uuid.UUID(str(tile['parenttile_id'])) if tile['parenttile_id'] else None
                        tile['nodegroup_id'] = NodeGroup(uuid.UUID(str(tile['nodegroup_id']))) if tile['nodegroup_id'] else None
                        tile['resourceinstance_id'] = ResourceInstance(uuid.UUID(str(tile['resourceinstance_id'])))
                        tile['tileid'] = uuid.UUID(str(tile['tileid']))

                        tile = Tile.objects.update_or_create(
                            resourceinstance = tile['resourceinstance_id'],
                            parenttile = Tile(uuid.UUID(str(tile['parenttile_id']))) if tile['parenttile_id'] else None,
                            nodegroup = tile['nodegroup_id'],
                            tileid = tile['tileid'],
                            data = tile['data']
                        )

        if type(business_data) == dict and business_data['relations']:
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
                relation.update_or_create()
    else:
        if type(business_data) == dict and business_data['resources']:
            blanktilecache = {}
            target_nodegroup_cardinalities = {}
            for nodegroup in JSONSerializer().serializeToPython(NodeGroup.objects.all()):
                target_nodegroup_cardinalities[nodegroup['nodegroupid']] = nodegroup['cardinality']

            def replace_source_nodeid(tiles, mapping):
                for tile in tiles:
                    for sourcekey in tile['data'].keys():
                        for row in mapping:
                            if row['sourcenodeid'] == sourcekey:
                                tile['data'][row['targetnodeid']] = tile['data'][sourcekey]
                                del tile['data'][sourcekey]
                    if sourcekey in tile['data'].keys():
                        del tile['data'][sourcekey]
                return tiles

            def cache(blank_tile):
                if blank_tile.data != {}:
                    for tile in blank_tile.tiles.values():
                        if isinstance(tile, Tile):
                            for key in tile.data.keys():
                                blanktilecache[key] = blank_tile
                # else:
                #     print blank_tile

            for resource in business_data['resources']:
                parenttileids = []
                populated_tiles = []
                resourceinstanceid = uuid.uuid4()
                populated_nodegroups = []

                for row in mapping:
                    if resource['resourceinstance']['graph_id'] == row['sourceresourcemodelid']:
                        target_resource_model = row['targetresourcemodelid']

                for tile in resource['tiles']:
                    if tile['data'] != {}:

                        def get_tiles(tile):
                            if tile['parenttile_id'] != None:
                                if tile['parenttile_id'] not in parenttileids:
                                    parenttileids.append(tile['parenttile_id'])
                                    ret = []
                                    for sibling_tile in resource['tiles']:
                                        if sibling_tile['parenttile_id'] == tile['parenttile_id']:
                                            ret.append(sibling_tile)
                                else:
                                    ret = None
                            else:
                                ret = [tile]

                            #deletes nodes that don't have values
                            if ret is not None:
                                for tile in ret:
                                    for key, value in tile['data'].iteritems():
                                        if value == "":
                                            del tile['data'][key]
                            return ret

                        def get_blank_tile(sourcetilegroup):
                            if len(sourcetilegroup) > 0:
                                if sourcetilegroup[0]['data'] != {}:
                                    if sourcetilegroup[0]['data'].keys()[0] not in blanktilecache:
                                        blank_tile = Tile.get_blank_tile(tiles[0]['data'].keys()[0], resourceid=resourceinstanceid)
                                        cache(blank_tile)
                                    else:
                                        blank_tile = blanktilecache[tiles[0]['data'].keys()[0]]
                                else:
                                    blank_tile = None
                            return blank_tile

                        tiles = get_tiles(tile)
                        if tiles is not None:
                            mapped_tiles = replace_source_nodeid(tiles, mapping)
                            blank_tile = get_blank_tile(tiles)

                            # def populate_tile_og(sourcetilegroup, target_tile):
                            #     need_new_tile = False
                            #     for source_tile in sourcetilegroup:
                            #         for nodeid in source_tile['data'].keys():
                            #             # check data array in first tile
                            #             if target_tile.data != None:
                            #                 if nodeid in target_tile.data.keys():
                            #                     target_tile.data[nodeid] = source_tile['data'][nodeid]
                            #                     del source_tile['data'][nodeid]
                            #             elif target_tile.tiles != None:
                            #                 # check if child tiles then check their data arrays
                            #                 for targetchildtiles in target_tile.tiles.values():
                            #                     for targetchildtile in targetchildtiles:
                            #                         if isinstance(targetchildtile, Tile):
                            #                             if nodeid in targetchildtile.data.keys():
                            #                                 targetchildtile.data[nodeid] = source_tile['data'][nodeid]
                            #                                 del source_tile['data'][nodeid]
                            #     populated_tiles.append(target_tile)
                            #
                            #     for source_tile in sourcetilegroup:
                            #         if len(source_tile['data'].keys()) > 0:
                            #             need_new_tile = True
                            #
                            #     if need_new_tile:
                            #         populate_tile(sourcetilegroup, get_blank_tile(sourcetilegroup))

                            def populate_tile(sourcetilegroup, target_tile):
                                need_new_tile = False
                                target_tile_cardinality = target_nodegroup_cardinalities[str(target_tile.nodegroup_id)]
                                # print target_tile.nodegroup_id
                                if str(target_tile.nodegroup_id) not in populated_nodegroups:
                                    if target_tile.data != None:
                                        for source_tile in sourcetilegroup:
                                            for nodeid in source_tile['data'].keys():
                                                if nodeid in target_tile.data.keys():
                                                    target_tile.data[nodeid] = source_tile['data'][nodeid]
                                                    del source_tile['data'][nodeid]

                                    elif target_tile.tiles != None:
                                        for nodegroupid, childtile in target_tile.tiles.iteritems():
                                            prototype_tile = childtile.pop()
                                            prototype_tile.tileid = None

                                            for source_tile in sourcetilegroup:
                                                prototype_tile_copy = deepcopy(prototype_tile)
                                                for nodeid in source_tile['data'].keys():
                                                    if nodeid in prototype_tile.data.keys():
                                                        prototype_tile_copy.data[nodeid] = source_tile['data'][nodeid]
                                                        del source_tile['data'][nodeid]
                                                childtile.append(prototype_tile_copy)
                                            if target_tile_cardinality == 1:
                                                break

                                    populated_tiles.append(target_tile)

                                    for source_tile in sourcetilegroup:
                                        if len(source_tile['data'].keys()) > 0:
                                            need_new_tile = True

                                    if need_new_tile:
                                        populate_tile(sourcetilegroup, get_blank_tile(sourcetilegroup))

                                    if target_tile_cardinality == '1':
                                        populated_nodegroups.append(str(target_tile.nodegroup_id))
                                else:
                                    print target_tile.nodegroup_id
                                    target_tile = None

                            if blank_tile != None:
                                populate_tile(mapped_tiles, blank_tile)

                newresourceinstance = ResourceInstance.objects.create(
                    resourceinstanceid = resourceinstanceid,
                    graph_id = target_resource_model,
                    resourceinstancesecurity = None
                )
                # print JSONSerializer().serialize(populated_tiles)
                for populated_tile in populated_tiles:
                    populated_tile.resourceinstance = newresourceinstance
                    populated_tile.save()



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
