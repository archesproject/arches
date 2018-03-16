import os
import sys
import traceback
import unicodecsv
from os import listdir
from os.path import isfile, join
from django.core import management
from django.db import connection, transaction
import concepts
from .. import utils
import arches.app.models.models as models
from arches.app.models.concept import Concept

import logging

def load_graphs(break_on_error=True, settings=None):
    
    if not settings:
        from django.conf import settings
    
    added_nodes_suffix = '_added_nodes.csv'
    errors = []
    
    for path in settings.ADDITIONAL_RESOURCE_GRAPH_LOCATIONS:
        if os.path.exists(path):
            print '\nLOADING ADDITION GRAPHS (%s)' % (path)
            print '-----------------'
            for f in listdir(path):
                if isfile(join(path,f)) and f.endswith(added_nodes_suffix):
                    path_to_file = join(path,f)
                    basepath = path_to_file[:-16]
                    name = basepath.split(os.sep)[-1]
                    if (settings.LIMIT_ENTITY_TYPES_TO_LOAD == None or name in settings.LIMIT_ENTITY_TYPES_TO_LOAD):
                        node_list = get_list_dict(basepath + '_added_nodes.csv', ['ID', 'LABEL', 'MERGENODE', 'BUSINESSTABLE'])
                        edge_list = get_list_dict(basepath + '_added_edges.csv', ['SOURCE', 'TARGET', 'TYPE', 'ID', 'LABEL', 'WEIGHT'])
                        altered_edge_list = get_list_dict(basepath + '_altered_edges.csv', ['SOURCE', 'TARGET', 'OLDTYPE', 'NEWTYPE'])
                        altered_node_list = get_list_dict(basepath + '_altered_nodes.csv', ['OLDENTITYTYPEID', 'NEWENTITYTYPEID', 'GROUPROOTNODEOLD', 'GROUPROOTNODENEW'])
                        file_errors = validate_graph(node_list, edge_list)
                        logging.warning('validation errors: %s', file_errors)
                        try:
                            insert_mappings(node_list, edge_list)
                            link_entitytypes_to_concepts(node_list)
                        except Exception as e:
                            logging.warning('error inserting mappings: %s\n%s', str(e), traceback.format_exc())
                            file_errors.append('\nERROR: %s\n%s' % (str(e), traceback.format_exc()))
                            pass
                        
                        if len(file_errors) > 0:
                            file_errors.insert(0, 'ERRORS IN FILE: %s\n' % (basepath))
                            file_errors.append('\n\n\n\n')
                        
                        logging.warning("\n\n\n------------------\nLoaded new ontology branches\nUpdating edges")
                        
                        #Update edges
                        for edge in altered_edge_list:
                            # simply update the property referenced by the rule
                            try:
                                rule = models.Rules.objects.all().get(
                                    propertyid=edge['OLDTYPE'],
                                    entitytypedomain=edge['SOURCE'],
                                    entitytyperange=edge['TARGET']
                                )
                        
                                newProperty = models.Properties.objects.all().get(propertyid=edge['NEWTYPE'])
                                rule.propertyid = newProperty
                                rule.save()
                                logging.warning("Updated property type for edge: %s", edge)
                            except:
                                logging.warning("couldn't find rule for edge: %s", edge)
                        
                        
                        logging.warning("\n\n\n------------------\nUpdated edges\nUpdating reference data")
                        
                        update_reference_data(altered_node_list)
        else:
            logging.warning('PATH DOESNT EXIST')
            errors.append('\n\nPath in settings.RESOURCE_GRAPH_LOCATIONS doesn\'t exist (%s)' % (path))                 
        
    utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'resource_graph_addition_errors.txt'), '')
    if len(errors) > 0:
        utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'resource_graph_addition_errors.txt'), '\n'.join(errors))
        print "\n\nERROR: There were errors in some of the resource graphs."
        print "Please review the errors at %s, \ncorrect the errors and then rerun this script." % (os.path.join(settings.PACKAGE_ROOT, 'logs', 'resource_graph_errors.txt'))
        if break_on_error:
            sys.exit(101)
    #         
    # print '\nINDEXING ENTITY NODES'
    # print '---------------------'
    # concepts.index_entity_concept_lables()
    # 
    # print '\nADDING NODE LEVEL PERMISSIONS'
    # print '-----------------------------'
    # management.call_command('packages', operation='build_permissions')
    

