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
    _short,
)


class CreateNode(_CreateRowOperation):
    model = models.Node
    state_collection = "nodes"
    pk_field = "nodeid"
    verbose_name = "node"

    @property
    def _label(self):
        return "%s (%s)" % (self.fields.get("alias"), self.fields.get("datatype"))

    @property
    def _fragment(self):
        return self.fields.get("alias") or _short(self._pk)


class AlterNode(_AlterRowOperation):
    """Datatype, config, alias, name, isrequired and friends.

    A datatype change alters only the node row; converting the values already
    stored in tiles needs a hand-written RunPackagePython migration in the same
    release -- arches_querysets casts tile JSONB straight to the node's declared
    datatype.
    """

    model = models.Node
    state_collection = "nodes"
    pk_attribute = "nodeid"
    verbose_name = "node"

    def __init__(self, graphid, nodeid, changes):
        super().__init__(graphid, changes)
        self.nodeid = nodeid


class DeleteNode(_DeleteRowOperation):
    model = models.Node
    state_collection = "nodes"
    verbose_name = "node"
