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

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os
import json
import time
from tests.base_test import ArchesTestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.test.client import Client
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from guardian.shortcuts import assign_perm
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Term
from arches.app.search.mappings import TERMS_INDEX, CONCEPTS_INDEX, RESOURCE_RELATIONS_INDEX, RESOURCES_INDEX

# these tests can be run from the command line via
# python manage.py test tests/views/search_tests.py --pattern="*.py" --settings="tests.test_settings"


class SearchTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        se = SearchEngineFactory().create()
        q = Query(se=se)
        for indexname in [TERMS_INDEX, CONCEPTS_INDEX, RESOURCE_RELATIONS_INDEX, RESOURCES_INDEX]:
            q.delete(index=indexname, refresh=True)

        cls.client = Client()
        cls.client.login(username="admin", password="admin")

        models.ResourceInstance.objects.all().delete()
        with open(os.path.join("tests/fixtures/resource_graphs/Search Test Model.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        cls.search_model_graphid = "d291a445-fa5f-11e6-afa8-14109fd34195"
        cls.search_model_cultural_period_nodeid = "7a182580-fa60-11e6-96d1-14109fd34195"
        cls.search_model_creation_date_nodeid = "1c1d05f5-fa60-11e6-887f-14109fd34195"
        cls.search_model_destruction_date_nodeid = "e771b8a1-65fe-11e7-9163-14109fd34195"
        cls.search_model_name_nodeid = "2fe14de3-fa61-11e6-897b-14109fd34195"
        cls.search_model_sensitive_info_nodeid = "57446fae-65ff-11e7-b63a-14109fd34195"
        cls.search_model_geom_nodeid = "3ebc6785-fa61-11e6-8c85-14109fd34195"

        cls.user = User.objects.create_user("unpriviliged_user", "unpriviliged_user@archesproject.org", "test")
        cls.user.groups.add(Group.objects.get(name="Guest"))

        nodegroup = models.NodeGroup.objects.get(pk=cls.search_model_destruction_date_nodeid)
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
                        {"value": "Mock concept", "language": "en-US", "category": "label", "type": "prefLabel", "id": "", "conceptid": ""},
                        {"value": "1950", "language": "en-US", "category": "note", "type": "min_year", "id": "", "conceptid": ""},
                        {"value": "1980", "language": "en-US", "category": "note", "type": "max_year", "id": "", "conceptid": ""},
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
            reverse("concept", kwargs={"conceptid": "00000000-0000-0000-0000-000000000001"}), post_data, content_type
        )
        response_json = json.loads(response.content)
        valueid = response_json["subconcepts"][0]["values"][0]["id"]
        cls.conceptid = response_json["subconcepts"][0]["id"]

        # add resource instance with only a cultural period defined
        cls.cultural_period_resource = Resource(graph_id=cls.search_model_graphid)
        tile = Tile(data={cls.search_model_cultural_period_nodeid: [valueid]}, nodegroup_id=cls.search_model_cultural_period_nodeid)
        cls.cultural_period_resource.tiles.append(tile)
        cls.cultural_period_resource.save()

        # add resource instance with a creation and destruction date defined
        cls.date_resource = Resource(graph_id=cls.search_model_graphid)
        tile = Tile(data={cls.search_model_creation_date_nodeid: "1941-01-01"}, nodegroup_id=cls.search_model_creation_date_nodeid)
        cls.date_resource.tiles.append(tile)
        tile = Tile(data={cls.search_model_destruction_date_nodeid: "1948-01-01"}, nodegroup_id=cls.search_model_destruction_date_nodeid)
        cls.date_resource.tiles.append(tile)
        tile = Tile(data={cls.search_model_name_nodeid: "testing 123"}, nodegroup_id=cls.search_model_name_nodeid)
        cls.date_resource.tiles.append(tile)
        cls.date_resource.save()

        # add resource instance with a creation date and a cultural period defined
        cls.date_and_cultural_period_resource = Resource(graph_id=cls.search_model_graphid)
        tile = Tile(data={cls.search_model_creation_date_nodeid: "1942-01-01"}, nodegroup_id=cls.search_model_creation_date_nodeid)
        cls.date_and_cultural_period_resource.tiles.append(tile)
        tile = Tile(data={cls.search_model_cultural_period_nodeid: [valueid]}, nodegroup_id=cls.search_model_cultural_period_nodeid)
        cls.date_and_cultural_period_resource.tiles.append(tile)
        cls.date_and_cultural_period_resource.save()

        # add resource instance with with no dates or periods defined
        cls.name_resource = Resource(graph_id=cls.search_model_graphid)
        tile = Tile(data={cls.search_model_name_nodeid: "some test name"}, nodegroup_id=cls.search_model_name_nodeid)
        cls.name_resource.tiles.append(tile)
        geom = {
            "type": "FeatureCollection",
            "features": [{"geometry": {"type": "Point", "coordinates": [0, 0]}, "type": "Feature", "properties": {}}],
        }
        tile = Tile(data={cls.search_model_geom_nodeid: geom}, nodegroup_id=cls.search_model_geom_nodeid)
        cls.name_resource.tiles.append(tile)
        cls.name_resource.save()

        # add delay to allow for indexes to be updated
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        models.GraphModel.objects.filter(pk=cls.search_model_graphid).delete()

    def test_temporal_only_search_1(self):
        """
        Search for resources that fall between 1940 and 1960

        """

        temporal_filter = {"fromDate": "1940-01-01", "toDate": "1960-01-01", "dateNodeId": "", "inverted": False}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 3)
        self.assertCountEqual(
            extract_pks(response_json),
            [str(self.cultural_period_resource.pk), str(self.date_resource.pk), str(self.date_and_cultural_period_resource.pk)],
        )

    def test_temporal_only_search_2(self):
        """
        Search for resources that DON'T fall between 1940 and 1960

        """

        temporal_filter = {"fromDate": "1940-01-01", "toDate": "1960-01-01", "dateNodeId": "", "inverted": True}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json), [str(self.cultural_period_resource.pk), str(self.date_and_cultural_period_resource.pk)]
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
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(extract_pks(response_json), [str(self.date_resource.pk), str(self.date_and_cultural_period_resource.pk)])

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
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 0)

    def test_temporal_only_search_5(self):
        """
        Search for resources that fall between 1950 and 1960 (the cultural period resource)

        """

        temporal_filter = {"fromDate": "1950-01-01", "toDate": "1960-01-01", "dateNodeId": "", "inverted": False}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json), [str(self.cultural_period_resource.pk), str(self.date_and_cultural_period_resource.pk)]
        )

    def test_temporal_only_search_6(self):
        """
        Search for resources that DON'T fall between 1950 and 1960 (the cultural period resource)

        """

        temporal_filter = {"fromDate": "1950-01-01", "toDate": "1960-01-01", "dateNodeId": "", "inverted": True}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 3)
        self.assertCountEqual(
            extract_pks(response_json),
            [str(self.cultural_period_resource.pk), str(self.date_resource.pk), str(self.date_and_cultural_period_resource.pk)],
        )

    def test_temporal_only_search_7(self):
        """
        Search for resources that fall between 1990 and 2000

        """

        temporal_filter = {"fromDate": "1990-01-01", "toDate": "2000-01-01", "dateNodeId": "", "inverted": False}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 0)

    def test_temporal_only_search_8(self):
        """
        Search for resources that DON'T fall between 1990 and 2000

        """

        temporal_filter = {"fromDate": "1990-01-01", "toDate": "2000-01-01", "dateNodeId": "", "inverted": True}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 3)
        self.assertCountEqual(
            extract_pks(response_json),
            [str(self.cultural_period_resource.pk), str(self.date_resource.pk), str(self.date_and_cultural_period_resource.pk)],
        )

    def test_temporal_only_search_9(self):
        """
        Search for resources that are greater then 1940

        """

        temporal_filter = {"fromDate": "1940-01-01", "toDate": "", "dateNodeId": "", "inverted": False}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 3)
        self.assertCountEqual(
            extract_pks(response_json),
            [str(self.cultural_period_resource.pk), str(self.date_resource.pk), str(self.date_and_cultural_period_resource.pk)],
        )

    def test_temporal_only_search_10(self):
        """
        Search for resources that AREN'T greater then 1940

        """

        temporal_filter = {"fromDate": "1940-01-01", "toDate": "", "dateNodeId": "", "inverted": True}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 0)

    def test_temporal_only_search_11(self):
        """
        Search for resources that AREN'T greater then 1950

        """

        temporal_filter = {"fromDate": "1950-01-01", "toDate": "", "dateNodeId": "", "inverted": True}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(extract_pks(response_json), [str(self.date_resource.pk), str(self.date_and_cultural_period_resource.pk)])

    def test_temporal_and_term_search_1(self):
        """
        Search for resources that fall between 1940 and 1960 and have the string "test" in them

        """

        temporal_filter = {"fromDate": "1940-01-01", "toDate": "1960-01-01", "dateNodeId": "", "inverted": False}
        term_filter = [
            {"type": "string", "context": "", "context_label": "", "id": "test", "text": "test", "value": "test", "inverted": False}
        ]
        response_json = get_response_json(self.client, temporal_filter=temporal_filter, term_filter=term_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 1)
        self.assertCountEqual(extract_pks(response_json), [str(self.date_resource.pk)])

    def test_temporal_and_term_search_2(self):
        """
        Search for resources that DON'T fall between 1940 and 1960 and have the string "test" in them

        """

        temporal_filter = {"fromDate": "1940-01-01", "toDate": "1960-01-01", "dateNodeId": "", "inverted": True}
        term_filter = [
            {"type": "string", "context": "", "context_label": "", "id": "test", "text": "test", "value": "test", "inverted": False}
        ]
        response_json = get_response_json(self.client, temporal_filter=temporal_filter, term_filter=term_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 0)

    def test_term_search_1(self):
        """
        Search for resources that have the string "test" in them as a "string" search

        """

        term_filter = [
            {"type": "string", "context": "", "context_label": "", "id": "test", "text": "test", "value": "test", "inverted": False}
        ]
        response_json = get_response_json(self.client, term_filter=term_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(extract_pks(response_json), [str(self.date_resource.pk), str(self.name_resource.pk)])

    def test_term_search_2(self):
        """
        Search for resources that DON'T have the string "test" in them as a "string" search

        """

        term_filter = [
            {"type": "string", "context": "", "context_label": "", "id": "test", "text": "test", "value": "test", "inverted": True}
        ]
        response_json = get_response_json(self.client, term_filter=term_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json), [str(self.date_and_cultural_period_resource.pk), str(self.cultural_period_resource.pk)]
        )

    def test_term_search_3(self):
        """
        Search for resources that have the string "test" in them as a "term" search

        """

        term_filter = [
            {"type": "term", "context": "", "context_label": "", "id": "test", "text": "test", "value": "test", "inverted": False}
        ]
        response_json = get_response_json(self.client, term_filter=term_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 1)
        self.assertCountEqual(extract_pks(response_json), [str(self.name_resource.pk)])

    def test_term_search_4(self):
        """
        Search for resources that DON'T have the string "test" in them as a "term" search

        """

        term_filter = [
            {"type": "term", "context": "", "context_label": "", "id": "test", "text": "test", "value": "test", "inverted": True}
        ]
        response_json = get_response_json(self.client, term_filter=term_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 3)
        self.assertCountEqual(
            extract_pks(response_json),
            [str(self.date_resource.pk), str(self.date_and_cultural_period_resource.pk), str(self.cultural_period_resource.pk)],
        )

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
        response_json = get_response_json(self.client, term_filter=term_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json), [str(self.date_and_cultural_period_resource.pk), str(self.cultural_period_resource.pk)]
        )

    def test_concept_search_2(self):
        """
        Search for resources that DON'T have the concept "Mock concept" in them as a "concept" search

        """

        term_filter = [
            {"type": "concept", "context": "", "context_label": "", "id": "test", "text": "test", "value": self.conceptid, "inverted": True}
        ]
        response_json = get_response_json(self.client, term_filter=term_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(extract_pks(response_json), [str(self.name_resource.pk), str(self.date_resource.pk)])

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
                    "properties": {"inverted": False, "buffer": {"width": "100", "unit": "ft"}},
                    "geometry": {"coordinates": [[[-1, -1], [-1, 1], [1, 1], [1, -1], [-1, -1]]], "type": "Polygon"},
                }
            ],
        }
        response_json = get_response_json(self.client, spatial_filter=spatial_filter)
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
                    "properties": {"inverted": True, "buffer": {"width": "100", "unit": "ft"}},
                    "geometry": {"coordinates": [[[-1, -1], [-1, 1], [1, 1], [1, -1], [-1, -1]]], "type": "Polygon"},
                }
            ],
        }
        response_json = get_response_json(self.client, spatial_filter=spatial_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 0)
        # self.assertCountEqual(extract_pks(response_json), [str(self.name_resource.pk)])

    #
    # -- ADD TESTS THAT INCLUDE PERMISSIONS REQUIREMENTS -- #
    #
    def test_temporal_and_permission_search_1(self):
        """
        Search for resources that fall between 1945 and 1960 with user permissions

        """

        temporal_filter = {"fromDate": "1945-01-01", "toDate": "1960-01-01", "dateNodeId": "", "inverted": False}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(
            extract_pks(response_json), [str(self.cultural_period_resource.pk), str(self.date_and_cultural_period_resource.pk)]
        )

    def test_temporal_and_permission_search_2(self):
        """
        Search for resources that fall between 1940 and 1945 with user permissions

        """

        temporal_filter = {"fromDate": "1940-01-01", "toDate": "1945-01-01", "dateNodeId": "", "inverted": False}
        response_json = get_response_json(self.client, temporal_filter=temporal_filter)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 2)
        self.assertCountEqual(extract_pks(response_json), [str(self.date_resource.pk), str(self.date_and_cultural_period_resource.pk)])


def extract_pks(response_json):
    return [result["_source"]["resourceinstanceid"] for result in response_json["results"]["hits"]["hits"]]


def get_response_json(client, temporal_filter=None, term_filter=None, spatial_filter=None):
    query = {}
    if temporal_filter is not None:
        query["time-filter"] = JSONSerializer().serialize(temporal_filter)
    if term_filter is not None:
        query["term-filter"] = JSONSerializer().serialize(term_filter)
    if spatial_filter is not None:
        query["map-filter"] = JSONSerializer().serialize(spatial_filter)
    resource_reviewer_group = Group.objects.get(name="Resource Reviewer")
    test_user = User.objects.get(username="unpriviliged_user")
    test_user.groups.add(resource_reviewer_group)
    client.login(username="unpriviliged_user", password="test")
    response = client.get("/search/resources", query)
    response_json = json.loads(response.content)
    return response_json
