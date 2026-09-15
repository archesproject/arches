"""Generate package migrations from committed graph JSON.

Like makemigrations, this diffs two things that both live in the repo: the state
the committed migrations replay to, and the desired state in
<app>/pkg/graphs/**/*.json. Neither is read from the database, so the same change
produces the same migration on every machine and the result is reproducible in CI.

Structural operations and chunked data operations are written into separate
migrations. Graph foreign keys are DEFERRABLE INITIALLY DEFERRED, which lets
structural operations run in any order inside one transaction -- a guarantee that
disappears under `atomic = False`, which the chunked data operations require.
"""

import json
import os
import re

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections, migrations

from arches.db.package_migrations.canonical import canonical_graph
from arches.db.package_migrations.diff import diff_package
from arches.db.package_migrations.loader import PackageMigrationLoader
from arches.db.package_migrations.writer import PackageMigrationWriter

MAX_NAME_LENGTH = 52


class Command(BaseCommand):
    help = "Creates package migrations from an application's committed graph JSON."

    def add_arguments(self, parser):
        parser.add_argument("app_label", help="Arches application to generate for.")
        parser.add_argument("--name", "-n", help="Name for the generated migration.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be generated, and write nothing.",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Exit non-zero if changes are missing a migration. Writes nothing.",
        )
        parser.add_argument("--database", default=DEFAULT_DB_ALIAS)

    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]
        app_label = options["app_label"]
        app_config = apps.get_app_config(app_label)
        if not getattr(app_config, "is_arches_application", False):
            raise CommandError("'%s' is not an Arches application." % app_label)

        loader = PackageMigrationLoader(connections[options["database"]])
        from_state = loader.project_state()
        to_graphs = self._committed_graphs(app_config)

        if not to_graphs:
            raise CommandError(
                "No graphs found under %s. Run exportgraph first."
                % os.path.join(app_config.path, "pkg", "graphs")
            )

        operations = diff_package(from_state.graphs, to_graphs)
        if not operations:
            if self.verbosity >= 1:
                self.stdout.write("No changes detected.")
            return

        structural = [
            operation
            for operation in operations
            if not operation.requires_non_atomic_migration
        ]
        data = [
            operation
            for operation in operations
            if operation.requires_non_atomic_migration
        ]

        if options["check"]:
            self._describe(operations)
            raise CommandError(
                "Changes detected with no package migration. Run makepkgmigrations."
            )

        if options["dry_run"]:
            self._describe(operations)
            return

        written = []
        dependency = self._leaf(loader, app_label)
        for group, atomic in ((structural, True), (data, False)):
            if not group:
                continue
            name = self._next_name(
                app_config, app_label, group, options["name"], written
            )
            migration = self._build(app_label, name, group, dependency, atomic)
            path = self._write(migration)
            written.append(name)
            dependency = (app_label, name)
            if self.verbosity >= 1:
                self.stdout.write("  %s" % os.path.relpath(path))
                for operation in group:
                    self.stdout.write("    - %s" % operation.describe())

    def _committed_graphs(self, app_config):
        root = os.path.join(app_config.path, "pkg", "graphs")
        graphs = {}
        for directory, _subdirs, filenames in os.walk(root):
            for filename in sorted(filenames):
                if not filename.endswith(".json"):
                    continue
                with open(os.path.join(directory, filename)) as source:
                    graph = canonical_graph(json.load(source))
                graphs[graph["graphid"]] = graph
        return graphs

    def _leaf(self, loader, app_label):
        leaves = loader.graph.leaf_nodes(app_label)
        return leaves[0] if leaves else None

    def _next_number(self, app_config):
        directory = os.path.join(app_config.path, "migrations", "package_migrations")
        numbers = []
        if os.path.isdir(directory):
            for filename in os.listdir(directory):
                match = re.match(r"^(\d+)_.*\.py$", filename)
                if match:
                    numbers.append(int(match.group(1)))
        return max(numbers) + 1 if numbers else 1

    def _next_name(self, app_config, app_label, operations, explicit, already_written):
        number = self._next_number(app_config) + len(already_written)
        if explicit and not already_written:
            return "%04d_%s" % (number, explicit)
        fragments = [operation.migration_name_fragment for operation in operations]
        candidate = "_".join(fragments)
        if not fragments:
            candidate = "auto"
        elif len(candidate) > MAX_NAME_LENGTH:
            candidate = "%s_and_more" % fragments[0]
        return "%04d_%s" % (number, re.sub(r"\W+", "_", candidate).lower())

    def _build(self, app_label, name, operations, dependency, atomic):
        attributes = {
            "operations": operations,
            "dependencies": [dependency] if dependency else [],
            "initial": dependency is None,
        }
        if not atomic:
            # Chunked data operations cannot run inside the migration transaction.
            attributes["atomic"] = False
        return type("Migration", (migrations.Migration,), attributes)(name, app_label)

    def _write(self, migration):
        writer = PackageMigrationWriter(migration)
        os.makedirs(writer.basedir, exist_ok=True)
        init = os.path.join(writer.basedir, "__init__.py")
        # Without __init__.py the directory is a namespace package, which
        # load_disk silently treats as "this app has no migrations".
        if not os.path.exists(init):
            open(init, "w").close()
        with open(writer.path, "w") as destination:
            destination.write(writer.as_string())
        return writer.path

    def _describe(self, operations):
        self.stdout.write("Changes detected:")
        for operation in operations:
            self.stdout.write("  - %s" % operation.describe())
