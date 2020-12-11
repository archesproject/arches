import pyprind
from django.db import connection
from django.db.models import Q
from arches.app.models import models
from arches.app.models.models import Value
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.search.search_engine_factory import SearchEngineInstance as se
from arches.app.search.elasticsearch_dsl_builder import Query, Term
from arches.app.search.base_index import get_index
from arches.app.search.mappings import TERMS_INDEX, CONCEPTS_INDEX, RESOURCE_RELATIONS_INDEX, RESOURCES_INDEX
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils import import_class_from_string
from datetime import datetime


def index_db(clear_index=True, batch_size=settings.BULK_IMPORT_BATCH_SIZE, quiet=False):
    """
    Deletes any existing indicies from elasticsearch and then indexes all
    concepts and resources from the database

    Keyword Arguments:
    clear_index -- set to True to remove all the resources and concepts from the index before the reindexing operation
    batch_size -- the number of records to index as a group, the larger the number to more memory required
    quiet -- Silences the status bar output during certain operations, use in celery operations for example

    """

    index_concepts(clear_index=clear_index, batch_size=batch_size)
    index_resources(clear_index=clear_index, batch_size=batch_size, quiet=quiet)
    index_custom_indexes(clear_index=clear_index, batch_size=batch_size, quiet=quiet)
    index_resource_relations(clear_index=clear_index, batch_size=batch_size)


def index_resources(clear_index=True, batch_size=settings.BULK_IMPORT_BATCH_SIZE, quiet=False):
    """
    Indexes all resources from the database

    Keyword Arguments:
    clear_index -- set to True to remove all the resources from the index before the reindexing operation
    batch_size -- the number of records to index as a group, the larger the number to more memory required
    quiet -- Silences the status bar output during certain operations, use in celery operations for example

    """

    if clear_index:
        q = Query(se=se)
        q.delete(index=TERMS_INDEX)

    resource_types = (
        models.GraphModel.objects.filter(isresource=True)
        .exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        .values_list("graphid", flat=True)
    )
    index_resources_by_type(resource_types, clear_index=clear_index, batch_size=batch_size, quiet=quiet)


def index_resources_by_type(resource_types, clear_index=True, batch_size=settings.BULK_IMPORT_BATCH_SIZE, quiet=False):
    """
    Indexes all resources of a given type(s)

    Arguments:
    resource_types -- array of graph ids that represent resource types

    Keyword Arguments:
    clear_index -- set to True to remove all the resources of the types passed in from the index before the reindexing operation
    batch_size -- the number of records to index as a group, the larger the number to more memory required
    quiet -- Silences the status bar output during certain operations, use in celery operations for example

    """

    status = ""
    datatype_factory = DataTypeFactory()
    node_datatypes = {str(nodeid): datatype for nodeid, datatype in models.Node.objects.values_list("nodeid", "datatype")}

    for resource_type in resource_types:
        start = datetime.now()
        resources = Resource.objects.filter(graph_id=str(resource_type))
        graph_name = models.GraphModel.objects.get(graphid=str(resource_type)).name
        print("Indexing resource type '{0}'".format(graph_name))

        q = Query(se=se)
        term = Term(field="graph_id", term=str(resource_type))
        q.add_query(term)
        if clear_index:
            q.delete(index=RESOURCES_INDEX, refresh=True)

        with se.BulkIndexer(batch_size=batch_size, refresh=True) as doc_indexer:
            with se.BulkIndexer(batch_size=batch_size, refresh=True) as term_indexer:
                if quiet is False:
                    bar = pyprind.ProgBar(len(resources), bar_char="█") if len(resources) > 1 else None
                for resource in resources:
                    if quiet is False and bar is not None:
                        bar.update(item_id=resource)
                    document, terms = resource.get_documents_to_index(
                        fetchTiles=True, datatype_factory=datatype_factory, node_datatypes=node_datatypes
                    )
                    doc_indexer.add(index=RESOURCES_INDEX, id=document["resourceinstanceid"], data=document)
                    for term in terms:
                        term_indexer.add(index=TERMS_INDEX, id=term["_id"], data=term["_source"])

        result_summary = {"database": len(resources), "indexed": se.count(index=RESOURCES_INDEX, body=q.dsl)}
        status = "Passed" if result_summary["database"] == result_summary["indexed"] else "Failed"
        print(
            "Status: {0}, Resource Type: {1}, In Database: {2}, Indexed: {3}, Took: {4} seconds".format(
                status, graph_name, result_summary["database"], result_summary["indexed"], (datetime.now() - start).seconds
            )
        )
    return status


def index_custom_indexes(index_name=None, clear_index=True, batch_size=settings.BULK_IMPORT_BATCH_SIZE, quiet=False):
    """
    Indexes any custom indexes, optionally by name

    Keyword Arguments:
    index_name -- if supplied will only reindex the custom index with the given name
    clear_index -- set to True to remove all the resources of the types passed in from the index before the reindexing operation
    batch_size -- the number of records to index as a group, the larger the number to more memory required
    quiet -- Silences the status bar output during certain operations, use in celery operations for example

    """

    if index_name is None:
        for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
            es_index = import_class_from_string(index["module"])(index["name"])
            es_index.reindex(clear_index=clear_index, batch_size=batch_size, quiet=quiet)
    else:
        es_index = get_index(index_name)
        es_index.reindex(clear_index=clear_index, batch_size=batch_size, quiet=quiet)


