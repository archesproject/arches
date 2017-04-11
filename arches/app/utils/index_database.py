import os
import types
import sys
from django.conf import settings
from django.db import connection
from django.db.models import Q
from django.forms.models import model_to_dict
from arches.app.models import models
from arches.app.models.models import Concept
from arches.app.models.models import Value
from arches.app.models.concept import Concept, CORE_CONCEPTS
from arches.app.models.resource import Resource
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Terms
from arches.app.datatypes.datatypes import DataTypeFactory
from django.core.management.base import BaseCommand, CommandError
import collections
from .. import utils
from datetime import datetime


def index_db(flush_index=True):
    """
    Deletes any existing indicies from elasticsearch and then indexes all
    concepts and resources from the database

    """

    #index_concepts(flush_index=flush_index)
    index_resources(flush_index=flush_index)

def index_resources(flush_index=True):
    """
    Deletes any existing indicies from elasticsearch related to resources 
    and then indexes all resources from the database

    """

    se = SearchEngineFactory().create()
    result_summary = {}

    # # clear existing indexes
    # for index_type in ['resource_relations', 'entity', 'resource', 'maplayers']:
    #     se.delete_index(index=index_type)
    # se.delete(index='term', body='{"query":{"bool":{"must":[{"constant_score":{"filter":{"missing":{"field":"value.options.conceptid"}}}}],"must_not":[],"should":[]}}}')

    # Resource().prepare_term_index(create=True)

    # cursor = connection.cursor()
    # cursor.execute("""select entitytypeid from data.entity_types where isresource = TRUE""")
    q = Query(se=se)
    q.delete(index='strings', doc_type='term')

    resource_types = models.GraphModel.objects.filter(isresource=True).values_list('graphid', flat=True)
    # Resource().prepare_resource_relations_index(create=True)

    # for resource_type in resource_types:
    #     Resource().prepare_search_index(resource_type[0], create=True)
    
    index_resources_by_type(resource_types, result_summary)

    # se.es.indices.refresh(index='entity')
    for resource_type in resource_types:
        result_summary[str(resource_type)]['indexed'] = se.es.count(index="resource", doc_type=str(resource_type))['count']

    print '\nResource Index Results:'
    for k, v in result_summary.iteritems():
        status = 'Passed' if v['database'] == v['indexed'] else 'failed'
        print "Status: {0}, Resource Type: {1}, In Database: {2}, Indexed: {3}".format(status, k, v['database'], v['indexed'])

def index_resources_by_type(resource_types, result_summary):
    """
    Collects and indexes all resources

    """
    se = SearchEngineFactory().create()
    datatype_factory = DataTypeFactory()
    node_datatypes = {str(nodeid): datatype for nodeid, datatype in models.Node.objects.values_list('nodeid', 'datatype')}

    for resource_type in resource_types:
        resources = Resource.objects.filter(graph_id=str(resource_type))
        print "Indexing {0} {1} resources".format(len(resources), resource_type)
        result_summary[str(resource_type)] = {'database':len(resources), 'indexed':0}
    #     errors = []
    #     for resource in resources:
    #         try:
    #             resource = Resource().get(resource.entityid)
    #             resource.index()
    #         except Exception as e:
    #             if e not in errors:
    #                 errors.append(e)
    #     if len(errors) > 0:
    #         print errors[0], ':', len(errors)

    #     se = SearchEngineFactory().create()
    #     related_resource_records = archesmodels.RelatedResource.objects.all()
    #     for related_resource_record in related_resource_records:
    #         se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(related_resource_record), idfield='resourcexid')

        q = Query(se=se)
        q.delete(index='resource', doc_type=str(resource_type))
        
        documents = []
        term_list = []

        for resource in resources:
            document, terms = resource.get_documents_to_index(fetchTiles=True, datatype_factory=datatype_factory, node_datatypes=node_datatypes)
            documents.append(se.create_bulk_item(index='resource', doc_type=document['graph_id'], id=document['resourceinstanceid'], data=document))
            for term in terms:
                term_list.append(se.create_bulk_item(index='strings', doc_type='term', id=term['_id'], data=term['_source']))

        # bulk index the resources, tiles and terms
        se.bulk_index(documents)
        se.bulk_index(term_list)

    return result_summary

