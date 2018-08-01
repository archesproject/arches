import os
import sys
import traceback
import unicodecsv
from os import listdir
from os.path import isfile, join
import arches.app.models.models as models
from arches.app.models.entity import Entity
from arches.app.models.resource import Resource
from arches.app.models.concept import Concept
from django.db.models import Q
from arches.app.search.search_engine_factory import SearchEngineFactory
from django.forms.models import model_to_dict
from .. import utils
import datetime



from itertools import groupby

import logging


# Script for migrating business data from one part of resource graph to elsewhere.
# Typically this will be part of a migration from one resource graph to another, after adding new parts from the new resource graph, but before removing old ones.
# The migration is carried out according to a csv which specifies which entities must be created or altered.


def migrate(settings=None):
    
    if not settings:
        from django.conf import settings
    
    suffix = '_altered_nodes.csv'
    errors = []

    for path in settings.ADDITIONAL_RESOURCE_GRAPH_LOCATIONS:
        if os.path.exists(path):
            print '\nLOADING NODE MIGRATION INFO (%s)' % (path)
            print '--------------'
            for f in listdir(path):
                if isfile(join(path, f)) and f.endswith(suffix):
                    path_to_file = join(path,f)
                    basepath = path_to_file[:-18]
                    name = basepath.split(os.sep)[-1]
                    
                    migrations = get_list_dict(basepath + '_altered_nodes.csv', ['OLDENTITYTYPEID', 'NEWENTITYTYPEID', 'GROUPROOTNODEOLD', 'GROUPROOTNODENEW'])
                
                    # Identify nodes which must be migrated
                    resource_entity_type = 'HERITAGE_RESOURCE_GROUP.E27'
                    mapping_schema = Entity.get_mapping_schema(resource_entity_type)
                    
                    # group migrations by groupRootNodeNew
                    groups = groupby(migrations, lambda x:(x['GROUPROOTNODEOLD'], x['GROUPROOTNODENEW']))
                    
                    for group_root_node_ids, group_migrations in groups:
                        
                        #Convert group_migrations to a list as we need to iterate it multiple times
                        group_migrations_list = []
                        for group_migration in group_migrations:
                            group_migrations_list.append(group_migration)
                        
                        group_root_node_id = group_root_node_ids[0]
                        new_group_root_node_id = group_root_node_ids[1]
                        
                        #Find all entities with the old group root node
                       
                        group_root_entities = models.Entities.objects.filter(entitytypeid=group_root_node_id)
                        print "ENTITIES COUNT: ", group_root_entities.count()
                        for group_root_entity_model in group_root_entities.iterator():
                            # Create a new subgraph for each of the migration steps, then merge them together at the group root node
                            
                            #get full resource graph for the root entity
                            try:
                                group_root_entity = Entity(group_root_entity_model.pk)
                            except:
                                print "Faulty group entity's ID %s and entitytype %s" % (group_root_entity_model.pk,group_root_entity_model.entitytypeid)
                                continue
                            new_group_root_entity = Entity().create_from_mapping(resource_entity_type, mapping_schema[new_group_root_node_id]['steps'], new_group_root_node_id, '')
                            
                            if group_migrations_list[0]['NEWENTITYTYPEID'] != new_group_root_node_id:
                                # create a node for the new group root
                                group_root_is_new_data_node = False
                            else:
                                group_root_is_new_data_node = True
                            
                            # get the root resource graph for this entity
                            resource_model = get_resource_for_entity(group_root_entity, resource_entity_type)
                            if not resource_model:
                                continue
                            resource = Resource().get(resource_model.entityid)
                            
                            for group_migration in group_migrations_list:
                                 
                                # get individual entities to be migrated in the source group
                                old_entities = group_root_entity.find_entities_by_type_id(group_migration['OLDENTITYTYPEID'])
                                for old_entity in old_entities:
                                    date_on = False
                                    # Create the corresponding entity in the new schema
                                    new_entity = Entity()
                                    #Disturbance dates need to be mapped to different nodes depending on the value of the now obsolete DISTURBANCE_DATE_TYPE.E55
                                    if group_migration['OLDENTITYTYPEID'] in ['DISTURBANCE_DATE_END.E49','DISTURBANCE_DATE_START.E49']:
                                        date_type_node = group_root_entity.find_entities_by_type_id('DISTURBANCE_DATE_TYPE.E55')
                                        if date_type_node:
                                            if date_type_node[0].label == 'Occurred before':
                                                new_entity_type_id = 'DISTURBANCE_DATE_OCCURRED_BEFORE.E61'
                                            elif date_type_node[0].label == 'Occurred on':
                                                if group_migration['OLDENTITYTYPEID'] =='DISTURBANCE_DATE_START.E49':
                                                    date_on = True
                                                else:
                                                    new_entity_type_id = 'DISTURBANCE_DATE_OCCURRED_ON.E61'
                                            else:
                                                new_entity_type_id = group_migration['NEWENTITYTYPEID']
                                    else:                                         
                                        new_entity_type_id = group_migration['NEWENTITYTYPEID']
                                    old_value = old_entity.value

                                    if old_entity.businesstablename == 'domains':
                                        # in some cases we move from domains to strings.
                                        newEntityType = models.EntityTypes.objects.get(entitytypeid=new_entity_type_id)
                                        if newEntityType.businesstablename == 'strings':
                                            old_value = old_entity.label
                                    
                                    if not date_on:
                                        new_entity.create_from_mapping(resource_entity_type, mapping_schema[new_entity_type_id]['steps'], new_entity_type_id, old_value)
                                    
                                    # In some cases a newly created data node is the new group root. In this case we should discard the previously created new group root and use this one instead.
                                    if new_group_root_node_id == new_entity_type_id:
                                        new_group_root_entity = new_entity
                                        group_root_is_new_data_node = True
                                    
                                    # UNUSED 
                                    # # If there is a node to be inserted, do it here
                                    # # if 'INSERT_NODE_RULE' in group_migration:
                                    # #     entityttypeid_to_insert = group_migration['INSERT_NODE_RULE'][1][1]
                                    # #     value_to_insert = group_migration['INSERT_NODE_RULE'][1][2]
                                    # # 
                                    # #     inserted_entity = Entity()
                                    # #     inserted_entity.create_from_mapping(resource_entity_type, mapping_schema[entityttypeid_to_insert]['steps'], entityttypeid_to_insert, value_to_insert)
                                    # # 
                                    # #     new_entity.merge(inserted_entity)


                                    # If there is a node in common with the existing node further down the chain than the group root node, merge there
                                    # follow links back from the parent
                    
                                    shouldnt_merge_with_group_root = group_root_is_new_data_node and new_group_root_node_id == new_entity_type_id
                                    
                                    if not shouldnt_merge_with_group_root:
                                        has_merged = False
                                        
                                        reversed_steps = mapping_schema[new_entity_type_id]['steps'][::-1]
                                        for step in reversed_steps:
                                            # find the entitytypedomain in the new_group_root_entity
                                            if not has_merged:
                                                mergeable_nodes = new_group_root_entity.find_entities_by_type_id(step['entitytypedomain'])
                                                if len(mergeable_nodes) > 0:
                                                    new_group_root_entity.merge_at(new_entity, step['entitytypedomain'])
                                                    has_merged = True
                                                    new_entity = None
