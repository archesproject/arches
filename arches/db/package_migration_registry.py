"""
Shared infrastructure for Arches package migrations.

Used by both the runpackagemigrations management command and the
ArchesPackageMigration operation base class so they operate on the same
migration graph and recorder.
"""

import pkgutil
from importlib import import_module

from django.apps import apps
from django.db import DEFAULT_DB_ALIAS, connections

from arches.app.models.models import PackageMigration as PackageMigrationRecord


PACKAGE_MIGRATIONS_SUBMODULE = "package_migrations"

# Sentinel value stored in PackageMigration.operation to mark migration-level
# tracking records (one per applied migration file).  Distinct from the
# per-operation records written by the operations themselves (e.g.
# "UpdateResourceInstancesPublicationId").
APPLIED_SENTINEL = "__applied__"


class PackageMigrationRecorder:
    """
    Tracks applied package migrations using the PackageMigration model,
    analogous to Django's MigrationRecorder for django_migrations.
    """

    def __init__(self, connection):
        self.connection = connection

    def has_table(self):
        with self.connection.cursor() as cursor:
            return "package_migrations" in self.connection.introspection.table_names(
                cursor
            )

    def ensure_schema(self):
        # The package_migrations table is created by Django's own migrate command
        # (via the Arches models migration), so it is guaranteed to exist when
        # this command runs.
        pass

    @property
    def applied_migrations(self):
        """Return a set of (app, name) tuples for applied package migrations."""
        if not self.has_table():
            return set()
        return set(PackageMigrationRecord.objects.filter().values_list("app", "name"))

    def record_applied(self, app, name):
        PackageMigrationRecord.objects.create(app=app, name=name)

    def record_unapplied(self, app, name):
        PackageMigrationRecord.objects.filter(app=app, name=name).delete()


def discover_package_migrations():
    """
    Return a sorted list of (app_label, name, migration_obj) tuples for all
    package migrations found under <app>/migrations/package_migrations/ across all
    installed apps.

    Results are sorted by (app_label, name) so numeric prefixes determine
    execution order within each app.
    """
    from django.core.management.base import CommandError

    result = []
    for app_config in apps.get_app_configs():
        module_path = f"{app_config.name}.migrations.{PACKAGE_MIGRATIONS_SUBMODULE}"
        try:
            pkg = import_module(module_path)
        except ImportError:
            continue

        for _, module_name, is_pkg in pkgutil.iter_modules(pkg.__path__):
            if module_name.startswith("_") or is_pkg:
                continue
            full_path = f"{module_path}.{module_name}"
            try:
                module = import_module(full_path)
            except ImportError as exc:
                raise CommandError(f"Could not import {full_path!r}: {exc}")
            if hasattr(module, "Migration"):
                migration = module.Migration(module_name, app_config.label)
                result.append((app_config.label, module_name, migration))

    result.sort(key=lambda x: (x[0], x[1]))
    return result


def get_next_unapplied_package_migration_name():
    """
    Return the name of the first unapplied package migration, or None if all
    are applied.

    This is called from within a package migration operation's database_forwards
    to determine which migration file is currently being applied.  Because
    runpackagemigrations records a migration as applied only *after* apply()
    returns (i.e. after all database_forwards calls complete), the migration
    currently being executed will always be the first unapplied one.
    """
    connection = connections[DEFAULT_DB_ALIAS]
    recorder = PackageMigrationRecorder(connection)
    applied = recorder.applied_migrations

    for app_label, name, _migration in discover_package_migrations():
        if (app_label, name) not in applied:
            return name

    return None
