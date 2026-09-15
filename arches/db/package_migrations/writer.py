"""Writing package migration files.

MigrationWriter.basedir calls MigrationLoader.migrations_module on the BASE class
(django writer.py:220), not on ``self``, so overriding that classmethod on
PackageMigrationLoader has no effect on where files land. Left alone, generated
package migrations are written into <app>/migrations/ -- where Django's own
loader picks them up and `manage.py migrate` executes them against a real
ProjectState.
"""

import os

from django.apps import apps
from django.db.migrations.writer import MigrationWriter


class PackageMigrationWriter(MigrationWriter):
    @property
    def basedir(self):
        app_config = apps.get_app_config(self.migration.app_label)
        if not getattr(app_config, "is_arches_application", False):
            raise ValueError(
                "App '%s' is not an Arches application, so it cannot hold package "
                "migrations." % self.migration.app_label
            )
        return os.path.join(app_config.path, "migrations", "package_migrations")
