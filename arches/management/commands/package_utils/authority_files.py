import os
import sys 
import uuid
import traceback
import unicodecsv
import concepts
import string
from time import time
from os import listdir
from os.path import isfile, join, exists
from django.db import connection, transaction
from django.conf import settings
from arches.app.models import models
from arches.app.models.concept import Concept, ConceptValue
from .. import utils

class Lookups(object):
    def __init__(self, *args, **kwargs):
        self.lookup = {}
        self.concept_relationships = []

    def add_lookup(self, concept=None, rownum=None):
        self.lookup[concept.legacyoid] = {'concept': concept, 'rownum': rownum}

    def get_lookup(self, legacyoid=''):
        if legacyoid in self.lookup:
            return self.lookup[legacyoid]['concept']
        else:
            raise Exception('Legacyoid (%s) not found.  Make sure your ParentConceptid in the csv file references a previously saved concept.' % (legacyoid))

    def add_relationship(self, source=None, type=None, target=None, rownum=None):
        self.concept_relationships.append({'source': source, 'type': type, 'target': target, 'rownum': rownum})

def load_authority_files(break_on_error=True):
    cursor = connection.cursor()
    file_list = []
    errors = []
    
    for path in settings.CONCEPT_SCHEME_LOCATIONS:
        if os.path.exists(path):
            print '\nLOADING AUTHORITY FILES (%s)' % (path)
            print '-----------------------'            
            
            for f in listdir(path):
                if isfile(join(path,f)) and '.values.csv' not in f and f != 'ENTITY_TYPE_X_ADOC.csv' and f[-4:] == '.csv':
                    file_list.append(f)
            
            file_list.sort()

            auth_file_to_entity_concept_mapping = entitytype_to_auth_doc_mapping(cursor, path)
            count = 1
            for file_name in file_list:
                errors = errors + load_authority_file(cursor, path, file_name, auth_file_to_entity_concept_mapping)
                if count > 10:
                    pass
                    #break
                count = count + 1
            #errors = errors + create_link_to_entity_types(cursor, path)
        else:
            errors.append('\n\nPath in settings.CONCEPT_SCHEME_LOCATIONS doesn\'t exist (%s)' % (path))  

    utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'authority_file_errors.txt'), '')
    if len(errors) > 0:
        utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'authority_file_errors.txt'), '\n'.join(errors))
        print "\n\nERROR: There were errors in some of the authority files."
        print "Please review the errors at %s, \ncorrect the errors and then rerun this script." % (os.path.join(settings.PACKAGE_ROOT, 'logs', 'authority_file_errors.txt'))
        if break_on_error:
            sys.exit(101)