def index_resource_relations(clear_index=True, batch_size=settings.BULK_IMPORT_BATCH_SIZE):
    """
    Indexes all resource to resource relation records

    Keyword Arguments:
    clear_index -- set to True to remove all the resources from the index before the reindexing operation
    batch_size -- the number of records to index as a group, the larger the number to more memory required

    """

    start = datetime.now()
    print("Indexing resource to resource relations")

    cursor = connection.cursor()
    if clear_index:
        q = Query(se=se)
        q.delete(index=RESOURCE_RELATIONS_INDEX)

    with se.BulkIndexer(batch_size=batch_size, refresh=True) as resource_relations_indexer:
        sql = """
            SELECT resourcexid, notes, datestarted, dateended, relationshiptype, resourceinstanceidfrom, resourceinstancefrom_graphid,
            resourceinstanceidto, resourceinstanceto_graphid, modified, created, inverserelationshiptype, tileid, nodeid
            FROM public.resource_x_resource
        """

        cursor.execute(sql)
        for resource_relation in cursor.fetchall():
            doc = {
                "resourcexid": resource_relation[0],
                "notes": resource_relation[1],
                "datestarted": resource_relation[2],
                "dateended": resource_relation[3],
                "relationshiptype": resource_relation[4],
                "resourceinstanceidfrom": resource_relation[5],
                "resourceinstancefrom_graphid": resource_relation[6],
                "resourceinstanceidto": resource_relation[7],
                "resourceinstanceto_graphid": resource_relation[8],
                "modified": resource_relation[9],
                "created": resource_relation[10],
                "inverserelationshiptype": resource_relation[11],
                "tileid": resource_relation[12],
                "nodeid": resource_relation[13],
            }
            resource_relations_indexer.add(index=RESOURCE_RELATIONS_INDEX, id=doc["resourcexid"], data=doc)

    index_count = se.count(index=RESOURCE_RELATIONS_INDEX)
    print(
        "Status: {0}, In Database: {1}, Indexed: {2}, Took: {3} seconds".format(
            "Passed" if cursor.rowcount == index_count else "Failed", cursor.rowcount, index_count, (datetime.now() - start).seconds
        )
    )


def index_concepts(clear_index=True, batch_size=settings.BULK_IMPORT_BATCH_SIZE):
    """
    Indxes all concepts from the database

    Keyword Arguments:
    clear_index -- set to True to remove all the concepts from the index before the reindexing operation
    batch_size -- the number of records to index as a group, the larger the number to more memory required

    """

    start = datetime.now()
    print("Indexing concepts")
    cursor = connection.cursor()
    if clear_index:
        q = Query(se=se)
        q.delete(index=CONCEPTS_INDEX)

    with se.BulkIndexer(batch_size=batch_size, refresh=True) as concept_indexer:
        indexed_values = []
        for conceptValue in models.Value.objects.filter(
            Q(concept__nodetype="Collection") | Q(concept__nodetype="ConceptScheme"), valuetype__category="label"
        ):
            doc = {
                "category": "label",
                "conceptid": conceptValue.concept_id,
                "language": conceptValue.language_id,
                "value": conceptValue.value,
                "type": conceptValue.valuetype_id,
                "id": conceptValue.valueid,
                "top_concept": conceptValue.concept_id,
            }
            concept_indexer.add(index=CONCEPTS_INDEX, id=doc["id"], data=doc)
            indexed_values.append(doc["id"])


        valueTypes = []
        for valuetype in models.DValueType.objects.filter(category="label").values_list("valuetype", flat=True):
            valueTypes.append("'%s'" % valuetype)
        valueTypes = ",".join(valueTypes)

        for conceptValue in models.Relation.objects.filter(relationtype="hasTopConcept"):
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
            """.format(
                topConcept, valueTypes
            )

            cursor.execute(sql)
            for conceptValue in cursor.fetchall():
                doc = {
                    "category": "label",
                    "conceptid": conceptValue[2],
                    "language": conceptValue[3],
                    "value": conceptValue[1],
                    "type": conceptValue[4],
                    "id": conceptValue[0],
                    "top_concept": topConcept,
                }
                concept_indexer.add(index=CONCEPTS_INDEX, id=doc["id"], data=doc)
                indexed_values.append(doc["id"])

        # we add this step to catch any concepts/values that are orphaned (have no parent concept)
        for conceptValue in models.Value.objects.filter(valuetype__category="label").exclude(valueid__in=indexed_values):
            doc = {
                "category": "label",
                "conceptid": conceptValue.concept_id,
                "language": conceptValue.language_id,
                "value": conceptValue.value,
                "type": conceptValue.valuetype_id,
                "id": conceptValue.valueid,
                "top_concept": conceptValue.concept_id,
            }
            concept_indexer.add(index=CONCEPTS_INDEX, id=doc["id"], data=doc)

    cursor.execute("SELECT count(*) from values WHERE valuetype in ({0})".format(valueTypes))
    concept_count_in_db = cursor.fetchone()[0]
    index_count = se.count(index=CONCEPTS_INDEX)

    print(
        "Status: {0}, In Database: {1}, Indexed: {2}, Took: {3} seconds".format(
            "Passed" if concept_count_in_db == index_count else "Failed", concept_count_in_db, index_count, (datetime.now() - start).seconds
        )
    )