#                                                     gc.collect()
                                        
                                        if not has_merged:
                                            logging.warning("Unable to merge newly created entity")
                                    
                                    
                                # merge the new group root entity into the resource
                                resource.merge_at(new_group_root_entity, resource_entity_type)
                            
                            logging.warning("SAVING RESOURCE, %s", resource)
                            # save the resource
                            resource.trim()
                            try:
                                resource._save()
                                resource=None
                            except Exception as e:
                                logging.warning("Error saving resource")
                                logging.warning(e)
                                errors.append("Error saving %s. Error was %s" % (resource, e))
                            
                            group_root_entity.clear()
                            group_root_entity = None
                            new_group_root_entity.clear()
                            new_group_root_entity = None
                            
                            # end for group root
                                
                        
                            # resource.index()
                            # logging.warning("SAVED RESOURCE, %s", resource)
                            
    utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'migration_errors.txt'), '')
    if len(errors) > 0:
        # utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'migration_errors.txt'), '\n'.join(errors))
        print "\n\nERROR: There were errors migrating some resources. See below"
        print errors

def insert_actors(settings=None):
    
    if not settings:
        from django.conf import settings
        
    logging.warning("INSERTING ACTORS")
    
    resource_entity_type = 'HERITAGE_RESOURCE_GROUP.E27'
    mapping_schema = Entity.get_mapping_schema(resource_entity_type)
    
    # access settings to determine which actor nodes should correspond to editors of which pre-existing nodes
    for entry in settings.ACTOR_NODES:
        
        # find all entities of the parent type
        actor_entitytypeid = entry[0]
        parent_entitytypeid = entry[1]
        source_entitytypeid = entry[2]
        
        mapping_step_to_actor = mapping_schema[actor_entitytypeid]['steps'][-1]
        
        parent_entities = models.Entities.objects.filter(entitytypeid=parent_entitytypeid).iterator()
        
        for parent_entity_model in parent_entities:
            # check whether an actor node already exists
            parent_entity = Entity().get(parent_entity_model.entityid)
            actors = parent_entity.find_entities_by_type_id(actor_entitytypeid)
            if(len(actors) == 0):
                # get the root resource
                root_resource_model = get_resource_for_entity(parent_entity_model, resource_entity_type)
                if not root_resource_model:
                    continue
                
                # find the last edit to the node that the data originated at
                edits = models.EditLog.objects.filter(resourceid=root_resource_model.entityid, attributeentitytypeid=source_entitytypeid).order_by('timestamp')
                first_edit = edits[0]
                actor_name = '%s %s' % (edits[0].user_firstname, edits[0].user_lastname)
                
                # create the actor node
                parent_entity.add_child_entity(actor_entitytypeid, mapping_step_to_actor['propertyid'], actor_name, '')
                
                # logging.warning("\n\nParent after insert")
                log_entity(parent_entity)
                parent_entity._save()
                
                root_resource = Resource()
                root_resource.get(root_resource_model.entityid)

