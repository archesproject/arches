"""MigrationExecutor with package state, loader and recorder."""

from django.db import transaction
from django.db.migrations.executor import MigrationExecutor

from arches.app.models import models
from arches.db.package_migrations.loader import PackageMigrationLoader
from arches.db.package_migrations.operations.graph import PublishGraph
from arches.db.package_migrations.recorder import PackageMigrationRecorder
from arches.db.package_migrations.state import PackageState


class PackageMigrationExecutor(MigrationExecutor):
    loader_class = PackageMigrationLoader
    recorder_class = PackageMigrationRecorder
    state_class = PackageState

    def __init__(self, connection, progress_callback=None):
        self.connection = connection
        self.loader = self.loader_class(self.connection)
        self.recorder = self.recorder_class(self.connection)
        self.progress_callback = progress_callback

    def _create_project_state(self, with_applied_migrations=False):
        state = self.state_class()
        if with_applied_migrations:
            full_plan = self.migration_plan(
                self.loader.graph.leaf_nodes(), clean_start=True
            )
            applied_migrations = {
                self.loader.graph.nodes[key]
                for key in self.loader.applied_migrations
                if key in self.loader.graph.nodes
            }
            for migration, _ in full_plan:
                if migration in applied_migrations:
                    migration.mutate_state(state, preserve=False)
        return state

    def unapply_migration(self, state, migration, fake=False):
        publications = [
            operation
            for operation in migration.operations
            if isinstance(operation, PublishGraph)
        ]
        if fake or not publications:
            return super().unapply_migration(state, migration, fake=fake)

        alias = self.connection.alias
        graphs = models.GraphModel.objects.using(alias)
        flags_before = {
            str(graphid): has_unpublished_changes
            for graphid, has_unpublished_changes in graphs.filter(
                pk__in=[publication.graphid for publication in publications]
            ).values_list("graphid", "has_unpublished_changes")
        }
        with transaction.atomic(using=alias):
            state = super().unapply_migration(state, migration, fake=fake)
            # Reversed rows after PublishGraph re-flag the graph as unpublished.
            for publication in publications:
                if publication.updates_in_place:
                    publication.refresh(alias)
                else:
                    graphs.filter(pk=publication.graphid).update(
                        has_unpublished_changes=flags_before[str(publication.graphid)]
                    )
        return state

    def detect_soft_applied(self, project_state, migration):
        # Django's version returns a mutated state, which would be applied twice.
        return False, project_state
