import multiprocessing
import os
import math
import logging
import uuid
import pyprind
import sys

from datetime import datetime
from django.db import connection, connections
from django.db.models import prefetch_related_objects, Prefetch, Q, QuerySet
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.search.search_engine_factory import SearchEngineInstance as se
from arches.app.search.elasticsearch_dsl_builder import Query, Term
from arches.app.search.base_index import get_index
from arches.app.search.mappings import TERMS_INDEX, CONCEPTS_INDEX, RESOURCES_INDEX
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils import import_class_from_string
from typing import Iterable


logger = logging.getLogger(__name__)
serialized_graphs = {}


def get_serialized_graph(graph):
    """
    Returns the serialized version of the graph from the database

    """
    if not graph:
        return None

    if graph.graphid not in serialized_graphs:
        published_graph = graph.get_published_graph()
        serialized_graphs[graph.graphid] = published_graph.serialized_graph
    return serialized_graphs[graph.graphid]


def index_db(
    clear_index=True,
    batch_size=settings.BULK_IMPORT_BATCH_SIZE,
    quiet=False,
    use_multiprocessing=False,
    max_subprocesses=0,
    recalculate_descriptors=False,
):
    """
    Deletes any existing indicies from elasticsearch and then indexes all
    concepts and resources from the database

    Keyword Arguments:
    clear_index -- set to True to remove all the resources and concepts from the index before the reindexing operation
    batch_size -- the number of records to index as a group, the larger the number to more memory required
    quiet -- Silences the status bar output during certain operations, use in celery operations for example
    use_multiprocessing (default False) -- runs the reindexing in multiple subprocesses to take advantage of parallel indexing
    max_subprocesses - limits multiprocessing to a this number of processes. Default is half cpu count.
    recalculate_descriptors - forces the primary descriptors to be recalculated before (re)indexing
    """

    index_concepts(clear_index=clear_index, batch_size=batch_size)
    index_resources(
        clear_index=clear_index,
        batch_size=batch_size,
        quiet=quiet,
        use_multiprocessing=use_multiprocessing,
        max_subprocesses=max_subprocesses,
        recalculate_descriptors=recalculate_descriptors,
    )
    index_custom_indexes(clear_index=clear_index, batch_size=batch_size, quiet=quiet)


def index_resources(
    clear_index=True,
    batch_size=settings.BULK_IMPORT_BATCH_SIZE,
    quiet=False,
    use_multiprocessing=False,
    max_subprocesses=0,
    recalculate_descriptors=False,
):
    """
    Indexes all resources from the database

    Keyword Arguments:
    clear_index -- set to True to remove all the resources from the index before the reindexing operation
    batch_size -- the number of records to index as a group, the larger the number to more memory required
    quiet -- Silences the status bar output during certain operations, use in celery operations for example
    use_multiprocessing (default False) -- runs the reindexing in multiple subprocesses to take advantage of parallel indexing
    max_subprocesses -- explicitly sets the size of process pool. Auto limits to cpu count if more than this.
    recalculate_descriptors - forces the primary descriptors to be recalculated before (re)indexing

    """

    resource_types = (
        models.GraphModel.objects.filter(isresource=True)
        .exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        .exclude(publication=None)
        .values_list("graphid", flat=True)
    )
    index_resources_by_type(
        resource_types,
        clear_index=clear_index,
        batch_size=batch_size,
        quiet=quiet,
        use_multiprocessing=use_multiprocessing,
        max_subprocesses=max_subprocesses,
        recalculate_descriptors=recalculate_descriptors,
    )


