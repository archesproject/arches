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
from arches.app.utils.i18n import LanguageSynchronizer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from guardian.shortcuts import assign_perm
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Term
from arches.app.search.mappings import TERMS_INDEX, CONCEPTS_INDEX, RESOURCES_INDEX

# these tests can be run from the command line via
# python manage.py test tests.search.spatial_search_tests --settings="tests.test_settings"

class SpatialSearchTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        se = SearchEngineFactory().create()
        q = Query(se=se)
        for indexname in [TERMS_INDEX, CONCEPTS_INDEX, RESOURCES_INDEX]:
            q.delete(index=indexname, refresh=True)

        cls.client = Client()
        cls.client.login(username="admin", password="admin")

        LanguageSynchronizer.synchronize_settings_with_db()
        models.ResourceInstance.objects.all().delete()
        with open(os.path.join("tests/fixtures/resource_graphs/Search Test Model.json"), "r") as f:
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

        cls.spatial_filter_geom_resourceid = 'cbb1e9df-5110-4f22-933c-9ccbeb57431b'
        cls.spatial_filter_geom_resource = Resource(graph_id=cls.search_model_graphid, resourceinstanceid=cls.spatial_filter_geom_resourceid)
        cls.spatial_filter_geom_resource.save()
        cls.polygon_feature_id = "2190cb9e-7c57-485c-bf1a-7b6f0389f8b1"
        
        geom_poly = {
            "type": "FeatureCollection",
            "features": [
                {
                    "geometry": {"type": "Polygon", "coordinates": [[
                            [-118.22687435396205, 34.04498354472949],
                            [-118.22673462509519, 34.045024944460636],
                            [-118.22661984555208, 34.044757071199754],
                            [-118.22675979254618, 34.044715607647184],
                            [-118.22687435396205, 34.04498354472949]
                        ]]
                    },
                    "type": "Feature", 
                    "id": cls.polygon_feature_id,
                    "properties": {}
                }
            ]
        }
        poly_tile = Tile.get_blank_tile(cls.search_model_geom_nodeid, resourceid=cls.spatial_filter_geom_resourceid)
        poly_tile.data[cls.search_model_geom_nodeid] = geom_poly
        poly_tile.save()
        cls.point_feature_id = "d41e81ac-4a53-4049-b266-c459b7641bc1"
        geom_point = {
            "type": "FeatureCollection",
            "features": [
                {
                    "geometry": {"type": "Point", "coordinates": [-118.22687435396205, 34.04498354472949]},
                    "type": "Feature", 
                    "id": cls.point_feature_id,
                    "properties": {}
                }
            ]
        }
        point_tile = Tile.get_blank_tile(cls.search_model_geom_nodeid, resourceid=cls.spatial_filter_geom_resourceid)
        point_tile.data[cls.search_model_geom_nodeid] = geom_point
        point_tile.save()
        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        Resource.objects.filter(graph_id=cls.search_model_graphid).delete()
        models.GraphModel.objects.filter(pk=cls.search_model_graphid).delete()
        super().tearDownClass()

    def test_spatial_search_by_featureid_and_resourceid_1(self):
        """
        Test spatial search functionality using featureid and resourceid to retrieve geometries.
        """
        # Simulate spatial filter with featureid and resourceid, not feature collection
        # spatial filter test data
        
        spatial_filter_poly_feature = {
            "featureid": self.polygon_feature_id,
            "resourceid": self.spatial_filter_geom_resourceid,
            "buffer": {
                "width": 25,
                "unit": 'm'
            },
            "inverted": False
        }
        response_json = get_response_json(self.client, spatial_filter=spatial_filter_poly_feature)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 1)

    def test_spatial_search_by_featureid_and_resourceid_2(self):
        """
        Test spatial search functionality using featureid and resourceid to retrieve geometries.
        """
        # Simulate spatial filter with featureid and resourceid, not feature collection
        # spatial filter test data

        spatial_filter_point_feature = {
            "featureid": self.point_feature_id,
            "resourceid": self.spatial_filter_geom_resourceid,
            "buffer": {
                "width": 75,
                "unit": 'm'
            },
            "inverted": False
        }
        response_json = get_response_json(self.client, spatial_filter=spatial_filter_point_feature)
        self.assertEqual(response_json["results"]["hits"]["total"]["value"], 1)


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