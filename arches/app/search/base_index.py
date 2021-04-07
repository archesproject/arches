import pyprind
from datetime import datetime
from django.utils.translation import ugettext as _
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.utils import import_class_from_string
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Term, Ids


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

    def index_resources(self, resources=None, batch_size=settings.BULK_IMPORT_BATCH_SIZE, quiet=False):
        """
        Indexes a list of resources in bulk to Elastic Search

        Keyword Arguments:
        resources -- the list of resource instances to index
        batch_size -- the number of records to index as a group, the larger the number to more memory required
        quiet -- Silences the status bar output during certain operations, use in celery operations for example

        Return: None
        """

        start = datetime.now()
        q = Query(se=self.se)
        self.se.refresh(index=self.index_name)
        count_before = self.se.count(index=self.index_name, body=q.dsl)
        result_summary = {"database": len(resources), "indexed": 0}
        if quiet is False:
            bar = pyprind.ProgBar(len(resources), bar_char="█") if len(resources) > 1 else None
        with self.se.BulkIndexer(batch_size=batch_size, refresh=True) as indexer:
            for resource in resources:
                if quiet is False and bar is not None:
                    bar.update(item_id=resource)
                tiles = list(models.TileModel.objects.filter(resourceinstance=resource))
                document, doc_id = self.get_documents_to_index(resource, tiles)
                if document is not None and id is not None:
                    indexer.add(index=self.index_name, id=doc_id, data=document)

        self.se.refresh(index=self.index_name)
        result_summary["indexed"] = self.se.count(index=self.index_name, body=q.dsl) - count_before
        status = "Passed" if result_summary["database"] == result_summary["indexed"] else "Failed"
        print(f"Custom Index - {settings.ELASTICSEARCH_PREFIX}_{self.index_name}")
        print(
            f"    Status: {status}, In Database: {result_summary['database']}, Indexed: {result_summary['indexed']}, Took: {(datetime.now() - start).seconds} seconds"
        )

    def delete_resources(self, resources=None):
        """
        Deletes documents from an indexed based on the passed in list of resources
        Delete by query, so this is a single operation

        Keyword Arguments:
        resources -- a single resource instance or a list of resource instances
        """

        q = Query(se=self.se)
        if not isinstance(resources, list):
            resourcelist = [resources]
        else:
            resourcelist = resources
        list_of_ids_to_delete = []
        for resource in resourcelist:
            list_of_ids_to_delete.append(resource.pk)
        ids_query = Ids(ids=list_of_ids_to_delete)
        q.add_query(ids_query)
        q.delete(index=self.index_name)

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

    def reindex(self, graphids=None, clear_index=True, batch_size=settings.BULK_IMPORT_BATCH_SIZE, quiet=False):
        """
        Reindexes the index.  By default this does nothing, it needs to be implemented in a subclass.
        By default you can pass in a list of graph ids to trigger the reindex.  This will loop through all resource instances of each graph type.

            Example subclass command:
            def reindex(self, clear_index=True):
                PARCEL_GRAPHID = "e3c35dca-5e72-11ea-a2d3-dca90488358a"
                super(CustomIndexName, self).reindex(graphids=[PARCEL_GRAPHID], clear_index=clear_index)

        Keyword Arguments:
        graphids -- list of graphs ids to trigger the reindex on, will get all resource instances of each graph id supplied
        clear_index -- True(default) to clear all documents out of the index before reindexing begins
        batch_size -- the number of records to index as a group, the larger the number to more memory required

        Return: None
        """

        if graphids is not None:
            if clear_index:
                self.delete_index()
                self.prepare_index()

            for graphid in graphids:
                resources = Resource.objects.filter(graph_id=graphid)
                self.index_resources(resources=resources, batch_size=batch_size, quiet=quiet)
        else:
            raise NotImplementedError

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
