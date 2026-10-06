"""Generate package migrations from the graphs in this database.

The graphs as they are here, edited and published in the Graph Designer, are the
desired state. They are diffed against the state this app's committed migrations
replay to, and because this database already has what a new graph migration
describes, that migration is recorded as applied here.

Structural operations and chunked data operations are written into separate
migrations. Graph foreign keys are DEFERRABLE INITIALLY DEFERRED, which lets
structural operations run in any order inside one transaction, a guarantee that
disappears under `atomic = False`, which the chunked data operations require.
"""

import os
import sysconfig
import uuid

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections, migrations, transaction
from django.db.migrations.autodetector import MigrationAutodetector

from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.data_management.resource_graphs import (
    exporter as ResourceGraphExporter,
)
from arches.db.package_migrations import labels
from arches.db.package_migrations.autodetector import changes_for_package
from arches.db.package_migrations.loader import (
    PACKAGE_MIGRATIONS_MODULE_NAME,
    PackageMigrationLoader,
)
from arches.db.package_migrations.operations.graph import CreateGraph
from arches.db.package_migrations.operations.node import AlterNode
from arches.db.package_migrations.recorder import PackageMigrationRecorder
from arches.db.package_migrations.state import canonical_graph
from arches.db.package_migrations.writer import PackageMigrationWriter


