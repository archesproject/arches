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

import json
import time
import uuid

from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.search.elasticsearch_dsl_builder import (
    Match,
    Query,
)
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.i18n import LanguageSynchronizer
from arches.app.views.search import search_terms
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.test.utils import captured_stdout
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.search.search_tests --settings="tests.test_settings"


class SearchTests(ArchesTestCase):
    @classmethod
    def tearDownClass(cls):
        models.GraphModel.objects.filter(
            pk="d291a445-fa5f-11e6-afa8-14109fd34195"
        ).delete()
        User.objects.filter(username="Tester").delete()
        Resource.objects.filter(pk="745f5e4a-d645-4c50-bafc-c677ea95f060").delete()
        se = SearchEngineFactory().create()
        with captured_stdout():
            se.delete_index(index="test")
            se.delete_index(index="bulk")
        super().tearDownClass()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        LanguageSynchronizer.synchronize_settings_with_db()
        User.objects.create_user(
            username="Tester", email="test@test.com", password="test12345!"
        )
        cls.loadOntology()
        cls.ensure_resource_test_model_loaded()

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
        with captured_stdout():
            se.create_index(index="test")

        documents = []
        count_before = se.count(index="test")
        for i in range(10):
            doc = {
                "id": i,
                "type": "prefLabel",
                "value": "test pref label",
            }
            documents.append(
                se.create_bulk_item(
                    op_type="index", index="test", id=doc["id"], data=doc
                )
            )

        se.bulk_index(documents, refresh=True)
        count_after = se.count(index="test")
        self.assertEqual(count_after - count_before, 10)

    def test_bulk_indexer(self):
        se = SearchEngineFactory().create()
        with captured_stdout():
            se.create_index(index="bulk")

        with se.BulkIndexer(batch_size=500, refresh=True) as bulk_indexer:
            for i in range(1001):
                doc = {"id": i, "type": "prefLabel", "value": "test pref label"}
                bulk_indexer.add(index="bulk", id=doc["id"], data=doc)

        count_after = se.count(index="bulk")
        self.assertEqual(count_after, 1001)

    def test_search_terms(self):
        """
        Test finding a resource by a term

        """

        nodeid = "c9b37b7c-17b3-11eb-a708-acde48001122"
        tileid = "bebffbea-daf6-414e-80c2-530ec88d2705"
        resourceinstanceid = "745f5e4a-d645-4c50-bafc-c677ea95f060"
        resource = Resource(uuid.UUID(resourceinstanceid))
        user = User.objects.get(username="Tester")
        resource.graph_id = "c9b37a14-17b3-11eb-a708-acde48001122"
        resource.save(user=user, transaction_id=uuid.uuid4())
        tile_data = {}
        tile_data[nodeid] = {
            "en": {"value": "Etiwanda Avenue Street Trees", "direction": "ltr"}
        }
        new_tile = Tile(
            tileid=uuid.UUID(tileid),
            resourceinstance_id=resourceinstanceid,
            data=tile_data,
            nodegroup_id=nodeid,
        )
        new_tile.save()
        time.sleep(1)  # wait a moment for ES to finish indexing
        request = HttpRequest()
        request.method = "GET"
        request.GET.__setitem__("lang", "en")
        request.GET.__setitem__("q", "Etiwanda")
        request.LANGUAGE_CODE = "en"
        request.user = user
        response = search_terms(request)
        result = {}
        try:
            result = json.loads(response.content)
        except json.decoder.JSONDecodeError:
            print("Failed to parse search result")
        self.assertTrue("terms" in result and len(result["terms"]) == 1)
