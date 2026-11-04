from types import SimpleNamespace
from unittest import mock

from arches.app.models.models import TileModel
from arches.extensions.querysets.models import ResourceTileTree, TileTree
from arches.extensions.querysets.querysets import (
    TileTreeQuerySet,
    cap_depth_to_graph,
)
from arches.extensions.querysets.utils.tests import GraphTestCase


class InternalsTests(GraphTestCase):
    def test_node_alias_collision_with_model_field(self):
        self.file_list_node_1.alias = "file"
        self.file_list_node_1.save()
        # Previously, this clashed with the related query name "file"
        qs = TileTree.get_tiles(
            graph_slug="datatype_lookups", nodegroup_alias="datatypes_1"
        )
        # TODO: determine the reserved namespace to use here.
        self.assertEqual(
            qs.filter(_arches_querysets_file__isnull=True)[0].resourceinstance_id,
            self.resource_none.pk,
        )

    def test_get_tiles_without_nodes_arg_decodes_every_nodegroup_node(self):
        """Default behavior (no explicit `nodes=`) is unchanged: every node
        in the tile's nodegroup gets decoded onto aliased_data."""
        tile = TileTree.get_tiles(
            graph_slug="datatype_lookups",
            nodegroup_alias="datatypes_1",
            resource_ids=[self.resource_42.pk],
            depth=0,
        ).get(resourceinstance_id=self.resource_42.pk)

        self.assertTrue(hasattr(tile.aliased_data, self.string_node_1.alias))
        self.assertTrue(hasattr(tile.aliased_data, self.number_node_1.alias))
        self.assertTrue(hasattr(tile.aliased_data, self.boolean_node_1.alias))

    def test_get_tiles_with_explicit_nodes_arg_decodes_only_those_nodes(self):
        """An explicit `nodes=` restricts per-tile decoding to just those
        nodes, instead of every node in the nodegroup -- this is what makes
        a narrowly-scoped get_tiles() call (e.g. for a single requested
        search-result column) cheap rather than paying to decode every
        sibling node in the nodegroup."""
        tile = TileTree.get_tiles(
            graph_slug="datatype_lookups",
            nodegroup_alias="datatypes_1",
            resource_ids=[self.resource_42.pk],
            nodes=[self.string_node_1],
            depth=0,
        ).get(resourceinstance_id=self.resource_42.pk)

        self.assertTrue(hasattr(tile.aliased_data, self.string_node_1.alias))
        self.assertFalse(hasattr(tile.aliased_data, self.number_node_1.alias))
        self.assertFalse(hasattr(tile.aliased_data, self.boolean_node_1.alias))

    def test_get_tiles_with_empty_tile_data(self):
        """A tile with no authoritative or provisional data makes the datatype's
        get_tile_data() return None; nodes should decode to None instead of
        raising AttributeError."""
        TileModel.objects.filter(pk=self.cardinality_1_tile.pk).update(
            data={}, provisionaledits=None
        )
        tile = TileTree.get_tiles(
            graph_slug="datatype_lookups",
            nodegroup_alias="datatypes_1",
            resource_ids=[self.resource_42.pk],
            depth=0,
        ).get(pk=self.cardinality_1_tile.pk)

        self.assertIsNone(getattr(tile.aliased_data, self.string_node_1.alias))
        self.assertIsNone(tile.data[str(self.string_node_1.pk)])

    def test_cap_depth_to_graph(self):
        def node(ng, parent_ng=None, grandparent_id=None):
            parent = None
            if parent_ng is not None:
                parent = SimpleNamespace(
                    pk=parent_ng, parentnodegroup_id=grandparent_id
                )
            ng_obj = SimpleNamespace(
                pk=ng, parentnodegroup=parent, parentnodegroup_id=parent_ng
            )
            return SimpleNamespace(nodegroup=ng_obj)

        self.assertEqual(cap_depth_to_graph(20, [node(1)]), 0)
        self.assertEqual(cap_depth_to_graph(20, [node(1), node(2, 1)]), 1)
        three = [node(1), node(2, 1), node(3, 2, 1)]
        self.assertEqual(cap_depth_to_graph(20, three), 2)
        self.assertEqual(cap_depth_to_graph(1, three), 1)
        # Unresolvable ancestor chain: fall back to the caller's depth.
        self.assertEqual(cap_depth_to_graph(20, [node(3, 2, 1)]), 20)

    def test_recursion_capped_at_graph_depth(self):
        real = TileTreeQuerySet.get_tiles
        with mock.patch.object(
            TileTreeQuerySet, "get_tiles", autospec=True, side_effect=real
        ) as spy:
            list(ResourceTileTree.get_tiles("datatype_lookups"))
        # Top-level tiles plus one child level (the graph nests one deep),
        # not the default 20.
        self.assertEqual(spy.call_count, 2)

    def test_explicit_depth_still_an_upper_bound(self):
        real = TileTreeQuerySet.get_tiles
        with mock.patch.object(
            TileTreeQuerySet, "get_tiles", autospec=True, side_effect=real
        ) as spy:
            list(ResourceTileTree.objects.get_tiles("datatype_lookups", depth=0))
        self.assertEqual(spy.call_count, 1)

    def test_nodegroup_alias_entry_loads_children(self):
        tile = TileTree.get_tiles(
            "datatype_lookups",
            "datatypes_1",
            resource_ids=[self.resource_42.pk],
        ).get()
        self.assertIn(
            self.cardinality_1_child_tile.pk, [c.pk for c in tile._tile_trees]
        )
