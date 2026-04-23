"""
Arches showdatamigrations management command.

Lists all data migrations found in <app>/migrations/data_migrations/ directories,
showing which have been applied and which are pending — modelled on Django's
built-in showmigrations command.
"""

import sys
from itertools import groupby

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections

from arches.app.models.models import DataMigration as DataMigrationRecord
from arches.db.data_migration_registry import (
    APPLIED_SENTINEL,
    DataMigrationRecorder,
    discover_data_migrations,
)


class Command(BaseCommand):
    help = "Shows all available data migrations and whether they have been applied."

    def add_arguments(self, parser):
        parser.add_argument(
            "app_label",
            nargs="*",
            help="App labels to limit output to (default: all apps).",
        )
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            choices=tuple(connections),
            help='Nominates a database to inspect. Defaults to the "default" database.',
        )
        formats = parser.add_mutually_exclusive_group()
        formats.add_argument(
            "--list",
            "-l",
            action="store_const",
            dest="format",
            const="list",
            help=(
                "Show migrations grouped by app, with [X] applied and [ ] pending. "
                "At verbosity 2+, the applied datetime is included."
            ),
        )
        formats.add_argument(
            "--plan",
            "-p",
            action="store_const",
            dest="format",
            const="plan",
            help="Show all migrations in execution order with their applied status.",
        )
        parser.set_defaults(format="list")

    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]
        connection = connections[options["database"]]
        recorder = DataMigrationRecorder(connection)
        applied = recorder.applied_migrations

        all_migrations = discover_data_migrations()

        app_labels = options["app_label"]
        if app_labels:
            self._validate_app_labels(app_labels)
            all_migrations = [m for m in all_migrations if m[0] in app_labels]

        if options["format"] == "plan":
            self._show_plan(all_migrations, applied)
        else:
            self._show_list(all_migrations, applied)

    def _validate_app_labels(self, app_labels):
        has_bad = False
        for label in app_labels:
            try:
                apps.get_app_config(label)
            except LookupError as exc:
                self.stderr.write(str(exc))
                has_bad = True
        if has_bad:
            sys.exit(2)

    def _applied_datetimes(self):
        """Return {(app, name): applied_datetime} for all applied data migrations."""
        return {
            (r.app, r.name): r.applied
            for r in DataMigrationRecord.objects.filter(operation=APPLIED_SENTINEL)
        }

    def _show_list(self, all_migrations, applied):
        datetimes = self._applied_datetimes() if self.verbosity >= 2 else {}

        for app_label, group in groupby(all_migrations, key=lambda x: x[0]):
            self.stdout.write(app_label, self.style.MIGRATE_LABEL)
            migrations = list(group)
            if not migrations:
                self.stdout.write("  (no data migrations)", self.style.ERROR)
                continue
            for _, name, _ in migrations:
                if (app_label, name) in applied:
                    line = f" [X] {name}"
                    if self.verbosity >= 2 and (app_label, name) in datetimes:
                        line += f" (applied at {datetimes[(app_label, name)].strftime('%Y-%m-%d %H:%M:%S')})"
                    self.stdout.write(line)
                else:
                    self.stdout.write(f" [ ] {name}")

        if not all_migrations:
            self.stdout.write("(no data migrations found)", self.style.ERROR)

    def _show_plan(self, all_migrations, applied):
        if not all_migrations:
            self.stdout.write("(no data migrations found)", self.style.ERROR)
            return

        datetimes = self._applied_datetimes() if self.verbosity >= 2 else {}

        for app_label, name, _ in all_migrations:
            if (app_label, name) in applied:
                line = f"[X]  {app_label}.{name}"
                if self.verbosity >= 2 and (app_label, name) in datetimes:
                    line += f" (applied at {datetimes[(app_label, name)].strftime('%Y-%m-%d %H:%M:%S')})"
            else:
                line = f"[ ]  {app_label}.{name}"
            self.stdout.write(line)
