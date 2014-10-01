import os
import csv
import types
import sys
from time import time
from django.conf import settings
from django.db import connection, transaction
#from arches.app.models.entity import Entity
from arches.app.models.entity import Entity
from pprint import pprint
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

class ResourceRelation(object):
    def __init__(self, *args):
        if len(args) == 0:
            self.resourceid1 = ''
            self.xref_entity_id1 = ''
            self.xref_value = ''
            self.resourceid2 = ''
            self.xref_entity_id2 = ''
            self.legacyid = ''
            self.relation_type = ''
            self.start_date = ''
            self.end_date = ''
    def __str__(self):
        return '{0},{1}'.format(self.start_date, self.end_date)


class DataLoader(object): 

    def load(self, filepath, resource_relation_entitytypeids=None, truncate=True):
        start = time()
        resource_info = open(filepath, 'rb')
        rows = [line.split("|") for line in resource_info]
        resourceList = []
        resource_id = ''
        group_id = ''

        if truncate:
            cursor = connection.cursor()
            cursor.execute("""
                TRUNCATE data.entities CASCADE;
            """ )

        for row in rows:
            if rows.index(row) != 0:
                if (settings.LIMIT_ENTITY_TYPES_TO_LOAD == None or row[1].strip() in settings.LIMIT_ENTITY_TYPES_TO_LOAD):
                    if row[0].strip() != resource_id:
                        resource = Resource(row)
                        resourceList.append(resource)
                        resource_id = row[0].strip()
                    
                    if row[4].strip() != '-1' and row[4].strip() != group_id:
                        resource.groups.append(Group(row))
                        group_id = row[4].strip()

                    if row[4].strip() == group_id:
                        resource.appendrow(Row(row), group_id=group_id)
                        #resourceList[len(resourceList)-1].groups[len(resourceList[len(resourceList)-1].groups)-1].rows.append(Row(row))

                    if row[4].strip() == '-1':
                        resource.appendrow(Row(row))
                        #resourceList[len(resourceList)-1].nongroups.append(Row(row))

        elapsed = (time() - start)
        print 'time to parse csv = %s' % (elapsed)
        return self.resource_list_to_entities(resourceList, resource_relation_entitytypeids, cursor)
    
    def resource_list_to_entities(self, resourceList, resource_relation_entitytypeids, cursor):
        start = time()
        ret = {'successfully_saved':0, 'successfully_indexed':0, 'failed_to_save':[], 'failed_to_index':[]}
        schema = None
        current_entitiy_type = None
        resource_relations = []



        for resource in resourceList:
            masterGraph = None
            entityData = []
            if current_entitiy_type != resource.entitytypeid:
                schema = Entity.get_mapping_schema(resource.entitytypeid)


            master_graph = self.build_master_graph(resource, schema)
            self.update_related_resources(master_graph, resourceList)



            master_graph.save(username=settings.ETL_USERNAME)
            resource.entityid = master_graph.entityid
            resource.legacyid = self.get_legacy_id(master_graph)




            # # Gather legacyids for all entities in resource_info.
            # if resource_relation_entitytypeids: 

            #     def traverse_down(entity, dictionary):
            #         for child in entity.relatedentities:
            #             if child.value != '':
            #                 dictionary[child.entitytypeid] = child.value
            #             traverse_down(child, dictionary)
            #         return dictionary

            #    for item in master_graph.find_entities_by_type_id('EXTERNAL XREF.E42'):
            #         relation = ResourceRelation()
            #         relation.resourceid1 = master_graph.entityid
            #         relation.legacyid = master_graph.entitytypeid.split('.')[0] + ':' + item.value
            #         resource_relations.append(relation)

            #     # If an entity in resource_info has an Arches Resource.E1 entity, grab it's value and the rest of the xref branch.
            #     for item in master_graph.find_entities_by_type_id('ARCHES RESOURCE.E1'):
            #         xref_attributes = {}
            #         relation = ResourceRelation()
            #         relation.resourceid1 = master_graph.entityid
            #         relation.xref_entity_id1 = item.entityid
            #         relation.xref_value = item.value
            #         xref_dic = {}
            #         if len(item.relatedentities) > 0:
            #             xref_attributes = traverse_down(item, xref_dic)
            #             # parse xref branch attributes and add to relation object
            #             if 'ARCHES RESOURCE CROSS-REFERENCE RELATIONSHIP TYPE.E55' in xref_attributes:
            #                 relation.relation_type = xref_attributes['ARCHES RESOURCE CROSS-REFERENCE RELATIONSHIP TYPE.E55']
            #             if 'DATE RESOURCE ASSOCIATION STARTED.E50' in xref_attributes:
            #                 relation.start_date = xref_attributes['DATE RESOURCE ASSOCIATION STARTED.E50']
            #             if 'DATE RESOURCE ASSOCIATION ENDED.E50' in xref_attributes:
            #                 relation.end_date = xref_attributes['DATE RESOURCE ASSOCIATION ENDED.E50']
            #         resource_relations.append(relation)

            ret['successfully_saved'] += 1
            master_graph.index()
            ret['successfully_indexed'] += 1

        # Compare resourceRelation objects and cross populate xref_entity_id's and resourceid's if resource.legacyid == related_resource.xref_value
        if resource_relation_entitytypeids and len(resource_relations) > 0:
            self.save_related_resources(resource_relations, resource_relation_entitytypeids, cursor)

        elapsed = (time() - start)
        print 'total time to etl = %s' % (elapsed)
        print 'average time per entity = %s' % (elapsed/len(resourceList))
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
        for item in entity.find_entities_by_type_id('EXTERNAL XREF.E42'):
            return item.value

    def update_related_resources(self, master_graph, resourceList):
        for item in master_graph.find_entities_by_type_id('ARCHES RESOURCE.E1'):
            for resource in resourceList:
                try:
                    if item.value == resource.legacyid:
                        item.value = resource.entityid
                except:pass

    def save_related_resources(self, resource_relations, resource_relation_entitytypeids, cursor):
        for resource in resource_relations:
            for resource2 in resource_relations:
                if resource2.legacyid and (resource.xref_value == resource2.legacyid):
                    resource.resourceid2 = resource2.resourceid1
                    resource.xref_entity_id2 = resource2.xref_entity_id1

            if resource.resourceid2:
                if resource.xref_entity_id2 == '':
                    resource.xref_entity_id2 = self.generate_uuid(cursor)

                    resource_entity = Entity().get(resource.resourceid2)
                    
                    mapping_nodes = collections.OrderedDict([
                        ('ARCHES RESOURCE.E1', resource.resourceid1),
                        ('ARCHES RESOURCE CROSS-REFERENCE RELATIONSHIP TYPE.E55', resource.relation_type),
                        ('DATE RESOURCE ASSOCIATION STARTED.E50', resource.start_date),
                        ('DATE RESOURCE ASSOCIATION ENDED.E50', resource.end_date)
                        ])

                    if resource_entity.entitytypeid in resource_relation_entitytypeids:
                        entities_to_merge = []
                        for entity_type_id, entity_value in mapping_nodes.iteritems():
                            entity = Entity() 
                            mapping_steps = self.get_mapping_steps(resource_entity, entity_type_id, cursor)
                            entity.create_from_mapping(resource_entity.entitytypeid, mapping_steps, entity_type_id, entity_value)
                            entities_to_merge.append(entity)

                        if len(entities_to_merge) > 0:
                            base_entity = entities_to_merge[0]
                            for entity in entities_to_merge[1:]:
                                base_entity.merge(entity)
                                
                            resource_entity.merge(base_entity)
                        
                            try:
                                resource_entity.save()
                                print 'successfully_saved'
                            except:
                                print 'failed to save' 

                #pprint(JSONSerializer().serializeToPython(resource_entity, ensure_ascii=True, indent=4))

                entity = Entity()
                related_resource = entity.get(resource.resourceid1)
                for item in related_resource.find_entities_by_type_id('ARCHES RESOURCE.E1'):
                    if item.value == resource.xref_value:
                        item.value = resource.resourceid2
                        related_resource.save()
                    else:
                        print '''ERROR: '%s' is not a valid resource legacyid''' %(item.value)

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

    def findmergenode(self, graph):
        """
        Logic to try and determine the proper node to merge multiple instances of the same types of data. Like address info.
        Currently unused.  

        """

        rank = None
        highestnodewithvalue = None
        entitieswithvalues = []
        def findentitieswithvalues(entity):
            if entity.value != '':
                entitieswithvalues.append(entity)
        graph.traverse(findentitieswithvalues)

        if len(entitieswithvalues) == 0:
            raise Exception("Entity graph has no values")
        for entity in entitieswithvalues:
            if rank == None:
                rank = entity.get_rank()
            if entity.get_rank() <= rank:
                rank = entity.get_rank()
                highestnodewithvalue = entity

        rank = None
        highestforkingnode = None
        entitiesthatfork = []
        def findentitiesthatfork(entity):
            if len(entity.relatedentities) > 1:
                entitiesthatfork.append(entity)
        graph.traverse(findentitiesthatfork)

        for entity in entitiesthatfork:
            if rank == None:
                rank = entity.get_rank()
            if entity.get_rank() <= rank:
                rank = entity.get_rank()
                highestforkingnode = entity


        # LOGIC SECTION
        if highestforkingnode == None or highestnodewithvalue.get_rank() >= highestforkingnode.get_rank():
            if highestnodewithvalue.get_parent().get_rank() == 0:
                return highestnodewithvalue.get_parent()
            else:
                return highestnodewithvalue.get_parent().get_parent()

        if highestnodewithvalue.get_rank() < highestforkingnode.get_rank():
            if highestforkingnode.get_rank() == 0:
                return highestforkingnode
            else:
                return highestforkingnode.get_parent()

        return None

        #     groupNode =



        # 1.) Identify highest node with value;
        # 2.) Identify node at which the group has a common parent;

        # 3.) Take the node that is closer to the root
        #     a.) if that is that is the node with a value: split two parents up or root
        #     b.) else: split one parent up

