import os
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
from arches.app.models.models import Concepts
from arches.app.models.models import Values
from arches.app.models.models import RelatedResource
from arches.app.models.concept import Concept
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.management.commands import utils
from optparse import make_option
from formats.archesfile import ArchesReader
from formats.shapefile import ShapeReader


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
        if file_format == '.shp':
            reader = ShapeReader()
        elif file_format == '.arches':
            reader = ArchesReader()
            print '\nVALIDATING ARCHES FILE ({0})'.format(source)
            print '-----------------------'
            reader.validate_file(source)

        start = time()
        resources = reader.load_file(source)

        print '\nLOADING RESOURCES ({0})'.format(source)
        print '-----------------------'
        relationships = None
        related_resource_records = []
        relationships_file = file_name + '.relations'
        elapsed = (time() - start)
        print 'time to parse {0} resources = {1}'.format(file_name, elapsed)
        results = self.resource_list_to_entities(resources)
        if os.path.exists(relationships_file):
            relationships = csv.DictReader(open(relationships_file, 'r'), delimiter='|')
            for relationship in relationships:
                related_resource_records.append(self.relate_resources(relationship, results['legacyid_to_entityid']))
        else:
            print 'No relationship file'

        #self.se.bulk_index(self.resources)


    def resource_list_to_entities(self, resource_list):
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

            masterGraph = None
            entityData = []
            if current_entitiy_type != resource.entitytypeid:
                schema = Resource.get_mapping_schema(resource.entitytypeid)

            master_graph = self.build_master_graph(resource, schema)

            self.pre_save(master_graph)
            master_graph.save(user=self.user, note=load_id)
            master_graph.index()
            resource.entityid = master_graph.entityid
            legacyid_to_entityid[resource.resource_id] = master_graph.entityid
            
            ret['successfully_saved'] += 1
            # self.resources.append({
            #     '_index': 'entity',
            #     '_type': master_graph.entitytypeid,
            #     '_id': master_graph.entityid,
            #     '_source': master_graph.prepare_documents_for_search_index()[0]
            # })
            

        ret['legacyid_to_entityid'] = legacyid_to_entityid
        elapsed = (time() - start)
        print len(resource_list), 'resources loaded'
        if len(resource_list) > 0:
            print 'total time to etl = %s' % (elapsed)
            print 'average time per entity = %s' % (elapsed/len(resource_list))
            print 'Load Identifier =', load_id
            print '***You can reverse this load with the following command:'
            print 'python hip remove_resources --load_id', load_id
        return ret

    def build_master_graph(self, resource, schema):
        master_graph = None
        entity_data = []
        for row in resource.nongroups:
            entity = Resource()
            entity.create_from_mapping(row.resourcetype, schema[row.attributename]['steps'], row.attributename, row.attributevalue)
            entity_data.append(entity)

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
        self.se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(related_resource_record), idfield='resourcexid')