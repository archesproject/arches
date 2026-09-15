"""Execution for package migrations.

Injecting the loader and recorder is not enough: _create_project_state()
hardcodes ProjectState (django executor.py:80) and is reached from three
branches of migrate() plus _migrate_all_backwards(). detect_soft_applied() is
CreateModel/AddField-specific and returns a MUTATED state while reporting False,
so inheriting it silently double-applies state under --fake-initial.
"""

from django.db.migrations.executor import MigrationExecutor

from arches.db.package_migrations.loader import PackageMigrationLoader
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
        state = self.state_class(real_apps=self.loader.unmigrated_apps)
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

    def detect_soft_applied(self, project_state, migration):
        """Django's implementation introspects information_schema for
        CreateModel/AddField operations. Package operations are never either, so
        it always reports False while handing back a mutated state, which then
        gets migrated on top of. Adoption of an already-loaded package is handled
        by `migratepkg --stamp`, not by soft-apply detection.
        """
        return False, project_state
