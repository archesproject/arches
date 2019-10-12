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
from arches.app.models.models import Ontology
from arches.app.search.search import SearchEngine
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from tests import test_settings
from django.core import management

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"


def setUpModule():
    pass


def tearDownModule():
    se = SearchEngineFactory().create()
    se.delete_index(index='terms,concepts')
    se.delete_index(index='resources')
    se.delete_index(index='resource_relations')


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
    def loadOntology(cls):
        ontologies_count = Ontology.objects.exclude(ontologyid__isnull=True).count()
        if ontologies_count == 0:
            extensions = [os.path.join(test_settings.ONTOLOGY_PATH, x) for x in test_settings.ONTOLOGY_EXT]
            management.call_command('load_ontology', source=os.path.join(test_settings.ONTOLOGY_PATH, test_settings.ONTOLOGY_BASE),
                version=test_settings.ONTOLOGY_BASE_VERSION, ontology_name=test_settings.ONTOLOGY_BASE_NAME, id=test_settings.ONTOLOGY_BASE_ID, extensions=','.join(extensions), verbosity=0)

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

    def __init__(self, **kwargs):
        super(TestSearchEngine, self).__init__(**kwargs)

    def delete(self, **kwargs):
        """
        Deletes a document from the index
        Pass an index and id to delete a specific document
        Pass a body with a query dsl to delete by query

        """

        #kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).delete(**kwargs)

    def delete_index(self, **kwargs):
        """
        Deletes an entire index

        """

        #kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).delete_index(**kwargs)

    def search(self, **kwargs):
        """
        Search for an item in the index.
        Pass an index and id to get a specific document
        Pass a body with a query dsl to perform a search

        """

        #kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).search(**kwargs)

    def create_index(self, **kwargs):
        #kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).create_index(**kwargs)

    def index_data(self, index=None, body=None, idfield=None, id=None, **kwargs):
        """
        Indexes a document or list of documents into Elasticsearch

        If "id" is supplied then will use that as the id of the document

        If "idfield" is supplied then will try to find that property in the
            document itself and use the value found for the id of the document

        """

        kwargs['index'] = index
        kwargs['body'] = body
        kwargs['idfield'] = idfield
        kwargs['id'] = id
        #kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).index_data(**kwargs)

    def bulk_index(self, data, **kwargs):
        kwargs['data'] = data
        #kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).bulk_index(**kwargs)

    def create_bulk_item(self, **kwargs):
        #kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).create_bulk_item(**kwargs)

    def count(self, **kwargs):
        #kwargs = self.reset_index(**kwargs)
        return super(TestSearchEngine, self).count(**kwargs)
