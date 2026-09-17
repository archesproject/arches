"""Resource instance operations.

A resource's graph_publication says "this resource matches the published graph".
It is business data, not graph structure: it moves only after the tile operations
have brought the resource's data in line, which is why this lives here and runs
after them.
"""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    PackageOperation,
    keyset_batches,
)

DEFAULT_BATCH_SIZE = 5000


class SetResourcePublication(PackageOperation):
    """Move a graph's resources onto a publication.

    Every resource of the graph moves, not only those on previous_publication_id:
    a site that adopted package migrations with --fake never had that publication,
    so a from-scoped update there matches nothing and silently leaves every
    resource pinned to the old one, where the editor redirects them to the
    read-only report.

    That is only true because the operations before it have already brought every
    tile of the graph in line -- the stamp says "this resource matches the
    published graph", so it must run last.

    Set-based rather than save(): ResourceInstance.save() would re-stamp
    graph_publication from the graph anyway, and doing this per row on a
    multi-million-resource graph is the single most expensive thing a migration
    can do.
    """

    reversible = True
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

    def state_forwards(self, app_label, state):
        pass  # data only, like RunPython

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        return self._move(
            self.qs(models.ResourceInstance, schema_editor)
            .filter(graph_id=self.graphid)
            .exclude(graph_publication_id=self.publication_id),
            self.publication_id,
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if self.previous_publication_id is None:
            raise NotImplementedError(
                "SetResourcePublication for graph %s has no previous publication "
                "to move resources back to." % self.graphid
            )
        return self._move(
            self.qs(models.ResourceInstance, schema_editor).filter(
                graph_id=self.graphid, graph_publication_id=self.publication_id
            ),
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
        return "Set resources on graph %s to publication %s" % (
            self.graphid,
            self.publication_id,
        )

    @property
    def migration_name_fragment(self):
        return "resource_publication_%s" % str(self.publication_id).replace("-", "")[:8]
