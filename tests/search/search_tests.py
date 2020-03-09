"""
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
"""

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
        se.delete_index(index="test")
        se.delete_index(index="bulk")

    def test_delete_by_query(self):
        """
        Test deleting documents by query in Elasticsearch

        """

        se = SearchEngineFactory().create()

        for i in range(10):
            x = {"id": i, "type": "prefLabel", "value": "test pref label"}
            se.index_data(index="test", body=x, idfield="id", refresh=True)
            y = {"id": i + 100, "type": "altLabel", "value": "test alt label"}
            se.index_data(index="test", body=y, idfield="id", refresh=True)

        time.sleep(3)

        query = Query(se, start=0, limit=100)
        match = Match(field="type", query="altLabel")
        query.add_query(match)

        query.delete(index="test", refresh=True)

        self.assertEqual(se.count(index="test"), 10)

    def test_bulk_add_documents(self):
        """
        Test adding documents to Elasticsearch in bulk

        """

        se = SearchEngineFactory().create()
        se.create_index(index="test")

        documents = []
        count_before = se.count(index="test")
        for i in range(10):
            doc = {
                "id": i,
                "type": "prefLabel",
                "value": "test pref label",
            }
            documents.append(se.create_bulk_item(op_type="index", index="test", id=doc["id"], data=doc))

        ret = se.bulk_index(documents, refresh=True)
        count_after = se.count(index="test")
        self.assertEqual(count_after - count_before, 10)

    def test_bulk_indexer(self):
        se = SearchEngineFactory().create()
        se.create_index(index="bulk")

        with se.BulkIndexer(batch_size=500, refresh=True) as bulk_indexer:
            for i in range(1001):
                doc = {"id": i, "type": "prefLabel", "value": "test pref label"}
                bulk_indexer.add(index="bulk", id=doc["id"], data=doc)

        count_after = se.count(index="bulk")
        self.assertEqual(count_after, 1001)