class Command(BaseCommand):
    help = "Creates package migrations from the graphs in this database."

    def add_arguments(self, parser):
        parser.add_argument("app_label", help="Arches application to generate for.")
        parser.add_argument(
            "--graph",
            "-g",
            action="append",
            dest="graphs",
            default=[],
            metavar="GRAPH",
            help="Id or slug of a graph to bring under this application's package migrations. Repeatable.",
        )
        parser.add_argument("--name", "-n", help="Name for the generated migration.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be generated, and write nothing.",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Exit non-zero if this database has graph changes no package migration describes. Writes nothing.",
        )

    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]
        app_label = options["app_label"]
        app_config = apps.get_app_config(app_label)
        if not getattr(app_config, "is_arches_application", False):
            raise CommandError(f"'{app_label}' is not an Arches application.")
        if options["name"] and not options["name"].isidentifier():
            raise CommandError(
                f"'{options['name']}' is not a valid migration name. Use letters, digits and underscores."
            )
        writing = not (options["check"] or options["dry_run"])
        if writing:
            self._refuse_unwritable(app_label, app_config)

        connection = connections[DEFAULT_DB_ALIAS]
        loader = PackageMigrationLoader(connection)
        loader.check_consistent_history(connection)
        leaf = self._leaf(loader, app_label)
        self._refuse_missing_files(loader, app_label, writing)
        self._refuse_unapplied(loader, leaf, app_label, writing)

        graphids_by_app = self._graphids_by_app(loader)
        graphids = graphids_by_app.get(app_label, set()) | self._requested_graphids(
            options["graphs"], graphids_by_app, app_label
        )
        if not graphids:
            raise CommandError(
                f"{app_label} has no package migrations yet, so nothing says which graphs belong to it. Name them:\n  python manage.py makepkgmigrations {app_label} --graph <graph id or slug>"
            )

        # Replay only this app's history: the default replays every app's leaves,
        # which would diff this app's graphs against other apps' graphs.
        from_state = loader.project_state(nodes=[leaf] if leaf else [])

        with transaction.atomic():
            present = self._lock(graphids)
            for graphid in sorted(graphids - present):
                self._warn(
                    f"Graph {graphid} is in {app_label}'s migration history but not in this database. Package migrations will not delete a graph, because that removes every resource instance on it."
                )
            self._refuse_unpublished(present, writing)

            to_graphs = self._database_graphs(present)
            self.names = labels.from_graphs(to_graphs)
            operations = changes_for_package(
                from_state.graphs, to_graphs, self._publication_ids(present)
            )
            self._warn_about_data_the_generator_cannot_convert(operations, to_graphs)
            if not operations:
                if self.verbosity >= 1:
                    self.stdout.write("No changes detected.")
                return

            if options["check"]:
                self._describe(operations)
                raise CommandError(
                    "This database has graph changes that no package migration describes. Run makepkgmigrations."
                )

            if options["dry_run"]:
                self._describe(operations)
                return

            written = self._build_migrations(
                app_label, operations, leaf, options["name"]
            )
            recorder = PackageMigrationRecorder(connection)
            for migration in written:
                if self._is_graph_migration(migration):
                    recorder.record_applied(app_label, migration.name)
            paths = self._write(written)

        self._report(app_label, written, paths, connection)

    def _refuse_unwritable(self, app_label, app_config):
        directory = os.path.realpath(
            os.path.join(app_config.path, *PACKAGE_MIGRATIONS_MODULE_NAME.split("."))
        )
        for key in ("purelib", "platlib"):
            installed = os.path.realpath(sysconfig.get_paths()[key])
            if directory.startswith(os.path.join(installed, "")):
                raise CommandError(
                    f"{app_label} is installed in {installed}, not checked out for development. Make package migrations in its source checkout."
                )
        existing = directory
        while not os.path.exists(existing):
            existing = os.path.dirname(existing)
        if not os.access(existing, os.W_OK):
            raise CommandError(f"Cannot write package migrations to {directory}.")

    def _refuse_missing_files(self, loader, app_label, writing):
        missing = sorted(
            name
            for migration_app_label, name in loader.applied_migrations
            if migration_app_label == app_label
            and (migration_app_label, name) not in loader.disk_migrations
        )
        if not missing:
            return
        missing_names = "\n  ".join(missing)
        self._refuse_or_warn(
            f"These package migrations are recorded as applied on this database, but their files are not in {app_label}:\n  {missing_names}\nA migration made now would fold whatever they changed into a new one. Restore the files, for example by checking out the branch that has them. To drop them instead, restore them and record them as unapplied with `migratepkg {app_label} <the migration before them> --fake`.",
            writing,
        )

    def _refuse_unapplied(self, loader, leaf, app_label, writing):
        if leaf is None:
            return
        unapplied = [
            key
            for key in loader.graph.forwards_plan(leaf)
            if key[0] == app_label and key not in loader.applied_migrations
        ]
        if not unapplied:
            return
        self._refuse_or_warn(
            "This database has not applied these package migrations:\n  "
            + "\n  ".join(f"{label}.{name}" for label, name in unapplied)
            + f"\nA migration made now would be built on changes this database does not have. Apply them, then run this command again:\n  python manage.py migratepkg {app_label}\n  python manage.py makepkgmigrations {app_label}",
            writing,
        )

    def _graphids_by_app(self, loader):
        graphids_by_app = {}
        for (migration_app_label, _name), migration in loader.disk_migrations.items():
            for operation in migration.operations:
                graphid = getattr(operation, "graphid", None)
                if graphid:
                    graphids_by_app.setdefault(migration_app_label, set()).add(
                        str(graphid)
                    )
        return graphids_by_app

    def _requested_graphids(self, values, graphids_by_app, app_label):
        requested = set()
        for value in values:
            graph = self._resolve(value)
            graphid = str(graph.graphid)
            for other_app_label, graphids in graphids_by_app.items():
                if other_app_label != app_label and graphid in graphids:
                    raise CommandError(
                        f"Graph {graph.slug} already belongs to {other_app_label}'s package migrations. Make its migrations there:\n  python manage.py makepkgmigrations {other_app_label}"
                    )
            requested.add(graphid)
        return requested

    def _resolve(self, value):
        try:
            uuid.UUID(value)
        except ValueError:
            graph = models.GraphModel.objects.filter(
                slug=value, source_identifier__isnull=True
            ).first()
        else:
            graph = models.GraphModel.objects.filter(pk=value).first()
        if graph is None:
            raise CommandError(
                f"No graph in this database has the id or slug '{value}'."
            )
        if graph.source_identifier_id:
            source_slug = graph.source_identifier.slug
            raise CommandError(
                f"Graph {value} is the Graph Designer's draft of graph {source_slug}. Name {source_slug} instead."
            )
        if str(graph.graphid) == settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID:
            raise CommandError(
                "The System Settings graph belongs to Arches itself, not to an application."
            )
        return graph

    def _lock(self, graphids):
        return {
            str(graphid)
            for graphid in models.GraphModel.objects.select_for_update()
            .filter(pk__in=graphids, source_identifier__isnull=True)
            .values_list("graphid", flat=True)
        }

    def _refuse_unpublished(self, graphids, writing):
        unpublished = set(
            models.GraphModel.objects.filter(
                pk__in=graphids, has_unpublished_changes=True
            ).values_list("slug", flat=True)
        ) | set(
            models.GraphModel.objects.filter(
                source_identifier_id__in=graphids, has_unpublished_changes=True
            ).values_list("source_identifier__slug", flat=True)
        )
        never_published = set(
            models.GraphModel.objects.filter(
                pk__in=graphids, publication__isnull=True
            ).values_list("slug", flat=True)
        )
        if not unpublished and not never_published:
            return
        lines = [
            f"{slug} has changes in the Graph Designer that are not published"
            for slug in sorted(unpublished)
        ] + [f"{slug} has never been published" for slug in sorted(never_published)]
        self._refuse_or_warn(
            "These graphs are not published as they are:\n  "
            + "\n  ".join(lines)
            + "\nPublish them in the Graph Designer, then run this command again.",
            writing,
        )

    def _database_graphs(self, graphids):
        # The exact call `packages -o export_graphs` makes, so histories built
        # from exported files see no change that is not there.
        if not graphids:
            return {}
        return {
            str(graph["graphid"]): canonical_graph(graph)
            for graph in ResourceGraphExporter.get_graphs_for_export(
                graphids=sorted(graphids)
            )["graph"]
        }

    def _publication_ids(self, graphids):
        return {
            str(graphid): str(publication_id) if publication_id else None
            for graphid, publication_id in models.GraphModel.objects.filter(
                pk__in=graphids
            ).values_list("graphid", "publication_id")
        }

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
                new_nodegroup_id = operation.changes["nodegroup_id"]
                self._warn(
                    f"Node {name} ({operation.pk}) is moving to nodegroup {new_nodegroup_id}. Values already stored for it stay in the old nodegroup's tiles, where nothing reads them. Moving them means moving values between tiles, which depends on cardinality: write a RunPackagePython migration to do it, or accept that the existing values are stranded."
                )

            if "datatype" in operation.changes:
                new_datatype = operation.changes["datatype"]
                self._warn(
                    f"Node {name} ({operation.pk}) is changing datatype to '{new_datatype}'. Values already stored for it keep the old shape, and tile JSONB is cast straight to the node's declared datatype when it is read: write a RunPackagePython migration in the same release to convert them."
                )

    def _build_migrations(self, app_label, operations, leaf, name):
        """One migration per kind of change. Graph operations rewrite the
        definition and run in a transaction; data operations rewrite business
        records, chunk their own work, and must not. Keeping them in separate
        files is what makes the ordering true rather than conventional: the graph
        is published first, and resources stay on the old publication --
        read-only, until the data migration has brought their tiles in line and
        moved them.

        Created graphs get a graph migration of their own, so a site that has
        them from load_package can record it and apply the rest.
        """
        created_graphids = {
            operation.graphid
            for operation in operations
            if isinstance(operation, CreateGraph)
        }
        groups = (
            (
                "graph",
                [
                    operation
                    for operation in operations
                    if operation.scope == "graph"
                    and str(operation.graphid) in created_graphids
                ],
            ),
            (
                "graph",
                [
                    operation
                    for operation in operations
                    if operation.scope == "graph"
                    and str(operation.graphid) not in created_graphids
                ],
            ),
            (
                "data",
                [operation for operation in operations if operation.scope == "data"],
            ),
        )

        if leaf:
            number = MigrationAutodetector.parse_number(leaf[1]) or 0
        else:
            number = 0
        dependency = leaf
        written = []
        for scope, group in groups:
            if not group:
                continue
            number += 1
            migration = self._build(
                app_label, group, dependency, atomic=scope == "graph"
            )
            suffix = name or migration.suggest_name()
            migration.name = f"{number:04d}_{scope}_{suffix}"
            written.append(migration)
            dependency = (app_label, migration.name)
        return written

    def _is_graph_migration(self, migration):
        return all(operation.scope == "graph" for operation in migration.operations)

    def _report(self, app_label, written, paths, connection):
        if self.verbosity < 1:
            return
        for migration, path in zip(written, paths):
            self.stdout.write(f"  {os.path.relpath(path)}")
            for operation in migration.operations:
                self.stdout.write(
                    f"    - {labels.humanize(operation.describe(), self.names)}"
                )
        recorded = [
            migration.name
            for migration in written
            if self._is_graph_migration(migration)
        ]
        if recorded:
            database = connection.settings_dict
            self.stdout.write(
                f"Recorded {', '.join(recorded)} as applied on {database['NAME']}@{database['HOST'] or 'localhost'}: this database already has their changes."
            )
        if len(recorded) < len(written):
            self.stdout.write(
                f"Bring this database's tiles and resources in line with them:\n  python manage.py migratepkg {app_label}"
            )

    def _warn(self, message):
        self.stderr.write(self.style.WARNING(message))

    def _refuse_or_warn(self, message, refuse):
        if refuse:
            raise CommandError(message)
        self._warn(message)

    def _leaf(self, loader, app_label):
        leaves = loader.graph.leaf_nodes(app_label)
        if len(leaves) > 1:
            conflicting_names = ", ".join(name for _app_label, name in leaves)
            raise CommandError(
                f"Conflicting package migrations in {app_label}: {conflicting_names}. Merge them by hand before generating another."
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

    def _write(self, written):
        writers = [PackageMigrationWriter(migration) for migration in written]
        sources = [(writer.path, writer.as_string()) for writer in writers]
        basedir = writers[0].basedir
        os.makedirs(basedir, exist_ok=True)
        init = os.path.join(basedir, "__init__.py")
        # Without __init__.py the directory is a namespace package, which
        # load_disk silently treats as "this app has no migrations".
        if not os.path.exists(init):
            open(init, "w").close()
        written_paths = []
        try:
            for path, source in sources:
                written_paths.append(path)
                with open(path, "w", encoding="utf-8") as destination:
                    destination.write(source)
        except BaseException:
            for path in written_paths:
                if os.path.exists(path):
                    os.remove(path)
            raise
        return written_paths

    def _describe(self, operations):
        self.stdout.write("Changes detected:")
        for operation in operations:
            self.stdout.write(
                f"  - {labels.humanize(operation.describe(), self.names)}"
            )
