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


    def load(self, source, format):
        if format == 'shp':
            reader = ShapeReader()
        elif format == 'arches':
            reader = ArchesReader()

        files = glob.glob(source + '//*.' + format)
        print files
        for f in files:
            start = time()
            resources = reader.load_file(f)
            elapsed = (time() - start)
            print 'time to parse input file = %s' % (elapsed)
            self.resource_list_to_entities(resources)


    def resource_list_to_entities(self, resource_list):
        '''Takes a collection of imported resource records and saves them as arches entities'''

        start = time()
        d = datetime.datetime.now()
        load_id = 'LOADID:{0}-{1}-{2}-{3}-{4}-{5}'.format(d.year, d.month, d.day, d.hour, d.minute, d.microsecond) #Should we append the timestamp to the exported filename?

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

            self.pre_save(master_graph)

            master_graph.save(username=settings.ETL_USERNAME, note=load_id)

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
            print 'saved', master_graph.entityid
            print 'indexing', master_graph.entityid
            master_graph.index()
            ret['successfully_indexed'] += 1

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

                        date_entity_types = [{
                            'entitytypeid': 'DATE RESOURCE ASSOCIATION STARTED.E50',
                            'key': 'date_started' 
                        },{
                            'entitytypeid': 'DATE RESOURCE ASSOCIATION ENDED.E50',
                            'key': 'date_ended' 
                        }]
                        for date_entity_type in date_entity_types:
                            started_entities = entity.find_entities_by_type_id(date_entity_type['entitytypeid'])
                            related[date_entity_type['key']] = None if started_entities == [] else started_entities[0].value

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