def load_authority_file(cursor, path_to_authority_files, filename, auth_file_to_entity_concept_mapping):
    print filename.upper()    

    start = time()
    value_types = models.ValueTypes.objects.all()
    filepath = os.path.join(path_to_authority_files, filename)
    unicodecsv.field_size_limit(sys.maxint)
    errors = []
    lookups = Lookups()

    #create nodes for each authority document file and relate them to the authority document node in the concept schema
    auth_doc_file_name = str(filename)
    display_file_name = string.capwords(auth_doc_file_name.replace('_',' ').replace('AUTHORITY DOCUMENT.csv', '').strip())
    if auth_doc_file_name.upper() != 'ARCHES RESOURCE CROSS-REFERENCE RELATIONSHIP TYPES.E32.CSV':
        concept = Concept()
        concept.id = str(uuid.uuid4())
        concept.nodetype = 'ConceptScheme'       
        concept.legacyoid = auth_doc_file_name
        concept.addvalue({'value':display_file_name, 'language': 'en-us', 'type': 'prefLabel', 'category': 'label'})
        scheme_id = concept
        lookups.add_relationship(source='00000000-0000-0000-0000-000000000001', type='narrower', target=concept.id)

    else:
        concept = Concept().get(id = '00000000-0000-0000-0000-000000000005')
        concept.legacyoid = 'ARCHES RESOURCE CROSS-REFERENCE RELATIONSHIP TYPES.E32.csv'
        scheme_id = concept

    lookups.add_lookup(concept=concept, rownum=0)
    
    try:
        with open(filepath, 'rU') as f:
            rows = unicodecsv.DictReader(f, fieldnames=['CONCEPTID','PREFLABEL','ALTLABELS','PARENTCONCEPTID','CONCEPTTYPE','PROVIDER'], 
                encoding='utf-8-sig', delimiter=',', restkey='ADDITIONAL', restval='MISSING')
            rows.next() # skip header row
            for row in rows:              
                try:
                    if 'MISSING' in row:
                        raise Exception('The row wasn\'t parsed properly. Missing %s' % (row['MISSING']))
                    else:
                        concept = Concept()
                        concept.id = str(uuid.uuid4())
                        concept.nodetype = 'Concept'# if row[u'CONCEPTTYPE'].upper() == 'INDEX' else 'Collection'
                        concept.legacyoid = row[u'CONCEPTID']
                        concept.addvalue({'value':row[u'PREFLABEL'], 'language': 'en-us', 'type': 'prefLabel', 'category': 'label'})
                        if row['CONCEPTTYPE'].lower() == 'collector':
                            concept.addvalue({'value':row[u'PREFLABEL'], 'language': 'en-us', 'type': 'collector', 'category': 'label'})
                        if row[u'ALTLABELS'] != '':
                            altlabel_list = row[u'ALTLABELS'].split(';')
                            for altlabel in altlabel_list:
                                concept.addvalue({'value':altlabel, 'language': 'en-us', 'type': 'altLabel', 'category': 'label'})    
                        if lookups.get_lookup(row[u'PARENTCONCEPTID']).values[0].type == 'collector':
                            lookups.add_relationship(source=lookups.get_lookup(legacyoid=row[u'PARENTCONCEPTID']).id, type='member', target=concept.id, rownum=rows.line_num)

                        lookups.add_relationship(source=lookups.get_lookup(legacyoid=row[u'PARENTCONCEPTID']).id, type='narrower', target=concept.id, rownum=rows.line_num)
                        
                        if auth_doc_file_name in auth_file_to_entity_concept_mapping:
                            lookups.add_relationship(source=auth_file_to_entity_concept_mapping[auth_doc_file_name]['ENTITYTYPE_CONCEPTID'], type='member', target=concept.id, rownum=rows.line_num)

                        if row[u'PARENTCONCEPTID'] == '' or (row[u'CONCEPTTYPE'].upper() != 'INDEX' and row[u'CONCEPTTYPE'].upper() != 'COLLECTOR'):
                            raise Exception('The row has invalid values.')

                        lookups.add_lookup(concept=concept, rownum=rows.line_num)    
                        
                except Exception as e:
                    errors.append('ERROR in row %s: %s' % (rows.line_num, str(e)))           
    
    except UnicodeDecodeError as e:
        errors.append('ERROR: Make sure the file is saved with UTF-8 encoding\n%s\n%s' % (str(e), traceback.format_exc()))
    except Exception as e:
        errors.append('ERROR: %s\n%s' % (str(e), traceback.format_exc()))
    
    if len(errors) > 0:
        errors.insert(0, 'ERRORS IN FILE: %s\n' % (filename))
        errors.append('\n\n\n\n')

    try:
        # try and open the values file if it exists
        if exists(filepath.replace('.csv', '.values.csv')):
            with open(filepath.replace('.csv', '.values.csv'), 'rU') as f:
                rows = unicodecsv.DictReader(f, fieldnames=['CONCEPTID','VALUE','VALUETYPE','PROVIDER'], 
                    encoding='utf-8-sig', delimiter=',', restkey='ADDITIONAL', restval='MISSING')
                rows.next() # skip header row
                for row in rows:
                    try:
                        if 'ADDITIONAL' in row:
                            raise Exception('The row wasn\'t parsed properly. Additional fields found %s.  Add quotes to values that have commas in them.' % (row['ADDITIONAL']))
                        else:
                            row_valuetype = row[u'VALUETYPE'].strip()
                            if row_valuetype not in value_types.values_list('valuetype', flat=True): 
                                valuetype = models.ValueTypes()
                                valuetype.valuetype = row_valuetype
                                valuetype.category = 'undefined'
                                valuetype.namespace = 'arches'
                                valuetype.save()
                            
                            value_types = models.ValueTypes.objects.all()
                            concept = lookups.get_lookup(legacyoid=row[u'CONCEPTID'])
                            category = value_types.get(valuetype=row_valuetype).category
                            concept.addvalue({'value':row[u'VALUE'], 'type': row[u'VALUETYPE'], 'category': category})

                    except Exception as e:
                        errors.append('ERROR in row %s (%s): %s' % (rows.line_num, str(e), row))
    
    except UnicodeDecodeError as e:
        errors.append('ERROR: Make sure the file is saved with UTF-8 encoding\n%s\n%s' % (str(e), traceback.format_exc()))
    except Exception as e:
        errors.append('ERROR: %s\n%s' % (str(e), traceback.format_exc()))            
        
    if len(errors) > 0:
        errors.insert(0, 'ERRORS IN FILE: %s\n' % (filename.replace('.csv', '.values.csv')))
        errors.append('\n\n\n\n')


    # insert and index the concpets
    for key in lookups.lookup:
        try:
            lookups.lookup[key]['concept'].save()
        except Exception as e:
            errors.append('ERROR in row %s (%s):\n%s\n' % (lookups.lookup[key]['rownum'], str(e), traceback.format_exc()))
        
        lookups.lookup[key]['concept'].index(scheme=scheme_id)            

    # insert the concept relations
    for relation in lookups.concept_relationships:
        sql = """
            INSERT INTO concepts.relations(conceptidfrom, conceptidto, relationtype)
            VALUES ('%s', '%s', '%s');
        """%(relation['source'], relation['target'], relation['type'])
        #print sql
        try:
            cursor.execute(sql)
        except Exception as e:
            errors.append('ERROR in row %s (%s):\n%s\n' % (relation['rownum'], str(e), traceback.format_exc()))
    
    if len(errors) > 0:
        errors.insert(0, 'ERRORS IN FILE: %s\n' % (filename))
        errors.append('\n\n\n\n')

    #print 'Time to parse = %s' % ("{0:.2f}".format(time() - start))    

    return errors

