# coding: utf-8

import os
from tests import test_settings
from tests import test_setup
from django.test import SimpleTestCase, TestCase
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"

def setUpModule():
    #pass
    se = SearchEngineFactory().create()
    se.delete_index(index='test')
    #test_setup.install()

def tearDownModule():
    pass
    # se = SearchEngineFactory().create()
    # se.delete_index(index='test')
    # #test_setup.install()

class SearchTests(SimpleTestCase):

    def test_bulk_delete(self):
        """
        Test bulk deleting of documents in Elasticsearch

        """

        se = SearchEngineFactory().create()
        # se.create_index(index='test')

        for i in range(10):
            x = {
                'id': i,
                'type': 'prefLabel',
                'value': 'test pref label',
            }
            se.index_data(index='test', doc_type='test', body=x, idfield='id', refresh=True)
            y = {
                'id': i + 100,
                'type': 'altLabel',
                'value': 'test alt label',
            }
            se.index_data(index='test', doc_type='test', body=y, idfield='id', refresh=True)


        query = Query(se, start=0, limit=100)
        match = Match(field='type', query='altLabel')
        query.add_query(match)

        query.delete(index='test', refresh=True)

        self.assertEqual(se.es.count(index='test', doc_type='test')['count'], 10)

