"""MigrationLoader for package migrations. build_graph() and
check_consistent_history() are overridden because Django hardcodes its own
recorder and graph in them.
"""

from django.apps import apps
from django.db.migrations.exceptions import (
    InconsistentMigrationHistory,
    NodeNotFoundError,
)
from django.db.migrations.loader import MigrationLoader

from arches.db.package_migrations.graph import PackageMigrationGraph
from arches.db.package_migrations.recorder import PackageMigrationRecorder

# load_disk only tolerates a missing module whose path contains "migrations".
PACKAGE_MIGRATIONS_MODULE_NAME = "migrations.package_migrations"


class PackageMigrationLoader(MigrationLoader):
    recorder_class = PackageMigrationRecorder
    graph_class = PackageMigrationGraph

    @classmethod
    def migrations_module(cls, app_label):
        app_config = apps.get_app_config(app_label)
        if not getattr(app_config, "is_arches_application", False):
            return None, False
        return f"{app_config.name}.{PACKAGE_MIGRATIONS_MODULE_NAME}", False

    def build_graph(self):
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
        except NodeNotFoundError as node_not_found_error:
            reverse_replacements = {}
            for key, migration in self.replacements.items():
                for replaced in migration.replaces:
                    reverse_replacements.setdefault(replaced, set()).add(key)
            if node_not_found_error.node in reverse_replacements:
                candidates = reverse_replacements[node_not_found_error.node]
                is_replaced = any(
                    candidate in self.graph.nodes for candidate in candidates
                )
                if not is_replaced:
                    tries = ", ".join(f"{app}.{name}" for app, name in candidates)
                    missing_app_label, missing_name = node_not_found_error.node
                    raise NodeNotFoundError(
                        f"Package migration {node_not_found_error.origin} depends on nonexistent node ('{missing_app_label}', '{missing_name}'). Tried [{tries}].",
                        node_not_found_error.node,
                    ) from node_not_found_error
            raise
        self.graph.ensure_not_cyclic()

    def check_consistent_history(self, connection):
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
                        f"Package migration {migration[0]}.{migration[1]} is applied before its dependency {parent[0]}.{parent[1]} on database '{connection.alias}'."
                    )
