"""Set-based tile operations. They must stay datatype-agnostic, avoid the Tile proxy,
and select tiles by content, never by graph_publication_id.
"""

import json

from django.db.models import JSONField, Q
from django.db.models.expressions import RawSQL

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    DEFAULT_BATCH_SIZE,
    PackageOperation,
    _short,
    keyset_batches,
)


class _ChunkedTileOperation(PackageOperation):
    scope = "data"

    def _tiles(self, alias):
        return models.TileModel.objects.using(alias).filter(
            nodegroup_id=self.nodegroup_id
        )

    def _drop_key(self, schema_editor):
        alias = schema_editor.connection.alias
        return self._apply_in_batches(
            self._tiles(alias).filter(data__has_key=str(self.nodeid)),
            RawSQL("tiledata - %s", [str(self.nodeid)], output_field=JSONField()),
        )

    def _apply_in_batches(self, base_queryset, expression):
        total = 0
        for tileids in keyset_batches(base_queryset, "tileid", self.batch_size):
            base_queryset.filter(tileid__in=tileids).update(data=expression)
            total += len(tileids)
        return total


class AddNodeToTiles(_ChunkedTileOperation):
    """Add a node's key to tiles that do not have it yet; a killed run resumes."""

    reversible = True

    def __init__(self, nodegroup_id, nodeid, value=None, batch_size=DEFAULT_BATCH_SIZE):
        self.nodegroup_id = nodegroup_id
        self.nodeid = nodeid
        self.value = value
        self.batch_size = batch_size

    def state_forwards(self, app_label, state):
        pass

    def _pending(self, alias):
        return self._tiles(alias).exclude(data__has_key=str(self.nodeid))

    def has_pending_work(self, using):
        return self._pending(using).exists()

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        return self._apply_in_batches(
            self._pending(schema_editor.connection.alias),
            RawSQL(
                "jsonb_set(tiledata, ARRAY[%s], %s::jsonb)",
                [str(self.nodeid), json.dumps(self.value)],
                output_field=JSONField(),
            ),
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        return self._drop_key(schema_editor)

    def describe(self):
        return f"Add node {self.nodeid} to tiles in nodegroup {self.nodegroup_id}"

    @property
    def migration_name_fragment(self):
        return f"add_node_to_tiles_{_short(self.nodeid)}"


class RemoveNodeFromTiles(_ChunkedTileOperation):
    """Strip a node's key from every tile in its nodegroup. Irreversible.

    Must run after the node is deleted, or the next TileModel.save() re-adds the key.
    """

    reversible = False

    def __init__(self, nodegroup_id, nodeid, batch_size=DEFAULT_BATCH_SIZE):
        self.nodegroup_id = nodegroup_id
        self.nodeid = nodeid
        self.batch_size = batch_size

    def state_forwards(self, app_label, state):
        pass

    def has_pending_work(self, using):
        return (
            self._tiles(using)
            .filter(
                Q(data__has_key=str(self.nodeid)) | Q(provisionaledits__isnull=False)
            )
            .exists()
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        total = self._drop_key(schema_editor)
        self._prune_provisional_edits(schema_editor)
        return total

    def _prune_provisional_edits(self, schema_editor):
        alias = schema_editor.connection.alias
        pending = self._tiles(alias).filter(provisionaledits__isnull=False)
        expression = RawSQL(
            # provisionaledits is {user_id: {"value": {nodeid: ...}, ...}}.
            """
            COALESCE((
                SELECT jsonb_object_agg(
                    edit.key,
                    CASE WHEN edit.value ? 'value'
                        THEN jsonb_set(
                            edit.value, '{value}', (edit.value -> 'value') - %s
                        )
                        ELSE edit.value
                    END
                )
                FROM jsonb_each(provisionaledits) AS edit
            ), provisionaledits)
            """,
            [str(self.nodeid)],
            output_field=JSONField(),
        )
        for tileids in keyset_batches(pending, "tileid", self.batch_size):
            pending.filter(tileid__in=tileids).update(provisionaledits=expression)

    def describe(self):
        return f"Remove node {self.nodeid} from tiles in nodegroup {self.nodegroup_id}"

    @property
    def migration_name_fragment(self):
        return f"remove_node_from_tiles_{_short(self.nodeid)}"


class DeleteTilesForNodeGroup(_ChunkedTileOperation):
    """Remove tiles left behind by a deleted nodegroup. Irreversible."""

    reversible = False

    def __init__(self, nodegroup_id, batch_size=DEFAULT_BATCH_SIZE):
        self.nodegroup_id = nodegroup_id
        self.batch_size = batch_size

    def state_forwards(self, app_label, state):
        pass

    def has_pending_work(self, using):
        return self._tiles(using).exists()

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        alias = schema_editor.connection.alias
        tiles = self._tiles(alias)
        total = 0
        for tileids in keyset_batches(tiles, "tileid", self.batch_size):
            models.TileModel.objects.using(alias).filter(tileid__in=tileids).delete()
            total += len(tileids)
        return total

    def describe(self):
        return f"Delete tiles for nodegroup {self.nodegroup_id}"

    @property
    def migration_name_fragment(self):
        return f"delete_tiles_{_short(self.nodegroup_id)}"
