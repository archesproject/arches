from arches.extensions.querysets.bulk_operations.tiles import TileTreeOperation
from arches.extensions.querysets.models import TileTree
from arches.extensions.querysets.utils.models import ensure_request
from arches.extensions.querysets.utils.tests import GraphTestCase


class TileTreeOperationTests(GraphTestCase):
    def test_partial_update_leaves_missing_nodes_alone(self):
        request = ensure_request(None, force_admin=True)
        test_tiles = TileTree.get_tiles("datatype_lookups", "datatypes_1")
        entry_tile = test_tiles.get(pk=self.cardinality_1_tile.pk)
        del entry_tile.aliased_data.boolean_alias
        operation = TileTreeOperation(entry=entry_tile, request=request, partial=True)
        operation.validate()
        with self.assertRaises(AttributeError):
            entry_tile.aliased_data.boolean_alias

    def test_full_update_resets_missing_nodes_to_default(self):
        request = ensure_request(None, force_admin=True)
        test_tiles = TileTree.get_tiles("datatype_lookups", "datatypes_1")
        entry_tile = test_tiles.get(pk=self.cardinality_1_tile.pk)
        self.assertIs(entry_tile.aliased_data.boolean_alias, True)
        del entry_tile.aliased_data.boolean_alias
        operation = TileTreeOperation(entry=entry_tile, request=request, partial=False)
        operation.validate()
        self.assertIs(entry_tile.aliased_data.boolean_alias, False)
