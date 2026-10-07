"""
Tests for provisional-edit overlay in aliased_data.

Covers:
  - _resolve_provisional_data() helper (unit tests, minimal DB)
  - TileTreeQuerySet.get_tiles(provisional_edits_for_user=...)
  - ResourceTileTreeQuerySet.get_tiles(provisional_edits_for_user=...)
  - reprocess_tiles_aliased_data(provisional_edits_for_user=...)
  - ResourceTileTree._provisional_edits_for_user stored at load time and used
    by refresh_from_db() and save() without an explicit param
  - TileTree._provisional_edits_for_user stored at load time and used by
    refresh_from_db() / save() (fixes tile endpoint returning authoritative data)
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.management import call_command

from arches.app.models.models import TileModel

from arches.extensions.querysets.models import ResourceTileTree, TileTree
from arches.extensions.querysets.querysets import (
    _resolve_provisional_data,
    reprocess_tiles_aliased_data,
)
from arches.extensions.querysets.utils.tests import GraphTestCase

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_provisional_edits(user_id, tile_data, provisional_number, number_node_pk):
    """Return a provisionaledits dict with all node values from tile_data,
    but with the number node overridden to provisional_number."""
    provisional_value = {
        **tile_data,
        str(number_node_pk): provisional_number,
    }
    return {
        str(user_id): {
            "value": provisional_value,
            "action": "update",
            "status": "review",
            "reviewer": None,
            "timestamp": "2026-01-01T00:00:00.000000Z",
            "reviewtimestamp": None,
        }
    }


# ---------------------------------------------------------------------------
# Unit tests for _resolve_provisional_data
# ---------------------------------------------------------------------------


class ResolveProvisionalDataTests(GraphTestCase):
    """
    _resolve_provisional_data is a pure function: tile and user are duck-typed,
    so we can use lightweight stand-ins for most cases and only hit the DB where
    the real user_is_resource_reviewer permission check is needed.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        call_command("add_test_users", verbosity=0)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _tile(self, provisionaledits):
        t = MagicMock()
        t.provisionaledits = provisionaledits
        return t

    def _user(self, pk):
        u = MagicMock()
        u.pk = pk
        return u

    # ------------------------------------------------------------------
    # No-op paths
    # ------------------------------------------------------------------

    def test_returns_none_when_user_is_none(self):
        tile = self._tile({"1": {"value": {"n": "v"}, "status": "review"}})
        self.assertIsNone(_resolve_provisional_data(tile, None))

    def test_returns_none_when_provisionaledits_is_none(self):
        tile = self._tile(provisionaledits=None)
        self.assertIsNone(_resolve_provisional_data(tile, self._user(1)))

    def test_returns_none_when_provisionaledits_is_empty(self):
        tile = self._tile(provisionaledits={})
        self.assertIsNone(_resolve_provisional_data(tile, self._user(1)))

    # ------------------------------------------------------------------
    # Edit author path
    # ------------------------------------------------------------------

    def test_returns_own_provisional_value(self):
        expected = {"node-pk": "my-value"}
        tile = self._tile({"99": {"value": expected, "status": "review"}})
        with patch(
            "arches.extensions.querysets.querysets.user_is_resource_reviewer",
            return_value=False,
        ):
            result = _resolve_provisional_data(tile, self._user(99))
        self.assertEqual(result, expected)

    def test_reviewer_status_checked_before_own_edit(self):
        """user_is_resource_reviewer is checked before the user_id lookup,
        so a reviewer never sees provisional data even if they authored an edit."""
        tile = self._tile({"5": {"value": {"n": "v"}, "status": "review"}})
        with patch(
            "arches.extensions.querysets.querysets.user_is_resource_reviewer",
            return_value=True,
        ) as mock_reviewer:
            result = _resolve_provisional_data(tile, self._user(5))
        mock_reviewer.assert_called_once()
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Non-reviewer without own edit
    # ------------------------------------------------------------------

    def test_returns_none_for_non_reviewer_without_own_edit(self):
        tile = self._tile({"99": {"value": {"n": "v"}, "status": "review"}})
        user = self._user(42)  # not in provisionaledits
        with patch(
            "arches.extensions.querysets.querysets.user_is_resource_reviewer",
            return_value=False,
        ):
            result = _resolve_provisional_data(tile, user)
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Reviewer path — always sees authoritative data
    # ------------------------------------------------------------------

    def test_reviewer_sees_authoritative_data(self):
        """Resource Reviewers always get authoritative data, never a provisional overlay."""
        tile = self._tile(
            {
                "99": self._provisional_edit(
                    {"node-pk": "editors-value"}, "2026-01-01T00:00:00.000000Z"
                )
            }
        )
        reviewer = self._user(1)  # pk not in provisionaledits
        with patch(
            "arches.extensions.querysets.querysets.user_is_resource_reviewer",
            return_value=True,
        ):
            result = _resolve_provisional_data(tile, reviewer)
        self.assertIsNone(result)

    def test_reviewer_with_no_provisional_edits_returns_none(self):
        tile = self._tile(provisionaledits=None)
        with patch(
            "arches.extensions.querysets.querysets.user_is_resource_reviewer",
            return_value=True,
        ):
            result = _resolve_provisional_data(tile, self._user(1))
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Real DB users (permission check against actual group membership)
    # ------------------------------------------------------------------

    def test_real_provisional_editor_sees_own_edit(self):
        provisional_editor = User.objects.get(username="tester3")
        expected = {"node": "value"}
        tile = self._tile(
            {str(provisional_editor.pk): {"value": expected, "status": "review"}}
        )
        result = _resolve_provisional_data(tile, provisional_editor)
        self.assertEqual(result, expected)

    def test_real_reviewer_sees_authoritative_data(self):
        """A real Resource Reviewer always gets authoritative data."""
        reviewer = User.objects.get(username="dev")
        tile = self._tile(
            {
                "9999": self._provisional_edit(
                    {"node": "value"}, "2026-01-01T00:00:00.000000Z"
                )
            }
        )
        result = _resolve_provisional_data(tile, reviewer)
        self.assertIsNone(result)

    def test_real_non_reviewer_cannot_see_others_edit(self):
        non_reviewer = User.objects.get(username="tester1")
        tile = self._tile({"9999": {"value": {"node": "v"}, "status": "review"}})
        result = _resolve_provisional_data(tile, non_reviewer)
        self.assertIsNone(result)

    def _provisional_edit(self, value, timestamp):
        return {
            "value": value,
            "action": "update",
            "status": "review",
            "reviewer": None,
            "timestamp": timestamp,
            "reviewtimestamp": None,
        }

    def test_reviewer_sees_authoritative_data_with_multiple_editors(self):
        """Reviewer sees authoritative data regardless of how many provisional edits exist."""
        tile = self._tile(
            {
                "10": self._provisional_edit(
                    {"node": "oldest"}, "2026-01-01T00:00:00.000000Z"
                ),
                "20": self._provisional_edit(
                    {"node": "newer"}, "2026-06-01T00:00:00.000000Z"
                ),
            }
        )
        reviewer = self._user(1)
        with patch(
            "arches.extensions.querysets.querysets.user_is_resource_reviewer",
            return_value=True,
        ):
            result = _resolve_provisional_data(tile, reviewer)
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# Integration tests — TileTreeQuerySet.get_tiles()
# ---------------------------------------------------------------------------


