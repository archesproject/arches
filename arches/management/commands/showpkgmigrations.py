"""Show which package migrations are applied."""

from itertools import groupby

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections

from arches.db.package_migrations.loader import PackageMigrationLoader


class Command(BaseCommand):
    help = "Shows all package migrations for Arches applications."

    def add_arguments(self, parser):
        parser.add_argument("app_label", nargs="*", help="App labels to limit to.")
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help="Database to inspect. Defaults to the 'default' database.",
        )
        formats = parser.add_mutually_exclusive_group()
        formats.add_argument(
            "--list", "-l", action="store_const", dest="format", const="list"
        )
        formats.add_argument(
            "--plan", "-p", action="store_const", dest="format", const="plan"
        )
        parser.set_defaults(format="list")

    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]
        connection = connections[options["database"]]
        loader = PackageMigrationLoader(connection)

        app_labels = options["app_label"]
        for app_label in app_labels:
            if app_label not in loader.migrated_apps:
                raise CommandError(
                    f"App '{app_label}' does not have package migrations."
                )

        if options["format"] == "plan":
            self._show_plan(loader, app_labels)
        else:
            self._show_list(loader, app_labels)

    def _show_list(self, loader, app_labels):
        applied = loader.applied_migrations
        nodes = sorted(loader.graph.nodes)
        if app_labels:
            nodes = [node for node in nodes if node[0] in app_labels]
        if not nodes:
            self.stdout.write("(no package migrations found)")
            return
        for app_label, group in groupby(nodes, key=lambda node: node[0]):
            self.stdout.write(app_label, self.style.MIGRATE_LABEL)
            for node in group:
                line = f" [X] {node[1]}" if node in applied else f" [ ] {node[1]}"
                if self.verbosity >= 2 and node in applied:
                    record = applied[node]
                    if getattr(record, "applied", None):
                        line += " (applied at %s)" % record.applied.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                self.stdout.write(line)

    def _show_plan(self, loader, app_labels):
        applied = loader.applied_migrations
        targets = loader.graph.leaf_nodes()
        seen, plan = set(), []
        for target in targets:
            for node in loader.graph.forwards_plan(target):
                if node not in seen:
                    seen.add(node)
                    plan.append(node)
        if app_labels:
            plan = [node for node in plan if node[0] in app_labels]
        if not plan:
            self.stdout.write("(no package migrations found)")
            return
        for node in plan:
            marker = "[X]" if node in applied else "[ ]"
            self.stdout.write(f"{marker}  {node[0]}.{node[1]}")
