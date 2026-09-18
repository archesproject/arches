"""Graph operations: the graph row and its publication.

The draft copy is derived state: migratepkg drops a stale one after a run.

CreateGraph uses models.GraphModel.objects.create(), NOT
Graph.objects.create_graph(). The latter mints a random root nodeid, publishes
with a random publicationid and creates a second GraphModel row (a draft), none
of which a migration can predict or reproduce on another install, and the
leftover draft then makes Graph.validate() raise code 1019 for every later
operation in the same migration.

(The NotImplementedError guard lives on the Graph PROXY's manager;
models.GraphModel.objects is a plain manager.)
"""

from django.conf import settings

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.package_migrations.state import STATE_COLLECTIONS
from arches.db.package_migrations.operations.base import (
    PackageOperation,
    _AlterRowOperation,
    _short,
)


class CreateGraph(PackageOperation):
    """Reversible only while the graph holds no resources.

    ResourceInstance.graph is on_delete=CASCADE, so deleting a graph destroys
    every resource on it and every tile under them. Rolling back a package on a
    dev machine, in CI, or on a fresh install is ordinary and safe; rolling one
    back on a site with data is not the same act at all, and migratepkg refuses
    it before anything runs rather than discovering it halfway through.
    """

    reversible = True
    scope = "graph"
    model = models.GraphModel
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

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if self.has_resources(schema_editor.connection.alias):
            raise ValueError(
                "Graph %s has resource instances. Deleting it would delete them "
                "and their tiles." % self.graphid
            )
        self.qs(models.GraphModel, schema_editor).filter(pk=self.graphid).delete()

    def has_resources(self, using):
        return (
            models.ResourceInstance.objects.using(using)
            .filter(graph_id=self.graphid)
            .exists()
        )

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
    verbose_name = "graph"

    def __init__(self, graphid, changes):
        super().__init__(graphid, graphid, changes)

    def _entry(self, state):
        return state.graph(self.graphid)

    def _entry_for_write(self, state):
        return state.graph_for_write(self.graphid)


class PublishGraph(PackageOperation):
    """Mint a publication with a portable id.

    Graph rows only. Moving resources onto the publication is SetResourcePublication's
    job, in the data operations. These two run in the same migration, but they are
    not the same change, and the reverse order matters: unapply() reverses operation
    order, so the resources come off this publication before it is deleted.
    """

    scope = "graph"

    def __init__(
        self, graphid, publication_id, previous_publication_id=None, notes=None
    ):
        self.graphid = graphid
        self.publication_id = publication_id
        self.previous_publication_id = previous_publication_id
        self.notes = notes

    @property
    def reversible(self):
        # Nothing to restore without the publication this one replaced.
        return self.previous_publication_id is not None

    def state_forwards(self, app_label, state):
        state.graph_for_write(self.graphid)["publication_id"] = str(self.publication_id)

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
