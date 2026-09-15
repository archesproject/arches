"""Publication lifecycle operations.

These three always run last and always together, but they are three operations
because they are three things that happen: a publication row is created,
resources are moved onto it, and the graph's draft copy is regenerated. The
autodetector is responsible for emitting them in that order.

RefreshDraftGraph is not optional. Every Arches graph carries a draft copy, and
the only supported edit path is promote_draft_graph_to_active_graph(), which
rebuilds the live graph entirely from that draft. A migration mutates the live
graph and leaves the draft stale, so the next Graph Designer publish reverts the
whole migration and CASCADE-deletes tiles in any nodegroup it added -- while the
ledger still says applied. Regenerating the draft from the migrated graph closes
that loop.
"""

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.package_migrations.operations.base import PackageOperation


class PublishGraph(PackageOperation):
    """Mint a publication with a portable id."""

    reversible = True

    def __init__(
        self, graphid, publication_id, previous_publication_id=None, notes=None
    ):
        self.graphid = graphid
        self.publication_id = publication_id
        self.previous_publication_id = previous_publication_id
        self.notes = notes

    def state_forwards(self, app_label, state):
        state.graphs[str(self.graphid)]["publication_id"] = str(self.publication_id)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        graph = Graph.objects.get(pk=self.graphid)
        graph.publish(notes=self.notes, publication_id=self.publication_id)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if self.previous_publication_id is None:
            raise NotImplementedError(
                "PublishGraph for graph %s has no previous publication to restore."
                % self.graphid
            )
        # Point the graph back at its prior publication, then drop the one this
        # operation minted. Order matters: graphs.publicationid references it.
        self.qs(models.GraphModel, schema_editor).filter(pk=self.graphid).update(
            publication_id=self.previous_publication_id, has_unpublished_changes=False
        )
        self.qs(models.GraphXPublishedGraph, schema_editor).filter(
            pk=self.publication_id
        ).delete()

    def describe(self):
        return "Publish graph %s as %s" % (self.graphid, self.publication_id)

    @property
    def migration_name_fragment(self):
        return "publish_%s" % str(self.publication_id).replace("-", "")[:8]


class RepointResourceInstances(PackageOperation):
    """Move resources from one publication to another.

    Set-based and bypassing save(): ResourceInstance.save() would re-stamp
    graph_publication from the graph anyway, and doing this per row on a
    multi-million-resource graph is the single most expensive thing a migration
    can do.

    Without this, every resource stays on the old publication and the resource
    editor redirects to the read-only report for all of them.
    """

    reversible = True
    requires_non_atomic_migration = True

    def __init__(self, graphid, from_publication_id, to_publication_id):
        self.graphid = graphid
        self.from_publication_id = from_publication_id
        self.to_publication_id = to_publication_id

    def state_forwards(self, app_label, state):
        pass

    def _repoint(self, schema_editor, from_publication_id, to_publication_id):
        return (
            self.qs(models.ResourceInstance, schema_editor)
            .filter(graph_id=self.graphid, graph_publication_id=from_publication_id)
            .update(graph_publication_id=to_publication_id)
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        return self._repoint(
            schema_editor, self.from_publication_id, self.to_publication_id
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        return self._repoint(
            schema_editor, self.to_publication_id, self.from_publication_id
        )

    def describe(self):
        return "Repoint resources on graph %s to publication %s" % (
            self.graphid,
            self.to_publication_id,
        )

    @property
    def migration_name_fragment(self):
        return "repoint_%s" % str(self.to_publication_id).replace("-", "")[:8]


class RefreshDraftGraph(PackageOperation):
    """Regenerate the graph's draft from its current (migrated) state.

    Safe to delete the old draft: copy(set_source=True) mints new ids for the
    draft's own nodegroups, so no tile references them, and TileModel.nodegroup is
    db_constraint=False / on_delete=DO_NOTHING regardless. A draft holds structure
    only, never business data.
    """

    reversible = False

    def __init__(self, graphid):
        self.graphid = graphid

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        graph = Graph.objects.get(pk=self.graphid)
        try:
            graph.delete_draft_graph()
        except Graph.DoesNotExist:
            pass
        Graph.objects.get(pk=self.graphid).create_draft_graph()

    def describe(self):
        return "Refresh draft graph for %s" % self.graphid

    @property
    def migration_name_fragment(self):
        return "refresh_draft_%s" % str(self.graphid).replace("-", "")[:8]