def index_resources_using_multiprocessing(
    resourceids,
    batch_size=settings.BULK_IMPORT_BATCH_SIZE,
    quiet=False,
    max_subprocesses=0,
    callback=None,
    recalculate_descriptors=False,
):
    try:
        multiprocessing.set_start_method("spawn")
    except:
        pass

    logger.debug(f"... multiprocessing method: {multiprocessing.get_start_method()}")
    resource_batches = []
    resource_count = 0
    batch_number = 0
    resource_batches.append([])

    for resource in resourceids:
        resource_count += 1
        resource_batches[batch_number].append(resource)
        if resource_count == batch_size:
            resource_batches.append([])
            batch_number += 1
            resource_count = 0

    connections.close_all()

    if quiet is False:
        bar = (
            pyprind.ProgBar(len(resource_batches), bar_char="█", stream=sys.stdout)
            if len(resource_batches) > 1
            else None
        )

    def process_complete_callback(result):
        if quiet is False and bar is not None:
            bar.update(item_id=result)
        if callback is not None:
            callback()

    def process_error_callback(err):
        import traceback

        if quiet is False and bar is not None:
            bar.update()
        try:
            raise err
        except:
            tb = traceback.format_exc()
        finally:
            logger.error(
                f"Error indexing resource batch, type {type(err)}, message: {err}, \n>>>>>>>>>>>>>> TRACEBACK: {tb}"
            )

    default_process_count = math.ceil(multiprocessing.cpu_count() / 2)
    if max_subprocesses == 0:
        process_count = default_process_count
    elif max_subprocesses > multiprocessing.cpu_count():
        process_count = multiprocessing.cpu_count()
        logger.debug(
            f"... max_subprocess count exceeds CPU count. Limiting to {process_count}"
        )
    else:
        process_count = max_subprocesses

    logger.debug(f"... multiprocessing process count: {process_count}")
    logger.debug(
        f"... resource type batch count (batch size={batch_size}): {len(resource_batches)}"
    )
    with multiprocessing.Pool(processes=process_count) as pool:
        for resource_batch in resource_batches:
            pool.apply_async(
                _index_resource_batch,
                args=(resource_batch, recalculate_descriptors, quiet),
                callback=process_complete_callback,
                error_callback=process_error_callback,
            )
        pool.close()
        pool.join()


def optimize_resource_iteration(resources: Iterable[Resource], chunk_size: int):
    """
    - select related graphs
    - prefetch tiles (onto .prefetched_tiles)
    - prefetch primary descriptors (onto graph.descriptor_function)
    - apply chunk_size to reduce memory footprint and spread the work
      of prefetching tiles across multiple queries

    The caller is responsible for moving the descriptor function
    prefetch from the graph to the resource instance--a symptom of
    this being more of a graph property--and for moving the prefetched
    tiles to .tiles (because the Resource proxy model initializes
    .tiles to an empty array and Django thinks that represents the
    state in the db.)
    """
    tiles_prefetch = Prefetch("tilemodel_set", to_attr="prefetched_tiles")
    # Same queryset as Resource.save_descriptors()
    descriptor_query = models.FunctionXGraph.objects.filter(
        function__functiontype="primarydescriptors",
    ).select_related("function")
    descriptor_prefetch = Prefetch(
        "graph__functionxgraph_set",
        queryset=descriptor_query,
        to_attr="descriptor_function",
    )

    if isinstance(resources, QuerySet):
        return (
            resources.select_related("graph")
            .prefetch_related(tiles_prefetch, descriptor_prefetch)
            .iterator(chunk_size=chunk_size)
        )
    else:  # public API that arches itself does not currently use
        for r in resources:
            r.clean_fields()  # ensure strings become UUIDs

        prefetch_related_objects(resources, tiles_prefetch, descriptor_prefetch)
        return resources


