"""Writing package migration files.

MigrationWriter.basedir calls MigrationLoader.migrations_module on the BASE class
(django writer.py:220), not on ``self``, so overriding that classmethod on
PackageMigrationLoader has no effect on where files land. Left alone, generated
package migrations are written into <app>/migrations/, where Django's own
loader picks them up and `manage.py migrate` executes them against a real
ProjectState.
"""

import os
import re

from django.apps import apps
from django.db.migrations.writer import MigrationWriter

from arches.db.package_migrations.loader import PACKAGE_MIGRATIONS_MODULE_NAME

PACKAGE = "arches.db.package_migrations"
OPERATIONS_MODULE = "%s.operations" % PACKAGE


class PackageMigrationWriter(MigrationWriter):
    def as_string(self):
        """Django's OperationWriter renders any non-Django operation as
        ``<module>.<ClassName>(``, which here is a 45-character prefix on every
        operation. Import the operations a migration actually uses and call them
        by name, so the file reads as what it does.
        """
        rendered = super().as_string()
        used = sorted(
            set(
                re.findall(
                    r"\b%s\.[a-z_]+\.(\w+)\(" % re.escape(OPERATIONS_MODULE), rendered
                )
            )
        )
        rendered = re.sub(
            r"\b%s\.[a-z_]+\." % re.escape(OPERATIONS_MODULE), "", rendered
        )
        rendered = re.sub(
            r"^import %s\.[a-z_]+\n" % re.escape(OPERATIONS_MODULE),
            "",
            rendered,
            flags=re.MULTILINE,
        )
        if not used:
            return rendered
        return rendered.replace(
            "from django.db import migrations",
            "from django.db import migrations\n\nfrom %s import (\n    %s,\n)"
            % (OPERATIONS_MODULE, ",\n    ".join(used)),
            1,
        )

    @property
    def basedir(self):
        app_config = apps.get_app_config(self.migration.app_label)
        if not getattr(app_config, "is_arches_application", False):
            raise ValueError(
                "App '%s' is not an Arches application, so it cannot hold package "
                "migrations." % self.migration.app_label
            )
        return os.path.join(app_config.path, *PACKAGE_MIGRATIONS_MODULE_NAME.split("."))
