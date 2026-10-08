from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    _AlterRowOperation,
    _CreateRowOperation,
    _DeleteRowOperation,
)


class CreateNodeGroup(_CreateRowOperation):
    # grouping_node_id's FK is deferred, so this relies on an atomic migration.

    model = models.NodeGroup
    verbose_name = "nodegroup"


class AlterNodeGroup(_AlterRowOperation):
    model = models.NodeGroup
    verbose_name = "nodegroup"


class DeleteNodeGroup(_DeleteRowOperation):
    """Cascades to the nodegroup's nodes, cards, widgets and edges, but not tiles.

    Irreversible: the cascade destroys rows this operation does not record.
    """

    model = models.NodeGroup
    verbose_name = "nodegroup"
    reversible = False

    def state_forwards(self, app_label, state):
        graph = state.graph_for_write(self.graphid)
        graph["nodegroups"].pop(self._pk, None)

        gone = {"nodes": set(), "cards": set()}
        for collection in gone:
            for key, entry in list(graph.get(collection, {}).items()):
                if str(entry.get("nodegroup_id")) == self._pk:
                    gone[collection].add(key)
                    del graph[collection][key]

        for key, widget in list(graph.get("widgets", {}).items()):
            if str(widget.get("card_id")) in gone["cards"]:
                del graph["widgets"][key]

        for key, edge in list(graph.get("edges", {}).items()):
            ends = {str(edge.get("domainnode_id")), str(edge.get("rangenode_id"))}
            if ends & gone["nodes"]:
                del graph["edges"][key]
