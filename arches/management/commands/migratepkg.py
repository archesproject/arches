"""Apply package migrations.

A thin wrapper over PackageMigrationExecutor, deliberately shaped like
`manage.py migrate` so an operator who knows one knows the other.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.exceptions import AmbiguityError

from arches.app.models.graph import Graph
from arches.db.package_migrations import drift, labels
from arches.db.package_migrations.executor import PackageMigrationExecutor


class Command(BaseCommand):
    help = "Applies package data migrations for Arches applications."

    PLAN_DETAIL_LIMIT = 25

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
            "--force",
            action="store_true",
            help="Apply even if this database has diverged from migration history.",
        )
        parser.add_argument(
            "--plan",
            action="store_true",
            help="Print the operations that would run, and exit.",
        )

    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]
        self.database = options["database"]
        connection = connections[self.database]

        executor = PackageMigrationExecutor(
            connection, progress_callback=self._progress
        )
        executor.loader.check_consistent_history(connection)

        conflicts = executor.loader.detect_conflicts()
        if conflicts:
            described = "; ".join(
                f"{app}: {', '.join(names)}" for app, names in conflicts.items()
            )
            raise CommandError(
                f"Conflicting package migrations detected; multiple leaf nodes in the migration graph ({described}). Resolve them before migrating."
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

        if options["fake"]:
            self._refuse_faking_data(plan, options["force"])
        else:
            self._refuse_drifted_database(plan, connection, options["force"])

        executor.migrate(targets, plan=plan, fake=options["fake"])

        if not options["fake"]:
            self._discard_stale_drafts(plan, connection.alias)

    def _targets(self, executor, options):
        graph = executor.loader.graph
        app_label = options["app_label"]
        migration_name = options["migration_name"]

        if app_label is None:
            return graph.leaf_nodes()

        if app_label not in executor.loader.migrated_apps:
            raise CommandError(f"App '{app_label}' does not have package migrations.")

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
                f"More than one package migration matches '{migration_name}' in app '{app_label}'. Give a more specific prefix."
            )
        except KeyError:
            raise CommandError(
                f"Cannot find a package migration matching '{migration_name}' for app '{app_label}'."
            )
        return [(app_label, migration.name)]

    def _discard_stale_drafts(self, plan, using):
        """A draft copied before this run would undo it on the next Designer
        publish, which rebuilds the live graph entirely from the draft. Dropping
        it is the whole fix: Arches builds a fresh one from the migrated graph
        when someone opens it.
        """
        graphids = {
            str(getattr(operation, "graphid", "") or "")
            for migration, _backwards in plan
            for operation in migration.operations
        } - {""}
        for graphid in sorted(graphids):
            graph = Graph.objects.using(using).filter(pk=graphid).first()
            if graph is not None and graph.get_draft_graph():
                graph.delete_draft_graph()

    def _refuse_faking_data(self, plan, force):
        """Faking structural work is safe when the rows already exist: the end
        state matches. Faking data work is not. Nothing else adds a key to a
        tile, and once the migration is recorded its content-addressed predicate
        is never consulted again, so the work is skipped in silence.
        """
        faked = [
            migration
            for migration, _backwards in plan
            if any(operation.scope == "data" for operation in migration.operations)
        ]
        if not faked:
            return
        message = (
            "These package migrations change business data, which nothing else "
            "will do if they are recorded rather than run:\n  %s\nFake the graph "
            "migrations only, by naming the last of them, then apply the rest:\n"
            "  python manage.py migratepkg %s <last graph migration> --fake\n"
            "  python manage.py migratepkg %s"
            % (
                "\n  ".join(f"{m.app_label}.{m.name}" for m in faked),
                faked[0].app_label,
                faked[0].app_label,
            )
        )
        if force:
            self.stderr.write(self.style.WARNING(message))
            return
        raise CommandError(f"{message}\nRe-run with --force to record them anyway.")

    def _refuse_drifted_database(self, plan, connection, force):
        """These migrations were generated against migration history, not against
        this database. If a curator has edited the graph since, an alter updates
        zero rows and reports success."""
        problems = drift.problems(plan, connection.alias)
        if not problems:
            return

        if all(problem.kind == "reference" for problem in problems):
            # A graph points at an ontology, a template, widgets and card
            # components. Those come from the package, not from graph rows.
            headline = (
                "These package migrations need reference data this database does "
                "not have. Install the package first, then migrate:\n"
                "  python manage.py packages -o load_package -s <app>/pkg -y\n"
                "Missing:"
            )
        elif all(problem.kind == "present" for problem in problems):
            # The machine the change was authored on already has the rows: the
            # Graph Designer wrote them before the migration existed.
            headline = (
                "Everything these package migrations create is already here, which "
                "is what the machine they were authored on looks like. Record them "
                "instead of applying them:\n  python manage.py migratepkg %s --fake"
                % (plan[0][0].app_label if plan else "<app>")
            )
        else:
            headline = (
                "This database has diverged from the migration history these "
                "package migrations were generated against"
            )
        message = "%s\n  %s" % (
            headline,
            "\n  ".join(problem.message for problem in problems),
        )
        if force:
            self.stderr.write(self.style.WARNING(message))
            return
        if all(problem.kind == "reference" for problem in problems):
            # --force would only move the failure deeper, into Graph.publish().
            raise CommandError(message)
        raise CommandError(
            f"{message}\nReconcile the graph, or re-run with --force to apply anyway."
        )

    def _refuse_half_reversals(self, plan):
        """Django unapplies migration by migration and only raises when it reaches
        the irreversible one, so a `zero` that cannot finish still unapplies
        everything before it, leaving the graph on the new publication and its
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
                    f"{migration.app_label}.{migration.name} cannot be unapplied: {type(irreversible[0]).__name__} is irreversible. Unapplying the migrations after it would leave the graph and its resources on different publications."
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
            self._print_operations(migration.operations)

    def _print_operations(self, operations):
        """A migration that adopts an existing package describes every row of
        every graph, which is thousands of lines nobody reads. Summarise by kind
        unless asked for the whole thing."""
        described = [operation.describe() for operation in operations]
        if self.verbosity >= 2 or len(operations) <= self.PLAN_DETAIL_LIMIT:
            names = labels.from_database("\n".join(described), self.database)
            for description in described:
                self.stdout.write(f"      {labels.humanize(description, names)}")
            return

        counts = {}
        for operation in operations:
            counts[type(operation).__name__] = (
                counts.get(type(operation).__name__, 0) + 1
            )
        for name in sorted(counts):
            self.stdout.write(f"      {name} x{counts[name]}")
        self.stdout.write(f"      ({len(operations)} operations; -v 2 lists them)")

    def _progress(self, action, migration=None, fake=False):
        if self.verbosity < 1:
            return
        if action == "apply_start":
            self.stdout.write(f"  Applying {migration}...", ending="")
            self.stdout.flush()
        elif action == "apply_success":
            self.stdout.write(self.style.SUCCESS(" FAKED" if fake else " OK"))
        elif action == "unapply_start":
            self.stdout.write(f"  Unapplying {migration}...", ending="")
            self.stdout.flush()
        elif action == "unapply_success":
            self.stdout.write(self.style.SUCCESS(" FAKED" if fake else " OK"))
