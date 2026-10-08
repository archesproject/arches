from django.conf import settings

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.package_migrations.state import STATE_COLLECTIONS
from arches.db.package_migrations.operations.base import (
    PackageMigrationError,
    PackageOperation,
    _AlterRowOperation,
    _short,
)


class CreateGraph(PackageOperation):
    """Reversible only while the graph holds no resources.

    Not Graph.objects.create_graph(): its random ids and draft are not reproducible.
    """

    reversible = True
    scope = "graph"
    model = models.GraphModel
    serialization_expand_args = ["fields"]

    def __init__(self, fields):
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
            fields["resource_instance_lifecycle_id"] = (
                settings.DEFAULT_RESOURCE_INSTANCE_LIFECYCLE_ID
            )
        self.qs(models.GraphModel, schema_editor).create(**fields)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if self.has_resources(schema_editor.connection.alias):
            raise PackageMigrationError(
                f"Graph {self.graphid} has resource instances. Deleting it would "
                "delete them and their tiles."
            )
        self.qs(models.GraphModel, schema_editor).filter(pk=self.graphid).delete()

    def has_resources(self, using):
        return (
            models.ResourceInstance.objects.using(using)
            .filter(graph_id=self.graphid)
            .exists()
        )

    def describe(self):
        return f"Create graph {self.fields.get('slug') or self.graphid}"

    @property
    def migration_name_fragment(self):
        return f"graph_{self.fields.get('slug') or _short(self.graphid)}"


class AlterGraph(_AlterRowOperation):
    # A queryset update, not Graph.save(): validate() refuses a published slug change.
    model = models.GraphModel
    verbose_name = "graph"

    def __init__(self, graphid, changes):
        super().__init__(graphid, graphid, changes)

    def _entry(self, state):
        return state.graph(self.graphid)

    def _entry_for_write(self, state):
        return state.graph_for_write(self.graphid)


class PublishGraph(PackageOperation):
    """Put the graph on the publication the authoring database was on.

    Refreshes that publication if it already exists, else creates it.
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
        return self.previous_publication_id is not None

    @property
    def updates_in_place(self):
        return str(self.publication_id) == str(self.previous_publication_id)

    def state_forwards(self, app_label, state):
        state.graph_for_write(self.graphid)["publication_id"] = str(self.publication_id)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        alias = schema_editor.connection.alias
        if (
            self.qs(models.GraphXPublishedGraph, schema_editor)
            .filter(pk=self.publication_id)
            .exists()
        ):
            self.qs(models.GraphModel, schema_editor).filter(pk=self.graphid).update(
                publication_id=self.publication_id
            )
            self.refresh(alias)
        else:
            Graph.objects.using(alias).get(pk=self.graphid).publish(
                notes=self.notes, publication_id=self.publication_id
            )

    def refresh(self, using):
        Graph.objects.using(using).get(pk=self.graphid).update_published_graphs(
            notes=self.notes
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if self.previous_publication_id is None:
            raise NotImplementedError(
                f"PublishGraph for graph {self.graphid} has no previous "
                "publication to restore."
            )
        if self.updates_in_place:
            # The executor re-snapshots it once the reversed rows are back.
            return
        publications = self.qs(models.GraphXPublishedGraph, schema_editor)
        if not publications.filter(pk=self.previous_publication_id).exists():
            raise PackageMigrationError(
                f"Graph {self.graphid} cannot go back to publication "
                f"{self.previous_publication_id}: this database never had it, "
                "because the migration that created it was recorded with --fake here."
            )
        remaining = (
            self.qs(models.ResourceInstance, schema_editor)
            .filter(graph_publication_id=self.publication_id)
            .count()
        )
        if remaining:
            raise PackageMigrationError(
                f"{remaining} resources of graph {self.graphid} are still on "
                f"publication {self.publication_id}. Unapply the data migration "
                "that follows this one as well, by targeting a migration before both."
            )
        # The graph references this publication, so it moves back before the delete.
        self.qs(models.GraphModel, schema_editor).filter(pk=self.graphid).update(
            publication_id=self.previous_publication_id
        )
        publications.filter(pk=self.publication_id).delete()

    def describe(self):
        return f"Publish graph {self.graphid} as {self.publication_id}"

    @property
    def migration_name_fragment(self):
        return f"publish_{_short(self.publication_id)}"