def remove_entitytypes_and_concepts(all_entitytypeids_to_remove, only_entitytypes = False):
    # if the entity_types are no longer associated to any resource graph, then delete the entity_types themselves and then proceed with pruning concepts
    if not isinstance(all_entitytypeids_to_remove, list):
        all_entitytypeids_to_remove = [all_entitytypeids_to_remove]
    for entity_to_remove in all_entitytypeids_to_remove:
        still_linked = False if not models.Mappings.objects.filter(entitytypeidto = entity_to_remove) else True
        if not still_linked: 
            entity_types = models.EntityTypes.objects.filter(entitytypeid=entity_to_remove)
            print len(entity_types)
            #### Prune the concepts
            concepts_to_delete = []
            
            for entity_type in entity_types:
                # Find the root concept
                concept = entity_type.conceptid
                
                # only add this for deletion if the concept isn't used by any other entitytypes
                relations = models.EntityTypes.objects.filter(conceptid=concept.pk)
                if len(relations) <= 1:
                    concepts_to_delete.append(entity_type.conceptid)
                else:
                    logging.warning("Concept type for entity in use (perhaps because this node was mapped to a new one). Not deleting. %s", entity_type)
                
            # delete the entity types, and then their concepts
            entity_types.delete()
            
            for concept_model in concepts_to_delete:
                # remove it and all of its relations and their values
                logging.warning("Removing concept and children/values/relationships for %s", concept_model.legacyoid)
                concept = Concept()
                concept.get(concept_model.pk, semantic=False, include_subconcepts=True)
                
                concept.delete(delete_self=True)
                concept_model.delete()
            
            logging.warning("Removed all entities and ontology data related to the following entity types: %s", entity_to_remove)                    

