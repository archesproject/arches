from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    DEFAULT_BATCH_SIZE,
    PackageMigrationError,
    PackageOperation,
    _short,
    keyset_batches,
)


class SetResourcePublication(PackageOperation):
    """Move every resource of a graph onto its current publication, after the tiles.

    Not scoped to the publication being left: a site adopted with --fake never had it.
    """

    scope = "data"

    def __init__(
        self,
        graphid,
        publication_id,
        previous_publication_id=None,
        batch_size=DEFAULT_BATCH_SIZE,
    ):
        self.graphid = graphid
        self.publication_id = publication_id
        self.previous_publication_id = previous_publication_id
        self.batch_size = batch_size

    @property
    def reversible(self):
        return self.previous_publication_id is not None

    def state_forwards(self, app_label, state):
        pass

    def _current_publication(self, alias):
        # Not self.publication_id: the two differ where the graph migration was faked.
        return (
            models.GraphModel.objects.using(alias)
            .filter(pk=self.graphid)
            .values_list("publication_id", flat=True)
            .first()
        )

    def _pending(self, alias, publication_id):
        return (
            models.ResourceInstance.objects.using(alias)
            .filter(graph_id=self.graphid)
            .exclude(graph_publication_id=publication_id)
        )

    def has_pending_work(self, using):
        publication_id = self._current_publication(using)
        if publication_id is None:
            return True
        return self._pending(using, publication_id).exists()

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        alias = schema_editor.connection.alias
        publication_id = self._current_publication(alias)
        if publication_id is None:
            raise PackageMigrationError(
                f"Graph {self.graphid} has no publication to move its resources onto."
            )
        return self._move(self._pending(alias, publication_id), publication_id)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if self.previous_publication_id is None:
            raise NotImplementedError(
                f"SetResourcePublication for graph {self.graphid} has no previous "
                "publication to move resources back to."
            )
        if str(self.publication_id) == str(self.previous_publication_id):
            return 0
        alias = schema_editor.connection.alias
        if (
            not models.GraphXPublishedGraph.objects.using(alias)
            .filter(pk=self.previous_publication_id)
            .exists()
        ):
            raise PackageMigrationError(
                f"Graph {self.graphid} cannot go back to publication "
                f"{self.previous_publication_id}: this database never had it, "
                "because the migration that created it was recorded with --fake here."
            )
        return self._move(
            self._pending(alias, self.previous_publication_id),
            self.previous_publication_id,
        )

    def _move(self, queryset, publication_id):
        total = 0
        for keys in keyset_batches(queryset, "resourceinstanceid", self.batch_size):
            total += queryset.filter(resourceinstanceid__in=keys).update(
                graph_publication_id=publication_id
            )
        return total

    def describe(self):
        return f"Set resources on graph {self.graphid} to its current publication"

    @property
    def migration_name_fragment(self):
        return f"resource_publication_{_short(self.publication_id)}"
