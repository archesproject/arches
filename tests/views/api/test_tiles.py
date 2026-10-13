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
import uuid
from http import HTTPStatus

from tests.base_test import ArchesTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.test.utils import captured_stdout, override_settings
from unittest.mock import patch, MagicMock

from arches.app.views.api import APIBase
from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

# these tests can be run from the command line via
# python manage.py test tests.views.api.test_tiles --settings="tests.test_settings"


class ResourceAPITests(ArchesTestCase):
    graph_fixtures = ["Data_Type_Model"]
    data_type_graphid = "330802c5-95bd-11e8-b7ac-acde48001122"
    non_legacy_resource_instanceid = "eb817333-2010-4cf5-a6e9-88003bfa8b64"
    geojson_nodeid = "38870840-95ed-11e8-b2a9-acde48001122"
    geojson_nodegroupid = "2e3b04c0-95ed-11e8-b68c-acde48001122"
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": "c2a6e3b6-6f27-4b3a-9c1c-2c5e6d8a1f00",
                "geometry": {"type": "Point", "coordinates": [-0.08, 51.5]},
                "properties": {},
            }
        ],
    }

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_users()

        # add resource and tile not sourced from legacy_load_testing_package
        cls.non_legacy_resource = Resource.objects.create(
            pk=uuid.UUID(cls.non_legacy_resource_instanceid),
            graph_id=cls.data_type_graphid,
        )
        models.TileModel.objects.create(
            nodegroup_id=uuid.UUID("e7364d1e-95c4-11e8-9e7c-acde48001122"),
            data={"f08a3057-95c4-11e8-9761-acde48001122": 55},
            resourceinstance=cls.non_legacy_resource,
        )

    def test_node_value_endpoint(self):
        user = User.objects.get(username="admin")
        self.client.force_login(user)
        tile = models.TileModel.objects.filter(
            resourceinstance_id=self.non_legacy_resource_instanceid
        ).first()
        nodeid = "f08a3057-95c4-11e8-9761-acde48001122"
        value = 42
        payload = {
            "tileid": str(tile.tileid),
            "nodeid": nodeid,
            "data": value,
            "operation": "create",
        }
        response = self.client.post(
            reverse("api_node_value"),
            payload,
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["data"][nodeid], value)

    def test_node_value_endpoint_without_tileid(self):
        user = User.objects.get(username="admin")
        self.client.force_login(user)
        nodeid = "f08a3057-95c4-11e8-9761-acde48001122"
        new_value = 99
        payload = {
            "resourceinstanceid": self.non_legacy_resource_instanceid,
            "nodeid": nodeid,
            "data": new_value,
            "operation": "create",
        }
        response = self.client.post(
            reverse("api_node_value"),
            payload,
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["data"][nodeid], new_value)

    def post_geometry_without_tileid(self, resource):
        self.client.force_login(User.objects.get(username="admin"))
        return self.client.post(
            reverse("api_node_value"),
            {
                "resourceinstanceid": str(resource.pk),
                "nodeid": self.geojson_nodeid,
                "data": json.dumps(self.feature_collection),
            },
        )

    def geometry_tiles_of(self, resource):
        return models.TileModel.objects.filter(
            resourceinstance=resource, nodegroup_id=self.geojson_nodegroupid
        )

    def test_node_value_endpoint_fills_tile_without_value(self):
        resource = Resource.objects.create(graph_id=self.data_type_graphid)
        empty_tile = models.TileModel.objects.create(
            nodegroup_id=self.geojson_nodegroupid,
            data={self.geojson_nodeid: None},
            resourceinstance=resource,
        )

        response = self.post_geometry_without_tileid(resource)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(json.loads(response.content)["tileid"], str(empty_tile.pk))
        self.assertEqual(self.geometry_tiles_of(resource).count(), 1)

    def test_node_value_endpoint_adds_tile_beside_one_with_value(self):
        resource = Resource.objects.create(graph_id=self.data_type_graphid)
        tile_with_geometry = models.TileModel.objects.create(
            nodegroup_id=self.geojson_nodegroupid,
            data={self.geojson_nodeid: self.feature_collection},
            resourceinstance=resource,
        )

        response = self.post_geometry_without_tileid(resource)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(
            json.loads(response.content)["tileid"], str(tile_with_geometry.pk)
        )
        self.assertEqual(self.geometry_tiles_of(resource).count(), 2)

    def test_node_value_endpoint_without_permission(self):
        user = User.objects.get(username="anonymous")
        self.client.force_login(user)
        nodeid = "f08a3057-95c4-11e8-9761-acde48001122"
        new_value = 99
        payload = {
            "resourceinstanceid": self.non_legacy_resource_instanceid,
            "nodeid": nodeid,
            "data": new_value,
            "operation": "create",
        }
        response = self.client.post(
            reverse("api_node_value"),
            payload,
        )
        self.assertEqual(response.status_code, 403)

    def test_tiles_endpoint(self):
        user = User.objects.get(username="ben")
        self.client.force_login(user)
        tile = models.TileModel.objects.filter(
            resourceinstance_id=self.non_legacy_resource_instanceid
        ).first()
        response = self.client.get(
            reverse("api_tiles", kwargs={"tileid": str(tile.tileid)})
        )
        self.assertEqual(response.status_code, 200)
