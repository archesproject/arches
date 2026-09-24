from arches.extensions.querysets.datatypes import DataTypeFactory
from arches.extensions.querysets.models import (
    GraphWithPrefetching,
    ResourceTileTree,
    TileTree,
)
from arches.extensions.querysets.utils.tests import GraphTestCase


class PerformanceTests(GraphTestCase):
    def test_get_graph_objects(self):
        # 1: graph
        # 2: graph -> node
        # 3: graph -> node -> cardxnodexwidget
        # 4: graph -> node -> nodegroup
        # 5: graph -> node -> nodegroup -> node
        # 6: graph -> node -> nodegroup -> node -> cardxnodexwidget
        # 7: graph -> node -> nodegroup -> card
        # (8-12): 3-7 again for (depth 2 nodegroup)
        # 13: depth 3 nodegroup (none!)
        with self.assertNumQueries(13):
            GraphWithPrefetching.objects.prefetch("datatype_lookups").get()

    def test_get_resources(self):
        # Clear the value lookups to avoid flakiness.
        factory = DataTypeFactory()
        concept_dt = factory.get_instance("concept")
        concept_dt.value_lookup = {}
        concept_list_dt = factory.get_instance("concept-list")
        concept_list_dt.value_lookup = {}

        # 1: nodes
        # 2: resources
        # 3-15: test_get_graph_objects()
        # 16: tile depth 1
        # 17: resource -> resourcexresource depth 1
        # 18: resource -> resourcexresource -> to_resource
        # (17-18 are a little unfortunate, but worth it for resourcexresource prefetches.
        # 19-21: depth 2
        # 22: concept value
        # (N+1 BUG: core arches) more concept values
        with self.assertNumQueries(22):
            qs = ResourceTileTree.get_tiles("datatype_lookups")
            self.assertCountEqual(qs, [self.resource_42, self.resource_none])

    def test_get_tiles(self):
        # 1-20 from test_get_resources()
        with self.assertNumQueries(20):
            qs = TileTree.get_tiles("datatype_lookups", "datatypes_1")
            self.assertCountEqual(
                qs, [self.cardinality_1_tile, self.cardinality_1_tile_none]
            )
