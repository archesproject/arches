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
from unittest.mock import patch

from django.contrib.auth.models import User, Group
from django.db import connection
from django.urls import reverse
from django.test.client import Client
from django.test.utils import CaptureQueriesContext
from guardian.shortcuts import assign_perm, get_perms
from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.exceptions import (
    InvalidNodeNameException,
    MultipleNodesFoundException,
)
from arches.app.utils.index_database import (
    index_resources_by_type,
    index_resources_using_singleprocessing,
)
from arches.test.utils import sync_overridden_test_settings_to_arches
from tests.base_test import ArchesTestCase

from django.test import override_settings

# these tests can be run from the command line via
# python manage.py test tests.models.resource_test --settings="tests.test_settings"


class ResourceTests(ArchesTestCase):
    graph_fixtures = ["Resource Test Model"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.client = Client()
        cls.client.login(username="admin", password="admin")

        cls.search_model_graphid = uuid.UUID("c9b37a14-17b3-11eb-a708-acde48001122")
        cls.search_model_cultural_period_nodeid = "c9b3882e-17b3-11eb-a708-acde48001122"
        cls.search_model_creation_date_nodeid = "c9b38568-17b3-11eb-a708-acde48001122"
        cls.search_model_destruction_date_nodeid = (
            "c9b3828e-17b3-11eb-a708-acde48001122"
        )
        cls.search_model_name_nodeid = "c9b37b7c-17b3-11eb-a708-acde48001122"
        cls.search_model_sensitive_info_nodeid = "c9b38aea-17b3-11eb-a708-acde48001122"
        cls.search_model_geom_nodeid = "c9b37f96-17b3-11eb-a708-acde48001122"

        cls.user = User.objects.create_user(
            "test", "test@archesproject.org", "password"
        )
        cls.user.groups.add(Group.objects.get(name="Guest"))

        graph = Graph.objects.get(pk=cls.search_model_graphid)
        graph.publish(user=cls.user)

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

        # Add resource with Name, Cultural Period, Creation Date and Geometry
        cls.test_resource = Resource(graph_id=cls.search_model_graphid)

        # Add Name
        tile = Tile(
            data={
                cls.search_model_name_nodeid: {
                    "en": {"value": "Test Name 1"},
                    "es": {"value": "Prueba Nombre 1"},
                }
            },
            nodegroup_id=cls.search_model_name_nodeid,
        )
        cls.test_resource.tiles.append(tile)

        # Add Cultural Period
        tile = Tile(
            data={cls.search_model_cultural_period_nodeid: [valueid]},
            nodegroup_id=cls.search_model_cultural_period_nodeid,
        )
        cls.test_resource.tiles.append(tile)

        # Add Creation Date
        tile = Tile(
            data={cls.search_model_creation_date_nodeid: "1941-01-01"},
            nodegroup_id=cls.search_model_creation_date_nodeid,
        )
        cls.test_resource.tiles.append(tile)

        # Add Geometry
        cls.geom = {
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
            data={cls.search_model_geom_nodeid: cls.geom},
            nodegroup_id=cls.search_model_geom_nodeid,
        )
        cls.test_resource.tiles.append(tile)

        cls.test_resource.save()

        # add delay to allow for indexes to be updated
        time.sleep(1)

    def test_get_node_value_string(self):
        """
        Query a string value
        """
        node_name = "Name"
        result = self.test_resource.get_node_values(node_name)
        self.assertEqual("Test Name 1", result[0]["en"]["value"])
        self.assertEqual("Prueba Nombre 1", result[0]["es"]["value"])

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
        tile = Tile(
            data={self.search_model_cultural_period_nodeid: ""},
            nodegroup_id=self.search_model_cultural_period_nodeid,
        )
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
        result = index_resources_by_type(
            [self.search_model_graphid], clear_index=True, batch_size=4000
        )

        self.assertEqual(result, "Passed")

    @override_settings(
        ELASTICSEARCH_CUSTOM_INDEXES=[
            {
                "module": "arches.app.search.base_index.BaseIndex",
                "name": "mock",
                "should_update_asynchronously": True,
            }
        ]
    )
    @patch("arches.app.search.base_index.BaseIndex.delete_resources")
    def test_delete_acts_on_custom_indices(self, mock):
        other_resource = Resource(pk=uuid.uuid4())
        with sync_overridden_test_settings_to_arches():
            self.test_resource.delete_index(other_resource.pk)
        self.assertIn(str(other_resource.pk), str(mock._mock_call_args))

    def test_publication_restored_on_save(self):
        """
        If a resource lacks a graph publication, it is restored by a call to save().
        """
        # Hack out the graph publication (bypass the guard in save())
        models.ResourceInstance.objects.filter(pk=self.test_resource.pk).update(
            graph_publication=None
        )
        self.test_resource.refresh_from_db()
        # Ensure test setup is good
        self.assertIsNone(self.test_resource.graph_publication)

        # update_or_create() delegates to save()
        obj, created = models.ResourceInstance.objects.filter(
            pk=self.test_resource.pk
        ).update_or_create(
            pk=self.test_resource.pk,
            graph=self.test_resource.graph,
        )
        obj.refresh_from_db()  # give test opportunity to fail on Django 4.2+

        self.assertIsNotNone(obj.graph_publication)

    def test_creator_has_permissions(self):
        """
        Test user that created instance has full permissions
        """

        user = User.objects.create_user(
            username="sam", email="sam@samsclub.com", password="Test12345!"
        )
        user.save()
        group = Group.objects.get(name="Resource Editor")
        group.user_set.add(user)
        test_resource = Resource(graph_id=self.search_model_graphid)
        test_resource.save(user=user)
        perms = set(get_perms(user, test_resource))
        self.assertNotEqual(
            perms,
            {
                "view_resourceinstance",
                "change_resourceinstance",
                "delete_resourceinstance",
            },
        )
        self.assertEqual(test_resource.principaluser, user)

    def test_provisional_user_can_delete_own_resource(self):
        """
        Test provisional user can delete resource instance they created
        """

        user = User.objects.create_user(
            username="sam", email="sam@samsclub.com", password="Test12345!"
        )
        user.save()
        group = Group.objects.get(name="Resource Editor")
        group.user_set.add(user)
        test_resource = Resource(graph_id=self.search_model_graphid)
        test_resource.save(user=user)

        other_user = User.objects.create_user(
            username="fred", email="fred@samsclub.com", password="Test12345!"
        )
        other_user.save()
        group = Group.objects.get(name="Resource Editor")
        group.user_set.add(other_user)

        with self.subTest(user="can't delete"):
            result = test_resource.delete(user=other_user)
            self.assertFalse(result)

        with self.subTest(user="can delete"):
            result = test_resource.delete(user=user)
            self.assertTrue(result)

        with self.subTest(user="can't delete"):
            test_resource = Resource(graph_id=self.search_model_graphid)
            test_resource.save(user=user)
            edit_log_entry = models.EditLog.objects.get(
                resourceinstanceid=test_resource.pk, edittype="create"
            )
            edit_log_entry.userid = ""
            edit_log_entry.save()
            result = test_resource.delete(user=user)
            self.assertFalse(result)

    def test_calculate_descriptors(self):
        """
        this is a test for the ticket #12272
        Test that descriptors are calculated correctly when
        saving a resource instance with tiles appended directly
        """

        graph = Graph.new(name="Descriptor Test Graph", is_resource=True)
        node_group = models.NodeGroup.objects.create()
        string_node = models.Node.objects.create(
            graph=graph,
            nodegroup=node_group,
            name="String Node",
            datatype="string",
            istopnode=False,
        )
        graph.add_node(string_node)

        edge = models.Edge.objects.create(
            graph=graph, domainnode=graph.root, rangenode=string_node
        )
        graph.add_edge(edge)
        graph.add_card(
            models.CardModel(
                graph=graph,
                nodegroup=node_group,
                description="Test Card",
            )
        )

        # Configure the primary descriptor to use the string node
        models.FunctionXGraph.objects.create(
            graph=graph,
            function_id="60000000-0000-0000-0000-000000000001",
            config={
                "descriptor_types": {
                    "name": {
                        "nodegroup_id": str(node_group.nodegroupid),
                        "string_template": "<String Node>",
                    },
                    "map_popup": {
                        "nodegroup_id": str(node_group.nodegroupid),
                        "string_template": "<String Node>",
                    },
                    "description": {
                        "nodegroup_id": str(node_group.nodegroupid),
                        "string_template": "<String Node>",
                    },
                },
            },
        )
        user = User.objects.get(username="admin")
        graph.save(validate=False)
        # Publish the graph to make it available for resources
        graph.publish(user=user)

        resource = Resource(graph=graph)
        tile = Tile(
            nodegroup=node_group,
            resourceinstance=resource,
            data={
                str(string_node.pk): {
                    "en": {"value": "test value", "direction": "ltr"},
                }
            },
            sortorder=0,
        )
        resource.tiles.append(tile)
        resource.save()

        for display_type in (
            resource.displayname,
            resource.displaydescription,
            resource.map_popup,
        ):
            with self.subTest(display_type=display_type):
                self.assertEqual(display_type(), "test value")

    def test_recalculate_descriptors_prefetch_related_objects(self):
        r1 = Resource(graph_id=self.search_model_graphid)
        r2 = Resource(graph_id=self.search_model_graphid)
        r1_tile = Tile(
            data={self.search_model_creation_date_nodeid: "1941-01-01"},
            nodegroup_id=self.search_model_creation_date_nodeid,
        )
        r1.tiles.append(r1_tile)
        r2_tile = Tile(
            data={self.search_model_creation_date_nodeid: "1941-01-01"},
            nodegroup_id=self.search_model_creation_date_nodeid,
        )
        r2.tiles.append(r2_tile)
        r1.save(index=False)
        r2.save(index=False)

        # Ensure we start from scratch
        r1.descriptor_function = None
        r2.descriptor_function = None

        for test_name, resources in (
            ("array", [r1, r2]),
            ("queryset", Resource.objects.filter(pk__in=[r1.pk, r2.pk])),
        ):
            with (
                self.subTest(iterable=test_name),
                CaptureQueriesContext(connection) as queries,
            ):
                index_resources_using_singleprocessing(
                    resources, recalculate_descriptors=True, quiet=True
                )

                function_x_graph_selects = [
                    q
                    for q in queries
                    if q["sql"].startswith('SELECT "functions_x_graphs"."id"')
                ]
                self.assertEqual(len(function_x_graph_selects), 1)

                tile_selects = [
                    q for q in queries if q["sql"].startswith('SELECT "tiles"."tileid"')
                ]
                self.assertEqual(len(tile_selects), 1)

    def test_self_referring_resource_instance_descriptor(self):
        # Create a nodegroup with a string node and a resource-instance node.
        graph = Graph.new(name="Self-referring descriptor test", is_resource=True)
        node_group = models.NodeGroup.objects.create()
        string_node = models.Node.objects.create(
            graph=graph,
            nodegroup=node_group,
            name="String Node",
            datatype="string",
            istopnode=False,
        )
        resource_instance_node = models.Node.objects.create(
            graph=graph,
            nodegroup=node_group,
            name="Resource Node",
            datatype="resource-instance",
            istopnode=False,
        )

        # Configure the primary descriptor to use the string node
        models.FunctionXGraph.objects.create(
            graph=graph,
            function_id="60000000-0000-0000-0000-000000000001",
            config={
                "descriptor_types": {
                    "name": {
                        "nodegroup_id": str(node_group.nodegroupid),
                        # The bug report did not have <Resource Node> in the descriptor
                        # template, but including it here to allow the assertion to fail
                        "string_template": "<String Node> <Resource Node>",
                    },
                    "map_popup": {
                        "nodegroup_id": None,
                        "string_template": "",
                    },
                    "description": {
                        "nodegroup_id": None,
                        "string_template": "",
                    },
                },
            },
        )

        # Create a tile that references itself
        resource = models.ResourceInstance.objects.create(graph=graph)
        tile = models.TileModel.objects.create(
            nodegroup=node_group,
            resourceinstance=resource,
            data={
                str(string_node.pk): {
                    "en": {"value": "test value", "direction": "ltr"},
                },
                str(resource_instance_node.pk): {
                    "resourceId": str(resource.pk),
                    "ontologyProperty": "",
                    "inverseOntologyProperty": "",
                },
            },
            sortorder=0,
        )
        models.ResourceXResource.objects.create(
            nodeid=resource_instance_node,
            resourceinstanceidfrom=resource,
            resourceinstanceidto=resource,
            tileid=tile,
        )
        r = Resource.objects.get(pk=resource.pk)
        r.save_descriptors()

        # Until 7.4, a RecursionError was caught after this value was repeated many times.
        self.assertEqual(r.displayname(), "test value ")

    @patch("django.contrib.auth.models.User.has_perm")
    def test_user_can_see_edit_history_if_resource_editor(self, mock_has_perm):
        user = User.objects.create_user(
            username="john", email="john@archesproject.org", password="Test12345!"
        )
        user.save()
        group = Group.objects.get(name="Resource Editor")
        group.user_set.add(user)

        self.client.login(username="john", password="Test12345!")
        self.client.get(reverse("resource_edit_log", args=[self.test_resource.pk]))
        mock_has_perm.assert_any_call(
            "read_nodegroup", self.test_resource.tiles[0].nodegroup
        )
