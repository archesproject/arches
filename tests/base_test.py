'''
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import os
from django.test import TestCase
from arches.app.models.graph import Graph
from arches.app.search.search import SearchEngine
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from django.core import management

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"

def setUpModule():
    pass

def tearDownModule():
    se = SearchEngineFactory().create()
    se.delete_index(index='strings')
    se.delete_index(index='resource')


class ArchesTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(ArchesTestCase, self).__init__(*args, **kwargs)
        if settings.DEFAULT_BOUNDS == None:
            management.call_command('migrate')
            with open(os.path.join('tests/fixtures/system_settings/Arches_System_Settings_Model.json'), 'rU') as f:
                archesfile = JSONDeserializer().deserialize(f)
            ResourceGraphImporter(archesfile['graph'], True)
            BusinessDataImporter('tests/fixtures/system_settings/Arches_System_Settings_Local.json').import_business_data()
            settings.update_from_db()

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def deleteGraph(cls, root):
        graph = Graph.objects.get(graphid=str(root))
        graph.delete()

    def setUp(self):
        pass

    def tearDown(self):
        pass


class TestSearchEngine(SearchEngine):

    def __init__(self):
        super(TestSearchEngine, self).__init__()
        self.index_prefix = 'test_'

    def reset_index(self, **kwargs):
        index = kwargs.get('index', None)
        if index:
            kwargs['index'] ='%s%s' % (self.index_prefix, index)
        return kwargs

    def delete(self, **kwargs):
        """
        Deletes a document from the index
        Pass an index, doc_type, and id to delete a specific document
        Pass a body with a query dsl to delete by query

        """

        kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).delete(**kwargs)

    def delete_index(self, **kwargs):
        """
        Deletes an entire index

        """

        kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).delete_index(**kwargs)

    def search(self, **kwargs):
        """
        Search for an item in the index.
        Pass an index, doc_type, and id to get a specific document
        Pass a body with a query dsl to perform a search

        """

        kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).search(**kwargs)

    def create_mapping(self, index, doc_type, fieldname='', fieldtype='string', fieldindex=None, body=None):
        """
        Creates an Elasticsearch body for a single field given an index name and type name

        """

        index = '%s%s' % (self.index_prefix, index)
        return super(TestSearchEngine, self).create_mapping(index, doc_type, fieldname=fieldname, fieldtype=fieldtype, fieldindex=fieldindex, body=body)

    def create_index(self, **kwargs):
        kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).create_index(**kwargs)

    def index_data(self, index=None, doc_type=None, body=None, idfield=None, id=None, **kwargs):
        """
        Indexes a document or list of documents into Elasticsearch

        If "id" is supplied then will use that as the id of the document

        If "idfield" is supplied then will try to find that property in the
            document itself and use the value found for the id of the document

        """

        kwargs['index'] = index
        kwargs['doc_type'] = doc_type
        kwargs['body'] = body
        kwargs['idfield'] = idfield
        kwargs['id'] = id
        kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).index_data(**kwargs)

    def bulk_index(self, data, **kwargs):
        kwargs['data'] = data
        kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).bulk_index(**kwargs)

    def create_bulk_item(self, **kwargs):
        kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).create_bulk_item(**kwargs)

    def count(self, **kwargs):
        kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).count(**kwargs)
