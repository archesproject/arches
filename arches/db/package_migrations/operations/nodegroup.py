"""Nodegroup operations."""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    _AlterRowOperation,
    _CreateRowOperation,
    _DeleteRowOperation,
)


class CreateNodeGroup(_CreateRowOperation):
    """grouping_node_id names a collector node CreateNode inserts afterwards. The
    FK is DEFERRABLE INITIALLY DEFERRED, so this relies on an atomic migration."""

    model = models.NodeGroup
    state_collection = "nodegroups"
    pk_field = "nodegroupid"
    verbose_name = "nodegroup"
    has_graph_fk = False


class AlterNodeGroup(_AlterRowOperation):
    model = models.NodeGroup
    state_collection = "nodegroups"
    pk_attribute = "nodegroupid"
    verbose_name = "nodegroup"

    def __init__(self, graphid, nodegroupid, changes):
        super().__init__(graphid, changes)
        self.nodegroupid = nodegroupid


class DeleteNodeGroup(_DeleteRowOperation):
    """ORM-cascades to the nodegroup's Nodes, Cards and (via Card) its
    CardXNodeXWidgets, so the state removal has to follow.

    It does NOT remove tiles: TileModel.nodegroup is db_constraint=False,
    on_delete=DO_NOTHING, so orphaned tiles need DeleteTilesForNodeGroup.

    Irreversible: the cascade destroys rows this operation does not record.
    """

    model = models.NodeGroup
    state_collection = "nodegroups"
    verbose_name = "nodegroup"
    has_graph_fk = False
    reversible = False

    def state_forwards(self, app_label, state):
        graph = state.graph(self.graphid)
        graph["nodegroups"].pop(self._pk, None)
        for collection in ("nodes", "cards"):
            for key, entry in list(graph.get(collection, {}).items()):
                if str(entry.get("nodegroup_id")) == self._pk:
                    del graph[collection][key]
