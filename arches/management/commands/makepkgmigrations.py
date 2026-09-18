"""Generate package migrations from committed graph JSON.

Like makemigrations, this diffs two things that both live in the repo: the state
the committed migrations replay to, and the desired state in
<app>/pkg/graphs/**/*.json. Neither is read from the database, so the same change
produces the same migration on every machine and the result is reproducible in CI.

Structural operations and chunked data operations are written into separate
migrations. Graph foreign keys are DEFERRABLE INITIALLY DEFERRED, which lets
structural operations run in any order inside one transaction, a guarantee that
disappears under `atomic = False`, which the chunked data operations require.
"""

import json
import os

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import migrations
from django.db.migrations.autodetector import MigrationAutodetector

from arches.db.package_migrations import labels
from arches.db.package_migrations.autodetector import changes_for_package
from arches.db.package_migrations.state import canonical_graph
from arches.db.package_migrations.loader import PackageMigrationLoader
from arches.db.package_migrations.operations.node import AlterNode
from arches.db.package_migrations.writer import PackageMigrationWriter


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

    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]
        app_label = options["app_label"]
        app_config = apps.get_app_config(app_label)
        if not getattr(app_config, "is_arches_application", False):
            raise CommandError(f"'{app_label}' is not an Arches application.")

        # No connection: generation reads the committed migrations and the
        # committed JSON, never the database, so the same repo produces the same
        # migration on every machine and --check can run in CI with no database.
        loader = PackageMigrationLoader(None)
        leaf = self._leaf(loader, app_label)
        # Replay only this app's history: the default replays every app's leaves,
        # which would diff this app's JSON against other apps' graphs.
        from_state = loader.project_state(nodes=[leaf] if leaf else [])
        to_graphs = self._committed_graphs(app_config)

        if not to_graphs:
            raise CommandError(
                "No graphs found under %s. Export them there first with "
                "`packages -o export_graphs -d <that directory> -g <graphid>`."
                % os.path.join(app_config.path, "pkg", "graphs")
            )

        for graphid in sorted(set(from_state.graphs) - set(to_graphs)):
            self.stderr.write(
                self.style.WARNING(
                    f"Graph {graphid} is in migration history but not in the committed package JSON. Package migrations will not delete a graph, because that removes every resource instance on it."
                )
            )

        self.names = labels.from_graphs(to_graphs)
        operations = changes_for_package(from_state.graphs, to_graphs)
        self._warn_about_data_the_generator_cannot_convert(operations, to_graphs)
        if not operations:
            if self.verbosity >= 1:
                self.stdout.write("No changes detected.")
            return

        if options["check"]:
            self._describe(operations)
            raise CommandError(
                "Changes detected with no package migration. Run makepkgmigrations."
            )

        if options["dry_run"]:
            self._describe(operations)
            return

        # One migration per kind of change. Graph operations rewrite the
        # definition and run in a transaction; data operations rewrite business
        # records, chunk their own work, and must not. Keeping them in separate
        # files is what makes the ordering true rather than conventional: the
        # graph is published first, and resources stay on the old publication --
        # read-only, until the data migration has brought their tiles in line
        # and moved them.
        dependency = leaf
        number = (MigrationAutodetector.parse_number(leaf[1]) if leaf else None) or 0
        for scope in ("graph", "data"):
            group = [operation for operation in operations if operation.scope == scope]
            if not group:
                continue
            number += 1
            migration = self._build(
                app_label, group, dependency, atomic=scope == "graph"
            )
            suffix = options["name"] if options["name"] else migration.suggest_name()
            migration.name = "%04d_%s_%s" % (number, scope, suffix)
            path = self._write(migration)
            dependency = (app_label, migration.name)
            if self.verbosity >= 1:
                self.stdout.write(f"  {os.path.relpath(path)}")
                for operation in group:
                    self.stdout.write(
                        f"    - {labels.humanize(operation.describe(), self.names)}"
                    )

    def _warn_about_data_the_generator_cannot_convert(self, operations, to_graphs):
        """Two node changes leave stored values behind, and neither can be fixed
        automatically: the conversion needs a decision a diff cannot make."""
        for operation in operations:
            if not isinstance(operation, AlterNode):
                continue
            node = (
                to_graphs.get(str(operation.graphid), {})
                .get("nodes", {})
                .get(str(operation.pk), {})
            )
            name = node.get("alias") or operation.pk

            if "nodegroup_id" in operation.changes:
                self._warn(
                    "Node %s (%s) is moving to nodegroup %s. Values already stored "
                    "for it stay in the old nodegroup's tiles, where nothing reads "
                    "them. Moving them means moving values between tiles, which "
                    "depends on cardinality: write a RunPackagePython migration to "
                    "do it, or accept that the existing values are stranded."
                    % (name, operation.pk, operation.changes["nodegroup_id"])
                )

            if "datatype" in operation.changes:
                self._warn(
                    "Node %s (%s) is changing datatype to '%s'. Values already "
                    "stored for it keep the old shape, and tile JSONB is cast "
                    "straight to the node's declared datatype when it is read: "
                    "write a RunPackagePython migration in the same release to "
                    "convert them."
                    % (name, operation.pk, operation.changes["datatype"])
                )

    def _warn(self, message):
        self.stderr.write(self.style.WARNING(message))

    def _committed_graphs(self, app_config):
        """The same graphs, projected into the shape state holds."""
        graphs = {}
        exported_by = {}
        for path, serialized_graph in self._read_committed(app_config):
            graph = canonical_graph(serialized_graph)
            graphid = graph["graphid"]
            if graphid in exported_by:
                # Exporting after a slug change writes a second file rather than
                # replacing the first, and the loser is decided by filename order.
                raise CommandError(
                    f"Graph {graphid} is exported twice, in {exported_by[graphid]} and {path}. Delete the stale file."
                )
            exported_by[graphid] = path
            graphs[graphid] = graph
        return graphs

    def _read_committed(self, app_config):
        root = os.path.join(app_config.path, "pkg", "graphs")
        for directory, _subdirs, filenames in os.walk(root):
            for filename in sorted(filenames):
                if not filename.endswith(".json"):
                    continue
                path = os.path.join(directory, filename)
                with open(path) as source:
                    try:
                        # The committed file is in the shape `load_package` reads;
                        # the canonical projection happens in memory.
                        serialized_graphs = json.load(source)["graph"]
                    except (ValueError, KeyError, TypeError):
                        raise CommandError(
                            f'{path} is not an Arches graph export. Files under pkg/graphs must hold {{"graph": [...]}}, which is what `packages -o export_graphs` writes.'
                        )
                for serialized_graph in serialized_graphs:
                    yield path, serialized_graph

    def _leaf(self, loader, app_label):
        leaves = loader.graph.leaf_nodes(app_label)
        if len(leaves) > 1:
            raise CommandError(
                "Conflicting package migrations in %s: %s. Merge them by hand "
                "before generating another."
                % (app_label, ", ".join(name for _app, name in leaves))
            )
        return leaves[0] if leaves else None

    def _build(self, app_label, operations, dependency, atomic):
        attributes = {
            "operations": operations,
            "dependencies": [dependency] if dependency else [],
            "initial": dependency is None,
        }
        if not atomic:
            # Chunked data operations cannot run inside the migration transaction.
            attributes["atomic"] = False
        return type("Migration", (migrations.Migration,), attributes)("", app_label)

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
            self.stdout.write(
                f"  - {labels.humanize(operation.describe(), self.names)}"
            )
