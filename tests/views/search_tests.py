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
import uuid
from http import HTTPStatus

from tests.base_test import ArchesTestCase
from tests.utils.search_test_utils import sync_es, get_response_json
from django.http import HttpRequest
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.test.client import Client
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.views.search import search_results
from guardian.shortcuts import assign_perm
from arches.app.search.components.base import SearchFilterFactory
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Bool, Match, Nested
from arches.app.search.mappings import TERMS_INDEX, CONCEPTS_INDEX, RESOURCES_INDEX
from arches.app.search.es_mapping_modifier import EsMappingModifier

# these tests can be run from the command line via
# python manage.py test tests.views.search_tests --settings="tests.test_settings"


class SearchTests(ArchesTestCase):
    graph_fixtures = ["Search Test Model"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        se = SearchEngineFactory().create()
        q = Query(se=se)
        for indexname in [TERMS_INDEX, CONCEPTS_INDEX, RESOURCES_INDEX]:
            q.delete(index=indexname, refresh=True)

        cls.client = Client()
        cls.client.login(username="admin", password="admin")

        cls.search_model_graphid = "d291a445-fa5f-11e6-afa8-14109fd34195"
        cls.search_model_cultural_period_nodeid = "7a182580-fa60-11e6-96d1-14109fd34195"
        cls.search_model_creation_date_nodeid = "1c1d05f5-fa60-11e6-887f-14109fd34195"
        cls.search_model_destruction_date_nodeid = (
            "e771b8a1-65fe-11e7-9163-14109fd34195"
        )
        cls.search_model_name_nodeid = "2fe14de3-fa61-11e6-897b-14109fd34195"
        cls.search_model_sensitive_info_nodeid = "57446fae-65ff-11e7-b63a-14109fd34195"
        cls.search_model_geom_nodeid = "3ebc6785-fa61-11e6-8c85-14109fd34195"

        cls.user = User.objects.create_user(
            "unpriviliged_user", "unpriviliged_user@archesproject.org", "test"
        )
        cls.user.groups.add(Group.objects.get(name="Guest"))

        nodegroup = models.NodeGroup.objects.get(
            pk=cls.search_model_destruction_date_nodeid
        )
        assign_perm("no_access_to_nodegroup", cls.user, nodegroup)

        # Add a concept that defines a min and max date
        concept = {
            "id": "00000000-0000-0000-0000-000000000001",
            "legacyoid": "ARCHES",
            "nodetype": "ConceptScheme",
            "values": [],
            "subconcepts": [
                {
                    "values": [
                        {
                            "value": "Mock concept",
                            "language": "en",
                            "category": "label",
                            "type": "prefLabel",
                            "id": "",
                            "conceptid": "",
                        },
                        {
                            "value": "1950",
                            "language": "en",
                            "category": "note",
                            "type": "min_year",
                            "id": "",
                            "conceptid": "",
                        },
                        {
                            "value": "1980",
                            "language": "en",
                            "category": "note",
                            "type": "max_year",
                            "id": "",
                            "conceptid": "",
                        },
                    ],
                    "relationshiptype": "hasTopConcept",
                    "nodetype": "Concept",
                    "id": "",
                    "legacyoid": "",
                    "subconcepts": [],
                    "parentconcepts": [],
                    "relatedconcepts": [],
                }
            ],
        }

        post_data = JSONSerializer().serialize(concept)
        content_type = "application/x-www-form-urlencoded"
        response = cls.client.post(
            reverse(
                "concept", kwargs={"conceptid": "00000000-0000-0000-0000-000000000001"}
            ),
            post_data,
            content_type,
        )
        response_json = json.loads(response.content)
        valueid = response_json["subconcepts"][0]["values"][0]["id"]
        cls.conceptid = response_json["subconcepts"][0]["id"]

        # add resource instance with only a cultural period defined
        cls.cultural_period_resourceid = str(uuid.uuid4())
        cls.cultural_period_resource = Resource(
            graph_id=cls.search_model_graphid,
            resourceinstanceid=cls.cultural_period_resourceid,
        )
        tile = Tile(
            data={cls.search_model_cultural_period_nodeid: [valueid]},
            nodegroup_id=cls.search_model_cultural_period_nodeid,
        )
        cls.cultural_period_resource.graph.is_active = True
        cls.cultural_period_resource.graph.save()
        cls.cultural_period_resource.tiles.append(tile)
        cls.cultural_period_resource.save()

        # add resource instance with a creation and destruction date defined
        cls.date_resourceid = str(uuid.uuid4())
        cls.date_resource = Resource(
            graph_id=cls.search_model_graphid, resourceinstanceid=cls.date_resourceid
        )
        tile = Tile(
            data={cls.search_model_creation_date_nodeid: "1941-01-01"},
            nodegroup_id=cls.search_model_creation_date_nodeid,
        )
        cls.date_resource.tiles.append(tile)
        tile = Tile(
            data={cls.search_model_destruction_date_nodeid: "1948-01-01"},
            nodegroup_id=cls.search_model_destruction_date_nodeid,
        )
        cls.date_resource.tiles.append(tile)
        tile = Tile(
            data={
                cls.search_model_name_nodeid: {
                    "en": {"value": "testing 123", "direction": "ltr"}
                }
            },
            nodegroup_id=cls.search_model_name_nodeid,
        )
        cls.date_resource.tiles.append(tile)
        cls.date_resource.save()

        # add resource instance with a creation date and a cultural period defined
        cls.date_and_cultural_period_resourceid = str(uuid.uuid4())
        cls.date_and_cultural_period_resource = Resource(
            graph_id=cls.search_model_graphid,
            resourceinstanceid=cls.date_and_cultural_period_resourceid,
        )
        tile = Tile(
            data={cls.search_model_creation_date_nodeid: "1942-01-01"},
            nodegroup_id=cls.search_model_creation_date_nodeid,
        )
        cls.date_and_cultural_period_resource.tiles.append(tile)
        tile = Tile(
            data={cls.search_model_cultural_period_nodeid: [valueid]},
            nodegroup_id=cls.search_model_cultural_period_nodeid,
        )
        cls.date_and_cultural_period_resource.tiles.append(tile)
        cls.date_and_cultural_period_resource.save()

        # add resource instance with with no dates or periods defined
        cls.name_resource = Resource(graph_id=cls.search_model_graphid)
        tile = Tile(
            data={
                cls.search_model_name_nodeid: {
                    "en": {"value": "some test name", "direction": "ltr"}
                }
            },
            nodegroup_id=cls.search_model_name_nodeid,
        )
        cls.name_resource.tiles.append(tile)
        geom = {
            "type": "FeatureCollection",
            "features": [
                {
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "type": "Feature",
                    "properties": {},
                }
            ],
        }
        tile = Tile(
            data={cls.search_model_geom_nodeid: geom},
            nodegroup_id=cls.search_model_geom_nodeid,
        )
        cls.name_resource.tiles.append(tile)
        cls.name_resource.save()

        sync_es(se)

    def test_temporal_only_search_1(self):
        """
        Search for resources that fall between 1940 and 1960

        """

        temporal_filter = {
            "fromDate": "1940-01-01",
            "toDate": "1960-01-01",
            "dateNodeId": "",
            "inverted": False,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 3)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.cultural_period_resource.pk),
                str(self.date_resource.pk),
                str(self.date_and_cultural_period_resource.pk),
            ],
        )

    def test_temporal_only_search_2(self):
        """
        Search for resources that DON'T fall between 1940 and 1960

        """

        temporal_filter = {
            "fromDate": "1940-01-01",
            "toDate": "1960-01-01",
            "dateNodeId": "",
            "inverted": True,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.cultural_period_resource.pk),
                str(self.date_and_cultural_period_resource.pk),
            ],
        )

    def test_temporal_only_search_3(self):
        """
        Search for resources that fall between 1940 and 1960 and date node is supplied

        """

        temporal_filter = {
            "fromDate": "1940-01-01",
            "toDate": "1960-01-01",
            "dateNodeId": self.search_model_creation_date_nodeid,
            "inverted": False,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.date_resource.pk),
                str(self.date_and_cultural_period_resource.pk),
            ],
        )

    def test_temporal_only_search_4(self):
        """
        Search for resources that DON'T fall between 1940 and 1960 and date node is supplied

        """

        temporal_filter = {
            "fromDate": "1940-01-01",
            "toDate": "1960-01-01",
            "dateNodeId": self.search_model_creation_date_nodeid,
            "inverted": True,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 0)

    def test_temporal_only_search_5(self):
        """
        Search for resources that fall between 1950 and 1960 (the cultural period resource)

        """

        temporal_filter = {
            "fromDate": "1950-01-01",
            "toDate": "1960-01-01",
            "dateNodeId": "",
            "inverted": False,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.cultural_period_resource.pk),
                str(self.date_and_cultural_period_resource.pk),
            ],
        )

    def test_temporal_only_search_6(self):
        """
        Search for resources that DON'T fall between 1950 and 1960 (the cultural period resource)

        """

        temporal_filter = {
            "fromDate": "1950-01-01",
            "toDate": "1960-01-01",
            "dateNodeId": "",
            "inverted": True,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 3)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.cultural_period_resource.pk),
                str(self.date_resource.pk),
                str(self.date_and_cultural_period_resource.pk),
            ],
        )

    def test_temporal_only_search_7(self):
        """
        Search for resources that fall between 1990 and 2000

        """

        temporal_filter = {
            "fromDate": "1990-01-01",
            "toDate": "2000-01-01",
            "dateNodeId": "",
            "inverted": False,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 0)

    def test_temporal_only_search_8(self):
        """
        Search for resources that DON'T fall between 1990 and 2000

        """

        temporal_filter = {
            "fromDate": "1990-01-01",
            "toDate": "2000-01-01",
            "dateNodeId": "",
            "inverted": True,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 3)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.cultural_period_resource.pk),
                str(self.date_resource.pk),
                str(self.date_and_cultural_period_resource.pk),
            ],
        )

    def test_temporal_only_search_9(self):
        """
        Search for resources that are greater then 1940

        """

        temporal_filter = {
            "fromDate": "1940-01-01",
            "toDate": "",
            "dateNodeId": "",
            "inverted": False,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 3)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.cultural_period_resource.pk),
                str(self.date_resource.pk),
                str(self.date_and_cultural_period_resource.pk),
            ],
        )

    def test_temporal_only_search_10(self):
        """
        Search for resources that AREN'T greater then 1940

        """

        temporal_filter = {
            "fromDate": "1940-01-01",
            "toDate": "",
            "dateNodeId": "",
            "inverted": True,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 0)

    def test_temporal_only_search_11(self):
        """
        Search for resources that AREN'T greater then 1950

        """

        temporal_filter = {
            "fromDate": "1950-01-01",
            "toDate": "",
            "dateNodeId": "",
            "inverted": True,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.date_resource.pk),
                str(self.date_and_cultural_period_resource.pk),
            ],
        )

    def test_temporal_and_term_search_1(self):
        """
        Search for resources that fall between 1940 and 1960 and have the string "test" in them

        """

        temporal_filter = {
            "fromDate": "1940-01-01",
            "toDate": "1960-01-01",
            "dateNodeId": "",
            "inverted": False,
        }
        term_filter = [
            {
                "type": "string",
                "context": "",
                "context_label": "",
                "id": "test",
                "text": "test",
                "value": "test",
                "inverted": False,
            }
        ]
        query = {"time-filter": temporal_filter, "term-filter": term_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 1)
        self.assertCountEqual(extract_pks(response_json), [str(self.date_resource.pk)])

    def test_temporal_and_term_search_2(self):
        """
        Search for resources that DON'T fall between 1940 and 1960 and have the string "test" in them

        """

        temporal_filter = {
            "fromDate": "1940-01-01",
            "toDate": "1960-01-01",
            "dateNodeId": "",
            "inverted": True,
        }
        term_filter = [
            {
                "type": "string",
                "context": "",
                "context_label": "",
                "id": "test",
                "text": "test",
                "value": "test",
                "inverted": False,
            }
        ]
        query = {"time-filter": temporal_filter, "term-filter": term_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 0)

    def test_term_search_1(self):
        """
        Search for resources that have the string "test" in them as a "string" search

        """

        term_filter = [
            {
                "type": "string",
                "context": "",
                "context_label": "",
                "id": "test",
                "text": "test",
                "value": "test",
                "inverted": False,
            }
        ]
        query = {"term-filter": term_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json),
            [str(self.date_resource.pk), str(self.name_resource.pk)],
        )

    def test_term_search_2(self):
        """
        Search for resources that DON'T have the string "test" in them as a "string" search

        """

        term_filter = [
            {
                "type": "string",
                "context": "",
                "context_label": "",
                "id": "test",
                "text": "test",
                "value": "test",
                "inverted": True,
            }
        ]
        query = {"term-filter": term_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.date_and_cultural_period_resource.pk),
                str(self.cultural_period_resource.pk),
            ],
        )

    def test_term_search_3(self):
        """
        Search for resources that have the string "test" in them as a "term" search

        """

        term_filter = [
            {
                "type": "term",
                "context": "",
                "context_label": "",
                "nodegroupid": self.search_model_name_nodeid,
                "id": "test",
                "text": "test",
                "value": "test",
                "inverted": False,
            }
        ]
        query = {"term-filter": term_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 1)
        self.assertCountEqual(extract_pks(response_json), [str(self.name_resource.pk)])

    def test_term_search_4(self):
        """
        Search for resources that DON'T have the string "test" in them as a "term" search

        """

        term_filter = [
            {
                "type": "term",
                "context": "",
                "context_label": "",
                "nodegroupid": self.search_model_name_nodeid,
                "id": "test",
                "text": "test",
                "value": "test",
                "inverted": True,
            }
        ]
        query = {"term-filter": term_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 3)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.date_resource.pk),
                str(self.date_and_cultural_period_resource.pk),
                str(self.cultural_period_resource.pk),
            ],
        )

    def test_resource_instance_id_search(self):
        """
        Search for a resource by its id

        """
        resource_id = str(self.name_resource.pk)
        request = HttpRequest()
        request.method = "GET"
        request.user = User.objects.get(username="anonymous")
        request.GET["id"] = resource_id
        response = search_results(request)
        response_json = json.loads(response.content)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 1)

    def test_term_search_on_resource_instance_id(self):
        """
        Search for a resource by its id using a term search

        """
        resource_id = str(self.name_resource.pk)

        term_filter = [
            {
                "inverted": False,
                "type": "string",
                "context": "",
                "context_label": "",
                "id": resource_id,
                "text": resource_id,
                "value": resource_id,
                "selected": True,
            }
        ]

        query = {"term-filter": term_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 1)

    def test_concept_search_1(self):
        """
        Search for resources that have the concept "Mock concept" in them as a "concept" search

        """

        term_filter = [
            {
                "type": "concept",
                "context": "",
                "context_label": "",
                "id": "test",
                "text": "test",
                "value": self.conceptid,
                "inverted": False,
            }
        ]
        query = {"term-filter": term_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.date_and_cultural_period_resource.pk),
                str(self.cultural_period_resource.pk),
            ],
        )

    def test_concept_search_2(self):
        """
        Search for resources that DON'T have the concept "Mock concept" in them as a "concept" search

        """

        term_filter = [
            {
                "type": "concept",
                "context": "",
                "context_label": "",
                "id": "test",
                "text": "test",
                "value": self.conceptid,
                "inverted": True,
            }
        ]
        query = {"term-filter": term_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json),
            [str(self.name_resource.pk), str(self.date_resource.pk)],
        )

    def test_spatial_search_1(self):
        """
        Search for resources that fall within a polygon

        """

        spatial_filter = {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": "ec1a2079cc12822bc71a6e6643c2f2b4",
                    "type": "Feature",
                    "properties": {
                        "inverted": False,
                        "buffer": {"width": "100", "unit": "ft"},
                    },
                    "geometry": {
                        "coordinates": [[[-1, -1], [-1, 1], [1, 1], [1, -1], [-1, -1]]],
                        "type": "Polygon",
                    },
                }
            ],
        }
        query = {"map-filter": spatial_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 1)
        self.assertCountEqual(extract_pks(response_json), [str(self.name_resource.pk)])

    def test_spatial_search_2(self):
        """
        Search for resources that DON'T fall within a polygon

        """

        spatial_filter = {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": "ec1a2079cc12822bc71a6e6643c2f2b4",
                    "type": "Feature",
                    "properties": {
                        "inverted": True,
                        "buffer": {"width": "100", "unit": "ft"},
                    },
                    "geometry": {
                        "coordinates": [[[-1, -1], [-1, 1], [1, 1], [1, -1], [-1, -1]]],
                        "type": "Polygon",
                    },
                }
            ],
        }
        query = {"map-filter": spatial_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 0)
        # self.assertCountEqual(extract_pks(response_json), [str(self.name_resource.pk)])

    #
    # -- ADD TESTS THAT INCLUDE PERMISSIONS REQUIREMENTS -- #
    #
    def test_temporal_and_permission_search_1(self):
        """
        Search for resources that fall between 1945 and 1960 with user permissions

        """

        temporal_filter = {
            "fromDate": "1945-01-01",
            "toDate": "1960-01-01",
            "dateNodeId": "",
            "inverted": False,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.cultural_period_resource.pk),
                str(self.date_and_cultural_period_resource.pk),
            ],
        )

    def test_temporal_and_permission_search_2(self):
        """
        Search for resources that fall between 1940 and 1945 with user permissions

        """

        temporal_filter = {
            "fromDate": "1940-01-01",
            "toDate": "1945-01-01",
            "dateNodeId": "",
            "inverted": False,
        }
        query = {"time-filter": temporal_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json),
            [
                str(self.date_resource.pk),
                str(self.date_and_cultural_period_resource.pk),
            ],
        )

    def test_search_returnDsl(self):
        """
        test that a Query object is returned when returnDsl is set to True

        """

        term_filter = [
            {
                "type": "string",
                "context": "",
                "context_label": "",
                "id": "test",
                "text": "test",
                "value": "test",
                "inverted": False,
            }
        ]

        request = HttpRequest()
        request.method = "GET"
        request.user = User.objects.get(username="anonymous")
        request.GET.__setitem__("term-filter", json.dumps(term_filter))
        resp = search_results(request, returnDsl=True)
        self.assertTrue(isinstance(resp, Query))

    def test_search_without_searchview(self):
        """
        Execute a search without setting a search-view component on the query

        """

        response_json = get_response_json(self.client)
        self.assertTrue(response_json["results"]["hits"]["total"]["value"] > 0)

    def test_search_with_bad_searchview(self):
        """
        Execute a search with a search-view component name that does not exist

        """
        query = {"search-view": "unavailable-search-view"}
        with self.assertLogs("django.request", level="WARNING"):
            response_json = get_response_json(self.client, query=query)
        self.assertFalse(response_json["success"])

        # Also test search_home route, not just search_results
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(
                reverse("search_home"), QUERY_STRING="search-view=nonexistent"
            )
        self.assertContains(
            response,
            "Search view instance not found",
            status_code=HTTPStatus.NOT_FOUND,
        )

    def test_searchview_searchview_component_from_admin(self):
        request = HttpRequest()
        request.method = "GET"
        request.user = User.objects.get(username="admin")
        search_component_factory = SearchFilterFactory(request)
        searchview_component_instance = (
            search_component_factory.get_searchview_instance()
        )
        self.assertTrue(searchview_component_instance is not None)

        search_components = searchview_component_instance.get_searchview_filters()
        # 14 available components + search-view component
        self.assertEqual(len(search_components), 15)

    def test_searchview_searchview_component_from_anonymous(self):
        request = HttpRequest()
        request.method = "GET"
        request.user = User.objects.get(username="anonymous")
        search_component_factory = SearchFilterFactory(request)
        searchview_component_instance = (
            search_component_factory.get_searchview_instance()
        )
        self.assertTrue(searchview_component_instance is not None)

        search_components = searchview_component_instance.get_searchview_filters()
        # 14 available components + search-view component
        self.assertEqual(len(search_components), 15)

    def test_search_bad_json(self):
        request = HttpRequest()
        request.method = "GET"
        request.user = User.objects.get(username="anonymous")
        request.GET.__setitem__("term-filter", '{"key": "value",}')
        with self.assertLogs("arches.app.search.components", level="WARNING"):
            resp = search_results(request)
        self.assertEqual(resp.status_code, 500)

    def test_custom_resource_index(self):
        for hit in get_response_json(self.client)["results"]["hits"]["hits"]:
            term_filter = [
                {
                    "type": "term",
                    "context": "",
                    "context_label": "",
                    "id": "business-specific-search-value-%s" % hit["_id"][:6],
                    "text": "business-specific-search-value-%s" % hit["_id"][:6],
                    "value": "business-specific-search-value-%s" % hit["_id"][:6],
                    "inverted": False,
                }
            ]
            query = {"term-filter": term_filter}
            response_json = get_response_json(self.client, query=query)
            self.assertEqual(response_json["results"]["hits"]["total"]["value"], 1)
            term_filter = [
                {
                    "type": "term",
                    "context": "",
                    "context_label": "",
                    "id": "business-specific-search-value-%s" % hit["_id"][:6],
                    "text": "business-specific-search-value-%s" % hit["_id"][:6],
                    "value": "business-specific-search-value-%s" % hit["_id"][:6],
                    "inverted": True,
                }
            ]
            query = {"term-filter": term_filter}
            response_json = get_response_json(self.client, query=query)
            self.assertEqual(response_json["results"]["hits"]["total"]["value"], 3)

        term_filter = [
            {
                "type": "term",
                "context": "",
                "context_label": "",
                "id": "business-specific-search-value-",
                "text": "business-specific-search-value-",
                "value": "business-specific-search-value-",
                "inverted": False,
            }
        ]
        query = {"term-filter": term_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 4)

        term_filter = [
            {
                "type": "term",
                "context": "",
                "context_label": "",
                "id": "business-specific-search-value-",
                "text": "business-specific-search-value-",
                "value": "business-specific-search-value-",
                "inverted": True,
            }
        ]
        query = {"term-filter": term_filter}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 0)

    def test_ids_filter(self):
        ids = [self.cultural_period_resourceid, self.date_resourceid]
        query = {"ids": ids}
        response_json = get_response_json(self.client, query=query)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)


