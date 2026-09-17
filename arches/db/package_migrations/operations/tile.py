"""Tile operations.

These are set-based BECAUSE the transformations here are datatype-agnostic:
adding or removing a JSON key with a literal value carries no datatype meaning,
creates no relationships and no geometries. Anything that does need datatype
semantics -- converting stored values, for instance -- must go through the
datatype layer instead, per tile. No operation in this module may branch on a
node's datatype; that knowledge belongs to DDataType and the datatype factory.

Derived state (Elasticsearch, geojson_geometries, resource_x_resource) is NOT
this module's concern either. Operations report which resources they touched and
the runner reconciles those graphs once, post-commit, using the maintenance
routines Arches already owns.

Avoiding the Tile proxy is also a hard performance requirement: Tile.__init__
calls load_serialized_graph(), which fetches a PublishedGraph row and parses a
multi-megabyte JSON blob per instance.

Selection is by tile CONTENT, never by resource_instances.graph_publication_id:
ResourceInstance.save() re-stamps that column on every write, so it is not a
stable marker of which shape a record's data is in.
"""

import json

from django.db.models import JSONField
from django.db.models.expressions import RawSQL

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    PackageOperation,
    keyset_batches,
)

DEFAULT_BATCH_SIZE = 5000


class _ChunkedTileOperation(PackageOperation):
    """Shared keyset-chunking over (nodegroupid, tileid).

    Leading underscore: __init_subclass__ skips the contract checks for
    intermediate bases.
    """

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
    """Add a node's key to tiles that do not have it yet.

    Idempotent by construction: the NOT (tiledata ? nodeid) predicate is the
    version test done directly, so a killed run simply resumes.
    """

    reversible = True

    def __init__(self, nodegroup_id, nodeid, value=None, batch_size=DEFAULT_BATCH_SIZE):
        self.nodegroup_id = nodegroup_id
        self.nodeid = nodeid
        self.value = value
        self.batch_size = batch_size

    def state_forwards(self, app_label, state):
        pass  # data only, like RunPython

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        return self._apply_in_batches(
            self._tiles(schema_editor.connection.alias).exclude(
                data__has_key=str(self.nodeid)
            ),
            RawSQL(
                "jsonb_set(tiledata, ARRAY[%s], %s::jsonb)",
                [str(self.nodeid), json.dumps(self.value)],
                output_field=JSONField(),
            ),
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        return self._drop_key(schema_editor)

    def describe(self):
        return "Add node %s to tiles in nodegroup %s" % (
            self.nodeid,
            self.nodegroup_id,
        )

    @property
    def migration_name_fragment(self):
        return "add_node_to_tiles_%s" % str(self.nodeid).replace("-", "")[:8]


class RemoveNodeFromTiles(_ChunkedTileOperation):
    """Strip a node's key from every tile in its nodegroup.

    Must run AFTER the node row is gone: TileModel.save() calls
    set_missing_keys_to_none(), which re-adds a key for any live Node in the
    nodegroup, so removing data while the node still exists is undone by the next
    ordinary save.

    Irreversible -- the values are discarded and nothing captures them.
    """

    reversible = False

    def __init__(self, nodegroup_id, nodeid, batch_size=DEFAULT_BATCH_SIZE):
        self.nodegroup_id = nodegroup_id
        self.nodeid = nodeid
        self.batch_size = batch_size

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        total = self._drop_key(schema_editor)
        self._prune_provisional_edits(schema_editor)
        return total

    def _prune_provisional_edits(self, schema_editor):
        """A pending provisional edit is keyed by the same nodeids as tiledata.

        A stale key there is written back into data when a reviewer approves the
        edit, and Tile.save() then raises Node.DoesNotExist because the node is
        gone -- a record no curator can fix from the UI. Arches' own graph-diff
        path prunes them for the same reason.
        """
        alias = schema_editor.connection.alias
        pending = self._tiles(alias).filter(provisionaledits__isnull=False)
        expression = RawSQL(
            # provisionaledits is {user_id: {"value": {nodeid: ...}, ...}}, so the
            # key has to come out of every user's edit, not off the top level.
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
        return "Remove node %s from tiles in nodegroup %s" % (
            self.nodeid,
            self.nodegroup_id,
        )

    @property
    def migration_name_fragment(self):
        return "remove_node_from_tiles_%s" % str(self.nodeid).replace("-", "")[:8]


class DeleteTilesForNodeGroup(_ChunkedTileOperation):
    """Remove tiles belonging to a nodegroup that no longer exists.

    TileModel.nodegroup is db_constraint=False, on_delete=DO_NOTHING, so deleting
    a nodegroup leaves its tiles behind with nothing to reference.

    Irreversible: the tiles and their data are gone.
    """

    reversible = False

    def __init__(self, nodegroup_id, batch_size=DEFAULT_BATCH_SIZE):
        self.nodegroup_id = nodegroup_id
        self.batch_size = batch_size

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        alias = schema_editor.connection.alias
        tiles = self._tiles(alias)
        total = 0
        for tileids in keyset_batches(tiles, "tileid", self.batch_size):
            models.TileModel.objects.using(alias).filter(tileid__in=tileids).delete()
            total += len(tileids)
        return total

    def describe(self):
        return "Delete tiles for nodegroup %s" % self.nodegroup_id

    @property
    def migration_name_fragment(self):
        return "delete_tiles_%s" % str(self.nodegroup_id).replace("-", "")[:8]
