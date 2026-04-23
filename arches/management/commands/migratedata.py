"""
Arches rundatamigrations management command.

Applies data migrations found in <app>/migrations/data_migrations/ directories,
tracking applied migrations using the DataMigration model (analogous to how
Django's migrate command uses the django_migrations table via MigrationRecorder).
"""

import time

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError, no_translations
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.state import ProjectState

from arches.db.data_migration_registry import (
    DataMigrationRecorder,
    discover_data_migrations,
)


class Command(BaseCommand):
    help = (
        "Applies data migrations stored in <app>/migrations/data_migrations/ "
        "directories, tracking state in the DataMigration model."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "app_label",
            nargs="?",
            help="App label to limit migrations to.",
        )
        parser.add_argument(
            "migration_name",
            nargs="?",
            help=(
                "Target migration name. Only migrations up to and including "
                "this name will be applied."
            ),
        )
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_false",
            dest="interactive",
            help="Tells Django to NOT prompt the user for input of any kind.",
        )
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            choices=tuple(connections),
            help=(
                'Nominates a database to synchronize. Defaults to the "default" database.'
            ),
        )
        parser.add_argument(
            "--fake",
            action="store_true",
            help="Mark migrations as run without actually running them.",
        )
        parser.add_argument(
            "--plan",
            action="store_true",
            help="Shows a list of the migration actions that will be performed.",
        )

    @no_translations
    def handle(self, *args, **options):
        database = options["database"]
        self.verbosity = options["verbosity"]
        self.interactive = options["interactive"]
        connection = connections[database]

        recorder = DataMigrationRecorder(connection)

        # Validate app_label if provided.
        app_label = options["app_label"]
        if app_label:
            try:
                apps.get_app_config(app_label)
            except LookupError as exc:
                raise CommandError(str(exc))

        # Discover all data migrations on disk.
        all_migrations = discover_data_migrations()

        # Determine which migrations have already been applied.
        applied = recorder.applied_migrations

        # Build the ordered plan of migrations to execute.
        plan = self._build_plan(all_migrations, applied, options)

        if options["plan"]:
            self._print_plan(plan)
            return

        if self.verbosity >= 1:
            self.stdout.write(self.style.MIGRATE_HEADING("Operations to perform:"))
            if plan:
                self.stdout.write(
                    self.style.MIGRATE_LABEL("  Apply all data migrations: ")
                    + ", ".join(
                        f"{app}.{name}"
                        for (app, name, _), backwards in plan
                        if not backwards
                    )
                )
            else:
                self.stdout.write("  (none)")

        if self.verbosity >= 1:
            self.stdout.write(self.style.MIGRATE_HEADING("Running data migrations:"))

        if not plan:
            if self.verbosity >= 1:
                self.stdout.write("  No data migrations to apply.")
            return

        state = ProjectState()
        with connection.schema_editor() as schema_editor:
            for (app, name, migration), backwards in plan:
                if backwards:
                    state = self._unapply(
                        migration, state, schema_editor, recorder, options["fake"]
                    )
                else:
                    state = self._apply(
                        migration, state, schema_editor, recorder, options["fake"]
                    )

    def _build_plan(self, all_migrations, applied, options):
        """
        Return a list of ((app_label, name, migration_obj), backwards) tuples
        representing the migrations that need to be applied, in execution order.
        """
        app_label = options.get("app_label")
        migration_name = options.get("migration_name")

        plan = []
        for app, name, migration in all_migrations:
            if app_label and app != app_label:
                continue
            if (app, name) not in applied:
                plan.append(((app, name, migration), False))
            # Stop after the target migration if one was specified.
            if migration_name and name.startswith(migration_name):
                break

        return plan

    def _apply(self, migration, state, schema_editor, recorder, fake):
        if self.verbosity >= 1:
            compute_time = self.verbosity > 1
            start = time.monotonic() if compute_time else None
            self.stdout.write(
                f"  Applying {migration.app_label}.{migration.name}...", ending=""
            )
            self.stdout.flush()

        if not fake:
            state = migration.apply(state, schema_editor)

        recorder.record_applied(migration.app_label, migration.name)

        if self.verbosity >= 1:
            elapsed = f" ({time.monotonic() - start:.3f}s)" if start else ""
            self.stdout.write(self.style.SUCCESS(" FAKED" if fake else " OK") + elapsed)

        return state

    def _unapply(self, migration, state, schema_editor, recorder, fake):
        if self.verbosity >= 1:
            compute_time = self.verbosity > 1
            start = time.monotonic() if compute_time else None
            self.stdout.write(
                f"  Unapplying {migration.app_label}.{migration.name}...", ending=""
            )
            self.stdout.flush()

        if not fake:
            state = migration.unapply(state, schema_editor)

        recorder.record_unapplied(migration.app_label, migration.name)

        if self.verbosity >= 1:
            elapsed = f" ({time.monotonic() - start:.3f}s)" if start else ""
            self.stdout.write(self.style.SUCCESS(" FAKED" if fake else " OK") + elapsed)

        return state

    def _print_plan(self, plan):
        self.stdout.write(
            "Planned data migration operations:", self.style.MIGRATE_LABEL
        )
        if not plan:
            self.stdout.write("  No planned data migration operations.")
            return
        for (app_label, name, migration), backwards in plan:
            prefix = "Undo " if backwards else ""
            self.stdout.write(
                f"  {prefix}{app_label}.{name}", self.style.MIGRATE_HEADING
            )
            for operation in migration.operations:
                self.stdout.write(f"    {operation.describe()}")
