"""Tests for _targeted_refresh_aliased_data.

Verifies that after save(), the in-memory aliased_data reflects the saved
state without requiring a full refresh_from_db().  Each test checks that
the optimised targeted-refresh path (not the fallback refresh_from_db path)
correctly updates the resource's aliased_data for common mutation scenarios.

Mutations are expressed through aliased_data.{alias} (the user-facing API),
which is what the save machinery reads when building tile data.
"""

from arches.extensions.querysets.models import ResourceTileTree, TileTree
from arches.extensions.querysets.utils.models import ensure_request
from arches.extensions.querysets.utils.tests import GraphTestCase


def _load_resource(resource, as_representation=True):
    """Reload a ResourceTileTree from the DB (for before/after comparisons)."""
    return ResourceTileTree.get_tiles(
        "datatype_lookups", as_representation=as_representation
    ).get(pk=resource.pk)


def _delete_request():
    """Return a force-admin request with delete_missing_tiles enabled."""
    request = ensure_request(None, True)
    request.GET["delete_missing_tiles"] = "true"
    return request


class TargetedRefreshTests(GraphTestCase):
    """Tests that _targeted_refresh_aliased_data correctly updates aliased_data.

    The targeted-refresh path is taken when:
      - The resource is *not* new (already has a PK / tiles in the DB).
      - The pre-save tile tree is non-empty.
      - The number of changed + deleted tiles is <= 20.

    Each test mutates the resource via aliased_data.{alias} (the user-facing
    API), calls save(), and then inspects aliased_data *directly* — without a
    further refresh_from_db() call — to confirm that the in-memory state
    matches what was persisted.
    """

    def setUp(self):
        # Reload a fresh copy of each resource before each test so mutations
        # in one test do not bleed into the next.
        self.r42 = _load_resource(self.resource_42)
        self.r_none = _load_resource(self.resource_none)

    # ------------------------------------------------------------------ #
    # 1. Update existing tile — aliased_data updated in place
    # ------------------------------------------------------------------ #

    def test_update_existing_top_level_tile(self):
        """Updating a field on an existing cardinality-1 tile is reflected immediately."""
        tile = self.r42.aliased_data.datatypes_1
        new_value = "targeted-refresh-test-value"
        self.assertNotEqual(tile.aliased_data.non_localized_string_alias, new_value)

        tile.aliased_data.non_localized_string_alias = new_value
        self.r42.save(force_admin=True)

        # aliased_data must already reflect the new value — no refresh_from_db needed.
        # In as_representation mode, aliased_data.{alias} is a dict with "node_value".
        result_tile = self.r42.aliased_data.datatypes_1
        self.assertIsNotNone(result_tile, "Tile should still exist after update")
        result_value = result_tile.aliased_data.non_localized_string_alias
        result_node_value = (
            result_value["node_value"]
            if isinstance(result_value, dict)
            else result_value
        )
        self.assertEqual(
            result_node_value,
            new_value,
            "Targeted refresh should update aliased_data with new tile value",
        )

    def test_update_existing_cardinality_n_tile(self):
        """Updating a cardinality-n tile is reflected in aliased_data."""
        tiles_n = self.r42.aliased_data.datatypes_n
        self.assertGreater(len(tiles_n), 0)
        tile = tiles_n[0]
        new_value = "targeted-refresh-n-test-value"
        self.assertNotEqual(tile.aliased_data.non_localized_string_alias_n, new_value)

        tile.aliased_data.non_localized_string_alias_n = new_value
        self.r42.save(force_admin=True)

        result_tiles = self.r42.aliased_data.datatypes_n
        result_value = result_tiles[0].aliased_data.non_localized_string_alias_n
        result_node_value = (
            result_value["node_value"]
            if isinstance(result_value, dict)
            else result_value
        )
        self.assertEqual(
            result_node_value,
            new_value,
            "Targeted refresh should update cardinality-n tile aliased_data",
        )

    def test_update_existing_cardinality_n_parent_and_child_simultaneously(self):
        """Updating both a cardinality-n parent and its child tile in one save reflects both."""
        parent_tile = self.r42.aliased_data.datatypes_n[0]
        child_tiles = parent_tile.aliased_data.datatypes_n_child
        self.assertEqual(len(child_tiles), 1, "Precondition: exactly 1 child tile")
        child_tile = child_tiles[0]

        new_parent_value = "update-n-parent-value"
        new_child_value = "update-n-child-value"
        self.assertNotEqual(
            parent_tile.aliased_data.non_localized_string_alias_n, new_parent_value
        )
        self.assertNotEqual(
            child_tile.aliased_data.non_localized_string_alias_n_child, new_child_value
        )

        parent_tile.aliased_data.non_localized_string_alias_n = new_parent_value
        child_tile.aliased_data.non_localized_string_alias_n_child = new_child_value
        self.r42.save(force_admin=True)

        def _node_value(v):
            return v["node_value"] if isinstance(v, dict) else v

        result_parents = self.r42.aliased_data.datatypes_n
        self.assertEqual(len(result_parents), 1)
        result_parent = result_parents[0]
        self.assertEqual(
            _node_value(result_parent.aliased_data.non_localized_string_alias_n),
            new_parent_value,
            "Parent value should be updated in aliased_data after simultaneous save",
        )

        result_children = result_parent.aliased_data.datatypes_n_child
        self.assertEqual(len(result_children), 1)
        result_child = result_children[0]
        self.assertEqual(
            _node_value(result_child.aliased_data.non_localized_string_alias_n_child),
            new_child_value,
            "Child value should be updated in aliased_data after simultaneous save",
        )

    # ------------------------------------------------------------------ #
    # 2. Insert child tile into existing parent
    # ------------------------------------------------------------------ #

    def test_insert_child_tile_updates_parent_aliased_data(self):
        """Inserting a child tile into an existing parent updates the parent's aliased_data."""
        # resource_none has a datatypes_1 parent; remove its child first.
        parent_tile = self.r_none.aliased_data.datatypes_1
        parent_tile.aliased_data.datatypes_1_child = None
        self.r_none.save(request=_delete_request(), force_admin=True)
        self.r_none = _load_resource(self.resource_none)

        parent_tile = self.r_none.aliased_data.datatypes_1
        self.assertIsNone(
            parent_tile.aliased_data.datatypes_1_child,
            "Precondition: parent has no child tile",
        )

        # Append a new blank child tile.
        parent_tile.append_tile("datatypes_1_child")
        new_child = parent_tile.aliased_data.datatypes_1_child
        self.assertIsNotNone(new_child, "append_tile should create a child tile object")

        new_child.aliased_data.non_localized_string_alias_child = "new-child-value"
        self.r_none.save(force_admin=True)

        # The parent tile's aliased_data must now point to the inserted child.
        result_parent = self.r_none.aliased_data.datatypes_1
        self.assertIsNotNone(result_parent, "Parent tile should still exist")
        result_child = result_parent.aliased_data.datatypes_1_child
        self.assertIsNotNone(
            result_child,
            "Parent aliased_data.datatypes_1_child must be populated after child insert",
        )
        self.assertIsInstance(result_child, TileTree)
        result_value = result_child.aliased_data.non_localized_string_alias_child
        result_node_value = (
            result_value["node_value"]
            if isinstance(result_value, dict)
            else result_value
        )
        self.assertEqual(result_node_value, "new-child-value")

    def test_insert_cardinality_n_child_into_existing_parent(self):
        """Appending a new cardinality-n child tile to an existing parent extends its list."""
        parent_tile = self.r42.aliased_data.datatypes_n[0]
        children_before = list(parent_tile.aliased_data.datatypes_n_child)
        self.assertEqual(
            len(children_before), 1, "Precondition: exactly 1 child tile in DB"
        )

        parent_tile.append_tile("datatypes_n_child")
        new_children = parent_tile.aliased_data.datatypes_n_child
        self.assertEqual(len(new_children), len(children_before) + 1)

        new_child = new_children[-1]
        new_child.aliased_data.non_localized_string_alias_n_child = (
            "appended-child-value"
        )

        self.r42.save(force_admin=True)

        result_parent = self.r42.aliased_data.datatypes_n[0]
        result_children = result_parent.aliased_data.datatypes_n_child
        self.assertEqual(
            len(result_children),
            len(children_before) + 1,
            "New child tile must appear in parent's aliased_data list after save",
        )

        def _node_value(v):
            return v["node_value"] if isinstance(v, dict) else v

        appended = [
            c
            for c in result_children
            if _node_value(c.aliased_data.non_localized_string_alias_n_child)
            == "appended-child-value"
        ]
        self.assertEqual(
            len(appended), 1, "Appended child tile should have its data in aliased_data"
        )

    # ------------------------------------------------------------------ #
    # 3. Delete child tile — parent aliased_data cleared
    # ------------------------------------------------------------------ #

    def test_delete_child_tile_clears_parent_aliased_data(self):
        """Setting child to None and saving clears the parent's aliased_data.datatypes_1_child."""
        parent_tile = self.r42.aliased_data.datatypes_1
        self.assertIsNotNone(
            parent_tile.aliased_data.datatypes_1_child,
            "Precondition: child tile must exist",
        )

        parent_tile.aliased_data.datatypes_1_child = None
        self.r42.save(request=_delete_request(), force_admin=True)

        # Targeted refresh must clear the child reference on the parent tile.
        result_parent = self.r42.aliased_data.datatypes_1
        self.assertIsNotNone(result_parent, "Parent tile should still exist")
        self.assertIsNone(
            result_parent.aliased_data.datatypes_1_child,
            "datatypes_1_child should be None after child tile deletion",
        )

    def test_delete_cardinality_n_child_tile_updates_parent_list(self):
        """Removing all cardinality-n child tiles from the list clears the parent's aliased_data list."""
        parent_tile = self.r42.aliased_data.datatypes_n[0]
        children_before = list(parent_tile.aliased_data.datatypes_n_child)
        self.assertGreater(
            len(children_before), 0, "Precondition: parent has >=1 child tile"
        )

        parent_tile.aliased_data.datatypes_n_child = []
        self.r42.save(request=_delete_request(), force_admin=True)

        result_parent = self.r42.aliased_data.datatypes_n[0]
        result_children = result_parent.aliased_data.datatypes_n_child
        self.assertEqual(
            len(result_children),
            0,
            "All child tiles should be removed from parent's aliased_data list",
        )

    # ------------------------------------------------------------------ #
    # 4. Simultaneous parent + child insert (subtree insert)
    # ------------------------------------------------------------------ #

    def test_insert_cardinality_n_parent_and_child_simultaneously(self):
        """Inserting a new cardinality-n parent + auto-created child in one save returns both."""
        # Remove all datatypes_n tiles so we can insert fresh ones.
        self.r_none.aliased_data.datatypes_n = []
        self.r_none.save(request=_delete_request(), force_admin=True)
        self.r_none = _load_resource(self.resource_none)

        self.assertEqual(
            self.r_none.aliased_data.datatypes_n,
            [],
            "Precondition: no datatypes_n tiles",
        )

        # Append a new parent tile.  append_tile() creates blank child tiles
        # recursively, so new_parent already has a blank datatypes_n_child tile.
        self.r_none.append_tile("datatypes_n")
        new_parent = self.r_none.aliased_data.datatypes_n[0]
        new_child = new_parent.aliased_data.datatypes_n_child[0]

        new_parent.aliased_data.non_localized_string_alias_n = "new-parent-value"
        new_child.aliased_data.non_localized_string_alias_n_child = "new-child-value"

        self.r_none.save(force_admin=True)

        # Both the parent and child tile must appear in aliased_data.
        result_parents = self.r_none.aliased_data.datatypes_n
        self.assertEqual(len(result_parents), 1, "One parent tile should be present")

        def _node_value(v):
            return v["node_value"] if isinstance(v, dict) else v

        result_parent = result_parents[0]
        self.assertIsInstance(result_parent, TileTree)
        self.assertEqual(
            _node_value(result_parent.aliased_data.non_localized_string_alias_n),
            "new-parent-value",
        )

        result_children = result_parent.aliased_data.datatypes_n_child
        self.assertEqual(len(result_children), 1, "One child tile should be present")
        self.assertEqual(
            _node_value(
                result_children[0].aliased_data.non_localized_string_alias_n_child
            ),
            "new-child-value",
        )

    # ------------------------------------------------------------------ #
    # Helper
    # ------------------------------------------------------------------ #

    @staticmethod
    def _node_value(v):
        return v["node_value"] if isinstance(v, dict) else v

    def test_insert_cardinality_1_parent_and_child_simultaneously(self):
        """Inserting a cardinality-1 parent + child tile in one save returns both."""
        # Remove the existing datatypes_1 tile and its children.
        self.r_none.aliased_data.datatypes_1 = None
        self.r_none.save(request=_delete_request(), force_admin=True)
        self.r_none = _load_resource(self.resource_none)

        self.assertIsNone(
            self.r_none.aliased_data.datatypes_1,
            "Precondition: no datatypes_1 tile",
        )

        # fill_blanks creates blank tiles for all nodegroups without tiles.
        self.r_none.fill_blanks()
        new_parent = self.r_none.aliased_data.datatypes_1
        self.assertIsNotNone(new_parent)
        new_child = new_parent.aliased_data.datatypes_1_child
        self.assertIsNotNone(new_child)

        new_parent.aliased_data.non_localized_string_alias = "new-card1-parent"
        new_child.aliased_data.non_localized_string_alias_child = "new-card1-child"

        self.r_none.save(force_admin=True)

        def _node_value(v):
            return v["node_value"] if isinstance(v, dict) else v

        result_parent = self.r_none.aliased_data.datatypes_1
        self.assertIsNotNone(result_parent, "Parent tile must appear in aliased_data")
        self.assertEqual(
            _node_value(result_parent.aliased_data.non_localized_string_alias),
            "new-card1-parent",
        )

        result_child = result_parent.aliased_data.datatypes_1_child
        self.assertIsNotNone(
            result_child, "Child tile must appear in parent aliased_data"
        )
        self.assertEqual(
            _node_value(result_child.aliased_data.non_localized_string_alias_child),
            "new-card1-child",
        )

    # ------------------------------------------------------------------ #
    # 5. Update existing child tile only (parent unchanged)
    # ------------------------------------------------------------------ #

    def test_update_card1_1_child_only(self):
        """Updating a card-1 child (1→1) without touching the parent is reflected."""
        child_tile = self.r42.aliased_data.datatypes_1.aliased_data.datatypes_1_child
        new_value = "update-1-1-child-only"
        self.assertNotEqual(
            self._node_value(child_tile.aliased_data.non_localized_string_alias_child),
            new_value,
        )
        child_tile.aliased_data.non_localized_string_alias_child = new_value
        self.r42.save(force_admin=True)

        result_child = self.r42.aliased_data.datatypes_1.aliased_data.datatypes_1_child
        self.assertIsNotNone(result_child)
        self.assertEqual(
            self._node_value(
                result_child.aliased_data.non_localized_string_alias_child
            ),
            new_value,
        )

    def test_update_card1_n_child_only(self):
        """Updating a card-n child (1→n) without touching the parent is reflected."""
        parent_tile = self.r42.aliased_data.datatypes_1
        children = parent_tile.aliased_data.datatypes_1_n_child
        self.assertGreater(len(children), 0, "Precondition: >=1 child tile")
        child_tile = children[0]
        new_value = "update-1-n-child-only"
        self.assertNotEqual(
            self._node_value(
                child_tile.aliased_data.non_localized_string_alias_1_n_child
            ),
            new_value,
        )
        child_tile.aliased_data.non_localized_string_alias_1_n_child = new_value
        self.r42.save(force_admin=True)

        result_children = (
            self.r42.aliased_data.datatypes_1.aliased_data.datatypes_1_n_child
        )
        self.assertEqual(len(result_children), 1)
        self.assertEqual(
            self._node_value(
                result_children[0].aliased_data.non_localized_string_alias_1_n_child
            ),
            new_value,
        )

    def test_update_cardn_1_child_only(self):
        """Updating a card-1 child (n→1) without touching the parent is reflected."""
        parent_tile = self.r42.aliased_data.datatypes_n[0]
        child_tile = parent_tile.aliased_data.datatypes_n_1_child
        self.assertIsNotNone(child_tile, "Precondition: child tile exists")
        new_value = "update-n-1-child-only"
        self.assertNotEqual(
            self._node_value(
                child_tile.aliased_data.non_localized_string_alias_n_1_child
            ),
            new_value,
        )
        child_tile.aliased_data.non_localized_string_alias_n_1_child = new_value
        self.r42.save(force_admin=True)

        result_child = self.r42.aliased_data.datatypes_n[
            0
        ].aliased_data.datatypes_n_1_child
        self.assertIsNotNone(result_child)
        self.assertEqual(
            self._node_value(
                result_child.aliased_data.non_localized_string_alias_n_1_child
            ),
            new_value,
        )

    def test_update_cardn_n_child_only(self):
        """Updating a card-n child (n→n) without touching the parent is reflected."""
        parent_tile = self.r42.aliased_data.datatypes_n[0]
        children = parent_tile.aliased_data.datatypes_n_child
        self.assertGreater(len(children), 0, "Precondition: >=1 child tile")
        child_tile = children[0]
        new_value = "update-n-n-child-only"
        self.assertNotEqual(
            self._node_value(
                child_tile.aliased_data.non_localized_string_alias_n_child
            ),
            new_value,
        )
        child_tile.aliased_data.non_localized_string_alias_n_child = new_value
        self.r42.save(force_admin=True)

        result_children = self.r42.aliased_data.datatypes_n[
            0
        ].aliased_data.datatypes_n_child
        self.assertEqual(len(result_children), 1)
        self.assertEqual(
            self._node_value(
                result_children[0].aliased_data.non_localized_string_alias_n_child
            ),
            new_value,
        )

    # ------------------------------------------------------------------ #
    # 6. Update parent only — new cardinality combinations (1→n, n→1)
    # ------------------------------------------------------------------ #

    def test_update_card1_n_parent_only(self):
        """Updating a card-1 parent (1→n) without touching its card-n children is reflected."""
        parent_tile = self.r42.aliased_data.datatypes_1
        children = parent_tile.aliased_data.datatypes_1_n_child
        self.assertGreater(len(children), 0, "Precondition: >=1 child tile")
        old_child_value = self._node_value(
            children[0].aliased_data.non_localized_string_alias_1_n_child
        )
        new_parent_value = "update-1-n-parent-only"
        parent_tile.aliased_data.non_localized_string_alias = new_parent_value
        self.r42.save(force_admin=True)

        result_parent = self.r42.aliased_data.datatypes_1
        self.assertEqual(
            self._node_value(result_parent.aliased_data.non_localized_string_alias),
            new_parent_value,
        )
        result_children = result_parent.aliased_data.datatypes_1_n_child
        self.assertGreater(len(result_children), 0)
        self.assertEqual(
            self._node_value(
                result_children[0].aliased_data.non_localized_string_alias_1_n_child
            ),
            old_child_value,
            "Child value should be unchanged after parent-only update",
        )

    def test_update_cardn_1_parent_only(self):
        """Updating a card-n parent (n→1) without touching its card-1 child is reflected."""
        parent_tile = self.r42.aliased_data.datatypes_n[0]
        child_tile = parent_tile.aliased_data.datatypes_n_1_child
        self.assertIsNotNone(child_tile, "Precondition: child tile exists")
        old_child_value = self._node_value(
            child_tile.aliased_data.non_localized_string_alias_n_1_child
        )
        new_parent_value = "update-n-1-parent-only"
        parent_tile.aliased_data.non_localized_string_alias_n = new_parent_value
        self.r42.save(force_admin=True)

        result_parent = self.r42.aliased_data.datatypes_n[0]
        self.assertEqual(
            self._node_value(result_parent.aliased_data.non_localized_string_alias_n),
            new_parent_value,
        )
        result_child = result_parent.aliased_data.datatypes_n_1_child
        self.assertIsNotNone(result_child)
        self.assertEqual(
            self._node_value(
                result_child.aliased_data.non_localized_string_alias_n_1_child
            ),
            old_child_value,
            "Child value should be unchanged after parent-only update",
        )

    # ------------------------------------------------------------------ #
    # 7. Update parent + child together — missing combinations (1→1, 1→n, n→1)
    # ------------------------------------------------------------------ #

    def test_update_cardinality_1_1_parent_and_child_simultaneously(self):
        """Updating a card-1 parent and its card-1 child in one save reflects both (1→1)."""
        parent_tile = self.r42.aliased_data.datatypes_1
        child_tile = parent_tile.aliased_data.datatypes_1_child
        self.assertIsNotNone(child_tile, "Precondition: child tile exists")

        new_parent_value = "update-1-1-parent"
        new_child_value = "update-1-1-child"
        parent_tile.aliased_data.non_localized_string_alias = new_parent_value
        child_tile.aliased_data.non_localized_string_alias_child = new_child_value
        self.r42.save(force_admin=True)

        result_parent = self.r42.aliased_data.datatypes_1
        self.assertEqual(
            self._node_value(result_parent.aliased_data.non_localized_string_alias),
            new_parent_value,
        )
        result_child = result_parent.aliased_data.datatypes_1_child
        self.assertIsNotNone(result_child)
        self.assertEqual(
            self._node_value(
                result_child.aliased_data.non_localized_string_alias_child
            ),
            new_child_value,
        )

    def test_update_cardinality_1_n_parent_and_child_simultaneously(self):
        """Updating a card-1 parent and its card-n child in one save reflects both (1→n)."""
        parent_tile = self.r42.aliased_data.datatypes_1
        children = parent_tile.aliased_data.datatypes_1_n_child
        self.assertGreater(len(children), 0, "Precondition: >=1 child tile")
        child_tile = children[0]

        new_parent_value = "update-1-n-parent"
        new_child_value = "update-1-n-child"
        parent_tile.aliased_data.non_localized_string_alias = new_parent_value
        child_tile.aliased_data.non_localized_string_alias_1_n_child = new_child_value
        self.r42.save(force_admin=True)

        result_parent = self.r42.aliased_data.datatypes_1
        self.assertEqual(
            self._node_value(result_parent.aliased_data.non_localized_string_alias),
            new_parent_value,
        )
        result_children = result_parent.aliased_data.datatypes_1_n_child
        self.assertEqual(len(result_children), 1)
        self.assertEqual(
            self._node_value(
                result_children[0].aliased_data.non_localized_string_alias_1_n_child
            ),
            new_child_value,
        )

    def test_update_cardinality_n_1_parent_and_child_simultaneously(self):
        """Updating a card-n parent and its card-1 child in one save reflects both (n→1)."""
        parent_tile = self.r42.aliased_data.datatypes_n[0]
        child_tile = parent_tile.aliased_data.datatypes_n_1_child
        self.assertIsNotNone(child_tile, "Precondition: child tile exists")

        new_parent_value = "update-n-1-parent"
        new_child_value = "update-n-1-child"
        parent_tile.aliased_data.non_localized_string_alias_n = new_parent_value
        child_tile.aliased_data.non_localized_string_alias_n_1_child = new_child_value
        self.r42.save(force_admin=True)

        result_parent = self.r42.aliased_data.datatypes_n[0]
        self.assertEqual(
            self._node_value(result_parent.aliased_data.non_localized_string_alias_n),
            new_parent_value,
        )
        result_child = result_parent.aliased_data.datatypes_n_1_child
        self.assertIsNotNone(result_child)
        self.assertEqual(
            self._node_value(
                result_child.aliased_data.non_localized_string_alias_n_1_child
            ),
            new_child_value,
        )

    # ------------------------------------------------------------------ #
    # 8. Insert child — missing combinations (1→n, n→1)
    # ------------------------------------------------------------------ #

    def test_insert_cardinality_1_n_child_into_existing_parent(self):
        """Appending a new card-n child (1→n) to an existing card-1 parent extends its list."""
        parent_tile = self.r42.aliased_data.datatypes_1
        children_before = list(parent_tile.aliased_data.datatypes_1_n_child)
        self.assertEqual(len(children_before), 1, "Precondition: exactly 1 child tile")

        parent_tile.append_tile("datatypes_1_n_child")
        new_children = parent_tile.aliased_data.datatypes_1_n_child
        self.assertEqual(len(new_children), len(children_before) + 1)
        new_child = new_children[-1]
        new_child.aliased_data.non_localized_string_alias_1_n_child = (
            "appended-1-n-child"
        )

        self.r42.save(force_admin=True)

        result_children = (
            self.r42.aliased_data.datatypes_1.aliased_data.datatypes_1_n_child
        )
        self.assertEqual(len(result_children), len(children_before) + 1)
        appended = [
            c
            for c in result_children
            if self._node_value(c.aliased_data.non_localized_string_alias_1_n_child)
            == "appended-1-n-child"
        ]
        self.assertEqual(
            len(appended), 1, "Appended child must have its data in aliased_data"
        )

    def test_insert_cardinality_n_1_child_into_existing_parent(self):
        """Inserting a card-1 child (n→1) into an existing card-n parent updates aliased_data."""
        # resource_none has an empty card-1 child tile; remove it first.
        parent_tile = self.r_none.aliased_data.datatypes_n[0]
        parent_tile.aliased_data.datatypes_n_1_child = None
        self.r_none.save(request=_delete_request(), force_admin=True)
        self.r_none = _load_resource(self.resource_none)

        parent_tile = self.r_none.aliased_data.datatypes_n[0]
        self.assertIsNone(
            parent_tile.aliased_data.datatypes_n_1_child,
            "Precondition: no card-1 child tile",
        )

        parent_tile.append_tile("datatypes_n_1_child")
        new_child = parent_tile.aliased_data.datatypes_n_1_child
        self.assertIsNotNone(new_child, "append_tile should create a child tile object")
        new_child.aliased_data.non_localized_string_alias_n_1_child = "new-n-1-child"
        self.r_none.save(force_admin=True)

        result_parent = self.r_none.aliased_data.datatypes_n[0]
        result_child = result_parent.aliased_data.datatypes_n_1_child
        self.assertIsNotNone(
            result_child, "Child must appear in aliased_data after insert"
        )
        self.assertIsInstance(result_child, TileTree)
        self.assertEqual(
            self._node_value(
                result_child.aliased_data.non_localized_string_alias_n_1_child
            ),
            "new-n-1-child",
        )

    # ------------------------------------------------------------------ #
    # 9. Delete child — missing combinations (1→n, n→1)
    # ------------------------------------------------------------------ #

    def test_delete_cardinality_1_n_child_updates_parent_list(self):
        """Removing all card-n children (1→n) clears the parent's aliased_data list."""
        parent_tile = self.r42.aliased_data.datatypes_1
        self.assertGreater(
            len(parent_tile.aliased_data.datatypes_1_n_child),
            0,
            "Precondition: >=1 child tile",
        )

        parent_tile.aliased_data.datatypes_1_n_child = []
        self.r42.save(request=_delete_request(), force_admin=True)

        result_children = (
            self.r42.aliased_data.datatypes_1.aliased_data.datatypes_1_n_child
        )
        self.assertEqual(
            len(result_children),
            0,
            "All card-n children should be removed from aliased_data",
        )

    def test_delete_cardinality_n_1_child_clears_parent_aliased_data(self):
        """Deleting a card-1 child (n→1) sets the parent's aliased_data reference to None."""
        parent_tile = self.r42.aliased_data.datatypes_n[0]
        self.assertIsNotNone(
            parent_tile.aliased_data.datatypes_n_1_child,
            "Precondition: child tile exists",
        )

        parent_tile.aliased_data.datatypes_n_1_child = None
        self.r42.save(request=_delete_request(), force_admin=True)

        result_child = self.r42.aliased_data.datatypes_n[
            0
        ].aliased_data.datatypes_n_1_child
        self.assertIsNone(
            result_child, "datatypes_n_1_child should be None after deletion"
        )

    # ------------------------------------------------------------------ #
    # 10. Insert parent + child simultaneously — missing combinations (1→n, n→1)
    # ------------------------------------------------------------------ #

    def test_insert_cardinality_1_n_parent_and_child_simultaneously(self):
        """Inserting a card-1 parent and its card-n child together in one save returns both."""
        self.r_none.aliased_data.datatypes_1 = None
        self.r_none.save(request=_delete_request(), force_admin=True)
        self.r_none = _load_resource(self.resource_none)
        self.assertIsNone(
            self.r_none.aliased_data.datatypes_1, "Precondition: no datatypes_1"
        )

        self.r_none.fill_blanks()
        new_parent = self.r_none.aliased_data.datatypes_1
        self.assertIsNotNone(new_parent)
        new_children = new_parent.aliased_data.datatypes_1_n_child
        self.assertGreater(
            len(new_children), 0, "fill_blanks should create a blank card-n child tile"
        )
        new_child = new_children[0]

        new_parent.aliased_data.non_localized_string_alias = "new-1-n-parent"
        new_child.aliased_data.non_localized_string_alias_1_n_child = "new-1-n-child"
        self.r_none.save(force_admin=True)

        result_parent = self.r_none.aliased_data.datatypes_1
        self.assertIsNotNone(result_parent, "Parent tile must appear in aliased_data")
        self.assertIsInstance(result_parent, TileTree)
        self.assertEqual(
            self._node_value(result_parent.aliased_data.non_localized_string_alias),
            "new-1-n-parent",
        )
        result_children = result_parent.aliased_data.datatypes_1_n_child
        self.assertEqual(len(result_children), 1, "One card-n child should be present")
        self.assertEqual(
            self._node_value(
                result_children[0].aliased_data.non_localized_string_alias_1_n_child
            ),
            "new-1-n-child",
        )

    def test_insert_cardinality_n_1_parent_and_child_simultaneously(self):
        """Inserting a card-n parent and its card-1 child together in one save returns both."""
        self.r_none.aliased_data.datatypes_n = []
        self.r_none.save(request=_delete_request(), force_admin=True)
        self.r_none = _load_resource(self.resource_none)
        self.assertEqual(
            self.r_none.aliased_data.datatypes_n,
            [],
            "Precondition: no datatypes_n tiles",
        )

        self.r_none.append_tile("datatypes_n")
        new_parent = self.r_none.aliased_data.datatypes_n[0]
        new_child = new_parent.aliased_data.datatypes_n_1_child
        self.assertIsNotNone(
            new_child, "append_tile should create a blank card-1 child tile"
        )

        new_parent.aliased_data.non_localized_string_alias_n = "new-n-1-parent"
        new_child.aliased_data.non_localized_string_alias_n_1_child = "new-n-1-child"
        self.r_none.save(force_admin=True)

        result_parents = self.r_none.aliased_data.datatypes_n
        self.assertEqual(len(result_parents), 1, "One parent tile should be present")
        result_parent = result_parents[0]
        self.assertIsInstance(result_parent, TileTree)
        self.assertEqual(
            self._node_value(result_parent.aliased_data.non_localized_string_alias_n),
            "new-n-1-parent",
        )
        result_child = result_parent.aliased_data.datatypes_n_1_child
        self.assertIsNotNone(result_child, "Card-1 child must appear in aliased_data")
        self.assertEqual(
            self._node_value(
                result_child.aliased_data.non_localized_string_alias_n_1_child
            ),
            "new-n-1-child",
        )
