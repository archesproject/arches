"""Node operations.

Structural only: creating a node does not put a key in any tile and deleting one
does not remove it. That is what the data operations are for, and keeping them
separate is what lets a chunked backfill run in its own non-atomic migration.

A non-collector node must be paired with a CreateEdge joining it to the tree.
Graph.copy() nulls every non-collector node's nodegroup and rebuilds membership
with populate_null_nodegroups(), which walks edges -- a stranded node makes the
graph uncopyable, so create_draft_graph() and promote_draft_graph_to_active_graph()
both fail.
"""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    _AlterRowOperation,
    _CreateRowOperation,
    _DeleteRowOperation,
)


class CreateNode(_CreateRowOperation):
    model = models.Node
    state_collection = "nodes"
    pk_field = "nodeid"

    def describe(self):
        return "Create node %s (%s) on graph %s" % (
            self.fields.get("alias"),
            self.fields.get("datatype"),
            self.graphid,
        )

    @property
    def migration_name_fragment(self):
        return "node_%s" % (self.fields.get("alias") or self._pk.replace("-", "")[:8])


class AlterNode(_AlterRowOperation):
    """Datatype, config, alias, name, isrequired and friends.

    A datatype change alters only the node row; converting the values already
    stored in tiles is CoerceNodeData's job, and must be in the same migration --
    arches_querysets casts tile JSONB straight to the node's declared datatype.
    """

    model = models.Node
    state_collection = "nodes"
    pk_attribute = "nodeid"

    def __init__(self, graphid, nodeid, changes):
        super().__init__(graphid, changes)
        self.nodeid = nodeid

    def describe(self):
        return "Alter node %s (%s)" % (self.nodeid, ", ".join(sorted(self.changes)))

    @property
    def migration_name_fragment(self):
        return "alter_node_%s" % str(self.nodeid).replace("-", "")[:8]


class DeleteNode(_DeleteRowOperation):
    model = models.Node
    state_collection = "nodes"
    pk_field = "nodeid"

    def describe(self):
        return "Delete node %s from graph %s" % (self.pk, self.graphid)

    @property
    def migration_name_fragment(self):
        return "delete_node_%s" % str(self.pk).replace("-", "")[:8]
