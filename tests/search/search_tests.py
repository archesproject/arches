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
import os
import time
import uuid

from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.models.models import NodeGroup
from arches.app.search.elasticsearch_dsl_builder import (
    Match,
    Query,
)
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.permission_backend import assign_perm, remove_perm
from arches.app.views.search import search_terms, search_results
from django.http import HttpRequest
from arches.app.utils.data_management.resource_graphs.importer import (
    import_graph as ResourceGraphImporter,
)
from django.contrib.auth.models import User
from django.test.utils import captured_stdout
from django.test import RequestFactory
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.search.search_tests --settings="tests.test_settings"


class SearchTests(ArchesTestCase):
    graph_fixtures = ["All_Datatypes", "Resource Test Model"]
    allDataTypeGraphId = "d71a8f56-987f-4fd1-87b5-538378740f15"

    def sync_es(self, search_engine=None, index="resources"):
        se = search_engine if search_engine else SearchEngineFactory().create()
        se.refresh(index=index)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.tester = User.objects.create_user(
            username="Tester", email="test@test.com", password="test12345!"
        )

    @classmethod
    def tearDownClass(cls):
        se = SearchEngineFactory().create()
        with captured_stdout():
            se.delete_index(index="test")
            se.delete_index(index="bulk")
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.delete_resources()

    def delete_resources(self):
        se = SearchEngineFactory().create()
        q = {"query": {"match_all": {}}}
        se.delete(index="resources", query=q)
        self.sync_es(se)

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

        self.sync_es(se)
        time.sleep(1)

        query = Query(se, start=0, limit=100)
        match = Match(field="type", query="altLabel")
        query.add_query(match)
        query.delete(index="test", refresh=True)
        self.sync_es(se)

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

    def test_search_terms_unpermitted_user(self):
        """
        Test search_terms method with an unpermitted user

        """
        se = SearchEngineFactory().create()
        admin_user = User.objects.get(username="admin")
        nodeid = "c9b37b7c-17b3-11eb-a708-acde48001122"
        nodegroup = NodeGroup.objects.get(pk=nodeid)
        tileid = "bebffbea-daf6-414e-80c2-530ec88d2705"
        resourceinstanceid = "745f5e4a-d645-4c50-bafc-c677ea95f060"
        resource = Resource(uuid.UUID(resourceinstanceid))
        resource.graph_id = "c9b37a14-17b3-11eb-a708-acde48001122"
        resource.save(user=admin_user, transaction_id=uuid.uuid4())
        assign_perm("no_access_to_nodegroup", self.tester, nodegroup)
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
        self.sync_es(se)
        # wait a moment for ES to finish indexing
        time.sleep(1)
        request = HttpRequest()
        request.method = "GET"
        request.GET.__setitem__("lang", "en")
        request.GET.__setitem__("q", "Etiwanda")
        request.LANGUAGE_CODE = "en"
        request.user = self.tester
        response = search_terms(request)
        result = {}
        try:
            result = json.loads(response.content)
        except json.decoder.JSONDecodeError:
            print("Failed to parse search result")
        self.assertTrue("terms" in result and len(result["terms"]) == 0)
        remove_perm("no_access_to_nodegroup", self.tester, nodegroup)

    def test_search_terms_permitted_user(self):
        """
        Test search terms method with a permitted user

        """
        admin_user = User.objects.get(username="admin")
        nodeid = uuid.UUID("c9b37b7c-17b3-11eb-a708-acde48001122")
        tileid = uuid.UUID("bebffbea-daf6-414e-80c2-530ec88d2705")
        resourceinstanceid = uuid.UUID("745f5e4a-d645-4c50-bafc-c677ea95f060")
        resource = Resource(resourceinstanceid)
        resource.graph_id = uuid.UUID("c9b37a14-17b3-11eb-a708-acde48001122")

        resource.save(user=admin_user, transaction_id=uuid.uuid4())
        tile_data = {}
        tile_data[str(nodeid)] = {
            "en": {"value": "Alpha Gamma Delta Eta Epsilon", "direction": "ltr"}
        }
        new_tile = Tile(
            tileid=tileid,
            resourceinstance_id=resourceinstanceid,
            data=tile_data,
            nodegroup_id=nodeid,
        )
        new_tile.save(index=False)
        new_tile.index()
        self.sync_es()
        # wait a moment for ES to finish indexing
        time.sleep(1)
        request = HttpRequest()
        request.method = "GET"
        request.GET.__setitem__("lang", "en")
        request.GET.__setitem__("q", "Alpha Gamma Delta")
        request.LANGUAGE_CODE = "en"
        request.user = admin_user
        response = search_terms(request)
        result = {}
        try:
            result = json.loads(response.content)
        except json.decoder.JSONDecodeError:
            print("Failed to parse search result")
        self.assertTrue("terms" in result and len(result["terms"]) == 1)

    def test_adv_search_on_non_null_geom_node(self):
        geojson_nodeid = "be25bdf0-c8bf-11ed-a172-0242ac130009"
        user = User.objects.get(username="admin")
        graphid = self.allDataTypeGraphId

        tileid = "aaaaaaaa-daf6-414e-80c2-530ec88d2705"
        resourceinstanceid = "bbbbbbbb-d645-4c50-bafc-c677ea95f060"
        resource = Resource(uuid.UUID(resourceinstanceid))
        resource.graph_id = graphid
        resource.graph.is_active = True
        resource.graph.save()
        resource.save(user=user, transaction_id=uuid.uuid4())
        tile_data = {}
        tile_data[geojson_nodeid] = {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": "b3496f23d0e20fe8fedd646dad1cb723",
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-123.79236180702188, 32.369335685437285],
                                [-113.79980207919247, 32.437401858468235],
                                [-114.83484221180882, 42.146158503110485],
                                [-124.85535408028454, 42.13410461202932],
                                [-123.79236180702188, 32.369335685437285],
                            ]
                        ],
                    },
                }
            ],
        }
        new_tile = Tile(
            tileid=uuid.UUID(tileid),
            resourceinstance_id=resourceinstanceid,
            data=tile_data,
            nodegroup_id=geojson_nodeid,
        )
        new_tile.save()

        tileid = "cccccccc-daf6-414e-80c2-530ec88d2705"
        resourceinstanceid = "dddddddd-d645-4c50-bafc-c677ea95f060"
        resource = Resource(uuid.UUID(resourceinstanceid))
        resource.graph_id = graphid
        resource.save(user=user, transaction_id=uuid.uuid4())
        tile_data = {}
        tile_data[geojson_nodeid] = {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": "a3496f23d0e20fe8fedd646dad1cb723",
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-123.79236180702188, 32.369335685437285],
                    },
                }
            ],
        }
        new_tile = Tile(
            tileid=uuid.UUID(tileid),
            resourceinstance_id=resourceinstanceid,
            data=tile_data,
            nodegroup_id=geojson_nodeid,
        )
        new_tile.save()
        self.sync_es()

        # test search for non-null geom
        request = HttpRequest()
        request.method = "GET"
        request.GET.__setitem__("paging-filter", "1")
        request.GET.__setitem__(
            "advanced-search",
            json.dumps(
                [
                    {
                        "op": "and",
                        geojson_nodeid: {
                            "op": "not_null",
                            "val": "",
                        },
                    }
                ]
            ),
        )
        request.user = user
        results = search_results(request=request)
        results = JSONDeserializer().deserialize(results.content)["results"]["hits"]
        self.assertEqual(2, len(results["hits"]))

        # test search for geom with Polygon type
        request = HttpRequest()
        request.method = "GET"
        request.GET.__setitem__("paging-filter", "1")
        request.GET.__setitem__(
            "advanced-search",
            json.dumps(
                [
                    {
                        "op": "and",
                        geojson_nodeid: {
                            "op": "Polygon",
                            "val": "",
                        },
                    }
                ]
            ),
        )
        request.user = user
        results = search_results(request=request)
        results = JSONDeserializer().deserialize(results.content)["results"]["hits"]
        self.assertEqual(1, len(results["hits"]))

    def test_adv_search_on_null_geom_node(self):
        non_localized_string_nodeid = "cb30d5aa-59c5-11ef-a45a-faffc210b420"
        geojson_nodeid = "be25bdf0-c8bf-11ed-a172-0242ac130009"
        tileid = "bebffbea-daf6-414e-80c2-530ec88d2705"
        resourceinstanceid = "745f5e4a-d645-4c50-bafc-c677ea95f060"
        resource = Resource(uuid.UUID(resourceinstanceid))
        user = User.objects.get(username="admin")
        resource.graph_id = self.allDataTypeGraphId
        resource.graph.is_active = True
        resource.graph.save()
        resource.save(user=user, transaction_id=uuid.uuid4())
        tile_data = {}
        tile_data[non_localized_string_nodeid] = "Etiwanda Avenue Street Trees"
        new_tile = Tile(
            tileid=uuid.UUID(tileid),
            resourceinstance_id=resourceinstanceid,
            data=tile_data,
            nodegroup_id=non_localized_string_nodeid,
        )
        new_tile.save()
        self.sync_es()

        # test search for null geom
        request = HttpRequest()
        request.method = "GET"
        request.GET.__setitem__("paging-filter", "1")
        request.GET.__setitem__(
            "advanced-search",
            json.dumps(
                [
                    {
                        "op": "and",
                        geojson_nodeid: {
                            "op": "null",
                            "val": "",
                        },
                    }
                ]
            ),
        )
        request.user = user
        results = search_results(request=request)
        results = JSONDeserializer().deserialize(results.content)["results"]["hits"]
        self.assertEqual(1, len(results["hits"]))

    def test_adv_search_on_non_null_file_list_node(self):
        filelist_nodeid = "1d1bfbea-c8bf-11ed-bf64-0242ac130009"
        user = User.objects.get(username="admin")
        graphid = self.allDataTypeGraphId

        tileid = "aaaaaaaa-daf6-414e-80c2-530ec88d2705"
        resourceinstanceid = "bbbbbbbb-d645-4c50-bafc-c677ea95f060"
        resource = Resource(uuid.UUID(resourceinstanceid))
        resource.graph_id = graphid
        resource.graph.is_active = True
        resource.graph.save()
        resource.save(user=user, transaction_id=uuid.uuid4())
        tile_data = {}
        tile_data[filelist_nodeid] = [
            {
                "url": None,
                "name": "Screenshot 2024-08-12 at 3.57.42\u202fPM.png",
                "size": 103033,
                "type": "image/png",
                "index": 0,
                "title": {"en": {"value": "", "direction": "ltr"}},
                "width": 1046,
                "height": 1082,
                "status": "added",
                "altText": {"en": {"value": "", "direction": "ltr"}},
                "content": "blob:http://localhost:8000/599de288-f394-4e2b-8b49-05452360c0d0",
                "file_id": None,
                "accepted": True,
                "attribution": {"en": {"value": "", "direction": "ltr"}},
                "description": {"en": {"value": "", "direction": "ltr"}},
                "lastModified": 1723503486969,
            }
        ]

        new_tile = Tile(
            tileid=uuid.UUID(tileid),
            resourceinstance_id=resourceinstanceid,
            data=tile_data,
            nodegroup_id=filelist_nodeid,
        )
        new_tile.save()
        self.sync_es()

        # test search for non-null file
        request = HttpRequest()
        request.method = "GET"
        request.GET.__setitem__("paging-filter", "1")
        request.GET.__setitem__(
            "advanced-search",
            json.dumps(
                [
                    {
                        "op": "and",
                        filelist_nodeid: {
                            "op": "not_null",
                            "val": "",
                        },
                    }
                ]
            ),
        )
        request.user = user
        results = search_results(request=request)
        results = JSONDeserializer().deserialize(results.content)["results"]["hits"]
        self.assertEqual(1, len(results["hits"]))

    def test_adv_search_on_null_file_node(self):
        non_localized_string_nodeid = "cb30d5aa-59c5-11ef-a45a-faffc210b420"
        filelist_nodeid = "1d1bfbea-c8bf-11ed-bf64-0242ac130009"
        tileid = "bebffbea-daf6-414e-80c2-530ec88d2705"
        resourceinstanceid = "745f5e4a-d645-4c50-bafc-c677ea95f060"
        resource = Resource(uuid.UUID(resourceinstanceid))
        user = User.objects.get(username="admin")
        resource.graph_id = self.allDataTypeGraphId
        resource.graph.is_active = True
        resource.graph.save()
        resource.save(user=user, transaction_id=uuid.uuid4())
        tile_data = {}
        tile_data[non_localized_string_nodeid] = "Etiwanda Avenue Street Trees"
        new_tile = Tile(
            tileid=uuid.UUID(tileid),
            resourceinstance_id=resourceinstanceid,
            data=tile_data,
            nodegroup_id=non_localized_string_nodeid,
        )
        new_tile.save()
        self.sync_es()

        # test search for null geom
        request = HttpRequest()
        request.method = "GET"
        request.GET.__setitem__("paging-filter", "1")
        request.GET.__setitem__(
            "advanced-search",
            json.dumps(
                [
                    {
                        "op": "and",
                        filelist_nodeid: {
                            "op": "null",
                            "val": "",
                        },
                    }
                ]
            ),
        )
        request.user = user
        results = search_results(request=request)
        results = JSONDeserializer().deserialize(results.content)["results"]["hits"]
        self.assertEqual(1, len(results["hits"]))

    def test_adv_search_on_resource_instance_node_in_list_all(self):
        with open(
            os.path.join("tests/fixtures/resource_graphs/Cardinality Test Model.json"),
            "r",
        ) as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])
        ri_dt_nodeid = "7f4406d0-c8c1-11ed-a172-0242ac130009"
        graphid = "d71a8f56-987f-4fd1-87b5-538378740f15"
        cardinality_graphid = "2f7f8e40-adbc-11e6-ac7f-14109fd34195"
        user = User.objects.get(username="admin")
        graph = Graph.objects.get(
            graphid=cardinality_graphid,
        )
        graph.is_active = True
        graph.save()
        graph.publish(user=user)
        new_cardinality_resource_1 = Resource(graph_id=cardinality_graphid)
        new_cardinality_resource_1.save(
            user=self.tester, transaction_id=uuid.uuid4(), index=False
        )
        new_cardinality_resource_1.index()
        new_cardinality_resource_2 = Resource(graph_id=cardinality_graphid)
        new_cardinality_resource_2.save(
            user=self.tester, transaction_id=uuid.uuid4(), index=False
        )
        new_cardinality_resource_2.index()
        new_resource_1 = Resource(graph_id=graphid)
        new_resource_1.graph.is_active = True
        new_resource_1.graph.save()
        new_resource_1.save(user=user, transaction_id=uuid.uuid4(), index=False)
        new_resource_1.index()
        new_resource_2 = Resource(graph_id=graphid)
        new_resource_2.save(user=user, transaction_id=uuid.uuid4(), index=False)
        new_resource_2.index()
        new_ri_tile_1 = Tile.get_blank_tile(
            ri_dt_nodeid, resourceid=str(new_resource_1.resourceinstanceid)
        )
        # print("PRINT")
        # print(new_cardinality_resource_1.resourceinstanceid)
        new_ri_tile_1.data[ri_dt_nodeid] = [
            {
                "resourceId": str(new_cardinality_resource_1.resourceinstanceid),
                "ontologyProperty": "",
                "inverseOntologyProperty": "",
                "resourceXresourceId": str(uuid.uuid4()),
            },
            {
                "resourceId": str(new_cardinality_resource_2.resourceinstanceid),
                "ontologyProperty": "",
                "inverseOntologyProperty": "",
                "resourceXresourceId": str(uuid.uuid4()),
            },
        ]
        new_ri_tile_1.save(index=False)
        new_ri_tile_1.index()
        new_ri_tile_2 = Tile.get_blank_tile(
            ri_dt_nodeid, resourceid=str(new_resource_2.resourceinstanceid)
        )
        new_ri_tile_2.data[ri_dt_nodeid] = [
            {
                "resourceId": str(new_cardinality_resource_1.resourceinstanceid),
                "ontologyProperty": "",
                "inverseOntologyProperty": "",
                "resourceXresourceId": str(uuid.uuid4()),
            },
        ]
        new_ri_tile_2.save(index=False)
        new_ri_tile_2.index()

        self.sync_es()
        time.sleep(2)
        # test search for non-null resource list
        request_1 = HttpRequest()
        request_1.method = "GET"
        request_1.GET.__setitem__("paging-filter", "1")
        request_1.GET.__setitem__(
            "advanced-search",
            json.dumps(
                [
                    {
                        "op": "and",
                        ri_dt_nodeid: {
                            "op": "in_list_all",
                            "val": [
                                str(new_cardinality_resource_1.resourceinstanceid),
                                str(new_cardinality_resource_2.resourceinstanceid),
                            ],
                        },
                    }
                ]
            ),
        )
        request_1.user = user
        results = search_results(request=request_1)
        results = JSONDeserializer().deserialize(results.content)["results"]["hits"]
        self.assertEqual(1, len(results["hits"]))

        # test for in_list_any
        request_2 = HttpRequest()
        request_2.method = "GET"
        request_2.GET.__setitem__("paging-filter", "1")
        request_2.GET.__setitem__(
            "advanced-search",
            json.dumps(
                [
                    {
                        "op": "and",
                        ri_dt_nodeid: {
                            "op": "in_list_any",
                            "val": [
                                str(new_cardinality_resource_1.resourceinstanceid),
                                str(new_cardinality_resource_2.resourceinstanceid),
                            ],
                        },
                    }
                ]
            ),
        )
        request_2.user = user
        results = search_results(request=request_2)
        results = JSONDeserializer().deserialize(results.content)["results"]["hits"]
        self.assertEqual(2, len(results["hits"]))

    def test_no_resources_from_unpublished_graphs(self):

        test_graph = Graph.objects.get(name="Resource Test Model")

        Resource.objects.create(
            graph=test_graph,
            name="Resource from unpublished graph",
            resourceinstanceid="53c2246a-dd01-4ee1-9e45-8b339197824e",
        )

        # add delay to allow for indexes to be updated
        time.sleep(1)

        user = User.objects.get(username="admin")

        factory = RequestFactory()
        request = factory.get("/search")
        request.user = user

        response = search_results(request)
        response_data = json.loads(response.content.decode("utf-8"))
        hits_data = response_data["results"]["hits"]["hits"]
        hit_ids = [hit["_id"] for hit in hits_data]

        self.assertNotIn("53c2246a-dd01-4ee1-9e45-8b339197824e", hit_ids)
