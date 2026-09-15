"""Nodegroup operations.

A nodegroup alone is not usable: a collector nodegroup with no CardModel is
invisible and uneditable in the resource editor, because the card API filters
``graph.cardmodel_set.filter(nodegroup__in=permitted_nodegroups)``. The
autodetector always pairs CreateNodeGroup with CreateCard; the card is a separate
operation because a card row is a separate thing that gets created.
"""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    PackageOperation,
    _AlterRowOperation,
)


class CreateNodeGroup(PackageOperation):
    reversible = True

    def __init__(
        self,
        graphid,
        nodegroupid,
        cardinality="1",
        parentnodegroup_id=None,
        grouping_node_id=None,
        legacygroupid=None,
    ):
        self.graphid = graphid
        self.nodegroupid = nodegroupid
        self.cardinality = cardinality
        self.parentnodegroup_id = parentnodegroup_id
        # node_groups.grouping_node_matches_pk_or_null constrains this to the
        # nodegroup's own pk or NULL, so the collector node shares the nodegroup id.
        self.grouping_node_id = grouping_node_id
        self.legacygroupid = legacygroupid

    def state_forwards(self, app_label, state):
        state.graphs[str(self.graphid)].setdefault("nodegroups", {})[
            str(self.nodegroupid)
        ] = {
            "nodegroupid": str(self.nodegroupid),
            "cardinality": self.cardinality,
            "parentnodegroup_id": (
                str(self.parentnodegroup_id)
                if self.parentnodegroup_id is not None
                else None
            ),
            "grouping_node_id": (
                str(self.grouping_node_id)
                if self.grouping_node_id is not None
                else None
            ),
            "legacygroupid": self.legacygroupid,
        }

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.NodeGroup, schema_editor).create(
            nodegroupid=self.nodegroupid,
            cardinality=self.cardinality,
            parentnodegroup_id=self.parentnodegroup_id,
            legacygroupid=self.legacygroupid,
        )
        if self.grouping_node_id is not None:
            # Set separately: the collector Node row does not exist yet when the
            # nodegroup is created, and grouping_node is a real FK.
            self.qs(models.NodeGroup, schema_editor).filter(pk=self.nodegroupid).update(
                grouping_node_id=self.grouping_node_id
            )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.NodeGroup, schema_editor).filter(pk=self.nodegroupid).delete()

    def describe(self):
        return "Create nodegroup %s on graph %s" % (self.nodegroupid, self.graphid)

    @property
    def migration_name_fragment(self):
        return "nodegroup_%s" % str(self.nodegroupid).replace("-", "")[:8]


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


class DeleteNodeGroup(PackageOperation):
    """Deleting a nodegroup ORM-cascades to its Nodes, Cards and (via Card) its
    CardXNodeXWidgets. It does NOT remove tiles: TileModel.nodegroup is
    db_constraint=False, on_delete=DO_NOTHING, so orphaned tiles must be cleared
    by DeleteTilesForNodeGroup.

    Irreversible: the cascade destroys rows this operation does not record.
    """

    reversible = False

    def __init__(self, graphid, nodegroupid):
        self.graphid = graphid
        self.nodegroupid = nodegroupid

    def state_forwards(self, app_label, state):
        graph = state.graphs[str(self.graphid)]
        graph.get("nodegroups", {}).pop(str(self.nodegroupid), None)
        for collection in ("nodes", "cards"):
            for key, entry in list(graph.get(collection, {}).items()):
                if str(entry.get("nodegroup_id")) == str(self.nodegroupid):
                    del graph[collection][key]

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.NodeGroup, schema_editor).filter(pk=self.nodegroupid).delete()

    def describe(self):
        return "Delete nodegroup %s from graph %s" % (self.nodegroupid, self.graphid)

    @property
    def migration_name_fragment(self):
        return "delete_nodegroup_%s" % str(self.nodegroupid).replace("-", "")[:8]
