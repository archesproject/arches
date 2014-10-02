import os
import csv
import types
import sys
from time import time
from django.conf import settings
from django.db import connection, transaction
from arches.app.models.entity import Entity
from arches.app.models.models import Concepts
from arches.app.models.models import Values
from arches.app.models.models import RelatedResource
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
import collections


class Row(object):
    def __init__(self, *args):
        if len(args) == 0:
            self.resource_id = ''
            self.resourcetype = ''
            self.attributename = ''
            self.attributevalue = ''
            self.group_id = ''
        elif isinstance(args[0], list):
            self.resource_id = args[0][0].strip()
            self.resourcetype = args[0][1].strip()
            self.attributename = args[0][2].strip()
            self.attributevalue = args[0][3].strip()
            self.group_id = args[0][4].strip()

    def __repr__(self):
        return ('"%s, %s, %s, %s"') % (self.resource_id, self. resourcetype, self. attributename, self.attributevalue)

class Group(object):
    def __init__(self, *args):
        if len(args) == 0:
            self.resource_id = ''
            self.group_id = ''
            self.rows = []
        elif isinstance(args[0], list):
            self.resource_id = args[0][0].strip()
            self.group_id = args[0][4].strip()
            self.rows = []   

class Resource(object):

    def __init__(self, *args):

        if len(args) == 0:
            self.resource_id = ''
            self.entitytypeid = ''
            self.groups = []
            self.nongroups = []

        elif isinstance(args[0], list):
            self.entitytypeid = args[0][1].strip()
            self.resource_id = args[0][0].strip()
            self.nongroups = []  
            self.groups = []


    def appendrow(self, row, group_id=None):
        if group_id != None:
            for group in self.groups:
                if group.group_id == group_id:
                    group.rows.append(row)
        else:
           self.nongroups.append(row)

    def __str__(self):
        return '{0},{1}'.format(self.resource_id, self.entitytypeid)


class Command(BaseCommand): 

    option_list = BaseCommand.option_list + (
        make_option('--source',
            action='store_true',
            dest='source',
            default='',
            help='.arches file containing resource records'),
         make_option('--truncate',
            action='store_true',
            default=True,
            help='Truncate existing resource records - this is the default'),
        )


    def handle(self, *args, **options):
        '''Reads an arches data file and creates resource graphs'''

        start = time()
        resource_info = open(options['source'], 'rb')
        rows = [line.split("|") for line in resource_info]
        resource_list = []
        resource_id = ''
        group_id = ''

        if options['truncate']:
            cursor = connection.cursor()
            cursor.execute("""
                TRUNCATE data.entities CASCADE;
            """ )

        for row in rows[1:]:
            group_val = row[4].strip()
            resource_type_val = row[1].strip()
            resource_id_val = row[0].strip()

            if (settings.LIMIT_ENTITY_TYPES_TO_LOAD == None or resource_type_val in settings.LIMIT_ENTITY_TYPES_TO_LOAD):
                if resource_id_val != resource_id:
                    resource = Resource(row)
                    resource_list.append(resource)
                    resource_id = resource_id_val
                
                if group_val != '-1' and group_val != group_id:  #create a new group of resouces
                    resource.groups.append(Group(row))
                    group_id = group_val

                if group_val == group_id:
                    resource.appendrow(Row(row), group_id=group_id)

                if group_val == '-1':
                    resource.appendrow(Row(row))

        elapsed = (time() - start)
        print 'time to parse input file = %s' % (elapsed)

        self.resource_list_to_entities(resource_list, cursor)
        print 'resources loaded'
    

    def resource_list_to_entities(self, resource_list, cursor):
        '''Takes a collection of imported resource records and saves them as arches entities'''

        start = time()
        ret = {'successfully_saved':0, 'successfully_indexed':0, 'failed_to_save':[], 'failed_to_index':[]}
        schema = None
        current_entitiy_type = None

        for resource in resource_list:
            masterGraph = None
            entityData = []
            if current_entitiy_type != resource.entitytypeid:
                schema = Entity.get_mapping_schema(resource.entitytypeid)

            master_graph = self.build_master_graph(resource, schema)

            related_resources = self.update_related_resources(master_graph, resource_list)

            master_graph.save(username=settings.ETL_USERNAME)

            for related_resource in related_resources:
                related_resource_record = RelatedResource(
                    entityid1 = master_graph.entityid,
                    entityid2 = related_resource['entityid'],
                    reason = 'ETL',
                    relationshiptype = related_resource['relationship_type_id'],
                    datestarted = related_resource['date_started'],
                    dateended = related_resource['date_ended'],
                    )

                related_resource_record.save()

            resource.entityid = master_graph.entityid
            resource.legacyid = self.get_legacy_id(master_graph)

            ret['successfully_saved'] += 1
            master_graph.index()
            ret['successfully_indexed'] += 1

        elapsed = (time() - start)
        print 'total time to etl = %s' % (elapsed)
        print 'average time per entity = %s' % (elapsed/len(resource_list))
        print ret
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


    def get_legacy_id(self, entity):
        for entity in entity.find_entities_by_type_id('EXTERNAL XREF.E42'):
            return entity.value


    def update_related_resources(self, master_graph, resource_list):
        """
        Assigns an entityid to related resources and collects information needed
        to create a related resource record.
        """
        related_resources = []

        for entity in master_graph.find_entities_by_type_id('ARCHES RESOURCE.E1'):
            for resource in resource_list:
                try:
                    if entity.value == resource.legacyid:
                        related = {}
                        entity.value = resource.entityid
                        related['entityid'] = resource.entityid
                        relationship_type_legacyoid = entity.find_entities_by_type_id('ARCHES RESOURCE CROSS-REFERENCE RELATIONSHIP TYPE.E55')[0].value
                        rel_type_concept_id = Concepts.objects.get(legacyoid=relationship_type_legacyoid).conceptid
                        related['relationship_type_id'] = Values.objects.get(conceptid=rel_type_concept_id, valuetype='prefLabel').valueid
                        related['date_started'] = entity.find_entities_by_type_id('DATE RESOURCE ASSOCIATION STARTED.E50')[0].value
                        related['date_ended'] = entity.find_entities_by_type_id('DATE RESOURCE ASSOCIATION ENDED.E50')[0].value
                        related_resources.append(related)
                except:
                    pass

        return related_resources


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


