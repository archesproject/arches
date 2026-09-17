"""Apply package migrations.

A thin wrapper over PackageMigrationExecutor, deliberately shaped like
`manage.py migrate` so an operator who knows one knows the other.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.exceptions import AmbiguityError

from arches.db.package_migrations.executor import PackageMigrationExecutor


class Command(BaseCommand):
    help = "Applies package data migrations for Arches applications."

    def add_arguments(self, parser):
        parser.add_argument(
            "app_label", nargs="?", help="App label of an Arches application."
        )
        parser.add_argument(
            "migration_name",
            nargs="?",
            help="Migration to bring the app to, or 'zero' to unapply all.",
        )
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help="Database to migrate. Defaults to the 'default' database.",
        )
        parser.add_argument(
            "--fake",
            action="store_true",
            help="Record migrations as applied without running them.",
        )
        parser.add_argument(
            "--plan",
            action="store_true",
            help="Print the operations that would run, and exit.",
        )

    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]
        connection = connections[options["database"]]

        executor = PackageMigrationExecutor(
            connection, progress_callback=self._progress
        )
        executor.loader.check_consistent_history(connection)

        conflicts = executor.loader.detect_conflicts()
        if conflicts:
            described = "; ".join(
                "%s: %s" % (app, ", ".join(names)) for app, names in conflicts.items()
            )
            raise CommandError(
                "Conflicting package migrations detected; multiple leaf nodes in "
                "the migration graph (%s). Resolve them before migrating." % described
            )

        targets = self._targets(executor, options)
        plan = executor.migration_plan(targets)

        if options["plan"]:
            self._print_plan(plan)
            return

        self._refuse_half_reversals(plan)
        if not plan:
            if self.verbosity >= 1:
                self.stdout.write("No package migrations to apply.")
            return

        executor.migrate(targets, plan=plan, fake=options["fake"])

    def _targets(self, executor, options):
        graph = executor.loader.graph
        app_label = options["app_label"]
        migration_name = options["migration_name"]

        if app_label is None:
            return graph.leaf_nodes()

        if app_label not in executor.loader.migrated_apps:
            raise CommandError("App '%s' does not have package migrations." % app_label)

        if migration_name is None:
            return graph.leaf_nodes(app_label)

        if migration_name == "zero":
            return [(app_label, None)]

        # MigrationLoader already does prefix resolution, and raises
        # AmbiguityError when a prefix matches more than one migration.
        try:
            migration = executor.loader.get_migration_by_prefix(
                app_label, migration_name
            )
        except AmbiguityError:
            raise CommandError(
                "More than one package migration matches '%s' in app '%s'. "
                "Give a more specific prefix." % (migration_name, app_label)
            )
        except KeyError:
            raise CommandError(
                "Cannot find a package migration matching '%s' for app '%s'."
                % (migration_name, app_label)
            )
        return [(app_label, migration.name)]

    def _refuse_half_reversals(self, plan):
        """Django unapplies migration by migration and only raises when it reaches
        the irreversible one, so a `zero` that cannot finish still unapplies
        everything before it -- leaving the graph on the new publication and its
        resources on the old, which is the read-only state. Refuse up front.
        """
        for migration, backwards in plan:
            if not backwards:
                continue
            irreversible = [
                operation
                for operation in migration.operations
                if not operation.reversible
            ]
            if irreversible:
                raise CommandError(
                    "%s.%s cannot be unapplied: %s is irreversible. Unapplying the "
                    "migrations after it would leave the graph and its resources on "
                    "different publications."
                    % (
                        migration.app_label,
                        migration.name,
                        type(irreversible[0]).__name__,
                    )
                )

    def _print_plan(self, plan):
        if not plan:
            self.stdout.write("No package migrations to apply.")
            return
        self.stdout.write("Planned package migrations:")
        for migration, backwards in plan:
            self.stdout.write(
                "  %s %s.%s"
                % (
                    "[ ]" if not backwards else "[x]",
                    migration.app_label,
                    migration.name,
                )
            )
            for operation in migration.operations:
                self.stdout.write("      %s" % operation.describe())

    def _progress(self, action, migration=None, fake=False):
        if self.verbosity < 1:
            return
        if action == "apply_start":
            self.stdout.write("  Applying %s..." % migration, ending="")
            self.stdout.flush()
        elif action == "apply_success":
            self.stdout.write(self.style.SUCCESS(" FAKED" if fake else " OK"))
        elif action == "unapply_start":
            self.stdout.write("  Unapplying %s..." % migration, ending="")
            self.stdout.flush()
        elif action == "unapply_success":
            self.stdout.write(self.style.SUCCESS(" FAKED" if fake else " OK"))
