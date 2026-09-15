"""Writing package migration files.

MigrationWriter.basedir calls MigrationLoader.migrations_module on the BASE
class (django writer.py:220), not on ``self``, so overriding that classmethod on
PackageMigrationLoader has no effect on where files land. Left alone, generated
package migrations are written into <app>/migrations/ -- where Django's own
loader picks them up and `manage.py migrate` executes them against a real
ProjectState.
"""

import os

from django.db.migrations.writer import MigrationWriter

from arches.db.package_migrations.loader import PackageMigrationLoader


class PackageMigrationWriter(MigrationWriter):
    @property
    def basedir(self):
        migrations_package_name, _explicit = PackageMigrationLoader.migrations_module(
            self.migration.app_label
        )
        if migrations_package_name is None:
            raise ValueError(
                "App %s is not an Arches application, so it cannot hold package "
                "migrations." % self.migration.app_label
            )
        from importlib import import_module

        # The package may not exist yet on the first migration for an app.
        parts = migrations_package_name.split(".")
        for index in range(len(parts), 0, -1):
            try:
                base = import_module(".".join(parts[:index]))
            except ImportError:
                continue
            base_dir = os.path.dirname(base.__file__)
            return os.path.join(base_dir, *parts[index:])
        raise ValueError("Could not locate %s on disk." % migrations_package_name)
