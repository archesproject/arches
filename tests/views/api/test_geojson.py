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

from django.contrib.auth.models import User
from django.urls import reverse

from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.permissions.arches_default_allow import (
    ArchesDefaultAllowPermissionFramework,
)
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineFactory
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.views.api.test_geojson --settings="tests.test_settings"


class GeoJSONAPITests(ArchesTestCase):
    graph_fixtures = ["Data_Type_Model"]
    data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
    geometry_nodeid = "38870840-95ed-11e8-b2a9-acde48001122"
    geometry_nodegroupid = "2e3b04c0-95ed-11e8-b68c-acde48001122"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_users()
        cls.user = User.objects.get(username="ben")
        cls.accessible_resource, cls.accessible_featureid = cls.create_mapped_resource(
            "Accessible site"
        )
        cls.restricted_resource, _featureid = cls.create_mapped_resource(
            "Restricted site"
        )

    @classmethod
    def create_mapped_resource(cls, name):
        featureid = str(uuid.uuid4())
        # A plain model save keeps the name: Resource.save recomputes descriptors.
        resource = models.ResourceInstance.objects.create(
            graph_id=cls.data_type_graphid, name=name
        )
        models.TileModel.objects.create(
            resourceinstance=resource,
            nodegroup_id=cls.geometry_nodegroupid,
            data={
                cls.geometry_nodeid: {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "id": featureid,
                            "type": "Feature",
                            "geometry": {"type": "Point", "coordinates": [0, 51]},
                            "properties": {},
                        }
                    ],
                }
            },
        )
        return resource, featureid

    def setUp(self):
        self.client.force_login(self.user)

    def get_features(self, **params):
        response = self.client.get(
            reverse("geojson"),
            {"nodeid": self.geometry_nodeid, "include_primary_name": "true", **params},
        )
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content)["features"]

    def features_by_resourceid(self, features):
        return {
            feature["properties"]["resourceinstanceid"]: feature for feature in features
        }

    def test_returns_features_with_featureid_and_name_without_resourceid(self):
        features = self.features_by_resourceid(self.get_features())

        accessible_feature = features[str(self.accessible_resource.pk)]
        self.assertEqual(
            accessible_feature["properties"]["featureid"], self.accessible_featureid
        )
        self.assertEqual(
            accessible_feature["properties"]["primary_name"], "Accessible site"
        )

    def test_omits_resources_the_user_cannot_access(self):
        ArchesDefaultAllowPermissionFramework().assign_perm(
            "no_access_to_resourceinstance", self.user, self.restricted_resource
        )
        Resource.objects.get(pk=self.restricted_resource.pk).index()
        SearchEngineFactory().create().refresh(index=RESOURCES_INDEX)

        features = self.features_by_resourceid(
            self.get_features(
                resourceid=f"{self.accessible_resource.pk},{self.restricted_resource.pk}"
            )
        )

        self.assertIn(str(self.accessible_resource.pk), features)
        self.assertNotIn(str(self.restricted_resource.pk), features)