def index_concepts(flush_index=True):
    """
    Collects all concepts and indexes both concepts and concept_labels

    """

    se = SearchEngineFactory().create()
    if flush_index:
        q = Query(se=se)
        q.delete(index='strings', doc_type='concept')
        
    with se.BulkIndexer(batch_size=settings.BULK_IMPORT_BATCH_SIZE) as bi:
        # se.delete_index(index='concept_labels')
        # se.delete(index='term', body='{"query":{"bool":{"must_not":[{"constant_score":{"filter":{"missing":{"field":"value.options.conceptid"}}}}],"must":[],"should":[]}}}')

        # Resource().prepare_term_index(create=True)


        start = datetime.now()

        concept_strings = []
        for conceptValue in models.Value.objects.filter(Q(concept__nodetype='Collection') | Q(concept__nodetype='ConceptScheme'), valuetype__category ='label'):
            doc  = {
                'category': 'label',
                'conceptid': conceptValue.concept_id,
                'language': conceptValue.language_id,
                'value': conceptValue.value,
                'type': conceptValue.valuetype_id,
                'id': conceptValue.valueid,
                'top_concept': conceptValue.concept_id
            }
            #se.create_bulk_item(index='strings', doc_type='concept', id=doc['id'], data=doc)
            bi.add(index='strings', doc_type='concept', id=doc['id'], data=doc)

        valueTypes = []
        for valuetype in models.DValueType.objects.filter(category='label').values_list('valuetype', flat=True):
            valueTypes.append("'%s'" % valuetype)
        valueTypes = ",".join(valueTypes)

        for conceptValue in models.Relation.objects.filter(relationtype='hasTopConcept'):
            topConcept = conceptValue.conceptto_id
            sql = """
                WITH RECURSIVE children_inclusive AS (
                    SELECT d.conceptidfrom, d.conceptidto, c.*, 1 AS depth          ---|NonRecursive Part
                        FROM relations d
                        JOIN values c ON(c.conceptid = d.conceptidto)
                        JOIN values c2 ON(c2.conceptid = d.conceptidfrom)
                        WHERE d.conceptidto = '{0}'
                        and c2.valuetype = 'prefLabel'
                        and c.valuetype in ({1})
                        and (d.relationtype = 'narrower' or d.relationtype = 'hasTopConcept')
                        UNION
                    SELECT d.conceptidfrom, d.conceptidto, v.*, depth+1             ---|RecursivePart
                        FROM relations  d
                        JOIN children_inclusive b ON(b.conceptidto = d.conceptidfrom)
                        JOIN values v ON(v.conceptid = d.conceptidto)
                        JOIN values v2 ON(v2.conceptid = d.conceptidfrom)
                        WHERE  v2.valuetype = 'prefLabel'
                        and v.valuetype in ({1})
                        and (d.relationtype = 'narrower' or d.relationtype = 'hasTopConcept')
                ) SELECT valueid, value, conceptid, languageid, valuetype FROM children_inclusive ORDER BY depth;
            """.format(topConcept, valueTypes)

            #print sql
            #print 'indexing concepts'

            cursor = connection.cursor()
            cursor.execute(sql)
            for conceptValue in cursor.fetchall():
                doc  = {
                    'category': 'label',
                    'conceptid': conceptValue[2],
                    'language': conceptValue[3],
                    'value': conceptValue[1],
                    'type': conceptValue[4],
                    'id': conceptValue[0],
                    'top_concept': topConcept
                }
                #se.create_bulk_item(index='strings', doc_type='concept', id=doc['id'], data=doc)
                bi.add(index='strings', doc_type='concept', id=doc['id'], data=doc)


    #bi.close()

    #se.bulk_index(concept_strings)



    # resources.append(newresourceinstance)
    #     if len(resources) == settings.BULK_IMPORT_BATCH_SIZE:
    #         Resource.bulk_save(resources=resources)
    #         del resources[:]  #clear out the array






    # cursor = connection.cursor()
    # cursor.execute("""select conceptid from concepts.concepts""")
    # conceptids = cursor.fetchall()
    # for c in conceptids:
    #     if c[0] not in CORE_CONCEPTS:
    #         concept = Concept().get(id=c[0], include_subconcepts=True, include_parentconcepts=False, include=['label'])
    #         concept.index()

    end = datetime.now()
    duration = end - start
    print 'indexing concepts required', duration.seconds, 'seconds'

    # cursor = connection.cursor()
    # sql = """
    #     select conceptid, conceptlabel from concepts.vw_concepts where conceptid not in ('%s')
    # """ % ("','".join(CORE_CONCEPTS))
    # cursor.execute(sql)
    # concepts = cursor.fetchall()
    # concept_index_results = {'count':len(concepts), 'passed':0, 'failed':0}

    # for conceptid, conceptvalue in concepts:
    #     result = get_indexed_concepts(se, conceptid, conceptvalue)
    #     if result != 'passed':
    #         concept_index_results['failed'] += 1
    #     else:
    #         concept_index_results['passed'] += 1

    # status = 'Passed' if concept_index_results['failed'] == 0 else 'Failed'
    # print '\nConcept Index Results:'
    # print "Status: {0}, In Database: {1}, Indexed: {2}".format(status, concept_index_results['count'], concept_index_results['passed'])


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