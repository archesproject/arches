"""Nodegroup operations."""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    _AlterRowOperation,
    _CreateRowOperation,
    _DeleteRowOperation,
)


class CreateNodeGroup(_CreateRowOperation):
    model = models.NodeGroup
    state_collection = "nodegroups"
    pk_field = "nodegroupid"
    has_graph_fk = False

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # grouping_node is a real FK to the collector Node, which does not exist
        # yet when the nodegroup is created. node_groups.grouping_node_matches_pk_or_null
        # constrains it to the nodegroup's own pk, so the collector node shares
        # the id and the reference is set once that node exists.
        fields = dict(self.fields)
        grouping_node_id = fields.pop("grouping_node_id", None)
        self.qs(models.NodeGroup, schema_editor).create(**fields)
        if grouping_node_id is not None:
            self.qs(models.NodeGroup, schema_editor).filter(pk=self._pk).update(
                grouping_node_id=grouping_node_id
            )

    def describe(self):
        return "Create nodegroup %s on graph %s" % (self._pk, self.graphid)

    @property
    def migration_name_fragment(self):
        return "nodegroup_%s" % self._pk.replace("-", "")[:8]


class AlterNodeGroup(_AlterRowOperation):
    model = models.NodeGroup
    state_collection = "nodegroups"
    pk_attribute = "nodegroupid"

    def __init__(self, graphid, nodegroupid, changes):
        super().__init__(graphid, changes)
        self.nodegroupid = nodegroupid

    def describe(self):
        return "Alter nodegroup %s (%s)" % (
            self.nodegroupid,
            ", ".join(sorted(self.changes)),
        )

    @property
    def migration_name_fragment(self):
        return "alter_nodegroup_%s" % str(self.nodegroupid).replace("-", "")[:8]


class DeleteNodeGroup(_DeleteRowOperation):
    """ORM-cascades to the nodegroup's Nodes, Cards and (via Card) its
    CardXNodeXWidgets, so the state removal has to follow.

    It does NOT remove tiles: TileModel.nodegroup is db_constraint=False,
    on_delete=DO_NOTHING, so orphaned tiles need DeleteTilesForNodeGroup.

    Irreversible: the cascade destroys rows this operation does not record.
    """

    model = models.NodeGroup
    state_collection = "nodegroups"
    pk_field = "nodegroupid"
    has_graph_fk = False
    reversible = False

    def state_forwards(self, app_label, state):
        graph = state.graphs[str(self.graphid)]
        graph["nodegroups"].pop(self._pk, None)
        for collection in ("nodes", "cards"):
            for key, entry in list(graph.get(collection, {}).items()):
                if str(entry.get("nodegroup_id")) == self._pk:
                    del graph[collection][key]

    def describe(self):
        return "Delete nodegroup %s from graph %s" % (self.pk, self.graphid)

    @property
    def migration_name_fragment(self):
        return "delete_nodegroup_%s" % str(self.pk).replace("-", "")[:8]
