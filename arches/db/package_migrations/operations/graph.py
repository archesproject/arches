"""Graph operations: the graph row, its publication, and its draft copy.

CreateGraph uses models.GraphModel.objects.create(), NOT
Graph.objects.create_graph(). The latter mints a random root nodeid, publishes
with a random publicationid and creates a second GraphModel row (a draft), none
of which a migration can predict or reproduce on another install -- and the
leftover draft then makes Graph.validate() raise code 1019 for every later
operation in the same migration.

(The NotImplementedError guard lives on the Graph PROXY's manager;
models.GraphModel.objects is a plain manager.)
"""

from django.conf import settings

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.package_migrations.canonical import STATE_COLLECTIONS
from arches.db.package_migrations.operations.base import (
    PackageOperation,
    _AlterRowOperation,
    _short,
)


class CreateGraph(PackageOperation):
    """Irreversible: deleting a graph CASCADEs through ResourceInstance to every
    tile on it. Removing a graph is a deliberate, separately-confirmed act, not
    the reverse of a migration.
    """

    reversible = False
    scope = "graph"
    serialization_expand_args = ["fields"]

    def __init__(self, fields):
        # The graph's own id lives in fields, like every other row's pk.
        self.fields = fields

    @property
    def graphid(self):
        return str(self.fields["graphid"])

    def state_forwards(self, app_label, state):
        graph = dict(self.fields)
        graph["graphid"] = self.graphid
        graph.update({collection: {} for collection in STATE_COLLECTIONS})
        state.add_graph(graph)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        fields = dict(self.fields)
        if fields.get("resource_instance_lifecycle_id") is None and fields.get(
            "isresource"
        ):
            # graphs.resource_instance_lifecycle_conditional_null requires a
            # non-null lifecycle on every non-draft resource graph.
            fields["resource_instance_lifecycle_id"] = (
                settings.DEFAULT_RESOURCE_INSTANCE_LIFECYCLE_ID
            )
        self.qs(models.GraphModel, schema_editor).create(**fields)

    def describe(self):
        return "Create graph %s" % (self.fields.get("slug") or self.graphid)

    @property
    def migration_name_fragment(self):
        return "graph_%s" % (self.fields.get("slug") or _short(self.graphid))


class AlterGraph(_AlterRowOperation):
    """Graph metadata and ontology.

    Writes through a queryset update rather than Graph.save(): validate() raises
    code 1018 ("You cannot change the slug of a published graph").
    """

    model = models.GraphModel
    state_collection = None  # the graph dict itself, not a collection on it
    verbose_name = "graph"

    @property
    def _pk(self):
        return self.graphid

    def _entry(self, state):
        return state.graph(self.graphid)


class PublishGraph(PackageOperation):
    """Mint a publication with a portable id.

    Graph rows only. Moving resources onto the publication is SetResourcePublication's
    job, in the data operations -- these two run in the same migration but they are
    not the same change, and the reverse order matters: unapply() reverses operation
    order, so the resources come off this publication before it is deleted.
    """

    reversible = True
    scope = "graph"

    def __init__(
        self, graphid, publication_id, previous_publication_id=None, notes=None
    ):
        self.graphid = graphid
        self.publication_id = publication_id
        self.previous_publication_id = previous_publication_id
        self.notes = notes

    def state_forwards(self, app_label, state):
        state.graph(self.graphid)["publication_id"] = str(self.publication_id)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        Graph.objects.using(schema_editor.connection.alias).get(
            pk=self.graphid
        ).publish(notes=self.notes, publication_id=self.publication_id)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if self.previous_publication_id is None:
            raise NotImplementedError(
                "PublishGraph for graph %s has no previous publication to restore."
                % self.graphid
            )
        # graphs.publicationid references the publication this operation minted,
        # so the graph moves back before it is deleted. Resources are already off
        # it: SetResourcePublication runs after this one, so it reverses first.
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


class RefreshDraftGraph(PackageOperation):
    """Regenerate the graph's draft from its current (migrated) state.

    Safe to delete the old draft: copy(set_source=True) mints new ids for the
    draft's own nodegroups, so no tile references them, and TileModel.nodegroup is
    db_constraint=False / on_delete=DO_NOTHING regardless. A draft holds structure
    only, never business data.
    """

    reversible = False
    scope = "graph"

    def __init__(self, graphid):
        self.graphid = graphid

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        graph = Graph.objects.using(schema_editor.connection.alias).get(pk=self.graphid)
        if graph.get_draft_graph():
            graph.delete_draft_graph()
        graph.create_draft_graph()

    def describe(self):
        return "Refresh draft graph for %s" % self.graphid

    @property
    def migration_name_fragment(self):
        return "refresh_draft_%s" % str(self.graphid).replace("-", "")[:8]