class TileTreeProvisionalEditsTests(GraphTestCase):
    """Provisional edits are overlaid on aliased_data when opted in via
    provisional_edits_for_user."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        call_command("add_test_users", verbosity=0)

    AUTHORITATIVE_NUMBER = 42
    PROVISIONAL_NUMBER = 99

    def setUp(self):
        self.provisional_editor = User.objects.get(username="tester3")
        self.reviewer = User.objects.get(username="dev")
        self.unrelated_user = User.objects.get(username="tester1")

        # Read current authoritative tile data so we can build a realistic
        # provisional edit that changes only the number node.
        tile = TileModel.objects.get(pk=self.cardinality_1_tile.pk)
        provisional_edits = _make_provisional_edits(
            user_id=self.provisional_editor.pk,
            tile_data=tile.data,
            provisional_number=self.PROVISIONAL_NUMBER,
            number_node_pk=self.number_node_1.pk,
        )
        # Set provisionaledits directly, bypassing save signals.
        # Django TestCase rolls this back after each test.
        TileModel.objects.filter(pk=tile.pk).update(provisionaledits=provisional_edits)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _fetch(self, *, as_representation=False, **kwargs):
        return TileTree.get_tiles(
            "datatype_lookups",
            "datatypes_1",
            as_representation=as_representation,
            **kwargs,
        ).get(pk=self.cardinality_1_tile.pk)

    # ------------------------------------------------------------------
    # Default (opt-out) behaviour
    # ------------------------------------------------------------------

    def test_default_shows_authoritative_data(self):
        """Without provisional_edits_for_user aliased_data reflects tile.data."""
        tile = self._fetch()
        self.assertEqual(tile.aliased_data.number_alias, self.AUTHORITATIVE_NUMBER)

    # ------------------------------------------------------------------
    # Opt-in: edit author
    # ------------------------------------------------------------------

    def test_provisional_editor_sees_own_value(self):
        tile = self._fetch(provisional_edits_for_user=self.provisional_editor)
        self.assertEqual(tile.aliased_data.number_alias, self.PROVISIONAL_NUMBER)

    # ------------------------------------------------------------------
    # Opt-in: Resource Reviewer — always sees authoritative data
    # ------------------------------------------------------------------

    def test_reviewer_sees_authoritative_data(self):
        tile = self._fetch(provisional_edits_for_user=self.reviewer)
        self.assertEqual(tile.aliased_data.number_alias, self.AUTHORITATIVE_NUMBER)

    # ------------------------------------------------------------------
    # Opt-in: unrelated non-reviewer
    # ------------------------------------------------------------------

    def test_unrelated_user_sees_authoritative_data(self):
        """A non-reviewer who did not author the edit sees authoritative data."""
        tile = self._fetch(provisional_edits_for_user=self.unrelated_user)
        self.assertEqual(tile.aliased_data.number_alias, self.AUTHORITATIVE_NUMBER)

    # ------------------------------------------------------------------
    # tile.data integrity
    # ------------------------------------------------------------------

    def test_tile_data_restored_after_evaluation(self):
        """tile.data must hold authoritative values after aliased_data is built;
        the provisional swap must not leak out of the queryset evaluation."""
        tile = self._fetch(provisional_edits_for_user=self.provisional_editor)
        node_id = str(self.number_node_1.pk)
        self.assertEqual(tile.data[node_id], self.AUTHORITATIVE_NUMBER)

    # ------------------------------------------------------------------
    # as_representation=True — display_value also reflects provisional data
    # ------------------------------------------------------------------

    def test_as_representation_provisional_editor_node_value(self):
        tile = self._fetch(
            as_representation=True,
            provisional_edits_for_user=self.provisional_editor,
        )
        self.assertEqual(
            tile.aliased_data.number_alias["node_value"], self.PROVISIONAL_NUMBER
        )

    def test_as_representation_default_node_value_is_authoritative(self):
        tile = self._fetch(as_representation=True)
        self.assertEqual(
            tile.aliased_data.number_alias["node_value"], self.AUTHORITATIVE_NUMBER
        )


# ---------------------------------------------------------------------------
# Integration tests — ResourceTileTreeQuerySet.get_tiles()
# ---------------------------------------------------------------------------


class ResourceTileTreeProvisionalEditsTests(GraphTestCase):
    """provisional_edits_for_user propagates through the prefetch chain to
    tile-level aliased_data when using ResourceTileTree.get_tiles()."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        call_command("add_test_users", verbosity=0)

    AUTHORITATIVE_NUMBER = 42
    PROVISIONAL_NUMBER = 99

    def setUp(self):
        self.provisional_editor = User.objects.get(username="tester3")
        self.reviewer = User.objects.get(username="dev")
        self.unrelated_user = User.objects.get(username="tester1")

        tile = TileModel.objects.get(pk=self.cardinality_1_tile.pk)
        provisional_edits = _make_provisional_edits(
            user_id=self.provisional_editor.pk,
            tile_data=tile.data,
            provisional_number=self.PROVISIONAL_NUMBER,
            number_node_pk=self.number_node_1.pk,
        )
        TileModel.objects.filter(pk=tile.pk).update(provisionaledits=provisional_edits)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _fetch_resource(self, **kwargs):
        return ResourceTileTree.get_tiles(
            "datatype_lookups",
            as_representation=False,
            **kwargs,
        ).get(pk=self.resource_42.pk)

    def _number_value(self, resource):
        return resource.aliased_data.datatypes_1.aliased_data.number_alias

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_default_shows_authoritative_data(self):
        resource = self._fetch_resource()
        self.assertEqual(self._number_value(resource), self.AUTHORITATIVE_NUMBER)

    def test_provisional_editor_sees_own_value(self):
        resource = self._fetch_resource(
            provisional_edits_for_user=self.provisional_editor
        )
        self.assertEqual(self._number_value(resource), self.PROVISIONAL_NUMBER)

    def test_reviewer_sees_authoritative_data(self):
        resource = self._fetch_resource(provisional_edits_for_user=self.reviewer)
        self.assertEqual(self._number_value(resource), self.AUTHORITATIVE_NUMBER)

    def test_unrelated_user_sees_authoritative_data(self):
        resource = self._fetch_resource(provisional_edits_for_user=self.unrelated_user)
        self.assertEqual(self._number_value(resource), self.AUTHORITATIVE_NUMBER)

    def test_tile_data_restored_after_evaluation(self):
        """Authoritative tile.data must be intact after the queryset materialises."""
        resource = self._fetch_resource(
            provisional_edits_for_user=self.provisional_editor
        )
        tile = resource.aliased_data.datatypes_1
        node_id = str(self.number_node_1.pk)
        self.assertEqual(tile.data[node_id], self.AUTHORITATIVE_NUMBER)


