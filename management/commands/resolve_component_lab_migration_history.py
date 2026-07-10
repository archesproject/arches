from django.apps import apps as global_apps
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections, migrations
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder


class Command(BaseCommand):
    help = (
        "Repairs migration history and data left inconsistent by the "
        "arches_component_lab to arches_vue_components switchover. Applies "
        "arches_vue_components's own migrations directly (bypassing "
        "check_consistent_history, which would otherwise block `migrate` "
        "entirely), then re-runs the RunPython effect of every other "
        "already-applied migration that depends on arches_vue_components, "
        "using whatever code is currently on disk for it. Safe to run "
        "repeatedly and in any partial state - nobody's migration history "
        "is ever touched."
    )

    def add_arguments(self, parser):
        parser.add_argument("--database", default=DEFAULT_DB_ALIAS)

    def handle(self, *args, **options):
        connection = connections[options["database"]]
        executor = MigrationExecutor(connection)
        recorder = MigrationRecorder(connection)
        applied = recorder.applied_migrations()

        consumers = []
        for migration_key in applied:
            if migration_key[0] == "arches_vue_components":
                continue
            node = executor.loader.graph.node_map.get(migration_key)
            if node is None:
                continue
            if any(parent[0] == "arches_vue_components" for parent in node.parents):
                consumers.append(migration_key)

        vue_components_targets = [
            key
            for key in executor.loader.graph.leaf_nodes()
            if key[0] == "arches_vue_components"
        ]
        self.stdout.write("Applying arches_vue_components's migrations...")
        executor.migrate(vue_components_targets)

        if not consumers:
            self.stdout.write(
                self.style.SUCCESS("No consumer migrations to re-sync. Done.")
            )
            return

        self.stdout.write(
            "Re-syncing the effect of these migrations, using the code "
            "currently on disk for each:"
        )
        with connection.schema_editor(
            atomic=connection.features.can_rollback_ddl
        ) as schema_editor:
            for app, name in consumers:
                self.stdout.write(f"  - {app}.{name}")
                migration = executor.loader.disk_migrations[(app, name)]
                for operation in migration.operations:
                    if isinstance(operation, migrations.RunPython):
                        operation.code(global_apps, schema_editor)

        self.stdout.write(self.style.SUCCESS("Done."))