def prune_ontology(settings=None, only_concepts=False):
    
    logging.warning("pruning ontology")
    
    if not settings:
        from django.conf import settings
        
    suffix = '_removed_nodes.csv'
    
    for path in settings.ADDITIONAL_RESOURCE_GRAPH_LOCATIONS:
        if os.path.exists(path):
            for f in listdir(path):
                if isfile(join(path,f)) and f.endswith(suffix):
                    path_to_file = join(path,f)
                    basepath = path_to_file[:-18]
                    name = basepath.split(os.sep)[-1]
                    
                    nodes_to_remove = get_list_dict(basepath + '_removed_nodes.csv', ['NodeId'])
                    
                    all_entitytypeids_to_remove = [x['NodeId'] for x in nodes_to_remove]
                    if only_concepts == True:
                        remove_entitytypes_and_concepts(all_entitytypeids_to_remove,only_concepts)
                        return
                    '''Given an resource type and a list of entity types, it returns a list of rules'''
                    def collect_leaf_rules(entitytypes,resource_type,rule_ids_to_delete):
                        for entitytype in entitytypes:
                            mappingid=models.Mappings.objects.get(entitytypeidfrom=resource_type, entitytypeidto =entitytype)
                            try:
                                rule_id = models.Rules.objects.get(ruleid__in=models.MappingSteps.objects.filter(mappingid=mappingid.pk).values_list('ruleid', flat=True), entitytyperange=entitytype)
                                rule_ids_to_delete.append(rule_id.ruleid)
                            except:
                                rule_id = models.Rules.objects.filter(ruleid__in=models.MappingSteps.objects.filter(mappingid=mappingid.pk).values_list('ruleid', flat=True), entitytyperange=entitytype).values_list('ruleid', flat=True)                                
                                rule_ids_to_delete.extend(rule_id)
                        return rule_ids_to_delete
                        
                    ''' Given an initial list of entity ids, it collects all of their child entity ids until the whole hierarchy has been analysed, then returns it all as a a list'''
                    def collect_leaf_entities_and_rules(relations, entities_to_delete, rule_ids_to_delete,mappings_to_delete,resource_type):
                        if relations.count() > 0:
                            logging.warning("Iteration of collect_leaf")
                            entities_to_delete.extend(relations)
                            collect_leaf_entities_and_rules(models.Relations.objects.filter(entityiddomain__in=list(relations)).values_list('entityidrange', flat=True),entities_to_delete, rule_ids_to_delete,mappings_to_delete, resource_type)
                        else:
                            logging.warning("Begin collation of leaf sets")
                            entitytypes = models.Entities.objects.filter(entityid__in=entities_to_delete).values_list('entitytypeid', flat=True).distinct()
                            logging.warning("entitytypes collected")
                            rule_ids_to_delete.extend(collect_leaf_rules(entitytypes,resource_type,rule_ids_to_delete))
                            logging.warning("rules collected")
                            mappings = models.Mappings.objects.filter(entitytypeidfrom=resource_type, entitytypeidto__in =entitytypes).values_list('mappingid', flat=True)
                            logging.warning("Mappings collected")
                            mappings_to_delete.extend(mappings)
                            logging.warning("Returning leaf lists")

                        return entities_to_delete,mappings_to_delete,rule_ids_to_delete
                           
                    ### Returns a list of entities to delete which have as top node the name of the name of the csv file containing the nodes to remove
                    def retrieve_entities_to_delete(resource_type, entitytypeids_to_remove, ontology=False):
                        entities_or_ontology = {
                            'entities_to_delete': [],
                            'mappings': [],
                            'rule_ids': []
                        }
                        entities_to_delete = []
                        rule_ids_to_delete = []
                        mappings_to_delete = []
                        for entitytypeid_to_remove in entitytypeids_to_remove:
                            try:
#                                 if not remove_graph:
                                mappingid=models.Mappings.objects.get(entitytypeidfrom=resource_type, entitytypeidto =entitytypeid_to_remove)
