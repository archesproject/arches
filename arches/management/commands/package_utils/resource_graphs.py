import os
import sys 
import codecs
import traceback
import unicodecsv
from os import listdir
from os.path import isfile, join
from django.core import management
from django.db import connection, transaction
# import concepts
from .. import utils
from arches.app.models.graph import Graph
import json
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

suffix = 'json'

def load_graphs(break_on_error=True, settings=None, path=None):
    """
    Iterates through the resource node and edge files to load entitytypes and mappings into the database.
    Generates node level permissions for each resourcetype/entitytype combination

    """

    if not settings:
        from django.conf import settings        
  
    errors = []
    graph_location = settings.RESOURCE_GRAPH_LOCATIONS
        
    if path:
        graph_location = [path]

    for path in graph_location:
        if os.path.exists(path):
            print '\nLOADING GRAPHS (%s)' % (path)
            print '---------------'
            if isfile(join(path)) and path.endswith(suffix):
                load_resource_graph_file(path)
            else:
                for f in listdir(path):
                    load_resource_graph_file(join(path,f))
        else:
            errors.append('\n\nPath in settings.RESOURCE_GRAPH_LOCATIONS doesn\'t exist (%s)' % (path))                 

    # utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'resource_graph_errors.txt'), '')
    # if len(errors) > 0:
    #     utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'resource_graph_errors.txt'), '\n'.join(errors))
    #     print "\n\nERROR: There were errors in some of the resource graphs."
    #     print "Please review the errors at %s, \ncorrect the errors and then rerun this script." % (os.path.join(settings.PACKAGE_ROOT, 'logs', 'resource_graph_errors.txt'))
    #     if break_on_error:
    #         sys.exit(101)

    # print '\nINDEXING ENTITY NODES'
    # print '---------------------'
    # concepts.index_entity_concept_lables()

    # print '\nADDING NODE LEVEL PERMISSIONS'
    # print '-----------------------------'
    # management.call_command('packages', operation='build_permissions') 

def load_resource_graph_file(path_to_file):
    if isfile(path_to_file) and path_to_file.endswith(suffix):
        basepath = path_to_file
        name = basepath.split(os.sep)[-1]
        
        with codecs.open(basepath, 'rU', encoding='utf-8') as f:
            file = json.load(f)
            resource_graph = Graph(file['graph'][0])
            resource_graph.save()

def append_branch(path_to_branch, node_list, edge_list):
    """
    Appends a branch to the root of the passed in graph (represented as the node_list and edge_list)

    Args:
       path_to_branch (str):  path to the file where the branch graph lives(minus the _nodes.csv or _edges.csv suffix) 
            (eg: '<path>/ARCHES_RECORD.E31', where the actual nodes and edges files look like ARCHES_RECORD.E31_nodes.csv and ARCHES_RECORD.E31_edges.csv)

    Returns:
       {'node_list': node_list_with_added_branch, 'edge_list': edge_list_with_added_branch}

    """

    nodes_to_append = get_list_dict(path_to_branch + '_nodes.csv', ['ID', 'LABEL', 'MERGENODE', 'BUSINESSTABLE'])
    edges_to_append = get_list_dict(path_to_branch + '_edges.csv', ['SOURCE', 'TARGET', 'TYPE', 'ID', 'LABEL', 'WEIGHT'])

    root_node_id_of_main_graph = get_root_node_id(edge_list)
    root_node_id_of_branch = get_root_node_id(edges_to_append)
    
    # rename branch root (which is a dummy value) to the graph root value
    for edge in edges_to_append:
        if edge['SOURCE'] == root_node_id_of_branch:
            edge['SOURCE'] = root_node_id_of_main_graph

    node_list = node_list + nodes_to_append
    edge_list = edge_list + edges_to_append
    
    return {'node_list': node_list, 'edge_list': edge_list}

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
        if node['BUSINESSTABLE'] != u'' and node['BUSINESSTABLE'] not in [u'strings', u'dates', u'domains', u'files', u'geometries', u'numbers']:
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

    # transaction.commit_unless_managed()

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

