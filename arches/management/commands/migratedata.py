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
from django.db.migrations.loader import MigrationLoader

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
                forwards = [f"{app}.{name}" for (app, name, _), bw in plan if not bw]
                backwards = [f"{app}.{name}" for (app, name, _), bw in plan if bw]
                if forwards:
                    self.stdout.write(
                        self.style.MIGRATE_LABEL("  Apply: ") + ", ".join(forwards)
                    )
                if backwards:
                    self.stdout.write(
                        self.style.MIGRATE_LABEL("  Unapply: ") + ", ".join(backwards)
                    )
            else:
                self.stdout.write("  (none)")

        if self.verbosity >= 1:
            self.stdout.write(self.style.MIGRATE_HEADING("Running data migrations:"))

        if not plan:
            if self.verbosity >= 1:
                self.stdout.write("  No data migrations to apply.")
            return

        state = MigrationLoader(connection).project_state()
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
        representing the migrations to run, in execution order.

        Supports:
          - No target: apply all unapplied migrations.
          - Named target (unapplied): apply forward up to and including it.
          - Named target (already applied): unapply back to just after it.
          - "zero": unapply all applied migrations in reverse order.
        """
        app_label = options.get("app_label")
        migration_name = options.get("migration_name")

        scoped = [
            (app, name, mig)
            for app, name, mig in all_migrations
            if not app_label or app == app_label
        ]

        if migration_name == "zero":
            return [
                ((app, name, mig), True)
                for app, name, mig in reversed(scoped)
                if (app, name) in applied
            ]

        if migration_name:
            target_idx = next(
                (
                    i
                    for i, (_, name, __) in enumerate(scoped)
                    if name.startswith(migration_name)
                ),
                None,
            )
            if target_idx is None:
                raise CommandError(
                    f"Data migration {migration_name!r} not found"
                    + (f" for app {app_label!r}" if app_label else "")
                    + "."
                )
            target_app, target_name, _ = scoped[target_idx]
            if (target_app, target_name) in applied:
                # Target is already applied — unapply everything after it.
                return [
                    ((app, name, mig), True)
                    for app, name, mig in reversed(scoped[target_idx + 1 :])
                    if (app, name) in applied
                ]
            else:
                # Target not yet applied — apply forward up to and including it.
                return [
                    ((app, name, mig), False)
                    for app, name, mig in scoped[: target_idx + 1]
                    if (app, name) not in applied
                ]

        # Default: apply all unapplied in order.
        return [
            ((app, name, mig), False)
            for app, name, mig in scoped
            if (app, name) not in applied
        ]

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