#                                 else:
#                                     mappingid=models.Mappings.objects.filter(entitytypeidfrom=resource_type).values_list('mappingid', flat=True)
                            except:
                                print "No mapping found for %s, moving on" % entitytypeid_to_remove
                                continue
                            try:
                                rule_id = models.Rules.objects.get(ruleid__in=models.MappingSteps.objects.filter(mappingid=mappingid.pk).values_list('ruleid', flat=True), entitytyperange=entitytypeid_to_remove)
                            except:
                                print "No rule found with mapping %s for entitytype %s, moving on" % (mappingid.pk,entitytypeid_to_remove)
                                continue
                            relations = models.Relations.objects.filter(ruleid=rule_id).values_list('entityidrange', flat=True)
                            entities_to_delete,mappings_to_delete,rule_ids_to_delete = collect_leaf_entities_and_rules(relations, entities_to_delete,rule_ids_to_delete,mappings_to_delete,resource_type)                        
                            entities_or_ontology['entities_to_delete'].extend(list(set(entities_to_delete)))
                            entities_or_ontology['mappings'].extend(list(set(mappings_to_delete))) if relations else entities_or_ontology['mappings'].append(mappingid.pk)
                            entities_or_ontology['rule_ids'].extend(list(set(rule_ids_to_delete))) if relations else entities_or_ontology['rule_ids'].append(rule_id.ruleid)
                        
                        return entities_or_ontology
                        
                    ### Remove entities and their associated values/relationships
                    entities_to_delete = retrieve_entities_to_delete(name, all_entitytypeids_to_remove)
                    
                    
                    if any(entities_to_delete.values()):                
                        print "Deleting %s data entities and associated values and relations" % len(entities_to_delete['entities_to_delete'])
                        # delete any value records for this entity id
                        # dates
#                         dates = models.Dates.objects.filter(entityid__in=entities_to_delete['entities_to_delete'][0]).values_list('val', flat=True)
#                         print "DATES to be deleted: %s" % dates
                        models.Dates.objects.filter(entityid__in=entities_to_delete['entities_to_delete']).delete()
                        # files
#                         files = models.Files.objects.filter(entityid__in=entities_to_delete['entities_to_delete'][0]).values_list('val', flat=True)
#                         print "FILES to be deleted: %s" % files
#                         models.Files.objects.filter(entityid__in=entities_to_delete['entities_to_delete'][0]).delete()
                        # strings
#                         strings = models.Strings.objects.filter(entityid__in=entities_to_delete['entities_to_delete'][0]).values_list('val', flat=True)
#                         print "STRINGS to be deleted: %s" % strings
                        models.Strings.objects.filter(entityid__in=entities_to_delete['entities_to_delete']).delete()
                        # geometries
                        models.Geometries.objects.filter(entityid__in=entities_to_delete['entities_to_delete']).delete()
                        # numbers
                        models.Numbers.objects.filter(entityid__in=entities_to_delete['entities_to_delete']).delete()
                        # domains
#                         domains = models.Domains.objects.filter(entityid__in=entities_to_delete['entities_to_delete'][0]).values_list('val', flat=True)
#                         print "DOMAINS to be deleted: %s" % domains
                        models.Domains.objects.filter(entityid__in=entities_to_delete['entities_to_delete']).delete()
                        # delete any relationships from or to this entity id
                        models.Relations.objects.filter( Q(entityiddomain__in=entities_to_delete['entities_to_delete']) | Q(entityidrange__in=entities_to_delete['entities_to_delete']) ).delete()
                        # delete the entity record
#                         entities = models.Entities.objects.filter(entityid__in=entities_to_delete['entities_to_delete'][0]).values_list('entitytypeid', flat=True)
#                         print "ENTITIES to be deleted: %s" % entities
                        models.Entities.objects.filter(entityid__in=entities_to_delete['entities_to_delete']).delete()
                            
                        
                        #### Prune the ontology
                        print "Removing entity types and mappings from ontology data (entity types, mappings, mapping_steps, and rules)"
                        # remove mappings to these entitytype if there is one               
                        models.Mappings.objects.filter(mappingid__in=entities_to_delete['mappings']).delete()
                        # remove mapping steps associated to the relevant rules
                        models.MappingSteps.objects.filter(ruleid__in=entities_to_delete['rule_ids'], mappingid__in =entities_to_delete['mappings']).delete()
                        # remove the rules
                        models.Rules.objects.filter(ruleid__in=entities_to_delete['rule_ids']).delete()
                        
                        remove_entitytypes_and_concepts(all_entitytypeids_to_remove)

