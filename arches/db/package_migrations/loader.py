"""Discovery and graph building for package migrations.

MigrationLoader hardcodes MigrationRecorder in two places and MigrationGraph in
one, so build_graph() and check_consistent_history() must be overridden as well
as migrations_module(). Without the build_graph override the loader reads
django_migrations, concludes nothing is applied, and re-runs every package
migration's database_forwards against live data.
"""

from django.apps import apps
from django.db.migrations.exceptions import (
    InconsistentMigrationHistory,
    NodeNotFoundError,
)
from django.db.migrations.loader import MigrationLoader

from arches.db.package_migrations.graph import PackageMigrationGraph
from arches.db.package_migrations.recorder import PackageMigrationRecorder

# The literal "migrations" segment is load-bearing: load_disk only swallows
# ModuleNotFoundError when MIGRATIONS_MODULE_NAME appears in the missing module
# path, so a top-level "<app>.package_migrations" would raise for every app that
# does not ship one.
PACKAGE_MIGRATIONS_MODULE_NAME = "migrations.package_migrations"


class PackageMigrationLoader(MigrationLoader):
    recorder_class = PackageMigrationRecorder
    graph_class = PackageMigrationGraph

    @classmethod
    def migrations_module(cls, app_label):
        app_config = apps.get_app_config(app_label)
        if not getattr(app_config, "is_arches_application", False):
            return None, False
        # explicit=False so load_disk treats a missing package as "unmigrated"
        # rather than raising.
        return f"{app_config.name}.{PACKAGE_MIGRATIONS_MODULE_NAME}", False

    def build_graph(self):
        """Mirrors MigrationLoader.build_graph, substituting the package
        recorder (django loader.py:287) and graph (loader.py:292).
        """
        self.load_disk()
        if self.connection is None:
            self.applied_migrations = {}
        else:
            recorder = self.recorder_class(self.connection)
            self.applied_migrations = recorder.applied_migrations()
        self.graph = self.graph_class()
        self.replacements = {}
        for key, migration in self.disk_migrations.items():
            self.graph.add_node(key, migration)
            if migration.replaces:
                self.replacements[key] = migration
        for key, migration in self.disk_migrations.items():
            self.add_internal_dependencies(key, migration)
        for key, migration in self.disk_migrations.items():
            self.add_external_dependencies(key, migration)
        if self.replace_migrations:
            self.replacements_progress = {}
            for migration_key in self.replacements.keys():
                self.replace_migration(migration_key)
        try:
            self.graph.validate_consistency()
        except NodeNotFoundError as exc:
            reverse_replacements = {}
            for key, migration in self.replacements.items():
                for replaced in migration.replaces:
                    reverse_replacements.setdefault(replaced, set()).add(key)
            if exc.node in reverse_replacements:
                candidates = reverse_replacements.get(exc.node, set())
                is_replaced = any(
                    candidate in self.graph.nodes for candidate in candidates
                )
                if not is_replaced:
                    tries = ", ".join(f"{app}.{name}" for app, name in candidates)
                    raise NodeNotFoundError(
                        "Package migration {0} depends on nonexistent node "
                        "('{1}', '{2}'). Tried [{3}].".format(
                            exc.origin, exc.node[0], exc.node[1], tries
                        ),
                        exc.node,
                    ) from exc
            raise
        self.graph.ensure_not_cyclic()

    def check_consistent_history(self, connection):
        """django loader.py:349 hardcodes MigrationRecorder, which would consult
        django_migrations.
        """
        recorder = self.recorder_class(connection)
        applied = recorder.applied_migrations()
        for migration in applied:
            if migration not in self.graph.nodes:
                continue
            for parent in self.graph.node_map[migration].parents:
                if parent not in applied:
                    if self.all_replaced_applied(parent.key, applied):
                        continue
                    raise InconsistentMigrationHistory(
                        "Package migration {}.{} is applied before its "
                        "dependency {}.{} on database '{}'.".format(
                            migration[0],
                            migration[1],
                            parent[0],
                            parent[1],
                            connection.alias,
                        )
                    )
