"""Tile-data operations.

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
from arches.db.package_migrations.operations.base import PackageOperation

DEFAULT_BATCH_SIZE = 5000


class _ChunkedTileDataOperation(PackageOperation):
    """Shared keyset-chunking over (nodegroupid, tileid).

    Leading underscore: __init_subclass__ skips the contract checks for
    intermediate bases.
    """

    requires_non_atomic_migration = True

    def _apply_in_batches(self, schema_editor, queryset_fn, expression):
        alias = schema_editor.connection.alias
        total = 0
        last_tileid = None
        while True:
            queryset = queryset_fn(alias)
            if last_tileid is not None:
                queryset = queryset.filter(tileid__gt=last_tileid)
            tileids = list(
                queryset.order_by("tileid").values_list("tileid", flat=True)[
                    : self.batch_size
                ]
            )
            if not tileids:
                break
            models.TileModel.objects.using(alias).filter(tileid__in=tileids).update(
                data=expression
            )
            total += len(tileids)
            last_tileid = tileids[-1]
        return total


class BackfillNodeData(_ChunkedTileDataOperation):
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
            schema_editor,
            lambda alias: models.TileModel.objects.using(alias)
            .filter(nodegroup_id=self.nodegroup_id)
            .exclude(data__has_key=str(self.nodeid)),
            RawSQL(
                "jsonb_set(tiledata, ARRAY[%s], %s::jsonb)",
                [str(self.nodeid), json.dumps(self.value)],
                output_field=JSONField(),
            ),
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        return self._apply_in_batches(
            schema_editor,
            lambda alias: models.TileModel.objects.using(alias).filter(
                nodegroup_id=self.nodegroup_id, data__has_key=str(self.nodeid)
            ),
            RawSQL("tiledata - %s", [str(self.nodeid)], output_field=JSONField()),
        )

    def describe(self):
        return "Backfill tile data for node %s" % self.nodeid

    @property
    def migration_name_fragment(self):
        return "backfill_%s" % str(self.nodeid).replace("-", "")[:8]


class RemoveNodeData(_ChunkedTileDataOperation):
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
        return self._apply_in_batches(
            schema_editor,
            lambda alias: models.TileModel.objects.using(alias).filter(
                nodegroup_id=self.nodegroup_id, data__has_key=str(self.nodeid)
            ),
            RawSQL("tiledata - %s", [str(self.nodeid)], output_field=JSONField()),
        )

    def describe(self):
        return "Remove tile data for node %s" % self.nodeid

    @property
    def migration_name_fragment(self):
        return "remove_data_%s" % str(self.nodeid).replace("-", "")[:8]