def prune_resource_graph(resource_type):
    print "Deleting resource graph %s" % resource_type
    mappings = models.Mappings.objects.filter(entitytypeidfrom=resource_type).values_list("mappingid", flat= True)
    entity_types = models.Mappings.objects.filter(entitytypeidfrom=resource_type).values_list("entitytypeidto", flat= True)
    rule_ids = models.MappingSteps.objects.filter(mappingid__in=mappings).values_list('ruleid', flat=True)
    relations = models.Relations.objects.filter(ruleid__in=rule_ids).values_list('entityidrange', flat=True)
    if relations.count() >0:
        print "There are still %s entities connected to this graph!" % relations.count()
        entitytypes = models.Entities.objects.filter(entityid__in=relations).values_list('entitytypeid', flat=True).distinct()
        print entitytypes
        return
    else:
        # remove mappings to these entitytype if there is one               
        models.Mappings.objects.filter(mappingid__in=mappings).delete()
        # remove mapping steps associated to the relevant rules
        models.MappingSteps.objects.filter(ruleid__in=rule_ids, mappingid__in =mappings).delete()
        # remove the rules
        models.Rules.objects.filter(ruleid__in=mappings).delete()        
        remove_entitytypes_and_concepts(entity_types)

def log_entity(entity):
    def do_log(subentity):
        logging.warning("--%s--", subentity)
    logging.warning("------Logging entity")
    entity.traverse(do_log)
    logging.warning("------End log entity")

def get_resource_for_entity(entity, resource_entity_type_id):
    parent = entity
    typeid = parent.entitytypeid
    logging.warning("Getting root resource for entity: %s", entity)
    
    try:
        while typeid != resource_entity_type_id:
            relationships = models.Relations.objects.filter(entityidrange=parent.entityid)
            if len(relationships) == 0:
                # no parent - either an orphan, or the root is not the type we are looking for
                return None
            elif len(relationships) > 1:
                    # too many parents. Corrupt data?
                    logging.warning("Multiple parent entities for this entity! Going with the first one")
                    relationship = relationships[0]
            else:
                relationship = relationships[0]
            parent = relationship.entityiddomain
            typeid = parent.entitytypeid.pk
        return parent
    except Exception as err:
        logging.warning("Couldn't find root resource. %s", err)
        return None
    

def convert_resources(config_file):
    #Load CSV files and migrate each resource
    if isfile(config_file):
        resources_to_convert = get_list_dict(config_file, ['resource_id', 'target_resource_type', 'related_resource', 'relationship'])
        logging.warning("Converting resources: %s", resources_to_convert)
        for resource in resources_to_convert:
            convert_resource(resource['resource_id'], resource['target_resource_type'])
            logging.warning("related to %s by %s", resource['related_resource'], resource['relationship'])
            if len(resource['related_resource']) and len(resource['relationship']):
                add_resource_relation(resource['resource_id'], resource['related_resource'], resource['relationship'].strip())


# Convert the given resource from an E27 (or whatever it currently is) to an E24.
def convert_resource(resourceid, target_entitytypeid):
    # find the resource
    logging.warning("Loading resource: %s", resourceid)
    resource = Resource()
    resource.get(resourceid)
    
    # change its entitytype
    resource_model = models.Entities.objects.get(pk=resourceid)
    logging.warning("Found resource: %s", resource_model)
    
    # update the ruleid for any steps from the root entity to its first children (subsequent entities use the same rules)
    # get first relations
    relations = models.Relations.objects.filter(entityiddomain=resourceid)
    for relation in relations:
        try:
            rule = relation.ruleid
            #now find the rule which maps to the same target, with the same property, from the new entity type
            new_rule = models.Rules.objects.get(entitytypedomain=target_entitytypeid, entitytyperange=rule.entitytyperange, propertyid=rule.propertyid)
            relation.ruleid = new_rule
            relation.save()
            
        except Exception as err:
            logging.warning("Unable to convert rule for relation: %s to %s", relation.ruleid.entitytypedomain, relation.ruleid.entitytyperange)
            logging.warning("error: %s", err)
        
    logging.info("Converted resource %s to %s", resource.entityid, target_entitytypeid)

    # remove from the search index
    resource.delete_index()
    
    # update type
    resource.entitytypeid = target_entitytypeid
    resource.save()

    # reindex
    resource.index()

