import os
import sys 
import traceback
import unicodecsv
from os import listdir
from os.path import isfile, join
from django.conf import settings
from django.db import connection, transaction
import concepts
from .. import utils

def load_graphs(packagepath, break_on_error=True):
    """
    Iterates through the resource node and edge files to load entitytypes and mappings into the database.

    """

    print '\nLOADING GRAPHS'
    print '---------------'
    suffix = '_nodes.csv'
    errors = []
    path_to_resource_graphs = os.path.join(packagepath, 'source_data', 'resource_graphs')
    
    file_list = []
    for f in listdir(path_to_resource_graphs):
        if isfile(join(path_to_resource_graphs,f)):
            file_list.append(f)

    for filename in file_list:
        if filename.endswith(suffix):
            name = filename[:-10]
            if (settings.LIMIT_ENTITY_TYPES_TO_LOAD == None or name in settings.LIMIT_ENTITY_TYPES_TO_LOAD):
                print name
                node_list = get_list_dict(path_to_resource_graphs, name + '_nodes.csv', ['ID', 'LABEL', 'MERGENODE', 'BUSINESSTABLE'])
                edge_list = get_list_dict(path_to_resource_graphs, name + '_edges.csv', ['SOURCE', 'TARGET', 'TYPE', 'ID', 'LABEL', 'WEIGHT'])
                mods = append_arches_record_branch(node_list, edge_list)
                node_list = mods['node_list']
                edge_list = mods['edge_list']

                file_errors = validate_graph(node_list, edge_list)
                try:
                    insert_mappings(node_list, edge_list)
                    link_entitytypes_to_concepts(node_list)
                except Exception as e:
                    file_errors.append('\nERROR: %s\n%s' % (str(e), traceback.format_exc()))
                    pass

                if len(file_errors) > 0:
                    file_errors.insert(0, 'ERRORS IN FILE: %s\n' % (filename))
                    file_errors.append('\n\n\n\n')
                    errors = errors + file_errors                    

    utils.write_to_file(os.path.join(path_to_resource_graphs, 'resource_graph_errors.txt'), '')
    if len(errors) > 0:
        utils.write_to_file(os.path.join(path_to_resource_graphs, 'resource_graph_errors.txt'), '\n'.join(errors))
        print "\n\nERROR: There were errors in some of the resource graphs."
        print "Please review the errors at %s, \ncorrect the errors and then rerun this script." % (os.path.join(path_to_resource_graphs, 'resource_graph_errors.txt'))
        if break_on_error:
            sys.exit(101)

def append_arches_record_branch(node_list, edge_list):
    name = 'ARCHES_RECORD.E31'
    path_to_resource_graphs = os.path.join(settings.ROOT_DIR, 'management', 'resource_graphs')
    nodes_to_append = get_list_dict(path_to_resource_graphs, name + '_nodes.csv', ['ID', 'LABEL', 'MERGENODE', 'BUSINESSTABLE'])
    edges_to_append = get_list_dict(path_to_resource_graphs, name + '_edges.csv', ['SOURCE', 'TARGET', 'TYPE', 'ID', 'LABEL', 'WEIGHT'])

    root_node_id_of_main_graph = get_root_node_id(edge_list)
    root_node_id_of_branch = get_root_node_id(edges_to_append)

    node_list = node_list + nodes_to_append
    edge_list = edge_list + edges_to_append

    edge_list.append({'SOURCE': '%s' % (root_node_id_of_main_graph), 'TARGET': '%s' % (root_node_id_of_branch), 
        'TYPE': 'Directed', 'ID': 'A09WROSIFEJAEF9ASKDLFKSJ', 'LABEL': 'P70', 'WEIGHT': '1.0'})
    
    return {'node_list': node_list, 'edge_list': edge_list}

def get_list_dict(pathtofile, filename, fieldnames):
    """
    Gets a list of dictionaries from a csv file

    """

    ret = []
    with open(os.path.join(pathtofile, filename), 'rU') as f:
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
        if node['LABEL'].strip().replace(' ','') != node['LABEL']:
            append_error('Spaces are not allowed in labels, use underscores instead', node)

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

    for node in nodes:
        entitytypeid = get_node(node["ID"], nodes)["LABEL"]
        if node['BUSINESSTABLE'] != '' and node['BUSINESSTABLE'] != 'entities':
            mapping = get_mapping_steps_from_node_id(node["ID"], nodes, edges) 
            sql = """
                SELECT ontology.insert_mappings('%s','%s');
                """ % (", ".join(mapping), node["MERGENODE"])
            # print sql
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
        WHERE conceptid = '00000000-0000-0000-0000-000000000002'
        """)
    sourcelegacyid = cursor.fetchone()[0]

    for node in nodes:
        concepts.insert_concept_relations(str(sourcelegacyid), 'has narrower concept', node["LABEL"])