def index_resources_using_singleprocessing(
    resources: Iterable[Resource],
    batch_size=settings.BULK_IMPORT_BATCH_SIZE,
    quiet=False,
    title=None,
    recalculate_descriptors=False,
):
    datatype_factory = DataTypeFactory()
    node_datatypes = {
        str(nodeid): datatype
        for nodeid, datatype in models.Node.objects.values_list("nodeid", "datatype")
    }
    with se.BulkIndexer(batch_size=batch_size, refresh=True) as doc_indexer:
        with se.BulkIndexer(batch_size=batch_size, refresh=True) as term_indexer:
            if quiet is False:
                if isinstance(resources, QuerySet):
                    resource_count = resources.count()
                else:
                    resource_count = len(resources)
                if resource_count > 1:
                    bar = pyprind.ProgBar(resource_count, bar_char="█", title=title)
                else:
                    bar = None
            chunk_size = max(batch_size // 8, 8)
            for resource in optimize_resource_iteration(
                resources, chunk_size=chunk_size
            ):
                resource.tiles = resource.prefetched_tiles
                resource.descriptor_function = resource.graph.descriptor_function
                resource.set_node_datatypes(node_datatypes)
                resource.set_serialized_graph(get_serialized_graph(resource.graph))
                if recalculate_descriptors:
                    resource.save_descriptors()
                if quiet is False and bar is not None:
                    bar.update(item_id=resource)
                document, terms = resource.get_documents_to_index(
                    fetchTiles=False,
                    datatype_factory=datatype_factory,
                    node_datatypes=node_datatypes,
                )
                doc_indexer.add(
                    index=RESOURCES_INDEX,
                    id=document["resourceinstanceid"],
                    data=document,
                )
                for term in terms:
                    term_indexer.add(
                        index=TERMS_INDEX, id=term["_id"], data=term["_source"]
                    )

    return os.getpid()


def index_resources_by_type(
    resource_types,
    clear_index=True,
    batch_size=settings.BULK_IMPORT_BATCH_SIZE,
    quiet=False,
    use_multiprocessing=False,
    max_subprocesses=0,
    recalculate_descriptors=False,
):
    """
    Indexes all resources of a given type(s)

    Arguments:
    resource_types -- array of graph ids that represent resource types

    Keyword Arguments:
    clear_index -- set to True to remove all the resources of the types passed in from the index before the reindexing operation
    batch_size -- the number of records to index as a group, the larger the number to more memory required
    quiet -- Silences the status bar output during certain operations, use in celery operations for example
    use_multiprocessing (default False) -- runs the reindexing in multiple subprocesses to take advantage of parallel indexing
    max_subprocesses (default 0) -- explicitly set the number of processes to use.
    recalculate_descriptors - forces the primary descriptors to be recalculated before (re)indexing

    """

    status = ""

    if isinstance(resource_types, str):
        try:
            resource_types = resource_types.split(",")
        except:
            pass

    for resource_type in resource_types:
        start = datetime.now()

        graph_name = models.GraphModel.objects.get(graphid=resource_type).name
        logger.info("Indexing resource type '{0}'".format(graph_name))

        if clear_index:
            tq = Query(se=se)
            cards = models.CardModel.objects.filter(graph_id=resource_type).only(
                "nodegroup_id"
            )
            for card in cards:
                term = Term(field="nodegroupid", term=str(card.nodegroup_id))
                tq.add_query(term)
            tq.delete(index=TERMS_INDEX, refresh=True)

            rq = Query(se=se)
            term = Term(field="graph_id", term=str(resource_type))
            rq.add_query(term)
            rq.delete(index=RESOURCES_INDEX, refresh=True)

        if use_multiprocessing:
            resource_ids = models.ResourceInstance.objects.filter(
                graph_id=resource_type
            ).values_list("resourceinstanceid", flat=True)
            index_resources_using_multiprocessing(
                resourceids=resource_ids,
                batch_size=batch_size,
                quiet=quiet,
                max_subprocesses=max_subprocesses,
                recalculate_descriptors=recalculate_descriptors,
            )

        else:
            from arches.app.search.search_engine_factory import (
                SearchEngineInstance as _se,
            )

            resources = Resource.objects.filter(graph_id=resource_type)
            index_resources_using_singleprocessing(
                resources=resources,
                batch_size=batch_size,
                quiet=quiet,
                title=graph_name,
                recalculate_descriptors=recalculate_descriptors,
            )

        q = Query(se=se)
        term = Term(field="graph_id", term=str(resource_type))
        q.add_query(term)
        result_summary = {
            "database": len(resources),
            "indexed": se.count(index=RESOURCES_INDEX, **q.dsl),
        }
        status = (
            "Passed"
            if result_summary["database"] == result_summary["indexed"]
            else "Failed"
        )
        logger.info(
            "Status: {0}, Resource Type: {1}, In Database: {2}, Indexed: {3}, Took: {4} seconds".format(
                status,
                graph_name,
                result_summary["database"],
                result_summary["indexed"],
                (datetime.now() - start).seconds,
            )
        )
    return status


def _index_resource_batch(resourceids, recalculate_descriptors, quiet=False):

    resources = Resource.objects.filter(resourceinstanceid__in=resourceids)
    batch_size = max(len(resourceids) // 2, 1)
    return index_resources_using_singleprocessing(
        resources=resources,
        batch_size=batch_size,
        quiet=quiet,
        title="Indexing Resource Batch",
        recalculate_descriptors=recalculate_descriptors,
    )


def index_custom_indexes(
    index_name=None,
    clear_index=True,
    batch_size=settings.BULK_IMPORT_BATCH_SIZE,
    quiet=False,
):
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
            es_index.reindex(
                clear_index=clear_index, batch_size=batch_size, quiet=quiet
            )
    else:
        es_index = get_index(index_name)
        es_index.reindex(clear_index=clear_index, batch_size=batch_size, quiet=quiet)


def index_concepts(clear_index=True, batch_size=settings.BULK_IMPORT_BATCH_SIZE):
    """
    Indxes all concepts from the database

    Keyword Arguments:
    clear_index -- set to True to remove all the concepts from the index before the reindexing operation
    batch_size -- the number of records to index as a group, the larger the number to more memory required

    """

    start = datetime.now()
    logger.info("Indexing concepts")
    cursor = connection.cursor()
    if clear_index:
        q = Query(se=se)
        q.delete(index=CONCEPTS_INDEX)

    with se.BulkIndexer(batch_size=batch_size, refresh=True) as concept_indexer:
        indexed_values = []
        for conceptValue in models.Value.objects.filter(
            Q(concept__nodetype="Collection") | Q(concept__nodetype="ConceptScheme"),
            valuetype__category="label",
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
        for valuetype in models.DValueType.objects.filter(category="label").values_list(
            "valuetype", flat=True
        ):
            valueTypes.append("'%s'" % valuetype)
        valueTypes = ",".join(valueTypes)

        for conceptValue in models.Relation.objects.filter(
            relationtype="hasTopConcept"
        ):
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
        for conceptValue in models.Value.objects.filter(
            valuetype__category="label"
        ).exclude(valueid__in=indexed_values):
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

    cursor.execute(
        "SELECT count(*) from values WHERE valuetype in ({0})".format(valueTypes)
    )
    concept_count_in_db = cursor.fetchone()[0]
    index_count = se.count(index=CONCEPTS_INDEX)

    logger.info(
        "Status: {0}, In Database: {1}, Indexed: {2}, Took: {3} seconds".format(
            "Passed" if concept_count_in_db == index_count else "Failed",
            concept_count_in_db,
            index_count,
            (datetime.now() - start).seconds,
        )
    )


def index_resources_by_transaction(
    transaction_id,
    batch_size=settings.BULK_IMPORT_BATCH_SIZE,
    quiet=False,
    use_multiprocessing=False,
    max_subprocesses=0,
    recalculate_descriptors=False,
):
    """
    Indexes all the resources with a transaction id

    Keyword Arguments:
    quiet -- Silences the status bar output during certain operations, use in celery operations for example
    recalculate_descriptors - forces the primary descriptors to be recalculated before (re)indexing

    """
    start = datetime.now()

    try:
        uuid.UUID(transaction_id)
    except ValueError:
        logger.error("A transaction id must be a valid uuid")
        return

    logger.info("Indexing transaction '{0}'".format(transaction_id))

    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT DISTINCT resourceinstanceid FROM edit_log WHERE transactionid = %s;""",
            [transaction_id],
        )
        rows = cursor.fetchall()
    resourceids = [id for (id,) in rows]

    if use_multiprocessing:
        index_resources_using_multiprocessing(
            resourceids=resourceids,
            batch_size=batch_size,
            quiet=quiet,
            max_subprocesses=max_subprocesses,
            recalculate_descriptors=recalculate_descriptors,
        )
    else:
        index_resources_using_singleprocessing(
            resources=Resource.objects.filter(pk__in=resourceids),
            batch_size=batch_size,
            quiet=quiet,
            title="transaction {}".format(transaction_id),
            recalculate_descriptors=recalculate_descriptors,
        )

    logger.info(
        "Transaction: {0}, In Database: {1}, Took: {2} seconds".format(
            transaction_id, len(resourceids), (datetime.now() - start).seconds
        )
    )