def extract_pks(response_json):
    return [
        result["_source"]["resourceinstanceid"]
        for result in response_json["results"]["hits"]["hits"]
    ]


class TestEsMappingModifier(EsMappingModifier):

    counter = 1

    def __init__(self):
        pass

    @staticmethod
    def add_search_terms(resourceinstance, document, terms):
        if EsMappingModifier.get_mapping_property() not in document:
            document[EsMappingModifier.get_mapping_property()] = []
        document[EsMappingModifier.get_mapping_property()].append(
            {
                "custom_value": "business-specific-search-value-%s"
                % str(resourceinstance.resourceinstanceid)[:6]
            }
        )
        TestEsMappingModifier.counter = TestEsMappingModifier.counter + 1

    @staticmethod
    def create_nested_custom_filter(term, original_element):
        if "nested" not in original_element:
            return original_element
        document_key = EsMappingModifier.get_mapping_property()
        custom_filter = Bool()
        custom_filter.should(
            Match(
                field="%s.custom_value" % document_key,
                query=term["value"],
                type="phrase_prefix",
            )
        )
        custom_filter.should(
            Match(
                field="%s.custom_value.folded" % document_key,
                query=term["value"],
                type="phrase_prefix",
            )
        )
        nested_custom_filter = Nested(path=document_key, query=custom_filter)
        new_must_element = Bool()
        new_must_element.should(original_element)
        new_must_element.should(nested_custom_filter)
        new_must_element.dsl["bool"]["minimum_should_match"] = 1
        return new_must_element

    @staticmethod
    def add_search_filter(
        search_query, term, permitted_nodegroups, include_provisional
    ):
        original_must_filter = search_query.dsl["bool"]["must"]
        search_query.dsl["bool"]["must"] = []
        for must_element in original_must_filter:
            search_query.must(
                TestEsMappingModifier.create_nested_custom_filter(term, must_element)
            )

        original_must_filter = search_query.dsl["bool"]["must_not"]
        search_query.dsl["bool"]["must_not"] = []
        for must_element in original_must_filter:
            search_query.must_not(
                TestEsMappingModifier.create_nested_custom_filter(term, must_element)
            )
