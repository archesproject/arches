import os
from time import time
import datetime
from django.conf import settings
from django.db import connection, transaction
from arches.app.models.entity import Entity
from arches.app.models.models import Concepts
from arches.app.models.models import Values
from arches.app.models.models import RelatedResource
from arches.app.models.concept import Concept
from optparse import make_option
from formats.archesfile import ArchesReader
from formats.shapefile import ShapeReader
from django.core.management.base import BaseCommand, CommandError
import glob
import csv


class ResourceLoader(object): 

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
        if file_format == '.shp':
            reader = ShapeReader()
        elif file_format == '.arches':
            reader = ArchesReader()

        start = time()
        resources = reader.load_file(source)
        relationships = None
        relationships_file = file_name + '.relations'
        elapsed = (time() - start)
        print 'time to parse {0} resources = {1}'.format(file_name, elapsed)
        results = self.resource_list_to_entities(resources)
        if os.path.exists(relationships_file):
            relationships = csv.DictReader(open(relationships_file, 'r'), delimiter='|')
            for relationship in relationships:
                self.relate_resources(relationship, results['legacyid_to_entityid'])
                print ('relationship {0} created').format(relationship)
        else:
            print 'No relationship file'


    def resource_list_to_entities(self, resource_list):
        '''Takes a collection of imported resource records and saves them as arches entities'''

        start = time()
        d = datetime.datetime.now()
        load_id = 'LOADID:{0}-{1}-{2}-{3}-{4}-{5}'.format(d.year, d.month, d.day, d.hour, d.minute, d.microsecond) #Should we append the timestamp to the exported filename?

        ret = {'successfully_saved':0, 'successfully_indexed':0, 'failed_to_save':[], 'failed_to_index':[]}
        schema = None
        current_entitiy_type = None
        legacyid_to_entityid = {}

        for resource in resource_list:
            masterGraph = None
            entityData = []
            if current_entitiy_type != resource.entitytypeid:
                schema = Entity.get_mapping_schema(resource.entitytypeid)

            master_graph = self.build_master_graph(resource, schema)

            self.pre_save(master_graph)
            master_graph.save(username=settings.ETL_USERNAME, note=load_id)
            resource.entityid = master_graph.entityid
            legacyid_to_entityid[resource.resource_id] = master_graph.entityid

            ret['successfully_saved'] += 1
            print 'saved', master_graph.entityid
            print 'indexing', master_graph.entityid
            master_graph.index()
            ret['successfully_indexed'] += 1

        ret['legacyid_to_entityid'] = legacyid_to_entityid
        elapsed = (time() - start)
        print 'total time to etl = %s' % (elapsed)
        print 'average time per entity = %s' % (elapsed/len(resource_list))
        print 'Load Identifier = ', load_id
        return ret


    def build_master_graph(self, resource, schema):
        master_graph = None
        entity_data = []
        for row in resource.nongroups:
            entity = Entity()
            entity.create_from_mapping(row.resourcetype, schema[row.attributename]['steps'], row.attributename, row.attributevalue)
            entity_data.append(entity)

        if len(entity_data) > 0:
            master_graph = entity_data[0]
            for mapping in entity_data[1:]:
                master_graph.merge(mapping)

        for group in resource.groups:
            entity_data2 = []
            for row in group.rows:
                entity = Entity()
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


    def relate_resources(self, relationship, legacyid_to_entityid):
        relationshiptype_concept = Concepts.objects.get(legacyoid = relationship['RELATION_TYPE'])
        concept_value = Values.objects.filter(conceptid = relationshiptype_concept.conceptid).filter(valuetype = 'prefLabel')
        start_date = None if relationship['START_DATE'] == '' else relationship['START_DATE']
        end_date = None if relationship['END_DATE'] == '' else relationship['END_DATE']
        related_resource_record = RelatedResource(
            entityid1 = legacyid_to_entityid[relationship['RESOURCEID_FROM']],
            entityid2 = legacyid_to_entityid[relationship['RESOURCEID_TO']],
            notes = relationship['NOTES'],
            relationshiptype = concept_value[0].valueid,
            datestarted = start_date,
            dateended = end_date,
            )
        related_resource_record.save()


    def generate_uuid(self, cursor):
        sql = """
            SELECT uuid_generate_v1mc()
        """
        cursor.execute(sql)
        return cursor.fetchone()[0]


    def get_mapping_steps(self, resource_entity, leaf_entity_type_id, cursor):
        sql = """
            SELECT mappingid FROM ontology.mappings WHERE entitytypeidfrom = '%s' AND entitytypeidto = '%s'
        """%(resource_entity.entitytypeid, leaf_entity_type_id)
        cursor.execute(sql)
        return resource_entity._get_mappings(cursor.fetchone()[0])