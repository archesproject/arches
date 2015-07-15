import os
import types
import sys
from django.conf import settings
from django.db import connection
from arches.app.models.models import Concepts
from arches.app.models.models import Values
from arches.app.models.concept import Concept
from arches.app.models.resource import Resource
import arches.app.models.models as archesmodels
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Terms
from django.core.management.base import BaseCommand, CommandError
import collections
from .. import utils
from datetime import datetime


def index_db():
    """Deletes any existing indicies from elasticsearch and then indexes all
    concepts and resources from the database"""

    result_summary = {}
    clear_existing_indexes()
    print 'indexes cleared'
    index_entity_concept_labels()
    print 'entitytypes indexed'
    print 'creating term index'
    Resource().prepare_term_index(create=True)
    print 'indexing concepts'
    start = datetime.now()
    index_concepts()
    print 'concepts indexed'
    end = datetime.now()
    duration = end - start
    print 'indexing concepts required', duration.seconds, 'seconds'

    se = SearchEngineFactory().create()
    cursor = connection.cursor()
    cursor.execute("""select conceptid, conceptlabel from concepts.vw_concepts""")
    concepts = cursor.fetchall()
    concept_index_results = {'count':len(concepts), 'passed':0, 'failed':0}

    for conceptid, conceptvalue in concepts:
        result = get_indexed_concepts(se, conceptid, conceptvalue)
        if result != 'passed':
            concept_index_results['failed'] += 1
        else:
            concept_index_results['passed'] += 1
    status = 'Passed' if concept_index_results['failed'] == 0 else 'failed'
    print '\nConcept Index Results:'
    print "Status: {0}, In Database: {1}, Indexed: {2}".format(status, concept_index_results['count'], concept_index_results['passed'])

    cursor.execute("""select entitytypeid from data.entity_types where isresource = TRUE""")
    resource_types = cursor.fetchall()
    Resource().prepare_resource_relations_index(create=True)

    for resource_type in resource_types:
        Resource().prepare_search_index(resource_type[0], create=True)
    
    index_resources(resource_types, result_summary)

    for resource_type in resource_types:
        indexed = get_indexed_resources(se, resource_type[0])
        result_summary[resource_type[0]]['indexed'] = len(indexed)

    print '\nResource Index Results:'
    for k, v in result_summary.iteritems():
        status = 'Passed' if v['database'] == v['indexed'] else 'failed'
        print "Status: {0}, Resource Type: {1}, In Database: {2}, Indexed: {3}".format(status, k, v['database'], v['indexed'])

def clear_existing_indexes():
    """Deletes all indicies"""
    # index_types = ['concept_labels', 'resource_relations', 'term', 'entity']
    index_types = ['resource_relations', 'entity']
    se = SearchEngineFactory().create()
    for index_type in index_types:
        se.delete_index(index=index_type)
    #     index.Command().handle('index', delete=index_type, index='', load='')

def index_entity_concept_labels():    
    domains_concept = Concept('00000000-0000-0000-0000-000000000003')
    entitynodes_concept = Concept('00000000-0000-0000-0000-000000000004')
    entitytypes = archesmodels.EntityTypes.objects.all()
    for entitytype in entitytypes:
        concept = Concept(entitytype.conceptid).get(include=['label'])
        if entitytype.businesstablename == 'domains':
            concept.index(scheme=domains_concept)
        else:
            concept.index(scheme=entitynodes_concept)

def index_concepts():
    """Collects all concepts and indexes both concepts and concept_labels"""
    cursor = connection.cursor()
    cursor.execute("""select conceptid from concepts.concepts""")
    conceptids = cursor.fetchall()
    for c in conceptids:
        if c[0] not in [
            '00000000-0000-0000-0000-000000000001', 
            '00000000-0000-0000-0000-000000000003', 
            '00000000-0000-0000-0000-000000000004',
            '00000000-0000-0000-0000-000000000005',
            '00000000-0000-0000-0000-000000000006']:
            concept = Concept().get(id=c[0], include_subconcepts=True, include_parentconcepts=False, include=['label'])
            concept.index()

def index_resources(resource_types, result_summary):
    """Collects and indexes all resources"""
    for resource_type in resource_types:
        resources = archesmodels.Entities.objects.filter(entitytypeid = resource_type)
        print "Indexing {0} {1} resources".format(len(resources), resource_type[0])
        result_summary[resource_type[0]] = {'database':len(resources), 'indexed':0}
        errors = []
        for resource in resources:
            try:
                resource = Resource().get(resource.entityid)
                resource.index()
            except Exception as e:
                if e not in errors:
                    errors.append(e)
        if len(errors) > 0:
            print errors[0], ':', len(errors)

    return result_summary

def get_indexed_resources(se, entitytypeid):
    """
    Searches for resources of an entity type.
    """
    resource_query = Query(se, start=0, limit=10000)
    type_term = Terms(field='entitytypeid', terms=[entitytypeid])
    resource_query.add_filter(Bool(must=type_term))
    search_results = resource_query.search(index='entity', type='')
    resources = search_results['hits']['hits']
    return resources

def get_indexed_concepts(se, conceptid, concept_value):
    """
    Searches for a conceptid from the database and confirms that the database concept value matches the indexed value 
    """
    result = 'failed: cannot find' + conceptid
    query = Query(se, start=0, limit=100)
    phrase = Match(field='conceptid', query=conceptid, type='phrase_prefix')
    query.add_query(phrase)
    results = query.search(index='concept_labels')
    if len(results['hits']['hits']) > 0:
        source = results['hits']['hits'][0]['_source']
        if conceptid == source['conceptid'] or concept_value == source['value']:
            result = 'passed'
        else:
            result = 'failed: concept value does not match'
    return result