import os
import sys 
import traceback
import unicodecsv
import concepts
from time import time
from os import listdir
from os.path import isfile, join
from django.db import connection, transaction
from arches.app.models import models
from arches.app.models.concept import Concept, ConceptValue
from .. import utils

def load_authority_files(path_to_authority_files, break_on_error=True):
    cursor = connection.cursor()
    file_list = []
    
    for f in listdir(path_to_authority_files):
        if isfile(join(path_to_authority_files, f)):
            file_list.append(f)
    
    file_list.sort()
    
    errors = []
    print '\nLOADING AUTHORITY FILES'
    print '------------------------'
    count = 1
    for file_name in file_list:
        errors = errors + load_authority_file(cursor, path_to_authority_files, file_name)
        if count > 0:
            pass
            #break
        count = count + 1
    errors = errors + create_link_to_entity_types(cursor, path_to_authority_files)

    utils.write_to_file(os.path.join(path_to_authority_files, 'authority_file_errors.txt'), '')
    if len(errors) > 0:
        utils.write_to_file(os.path.join(path_to_authority_files, 'authority_file_errors.txt'), '\n'.join(errors))
        print "\n\nERROR: There were errors in some of the authority files."
        print "Please review the errors at %s, \ncorrect the errors and then rerun this script." % (os.path.join(path_to_authority_files, 'authority_file_errors.txt'))
        if break_on_error:
            sys.exit(101)

    #index_concepts()
    
def load_authority_file(cursor, path_to_authority_files, filename):
    start = time()
    cursor.execute("""
            SELECT valuetype FROM concepts.d_valuetypes
        """)

    value_types = [str(value_type[0]) for value_type in cursor.fetchall()]

    sql = """
        SELECT legacyoid FROM concepts.concepts WHERE conceptid = '00000000-0000-0000-0000-000000000004';
    """
    cursor.execute(sql)
    legacyoid = cursor.fetchone()[0]

    filepath = os.path.join(path_to_authority_files, filename)
    unicodecsv.field_size_limit(sys.maxint)
    errors = []
    if filename != 'ENTITY_TYPE_X_ADOC.csv' and filename[-4:] == '.csv':
        print filename.upper()
        try:
            if '.values.' not in filename:
                #create nodes for each authority document file and relate them to the authority document node in the concept schema
                file_legacyid = str(filename)
                concepts.insert_concept(file_legacyid, '', 'en-us', file_legacyid)
                concepts.insert_concept_relations(legacyoid, 'has narrower concept', file_legacyid)
                
                with open(filepath, 'rU') as f:
                    rows = unicodecsv.DictReader(f, fieldnames=['CONCEPTID','PREFLABEL','ALTLABELS','PARENTCONCEPTID','CONCEPTTYPE','PROVIDER'], 
                        encoding='utf-8-sig', delimiter=',', restkey='ADDITIONAL', restval='MISSING')
                    rows.next() # skip header row
                    for row in rows:              
                        try:
                            if 'MISSING' in row:
                                raise Exception('The row wasn\'t parsed properly. Missing %s' % (row['MISSING']))
                            else:
                                concepts.insert_concept(row[u'PREFLABEL'], '', 'en-us', row[u'CONCEPTID'])
                                if row[u'CONCEPTTYPE'].upper() == 'INDEX' and row[u'PARENTCONCEPTID'] != '':
                                    concepts.insert_concept_relations(row[u'PARENTCONCEPTID'], 'includes', row[u'CONCEPTID'])
                                elif row[u'CONCEPTTYPE'].upper() == 'COLLECTOR' and row[u'PARENTCONCEPTID'] != '':
                                    concepts.insert_concept_relations(row[u'PARENTCONCEPTID'], 'has collection', row[u'CONCEPTID'])
                                else:
                                    raise Exception('The row has invalid values.')

                                if row[u'ALTLABELS'] != '':
                                    altlabel_list = row[u'ALTLABELS'].split(';')
                                    for altlabel in altlabel_list:
                                        concepts.insert_concept_value(row[u'CONCEPTID'], altlabel, 'altLabel', 'en-us')
                        except Exception as e:
                            errors.append('ERROR in row %s (%s): %s' % (rows.line_num, str(e), row[u'PREFLABEL']))
                    
                    transaction.commit_unless_managed()
            else:
                with open(filepath, 'rU') as f:
                    rows = unicodecsv.DictReader(f, fieldnames=['CONCEPTID','VALUE','VALUETYPE','PROVIDER'], 
                        encoding='utf-8-sig', delimiter=',', restkey='ADDITIONAL', restval='MISSING')
                    rows.next() # skip header row
                    for row in rows:
                        if row[u'VALUETYPE'] not in value_types: 
                            value_types.append(row[u'VALUETYPE'])
                            cursor.execute("""insert into concepts.d_valuetypes (valuetype) values ('{0}')""".format(row[u'VALUETYPE']))
                        try:
                            concepts.insert_concept_value(row[u'CONCEPTID'], row[u'VALUE'], row[u'VALUETYPE'])
                        except Exception as e:
                            errors.append('ERROR in row %s (%s): %s' % (rows.line_num, str(e), row))

                        transaction.commit_unless_managed()
        except UnicodeDecodeError as e:
            errors.append('ERROR: Make sure the file is saved with UTF-8 encoding\n%s\n%s' % (str(e), traceback.format_exc()))
        except Exception as e:
            errors.append('ERROR: %s\n%s' % (str(e), traceback.format_exc()))

    #print 'Time to parse = %s' % ("{0:.2f}".format(time() - start))    
    if len(errors) > 0:
        errors.insert(0, 'ERRORS IN FILE: %s\n' % (filename))
        errors.append('\n\n\n\n')
    return errors

def create_link_to_entity_types(cursor, path_to_authority_files):
    filepath = os.path.join(path_to_authority_files, 'ENTITY_TYPE_X_ADOC.csv')
    errors = []
    with open(filepath, 'rU') as f:
        rows = unicodecsv.DictReader(f, fieldnames=['ENTITYTYPE','AUTHORITYDOC'], 
                    encoding='utf-8-sig', delimiter=',', restkey='ADDITIONAL', restval='MISSING')
        rows.next() # skip header row
        adoc_dict_list = []
        for row in rows:
            sql = """
                SELECT legacyoid FROM concepts.concepts 
                WHERE conceptid IN (SELECT conceptid FROM data.entity_types WHERE entitytypeid = '%s')
            """%(row[u'ENTITYTYPE'])
            #print sql

            try:
                cursor.execute(sql)
                entity_type = str(cursor.fetchone()[0])
                concepts.insert_concept_relations(entity_type, 'has authority document', str(row['AUTHORITYDOC']))
            except Exception as e:
                errors.append('ERROR in row %s (%s):\n%s\n%s' % (rows.line_num, str(e), sql, traceback.format_exc()))

    if len(errors) > 0:
        errors.insert(0, 'ERRORS IN FILE: %s\n' % (filepath))
        errors.append('\n\n\n\n')
    return errors

def index_concepts():
    start = time()
    from arches.app.utils.betterJSONSerializer import JSONSerializer
    concepts = models.Concepts.objects.all()
    for concept in concepts:
        concept_graph = Concept().get(concept.pk, include=['label'])
        #print JSONSerializer().serialize(concept_graph)
        concept_graph.index()
    print 'Time to index = %s' % ("{0:.2f}".format(time() - start)) 
    print 'Time per concept: %s' % ((time() - start)/len(concepts))