def update_reference_data(altered_node_list):
    # After the new part of ontology has been inserted. Update the reference data for moved nodes
    for node in altered_node_list:
        
        if node['OLDENTITYTYPEID'] == '':
            # ignore empty rows
            continue;
        
        try:
            logging.warning("---")
            logging.warning("UPDATING REFERENCE DATA FOR %s", node['NEWENTITYTYPEID'])
            # get root concept for the old node
            old_entity_type = models.EntityTypes.objects.all().get(entitytypeid=node['OLDENTITYTYPEID'])
            new_entity_type = models.EntityTypes.objects.all().get(entitytypeid=node['NEWENTITYTYPEID'])
            
            # set as the root concept for the new node
            new_entity_type.conceptid = old_entity_type.conceptid
            new_entity_type.save()
            
            # traverse all related concepts, updating legacyOID for concepts which are EntityType or Collection
            try:
                root_concept = Concept()
                root_concept.get(new_entity_type.conceptid)
                # rewrite_concept(root_concept, new_entity_type.pk)
                root_concept.traverse(rewrite_concept, scope=new_entity_type.pk)
                
            except Exception as e:
                logging.warning("\n\nUnable to update concepts for migration mapping: %s \n%s", node, e)
        except Exception as e:
            logging.warning("\n\nUnable to update reference data for migration mapping: %s \n%s", node, e)

        # Now migrate the authority document concepts also
        try:
            logging.warning("Updating auth doc concept for %s", node)
            # find the old authority document entitytype corresponding to this entitytype
            old_authority_document_entitytype_rule = models.Rules.objects.get(entitytypedomain=node['OLDENTITYTYPEID'], propertyid='-P71')
            old_authority_document_entitytypeid = old_authority_document_entitytype_rule.entitytyperange
            
            new_authority_document_entitytype_rule = models.Rules.objects.get(entitytypedomain=node['NEWENTITYTYPEID'], propertyid='-P71')
            new_authority_document_entitytypeid = new_authority_document_entitytype_rule.entitytyperange
            
            old_authority_document_entitytype = models.EntityTypes.objects.get(entitytypeid=old_authority_document_entitytypeid)
            new_authority_document_entitytype = models.EntityTypes.objects.get(entitytypeid=new_authority_document_entitytypeid)
            
            # point the new authority document entitytype at the concept for the old one
            new_authority_document_entitytype.conceptid = old_authority_document_entitytype.conceptid
            new_authority_document_entitytype.save()
            
            # update the value
            top_concept_value = models.Values.objects.get(conceptid=old_authority_document_entitytype.conceptid, languageid='en-US')
            top_concept_value.value = node['NEWENTITYTYPEID']
            top_concept_value.save()
            
            # remove the old stub concept created for the new auth doc node?
        
        except Exception as e:
            logging.warning("\n\nUnable to update Entity %s", e)

def rewrite_concept(concept, entitytypeid):
    try:
        if concept.nodetype == 'Collection':
            #delete the concept which was created when the entitytype was added
            created_concept_model = models.Concepts.objects.all().get(legacyoid=entitytypeid)
            created_concept_model.delete()
            
            #rename the legacyoid
            concept_model = models.Concepts.objects.all().get(conceptid=concept.id)
            concept_model.legacyoid = entitytypeid
            concept_model.save()
            
            # also update value of the root collection concept
            try:
                value = models.Values.objects.get(conceptid=concept.id, languageid='en-US')
                print value.value
                value.value = entitytypeid
                value.save()
                
            except Exception as e:
                logging.warning("Couldn't update en-US value for collection concept: %s", concept.legacyoid)
            
        elif concept.nodetype == 'EntityType':
            #delete the concept which was created when the entitytype was added
            created_concept_model = models.Concepts.objects.all().get(legacyoid=entitytypeid)
            created_concept_model.delete()
            
            #rename the legacyoid
            concept_model = models.Concepts.objects.all().get(conceptid=concept.id)
            concept_model.legacyoid = entitytypeid
            concept_model.save()
        
    except Exception as e:
        logging.warning("Unable to update concept to match entitytype %s\n%s", entitytypeid, e)
        
        


