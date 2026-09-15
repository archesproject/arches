"""Edge operations.

An edge carries the ontology relationship between two nodes. It changes
independently of either node -- ontologyproperty can be corrected without the
nodes moving -- so it gets its own Create/Alter/Delete rather than riding along
with CreateNode.
"""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    PackageOperation,
    _AlterRowOperation,
)


class CreateEdge(PackageOperation):
    reversible = True

    def __init__(
        self,
        graphid,
        edgeid,
        domainnode_id,
        rangenode_id,
        ontologyproperty=None,
        name=None,
        description=None,
    ):
        self.graphid = graphid
        self.edgeid = edgeid
        self.domainnode_id = domainnode_id
        self.rangenode_id = rangenode_id
        self.ontologyproperty = ontologyproperty
        self.name = name
        self.description = description

    def state_forwards(self, app_label, state):
        state.graphs[str(self.graphid)].setdefault("edges", {})[str(self.edgeid)] = {
            "edgeid": str(self.edgeid),
            "domainnode_id": str(self.domainnode_id),
            "rangenode_id": str(self.rangenode_id),
            "ontologyproperty": self.ontologyproperty,
            "name": self.name,
            "description": self.description,
        }

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.Edge, schema_editor).create(
            edgeid=self.edgeid,
            graph_id=self.graphid,
            domainnode_id=self.domainnode_id,
            rangenode_id=self.rangenode_id,
            ontologyproperty=self.ontologyproperty,
            name=self.name,
            description=self.description,
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.Edge, schema_editor).filter(pk=self.edgeid).delete()

    def describe(self):
        return "Create edge %s on graph %s" % (self.edgeid, self.graphid)

    @property
    def migration_name_fragment(self):
        return "edge_%s" % str(self.edgeid).replace("-", "")[:8]


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


class DeleteEdge(PackageOperation):
    reversible = True

    def __init__(self, graphid, edgeid):
        self.graphid = graphid
        self.edgeid = edgeid

    def state_forwards(self, app_label, state):
        del state.graphs[str(self.graphid)]["edges"][str(self.edgeid)]

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.Edge, schema_editor).filter(pk=self.edgeid).delete()

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        edge = to_state.graphs[str(self.graphid)]["edges"][str(self.edgeid)]
        self.qs(models.Edge, schema_editor).create(
            edgeid=edge["edgeid"],
            graph_id=self.graphid,
            domainnode_id=edge["domainnode_id"],
            rangenode_id=edge["rangenode_id"],
            ontologyproperty=edge.get("ontologyproperty"),
            name=edge.get("name"),
            description=edge.get("description"),
        )

    def describe(self):
        return "Delete edge %s from graph %s" % (self.edgeid, self.graphid)

    @property
    def migration_name_fragment(self):
        return "delete_edge_%s" % str(self.edgeid).replace("-", "")[:8]