def entitytype_to_auth_doc_mapping(cursor, path_to_authority_files):
    filepath = os.path.join(path_to_authority_files, 'ENTITY_TYPE_X_ADOC.csv')
    errors = []
    ret = {}
    with open(filepath, 'rU') as f:
        rows = unicodecsv.DictReader(f, fieldnames=['ENTITYTYPE','AUTHORITYDOC'], 
                    encoding='utf-8-sig', delimiter=',', restkey='ADDITIONAL', restval='MISSING')
        rows.next() # skip header row
        for row in rows:
            if row[u'ENTITYTYPE'] != 'ARCHES RESOURCE CROSS-REFERENCE RELATIONSHIP TYPES.E32.csv':
                sql = """
                    SELECT conceptid FROM data.entity_types WHERE entitytypeid = '%s'
                """%(row[u'ENTITYTYPE'])
                #print sql

            try:
                cursor.execute(sql)
                entity_type_conceptid = str(cursor.fetchone()[0])
                ret[str(row['AUTHORITYDOC'])] = {'ENTITYTYPE' : row[u'ENTITYTYPE'], 'ENTITYTYPE_CONCEPTID': entity_type_conceptid}
            except Exception as e:
                errors.append('ERROR in row %s (%s):\n%s\n%s' % (rows.line_num, str(e), sql, traceback.format_exc()))

    if len(errors) > 0:
        errors.insert(0, 'ERRORS IN FILE: %s\n' % (filepath))
        errors.append('\n\n\n\n')
    return ret

