"""
Tests for arches.app.functions.multicard_resource_descriptor
"""

import uuid

from django.db import connection
from django.test.utils import CaptureQueriesContext

from arches.app.functions.multicard_resource_descriptor import (
    MulticardResourceDescriptor,
)
from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.models.function_tests --settings="tests.test_settings"


class MulticardResourceDescriptorTests(ArchesTestCase):
    """
    Tests for MulticardResourceDescriptor.get_primary_descriptor_from_nodes.
    Covers correctness and node caching.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Ensure the class-level node cache does not carry state from prior runs.
        MulticardResourceDescriptor._node_cache.clear()

        cls.graph = Graph.objects.create_graph(
            name="Multicard Descriptor Unit Test", is_resource=True
        )
        cls.node_group = models.NodeGroup.objects.create()
        cls.string_node = models.Node.objects.create(
            graph=cls.graph,
            nodegroup=cls.node_group,
            alias="test_place_name",
            name="Test Place Name",
            datatype="string",
            istopnode=False,
        )

        user = cls.test_users["admin"]
        cls.graph.publish(user=user)

        # A resource + tile persisted to the DB, used by the DB-fallback test.
        cls.saved_resource = Resource(graph_id=cls.graph.pk)
        cls.saved_resource.save(index=False)
        cls.saved_tile = models.TileModel.objects.create(
            resourceinstance=cls.saved_resource,
            nodegroup=cls.node_group,
            data={
                str(cls.string_node.pk): {
                    "en": {"value": "Pyramids of Giza", "direction": "ltr"}
                }
            },
        )

        cls.descriptor_config = {
            "nodegroup_id": str(cls.node_group.nodegroupid),
            "string_template": "<test_place_name>",
        }

    def setUp(self):
        MulticardResourceDescriptor._node_cache.clear()

    def _make_resource(self):
        resource = Resource()
        resource.resourceinstanceid = uuid.uuid4()
        resource.graph_id = self.graph.pk
        resource.descriptors = {}
        resource.name = {}
        return resource

    def _make_tile(self, resource, string_value):
        return models.TileModel(
            tileid=uuid.uuid4(),
            resourceinstance_id=resource.resourceinstanceid,
            nodegroup_id=self.node_group.nodegroupid,
            data={
                str(self.string_node.pk): {
                    "en": {"value": string_value, "direction": "ltr"}
                }
            },
        )

    def test_returns_correct_value_from_prefetched_tile(self):
        resource = self._make_resource()
        resource.tiles = [self._make_tile(resource, "Colosseum")]

        result = MulticardResourceDescriptor().get_primary_descriptor_from_nodes(
            resource, self.descriptor_config, context={"language": "en"}
        )

        self.assertEqual(result, "Colosseum")

    def test_no_tile_db_queries_when_tiles_are_prefetched(self):
        resource = self._make_resource()
        resource.tiles = [self._make_tile(resource, "Stonehenge")]

        with CaptureQueriesContext(connection) as queries:
            MulticardResourceDescriptor().get_primary_descriptor_from_nodes(
                resource, self.descriptor_config, context={"language": "en"}
            )

        tile_queries = [q for q in queries if '"tiles"."tileid"' in q["sql"]]
        self.assertEqual(
            len(tile_queries),
            0,
            "TileModel should not be queried when resource.tiles is already populated.",
        )

    def test_returns_correct_value_from_db_when_tiles_not_prefetched(self):
        """Falls back to a DB query when resource.tiles is empty."""
        # Use the resource + tile created in setUpTestData.
        resource = Resource.objects.get(pk=self.saved_resource.pk)
        resource.descriptors = resource.descriptors or {}
        resource.name = resource.name or {}
        resource.tiles = []  # simulate tiles NOT being pre-fetched

        result = MulticardResourceDescriptor().get_primary_descriptor_from_nodes(
            resource, self.descriptor_config, context={"language": "en"}
        )

        self.assertEqual(result, "Pyramids of Giza")

    def test_tile_db_query_made_when_tiles_not_prefetched(self):
        resource = Resource.objects.get(pk=self.saved_resource.pk)
        resource.descriptors = resource.descriptors or {}
        resource.name = resource.name or {}
        resource.tiles = []

        with CaptureQueriesContext(connection) as queries:
            MulticardResourceDescriptor().get_primary_descriptor_from_nodes(
                resource, self.descriptor_config, context={"language": "en"}
            )

        tile_queries = [q for q in queries if '"tiles"."tileid"' in q["sql"]]
        self.assertGreater(
            len(tile_queries),
            0,
            "A TileModel query should be issued when resource.tiles is empty.",
        )
