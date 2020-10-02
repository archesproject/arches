from datetime import datetime
from django.utils.translation import ugettext as _
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils import import_class_from_string
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Term


class BaseIndex(object):
    def __init__(self, index_name=None):
        if index_name is None or index_name == "":
            raise SearchIndexError("Index name is not defined")

        self.se = SearchEngineFactory().create()
        self.index_metadata = None
        self.index_name = index_name

    def prepare_index(self):
        """
        Defines the Elastic Search mapping and settings for an index

        Arguments:
        None

        Keyword Arguments:
        None

        Return: None
        """

        if self.index_metadata is not None:
            self.se.create_index(index=self.index_name, body=self.index_metadata)
        else:
            raise SearchIndexError("No index metadata defined.")

    def get_documents_to_index(self, resourceinstance, tiles):
        """
        Gets a document to index into Elastic Search

        Arguments:
        resourceinstance -- resource instance object
        tiles -- list of tiles that make up the resource instance

        Keyword Arguments:
        None

        Return: tuple of (document, document id)
        """

        raise NotImplementedError

    def index_document(self, document=None, id=None):
        """
        Indexes a document into Elastic Search

        Arguments:
        None

        Keyword Arguments:
        document -- the document to index
        id -- the id of the document

        Return: None
        """

        if document is not None and id is not None:
            self.se.index_data(index=self.index_name, body=document, id=id)

    def bulk_index(self, resources=None, resource_type=None, graph_name=None, clear_index=True):
        """
        Indexes a list of documents in bulk to Elastic Search

        Arguments:
        None

        Keyword Arguments:
        resources -- the list of resource instances to index
        resource_type -- the type of resources being indexed
        graph_name -- the name of the graph model that represents the resources being indexed
        clear_index -- True(default) to remove all index records of type "resource_type" before indexing, 
            assumes that a field called "graph_id" exists on the indexed documents

        Return: None
        """

        start = datetime.now()
        q = Query(se=self.se)
        if clear_index:
            term = Term(field="graph_id", term=str(resource_type))
            q.add_query(term)
            q.delete(index=self.index_name, refresh=True)

        q = Query(se=self.se)
        count_before = self.se.count(index=self.index_name, body=q.dsl)

        result_summary = {"database": len(resources), "indexed": 0}
        with self.se.BulkIndexer(batch_size=settings.BULK_IMPORT_BATCH_SIZE, refresh=True) as indexer:
            for resource in resources:
                tiles = list(models.TileModel.objects.filter(resourceinstance=resource))
                document, doc_id = self.get_documents_to_index(resource, tiles)
                if document is not None and id is not None:
                    indexer.add(index=self.index_name, id=doc_id, data=document)

        result_summary["indexed"] = self.se.count(index=self.index_name, body=q.dsl) - count_before
        status = "Passed" if result_summary["database"] == result_summary["indexed"] else "Failed"
        print("Custom Index - %s:" % self.index_name)
        print(
            "    Status: {0}, Resource Type: {1}, In Database: {2}, Indexed: {3}, Took: {4} seconds".format(
                status, graph_name, result_summary["database"], result_summary["indexed"], (datetime.now() - start).seconds
            )
        )

    def delete_index(self):
        """
        Deletes this index from Elastic Search

        Arguments:
        None

        Keyword Arguments:
        None

        Return: None
        """

        self.se.delete_index(index=self.index_name)


def get_index(name):
    for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
        if index["name"] == name:
            return import_class_from_string(index["module"])(name)
    raise SearchIndexNotDefinedError(name=name)


class SearchIndexError(Exception):
    def __init__(self, message, code=None):
        self.title = _("Search Index Error:")
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)


class SearchIndexNotDefinedError(Exception):
    def __init__(self, name=None):
        self.title = _("Search Index Not Defined Error:")
        self.message = _('The index "%s" is not defined in settings.ELASTICSEARCH_CUSTOM_INDEXES' % name)

    def __str__(self):
        return repr(self.message)
