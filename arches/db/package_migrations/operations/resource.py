"""Resource instance operations.

A resource's graph_publication says "this resource matches the published graph".
It is business data, not graph structure: it moves only after the tile operations
have brought the resource's data in line, which is why this lives here and runs
after them.
"""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    DEFAULT_BATCH_SIZE,
    PackageMigrationError,
    PackageOperation,
    keyset_batches,
)


class SetResourcePublication(PackageOperation):
    """Move a graph's resources onto a publication.

    Every resource of the graph moves, in both directions, not only those on the
    publication being left: a site that adopted package migrations with --fake
    never had that publication, so a from-scoped update there matches nothing and
    silently leaves every resource pinned to the old one, where the editor
    redirects them to the read-only report.

    That is only true because the operations before it have already brought every
    tile of the graph in line: the stamp says "this resource matches the
    published graph", so it must run last.

    Set-based rather than save(): ResourceInstance.save() would re-stamp
    graph_publication from the graph anyway, and doing this per row on a
    multi-million-resource graph is the single most expensive thing a migration
    can do.
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
        # Nowhere to move resources back to without the previous publication.
        return self.previous_publication_id is not None

    def state_forwards(self, app_label, state):
        pass  # data only, like RunPython

    def _current_publication(self, alias):
        # The graph's CURRENT publication, not the one recorded here. They are the
        # same on any install that ran the graph migration, and they differ where
        # the graph migration was recorded rather than run. Reading it makes this
        # operation say what it means: resources match the graph.
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
            # Updated in place: the publication is the one resources were already on.
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
        """Batched: one UPDATE over every resource of a large graph is a single
        long statement, a lock on every row it touches, and the first thing to die
        under statement_timeout."""
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
        return f"resource_publication_{str(self.publication_id).replace('-', '')[:8]}"
