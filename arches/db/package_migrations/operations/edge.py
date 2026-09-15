"""Edge operations.

An edge carries the ontology relationship between two nodes and changes
independently of either -- ontologyproperty can be corrected without the nodes
moving -- so it gets its own operations.
"""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    _AlterRowOperation,
    _CreateRowOperation,
    _DeleteRowOperation,
)


class CreateEdge(_CreateRowOperation):
    model = models.Edge
    state_collection = "edges"
    pk_field = "edgeid"

    def describe(self):
        return "Create edge %s on graph %s" % (self._pk, self.graphid)

    @property
    def migration_name_fragment(self):
        return "edge_%s" % self._pk.replace("-", "")[:8]


class AlterEdge(_AlterRowOperation):
    model = models.Edge
    state_collection = "edges"
    pk_attribute = "edgeid"

    def __init__(self, graphid, edgeid, changes):
        super().__init__(graphid, changes)
        self.edgeid = edgeid

    def describe(self):
        return "Alter edge %s (%s)" % (self.edgeid, ", ".join(sorted(self.changes)))

    @property
    def migration_name_fragment(self):
        return "alter_edge_%s" % str(self.edgeid).replace("-", "")[:8]


class DeleteEdge(_DeleteRowOperation):
    model = models.Edge
    state_collection = "edges"
    pk_field = "edgeid"

    def describe(self):
        return "Delete edge %s from graph %s" % (self.pk, self.graphid)

    @property
    def migration_name_fragment(self):
        return "delete_edge_%s" % str(self.pk).replace("-", "")[:8]
