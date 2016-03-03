import os
import types
import sys
from django.conf import settings
from django.db import connection
from django.forms.models import model_to_dict
from arches.app.models.models import Concept
from arches.app.models.models import Value
from arches.app.models.concept import Concept, CORE_CONCEPTS
from arches.app.models.resource import Resource
import arches.app.models.models as archesmodels
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Terms
from django.core.management.base import BaseCommand, CommandError
import collections
from .. import utils
from datetime import datetime


def index_db():
    """
    Deletes any existing indicies from elasticsearch and then indexes all
    concepts and resources from the database

    """

    index_concepts()
    index_resources()

def index_resources():
    """
    Deletes any existing indicies from elasticsearch related to resources 
    and then indexes all resources from the database

    """

    result_summary = {}
    se = SearchEngineFactory().create()

    # clear existing indexes
    for index_type in ['resource_relations', 'entity', 'resource', 'maplayers']:
        se.delete_index(index=index_type)
    se.delete(index='term', body='{"query":{"bool":{"must":[{"constant_score":{"filter":{"missing":{"field":"value.options.conceptid"}}}}],"must_not":[],"should":[]}}}')

    Resource().prepare_term_index(create=True)

    cursor = connection.cursor()
    cursor.execute("""select entitytypeid from data.entity_types where isresource = TRUE""")
    resource_types = cursor.fetchall()
    Resource().prepare_resource_relations_index(create=True)

    for resource_type in resource_types:
        Resource().prepare_search_index(resource_type[0], create=True)
    
    index_resources_by_type(resource_types, result_summary)

    se.es.indices.refresh(index='entity')
    for resource_type in resource_types:
        result_summary[resource_type[0]]['indexed'] = se.es.count(index="entity", doc_type=resource_type[0])['count']

    print '\nResource Index Results:'
    for k, v in result_summary.iteritems():
        status = 'Passed' if v['database'] == v['indexed'] else 'failed'
        print "Status: {0}, Resource Type: {1}, In Database: {2}, Indexed: {3}".format(status, k, v['database'], v['indexed'])

def index_resources_by_type(resource_types, result_summary):
    """
    Collects and indexes all resources

    """

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

        se = SearchEngineFactory().create()
        related_resource_records = archesmodels.RelatedResource.objects.all()
        for related_resource_record in related_resource_records:
            se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(related_resource_record), idfield='resourcexid')

    return result_summary

def index_concepts():
    """
    Collects all concepts and indexes both concepts and concept_labels

    """

    se = SearchEngineFactory().create()
    se.delete_index(index='concept_labels')
    se.delete(index='term', body='{"query":{"bool":{"must_not":[{"constant_score":{"filter":{"missing":{"field":"value.options.conceptid"}}}}],"must":[],"should":[]}}}')

    Resource().prepare_term_index(create=True)

    print 'indexing concepts'
    start = datetime.now()

    cursor = connection.cursor()
    cursor.execute("""select conceptid from concepts.concepts""")
    conceptids = cursor.fetchall()
    for c in conceptids:
        if c[0] not in CORE_CONCEPTS:
            concept = Concept().get(id=c[0], include_subconcepts=True, include_parentconcepts=False, include=['label'])
            concept.index()

    end = datetime.now()
    duration = end - start
    print 'indexing concepts required', duration.seconds, 'seconds'

    cursor = connection.cursor()
    sql = """
        select conceptid, conceptlabel from concepts.vw_concepts where conceptid not in ('%s')
    """ % ("','".join(CORE_CONCEPTS))
    cursor.execute(sql)
    concepts = cursor.fetchall()
    concept_index_results = {'count':len(concepts), 'passed':0, 'failed':0}

    for conceptid, conceptvalue in concepts:
        result = get_indexed_concepts(se, conceptid, conceptvalue)
        if result != 'passed':
            concept_index_results['failed'] += 1
        else:
            concept_index_results['passed'] += 1

    status = 'Passed' if concept_index_results['failed'] == 0 else 'Failed'
    print '\nConcept Index Results:'
    print "Status: {0}, In Database: {1}, Indexed: {2}".format(status, concept_index_results['count'], concept_index_results['passed'])


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