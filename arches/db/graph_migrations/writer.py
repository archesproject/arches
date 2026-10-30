"""MigrationWriter for graph migrations. basedir is overridden because Django's
calls MigrationLoader.migrations_module directly, not the graph migration loader's.
"""

import os
import re

from django.apps import apps
from django.db.migrations.writer import MigrationWriter

from arches.db.graph_migrations.loader import GRAPH_MIGRATIONS_MODULE_NAME

OPERATIONS_MODULE = "arches.db.graph_migrations.operations"


class GraphMigrationWriter(MigrationWriter):
    def as_string(self):
        """Imports the operations used by name instead of by full module path."""
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
        used_operations = ",\n    ".join(used)
        return rendered.replace(
            "from django.db import migrations",
            f"from django.db import migrations\n\nfrom {OPERATIONS_MODULE} import (\n    {used_operations},\n)",
            1,
        )

    @property
    def basedir(self):
        app_config = apps.get_app_config(self.migration.app_label)
        if not getattr(app_config, "is_arches_application", False):
            raise ValueError(
                f"App '{self.migration.app_label}' is not an Arches application, "
                "so it cannot hold graph migrations."
            )
        return os.path.join(app_config.path, *GRAPH_MIGRATIONS_MODULE_NAME.split("."))
