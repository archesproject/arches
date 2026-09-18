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
OPERATIONS_MODULE = f"{PACKAGE}.operations"


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
                    rf"\b{re.escape(OPERATIONS_MODULE)}\.[a-z_]+\.(\w+)\(", rendered
                )
            )
        )
        rendered = re.sub(rf"\b{re.escape(OPERATIONS_MODULE)}\.[a-z_]+\.", "", rendered)
        rendered = re.sub(
            rf"^import {re.escape(OPERATIONS_MODULE)}\.[a-z_]+\n",
            "",
            rendered,
            flags=re.MULTILINE,
        )
        if not used:
            return rendered
        return rendered.replace(
            "from django.db import migrations",
            f"from django.db import migrations\n\n"
            f"from {OPERATIONS_MODULE} import (\n    " + ",\n    ".join(used) + ",\n)",
            1,
        )

    @property
    def basedir(self):
        app_config = apps.get_app_config(self.migration.app_label)
        if not getattr(app_config, "is_arches_application", False):
            raise ValueError(
                f"App '{self.migration.app_label}' is not an Arches application, "
                "so it cannot hold package migrations."
            )
        return os.path.join(app_config.path, *PACKAGE_MIGRATIONS_MODULE_NAME.split("."))
