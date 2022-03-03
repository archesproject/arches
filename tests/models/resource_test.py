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

from tests import test_settings
from django.contrib.auth.models import User, Group
from django.core import management
from django.urls import reverse
from django.test.client import Client
from guardian.shortcuts import assign_perm, get_perms
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as resource_graph_importer
from arches.app.utils.exceptions import InvalidNodeNameException, MultipleNodesFoundException
from arches.app.utils.index_database import index_resources_by_type
from tests.base_test import ArchesTestCase


# these tests can be run from the command line via
# python manage.py test tests/models/resource_test.py --pattern="*.py" --settings="tests.test_settings"


class ResourceTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        models.ResourceInstance.objects.all().delete()

        cls.client = Client()
        cls.client.login(username="admin", password="admin")

        with open(os.path.join("tests/fixtures/resource_graphs/Resource Test Model.json"), "rU") as f:
            archesfile = JSONDeserializer().deserialize(f)
        resource_graph_importer(archesfile["graph"])

        cls.search_model_graphid = "c9b37a14-17b3-11eb-a708-acde48001122"
        cls.search_model_cultural_period_nodeid = "c9b3882e-17b3-11eb-a708-acde48001122"
        cls.search_model_creation_date_nodeid = "c9b38568-17b3-11eb-a708-acde48001122"
        cls.search_model_destruction_date_nodeid = "c9b3828e-17b3-11eb-a708-acde48001122"
        cls.search_model_name_nodeid = "c9b37b7c-17b3-11eb-a708-acde48001122"
        cls.search_model_sensitive_info_nodeid = "c9b38aea-17b3-11eb-a708-acde48001122"
        cls.search_model_geom_nodeid = "c9b37f96-17b3-11eb-a708-acde48001122"

        cls.user = User.objects.create_user("test", "test@archesproject.org", "password")
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

        # Add resource with Name, Cultural Period, Creation Date and Geometry
        cls.test_resource = Resource(graph_id=cls.search_model_graphid)

        # Add Name
        tile = Tile(data={cls.search_model_name_nodeid: "Test Name 1"}, nodegroup_id=cls.search_model_name_nodeid)
        cls.test_resource.tiles.append(tile)

        # Add Cultural Period
        tile = Tile(data={cls.search_model_cultural_period_nodeid: [valueid]}, nodegroup_id=cls.search_model_cultural_period_nodeid)
        cls.test_resource.tiles.append(tile)

        # Add Creation Date
        tile = Tile(data={cls.search_model_creation_date_nodeid: "1941-01-01"}, nodegroup_id=cls.search_model_creation_date_nodeid)
        cls.test_resource.tiles.append(tile)

        # Add Gometry
        cls.geom = {
            "type": "FeatureCollection",
            "features": [{"geometry": {"type": "Point", "coordinates": [0, 0]}, "type": "Feature", "properties": {}}],
        }
        tile = Tile(data={cls.search_model_geom_nodeid: cls.geom}, nodegroup_id=cls.search_model_geom_nodeid)
        cls.test_resource.tiles.append(tile)

        cls.test_resource.save()

        # add delay to allow for indexes to be updated
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        models.GraphModel.objects.filter(pk=cls.search_model_graphid).delete()

    def test_get_node_value_string(self):
        """
        Query a string value
        """
        node_name = "Name"
        result = self.test_resource.get_node_values(node_name)
        self.assertEqual("Test Name 1", result[0])

    def test_get_node_value_date(self):
        """
        Query a date value
        """
        node_name = "Creation Date"
        result = self.test_resource.get_node_values(node_name)
        self.assertEqual("1941-01-01", result[0])

    def test_get_node_value_concept(self):
        """
        Query a concept value
        """
        node_name = "Cultural Period Concept"
        result = self.test_resource.get_node_values(node_name)
        self.assertEqual("Mock concept", result[0])

    def test_get_not_existing_value_from_concept(self):
        """
        Query a concept node without a value
        """

        test_resource_no_value = Resource(graph_id=self.search_model_graphid)
        tile = Tile(data={self.search_model_cultural_period_nodeid: ""}, nodegroup_id=self.search_model_cultural_period_nodeid)
        test_resource_no_value.tiles.append(tile)
        test_resource_no_value.save()

        node_name = "Cultural Period Concept"
        result = test_resource_no_value.get_node_values(node_name)
        self.assertEqual(None, result[0])
        test_resource_no_value.delete()

    def test_get_value_from_not_existing_concept(self):
        """
        Query a concept value that does not exist
        """
        node_name = "Not Existing Concept"
        with self.assertRaises(InvalidNodeNameException):
            self.test_resource.get_node_values(node_name)

    def test_get_duplicate_node_value_concept(self):
        """
        Query a concept value on a node that exists twice
        """
        node_name = "Duplicate Node Concept"
        with self.assertRaises(MultipleNodesFoundException):
            self.test_resource.get_node_values(node_name)

    def test_get_node_value_geometry(self):
        """
        Query a geometry value
        """
        node_name = "Geometry"
        result = self.test_resource.get_node_values(node_name)
        self.assertEqual(self.geom, result[0])

    def test_reindex_by_resource_type(self):
        """
        Test re-index a resource by type
        """

        time.sleep(1)
        result = index_resources_by_type([self.search_model_graphid], clear_index=True, batch_size=4000)

        self.assertEqual(result, "Passed")

    def test_creator_has_permissions(self):
        """
        Test user that created instance has full permissions
        """

        user = User.objects.create_user(username="sam", email="sam@samsclub.com", password="Test12345!")
        user.save()
        group = Group.objects.get(name="Resource Editor")
        group.user_set.add(user)
        test_resource = Resource(graph_id=self.search_model_graphid)
        test_resource.save(user=user)
        perms = set(get_perms(user, test_resource))
        self.assertEqual(perms, {"view_resourceinstance", "change_resourceinstance", "delete_resourceinstance"})