def insert_mappings(nodes, edges):
    """
    Inserts the mappings, mapping steps, and entitytypes into the database

    """

    cursor = connection.cursor()

    root_node_id = get_root_node_id(edges)

    for node in nodes:
        if node['ID'] != root_node_id:
            mapping = get_mapping_steps_from_node_id(node["ID"], nodes, edges) 
            sql = """
                SELECT ontology.insert_mappings('%s','%s');
                """ % (", ".join(mapping), node["MERGENODE"])
            #print sql
            cursor.execute(sql)
            cursor.fetchone()

    transaction.commit_unless_managed()
    


def get_mapping_steps_from_node_id(node_id, nodes, edges, mapping=None):
    """
    Gets a complete mapping (from root to leaf) for a given leaf node

    """

    for edge in edges:
        if mapping == None:
            mapping = []
            node = get_node(node_id, nodes)
            mapping.append(node["LABEL"])
            mapping.append(node["BUSINESSTABLE"])
        if node_id == edge['TARGET']:
            mapping.insert(0, edge["LABEL"])
            node = get_node(edge["SOURCE"], nodes)
            mapping.insert(0, node["BUSINESSTABLE"])
            mapping.insert(0, node["LABEL"])
            get_mapping_steps_from_node_id(edge["SOURCE"], nodes, edges, mapping)
    return mapping

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


def validate_graph(node_list, edge_list):
    """
    Validate that the graphs meet certain criteria

    """

    errors = []
    node_types = []
    nodes_referenced_in_edgefile = []
    for i in edge_list:
        nodes_referenced_in_edgefile.append(i['SOURCE'])
        nodes_referenced_in_edgefile.append(i['TARGET'])
    nodes_referenced_in_edgefile = list(set(nodes_referenced_in_edgefile))

    def append_error(text, node):
         errors.append('ERROR (%s): in node %s: %s' % (text, node['LABEL'], node))

    for node in node_list:
        # validate business table name
        if node['BUSINESSTABLE'] != u'' and node['BUSINESSTABLE'] not in [u'strings', u'dates', u'domains', u'files', u'geometries', u'numbers', u'uniqueids']:
            append_error('Incorrect business table', node)

        # validate node uniqueness
        if node['LABEL'] in node_types:
            append_error('Duplicate label', node)
            node_types.append(node['LABEL'])

        # validate no spaces in node label
        # if node['LABEL'].strip().replace(' ','') != node['LABEL']:
        #     append_error('Spaces are not allowed in labels, use underscores instead', node)

        # validate uppercase convention in node label
        if node['LABEL'].upper() != node['LABEL']:
            append_error('Use all upper case for labels', node)
    
        # validate nodes have edges
        if node['ID'] not in nodes_referenced_in_edgefile:
            append_error('Node isn\'t connected to any other node', node)

        if 'MISSING' in node:
            append_error('A row in the csv file wasn\'t parsed properly. Node: %s' % (node))

    return errors


def get_node(id, node_list):
    for node in node_list:
        if id == node["ID"]:
            return node
        

def get_root_node_id(edge_list):
    target_nodes = []
    for edge in edge_list:
        target_nodes.append(edge['TARGET'])

    for edge in edge_list:
        if edge['SOURCE'] not in target_nodes:
            return edge['SOURCE']
        
def link_entitytypes_to_concepts(nodes):
    """
    Links entitytypes to their associated concepts

    """

    cursor = connection.cursor()
    cursor.execute("""SELECT legacyoid FROM concepts.concepts 
        WHERE conceptid = '00000000-0000-0000-0000-000000000003'
        """)
    domainlegacyid = cursor.fetchone()[0]

    cursor.execute("""SELECT legacyoid FROM concepts.concepts 
        WHERE conceptid = '00000000-0000-0000-0000-000000000004'
        """)
    otherlegacyid = cursor.fetchone()[0]

    for node in nodes:
        if node['BUSINESSTABLE'] == 'domains':
            concepts.insert_concept_relations(str(domainlegacyid), 'hasCollection', node["LABEL"])
        else:
            concepts.insert_concept_relations(str(otherlegacyid), 'hasEntity', node["LABEL"])