# ---------------------------------------------------------------------------
# Integration tests — reprocess_tiles_aliased_data()
# ---------------------------------------------------------------------------


class ReprocessTilesProvisionalEditsTests(GraphTestCase):
    """reprocess_tiles_aliased_data() overlays provisional edits on aliased_data
    when provisional_edits_for_user is supplied."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        call_command("add_test_users", verbosity=0)

    AUTHORITATIVE_NUMBER = 42
    PROVISIONAL_NUMBER = 99

    def setUp(self):
        self.provisional_editor = User.objects.get(username="tester3")

        tile = TileModel.objects.get(pk=self.cardinality_1_tile.pk)
        self.authoritative_tile_data = dict(tile.data)
        provisional_edits = _make_provisional_edits(
            user_id=self.provisional_editor.pk,
            tile_data=tile.data,
            provisional_number=self.PROVISIONAL_NUMBER,
            number_node_pk=self.number_node_1.pk,
        )
        TileModel.objects.filter(pk=tile.pk).update(provisionaledits=provisional_edits)

    def _fetch_tiles(self):
        """Return a list of TileTree instances for the cardinality-1 nodegroup.

        The instances come from a fully evaluated get_tiles() queryset so their
        nodegroup is properly attached.  We clear _tile_trees so that the
        grouping_node_lookup for child tiles is irrelevant to these tests.
        """
        tiles = list(
            TileTree.get_tiles("datatype_lookups", "datatypes_1").filter(
                pk=self.cardinality_1_tile.pk
            )
        )
        for tile in tiles:
            tile._tile_trees = []
        return tiles

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_default_uses_authoritative_data(self):
        tiles = self._fetch_tiles()
        reprocess_tiles_aliased_data(
            tiles, as_representation=False, grouping_node_lookup={}
        )
        self.assertEqual(tiles[0].aliased_data.number_alias, self.AUTHORITATIVE_NUMBER)

    def test_provisional_editor_sees_own_value(self):
        tiles = self._fetch_tiles()
        reprocess_tiles_aliased_data(
            tiles,
            as_representation=False,
            grouping_node_lookup={},
            provisional_edits_for_user=self.provisional_editor,
        )
        self.assertEqual(tiles[0].aliased_data.number_alias, self.PROVISIONAL_NUMBER)

    def test_tile_data_restored_after_reprocess(self):
        """tile.data must revert to the authoritative record after reprocessing."""
        tiles = self._fetch_tiles()
        reprocess_tiles_aliased_data(
            tiles,
            as_representation=False,
            grouping_node_lookup={},
            provisional_edits_for_user=self.provisional_editor,
        )
        node_id = str(self.number_node_1.pk)
        self.assertEqual(tiles[0].data[node_id], self.AUTHORITATIVE_NUMBER)

    def test_reviewer_sees_authoritative_data(self):
        reviewer = User.objects.get(username="dev")
        tiles = self._fetch_tiles()
        reprocess_tiles_aliased_data(
            tiles,
            as_representation=False,
            grouping_node_lookup={},
            provisional_edits_for_user=reviewer,
        )
        self.assertEqual(tiles[0].aliased_data.number_alias, self.AUTHORITATIVE_NUMBER)

    def test_unrelated_user_sees_authoritative_data(self):
        unrelated_user = User.objects.get(username="tester1")
        tiles = self._fetch_tiles()
        reprocess_tiles_aliased_data(
            tiles,
            as_representation=False,
            grouping_node_lookup={},
            provisional_edits_for_user=unrelated_user,
        )
        self.assertEqual(tiles[0].aliased_data.number_alias, self.AUTHORITATIVE_NUMBER)


# ---------------------------------------------------------------------------
# Integration tests — refresh_from_db() and save(provisional_edits_for_user=)
# ---------------------------------------------------------------------------


class SaveWithProvisionalEditsTests(GraphTestCase):
    """provisional_edits_for_user is stored on the instance at load time and
    used automatically by refresh_from_db() and save(), so the in-memory
    aliased_data reflects provisional values without requiring a separate
    get_tiles() call or an explicit param on every operation.

    Covers:
      - refresh_from_db() inherits _provisional_edits_for_user from the instance
      - refresh_from_db() on an instance loaded without a user shows authoritative
      - save() uses _provisional_edits_for_user for the targeted refresh
      - save() on an instance loaded without a user shows authoritative after save
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        call_command("add_test_users", verbosity=0)

    AUTHORITATIVE_NUMBER = 42
    PROVISIONAL_NUMBER = 99

    def setUp(self):
        self.provisional_editor = User.objects.get(username="tester3")

        tile = TileModel.objects.get(pk=self.cardinality_1_tile.pk)
        provisional_edits = _make_provisional_edits(
            user_id=self.provisional_editor.pk,
            tile_data=tile.data,
            provisional_number=self.PROVISIONAL_NUMBER,
            number_node_pk=self.number_node_1.pk,
        )
        TileModel.objects.filter(pk=tile.pk).update(provisionaledits=provisional_edits)

    def _load_resource(self, provisional_edits_for_user=None):
        return ResourceTileTree.get_tiles(
            "datatype_lookups",
            as_representation=False,
            provisional_edits_for_user=provisional_edits_for_user,
        ).get(pk=self.resource_42.pk)

    def _number_value(self, resource):
        return resource.aliased_data.datatypes_1.aliased_data.number_alias

    # ------------------------------------------------------------------
    # refresh_from_db
    # ------------------------------------------------------------------

    def test_refresh_from_db_overlays_provisional_edits(self):
        resource = self._load_resource()
        self.assertEqual(self._number_value(resource), self.AUTHORITATIVE_NUMBER)

        resource._provisional_edits_for_user = self.provisional_editor
        resource.refresh_from_db()

        self.assertEqual(self._number_value(resource), self.PROVISIONAL_NUMBER)

    def test_refresh_from_db_default_inherits_provisional_user(self):
        resource = self._load_resource(
            provisional_edits_for_user=self.provisional_editor
        )
        self.assertEqual(self._number_value(resource), self.PROVISIONAL_NUMBER)

        resource.refresh_from_db()

        self.assertEqual(self._number_value(resource), self.PROVISIONAL_NUMBER)

    # ------------------------------------------------------------------
    # save() — targeted refresh path
    # ------------------------------------------------------------------

    def test_targeted_refresh_applies_provisional_overlay_on_reprocessed_tile(self):
        resource = self._load_resource(
            provisional_edits_for_user=self.provisional_editor
        )
        self.assertEqual(
            self._number_value(resource),
            self.PROVISIONAL_NUMBER,
            "Precondition: provisional overlay active before save",
        )

        # Mutate the same tile to put it in to_update and trigger reprocessing.
        # Save as admin so that provisional_edits dict in the DB is untouched.
        tile = resource.aliased_data.datatypes_1
        tile.aliased_data.non_localized_string_alias = "post-save-string"
        resource.save(force_admin=True)

        # Targeted refresh reprocesses the tile; provisional overlay must be applied.
        self.assertEqual(self._number_value(resource), self.PROVISIONAL_NUMBER)

    def test_targeted_refresh_without_param_shows_authoritative_on_reprocessed_tile(
        self,
    ):
        """save() without provisional_edits_for_user shows authoritative data on
        reprocessed tiles, regardless of whether provisional edits exist."""
        # Fetch WITHOUT provisional overlay so aliased_data holds authoritative values.
        resource = self._load_resource()
        self.assertEqual(self._number_value(resource), self.AUTHORITATIVE_NUMBER)

        tile = resource.aliased_data.datatypes_1
        tile.aliased_data.non_localized_string_alias = "post-save-no-prov"
        resource.save(force_admin=True)  # no provisional_edits_for_user

        # Targeted refresh runs without the overlay; authoritative data is shown.
        self.assertEqual(self._number_value(resource), self.AUTHORITATIVE_NUMBER)


