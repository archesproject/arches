from arches.extensions.querysets.models import TileTree
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