def rename_entity_type(old_entitytype_id, new_entitytype_id):
    logging.warning("renaming entitytype from %s to %s", old_entitytype_id, new_entitytype_id)
    

        
    # update the entity_type model and save
    newentitytype = models.EntityTypes.objects.get(entitytypeid=old_entitytype_id)
    newentitytype.entitytypeid=new_entitytype_id
    newentitytype.save()
    
    # update the Rules
    #First find if Rules with the new entitytypeid already exist, if so, delete them and replace their ruleid into mapping_steps with that of the old entitytypeid rule, then rename the rules
    pre_existing_ruleout = models.Rules.objects.filter(entitytypedomain=new_entitytype_id)
    pre_existing_rulein = models.Rules.objects.filter(entitytyperange=new_entitytype_id)
    if pre_existing_ruleout:
        ruleid_to_replace_with = models.Rules.objects.filter(entitytypedomain=old_entitytype_id)
        steps = models.MappingSteps.objects.filter(ruleid= pre_existing_ruleout)
        pre_existing_ruleout.delete()
        for step in steps:
            step.ruleid_id = ruleid_to_replace_with.ruleid
            step.save()
        
    
    if pre_existing_rulein:
        ruleid_to_replace_with = models.Rules.objects.filter(entitytyperange=old_entitytype_id)
        steps = models.MappingSteps.objects.filter(ruleid= pre_existing_rulein)
        pre_existing_rulein.delete()
        for step in steps:
            step.ruleid_id = ruleid_to_replace_with.ruleid
            step.save()
        
        
    rulesout = models.Rules.objects.filter(entitytypedomain=old_entitytype_id)
    for r in rulesout:
        r.entitytypedomain=newentitytype
        r.save()
    
    rulesin = models.Rules.objects.filter(entitytyperange=old_entitytype_id)
    for r in rulesin:
        r.entitytyperange=newentitytype
        r.save()
    
    # update the Mappings
    mappingsout = models.Mappings.objects.filter(entitytypeidfrom=old_entitytype_id)
    for m in mappingsout:
        m.entitytypeidfrom=newentitytype
        m.save()

    mappingsin = models.Mappings.objects.filter(entitytypeidto=old_entitytype_id)
    for m in mappingsin:
        m.entitytypeidto=newentitytype
        m.save()
    
    #update the mergenodeids in the Mappings
    mappingsmergenodes = models.Mappings.objects.filter(mergenodeid=old_entitytype_id)
    for m in mappingsmergenodes:
        m.mergenodeid=newentitytype
        m.save()    
    
    # update the entities
    entities = models.Entities.objects.filter(entitytypeid=old_entitytype_id)
    for e in entities:
        logging.warning("Changing type of entity %s from %s to %s", e, old_entitytype_id, newentitytype)
        e.entitytypeid=newentitytype
        e.save()

    # delete the original entity type (saving the old one with a new pk actually duplicates it)
#     models.EntityTypes.objects.get(entitytypeid=old_entitytype_id).delete()
    remove_entitytypes_and_concepts([old_entitytype_id,new_entitytype_id])

def add_resource_relation(entityid1, entityid2, relationship_type_string):
    # find the relationship type
    se = SearchEngineFactory().create()
    try:
        
        logging.warning("finding relationship: %s", relationship_type_string)
        value = models.Values.objects.get(value__icontains=relationship_type_string)
        relationship = models.RelatedResource(entityid1=entityid1, entityid2=entityid2, relationshiptype=value.pk)
        relationship.save()
        se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(relationship), idfield='resourcexid')
        logging.warning("Added relationship")
    except Exception as e:
        logging.warning("Unable to create relation %s to %s. %s", entityid1, entityid2, e)
        
    

def get_list_dict(pathtofile, fieldnames):
    """
    Gets a list of dictionaries from a csv file

    """

    ret = []
    with open(pathtofile, 'rU') as f:
        rows = unicodecsv.DictReader(f, fieldnames=fieldnames, 
            encoding='utf-8-sig', delimiter=',', restkey='ADDITIONAL', restval='MISSING')
        rows.next() # skip header row
        for row in rows:  
            ret.append(row)
    return ret