class TileTreeSaveWithProvisionalEditsTests(GraphTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        call_command("add_test_users", verbosity=0)

    AUTHORITATIVE_NUMBER = 42
    PROVISIONAL_NUMBER = 99

    def setUp(self):
        self.provisional_editor = User.objects.get(username="tester3")

        tile = TileModel.objects.get(pk=self.cardinality_1_tile.pk)
        provisional_edits = _make_provisional_edits(
            user_id=self.provisional_editor.pk,
            tile_data=tile.data,
            provisional_number=self.PROVISIONAL_NUMBER,
            number_node_pk=self.number_node_1.pk,
        )
        TileModel.objects.filter(pk=tile.pk).update(provisionaledits=provisional_edits)

    def _load_tile(self, provisional_edits_for_user=None):
        return TileTree.get_tiles(
            "datatype_lookups",
            "datatypes_1",
            provisional_edits_for_user=provisional_edits_for_user,
        ).get(pk=self.cardinality_1_tile.pk)

    def _number_value(self, tile):
        return tile.aliased_data.number_alias

    def test_refresh_from_db_inherits_provisional_user(self):
        """refresh_from_db() with no args uses _provisional_edits_for_user stored
        at load time, preserving the provisional overlay."""
        tile = self._load_tile(provisional_edits_for_user=self.provisional_editor)
        self.assertEqual(self._number_value(tile), self.PROVISIONAL_NUMBER)

        tile.refresh_from_db()

        self.assertEqual(self._number_value(tile), self.PROVISIONAL_NUMBER)

    def test_refresh_from_db_without_stored_user_shows_authoritative(self):
        """refresh_from_db() on a tile loaded without a user shows authoritative."""
        tile = self._load_tile()
        self.assertEqual(self._number_value(tile), self.AUTHORITATIVE_NUMBER)

        tile.refresh_from_db()

        self.assertEqual(self._number_value(tile), self.AUTHORITATIVE_NUMBER)

    def test_save_preserves_provisional_overlay(self):
        """TileTree.save() uses the stored _provisional_edits_for_user so the
        post-save refresh returns provisional data (fixes tile PUT/PATCH endpoint)."""
        tile = self._load_tile(provisional_edits_for_user=self.provisional_editor)
        self.assertEqual(self._number_value(tile), self.PROVISIONAL_NUMBER)

        tile.aliased_data.non_localized_string_alias = "post-save-string"
        tile.save(force_admin=True)

        self.assertEqual(self._number_value(tile), self.PROVISIONAL_NUMBER)

    def test_save_without_stored_user_shows_authoritative(self):
        """TileTree.save() on a tile loaded without a user shows authoritative
        data after save."""
        tile = self._load_tile()
        self.assertEqual(self._number_value(tile), self.AUTHORITATIVE_NUMBER)

        tile.aliased_data.non_localized_string_alias = "post-save-no-prov"
        tile.save(force_admin=True)

        self.assertEqual(self._number_value(tile), self.AUTHORITATIVE_NUMBER)
