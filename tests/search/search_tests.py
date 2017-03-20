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

import time
import uuid
from tests.base_test import ArchesTestCase
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range

# these tests can be run from the command line via
# python manage.py test tests/search/search_tests.py --pattern="*.py" --settings="tests.test_settings"


class SearchTests(ArchesTestCase):

    @classmethod
    def tearDownClass(cls):
        se = SearchEngineFactory().create()
        se.delete_index(index='test')

    def test_bulk_delete(self):
        """
        Test bulk deleting of documents in Elasticsearch

        """

        se = SearchEngineFactory().create()

        doc_type = uuid.uuid4()

        for i in range(10):
            x = {
                'id': i,
                'type': 'prefLabel',
                'value': 'test pref label',
            }
            se.index_data(index='test', doc_type=doc_type, body=x, idfield='id', refresh=True)
            y = {
                'id': i + 100,
                'type': 'altLabel',
                'value': 'test alt label',
            }
            se.index_data(index='test', doc_type=doc_type, body=y, idfield='id', refresh=True)

        time.sleep(1)
        
        query = Query(se, start=0, limit=100)
        match = Match(field='type', query='altLabel')
        query.add_query(match)

        query.delete(index='test', doc_type=doc_type, refresh=True)

        self.assertEqual(se.count(index='test', doc_type=doc_type), 10)

