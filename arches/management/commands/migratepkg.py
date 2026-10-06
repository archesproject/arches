"""Apply package migrations.

A thin wrapper over PackageMigrationExecutor, deliberately shaped like
`manage.py migrate` so an operator who knows one knows the other.
"""

import os

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.exceptions import AmbiguityError

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.package_migrations import drift, labels
from arches.db.package_migrations.executor import PackageMigrationExecutor
from arches.db.package_migrations.operations.base import PackageMigrationError
from arches.db.package_migrations.operations.python import RunPackagePython


class Command(BaseCommand):
    help = "Applies package migrations for Arches applications."

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
            help="Go ahead where a refusal offers --force: skip rows missing here, discard unpublished Graph Designer drafts, unapply nodegroups that hold tiles, record data work with --fake, or start from the earliest point a database fits.",
        )
        parser.add_argument(
            "--plan",
            action="store_true",
            help="Print the operations that would run, and exit.",
        )

    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]
        self.database = options["database"]
        self.app_label = options["app_label"]
        self.target = options["migration_name"]
        self.fake = options["fake"]
        self.force = options["force"]
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

        self._warn_about_missing_files(executor.loader)

        targets = self._targets(executor, options)
        plan = executor.migration_plan(targets)

        if options["plan"]:
            self._print_plan(plan)
            return

        if not self.fake:
            self._refuse_half_reversals(plan)
        if not plan:
            if self.verbosity >= 1:
                self.stdout.write("No package migrations to apply.")
            return

        self._refuse_missing_references(plan)
        if self.fake:
            self._refuse_faking_work(plan)
        else:
            self._refuse_destructive_reversals(plan)
            self._refuse_discarding_unpublished_drafts(plan)
            self._refuse_misfit_database(plan)

        self.completed = []
        try:
            executor.migrate(targets, plan=plan, fake=self.fake)
        except PackageMigrationError as error:
            raise CommandError(str(error)) from error
        finally:
            if not self.fake:
                completed = [
                    (migration, backwards)
                    for migration, backwards in plan
                    if migration in self.completed
                ]
                self._discard_stale_drafts(completed)
                self._remind_to_reindex(completed)

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

    def _warn_about_missing_files(self, loader):
        missing = sorted(
            key
            for key in loader.applied_migrations
            if key not in loader.disk_migrations and self.app_label in (None, key[0])
        )
        if not missing:
            return
        missing_names = "\n  ".join(
            f"{app_label}.{name}" for app_label, name in missing
        )
        self.stderr.write(
            self.style.WARNING(
                f"These package migrations are recorded as applied on this database, but their files are missing:\n  {missing_names}\nRestore them, for example by checking out the branch that has them."
            )
        )

    def _refuse_missing_references(self, plan):
        problems = drift.missing_references(plan, self.database)
        if not problems:
            return
        app_labels = sorted({migration.app_label for migration, _backwards in plan})
        install_commands = "\n  ".join(
            f"python manage.py packages -o load_package -s {os.path.join(apps.get_app_config(app_label).path, 'pkg')}"
            for app_label in app_labels
        )
        self._refuse(
            "These package migrations point at things this database does not have, "
            "which come from installing the package rather than from package migrations:\n  "
            + "\n  ".join(problem.message for problem in problems)
            + f"\nInstall them, then run this command again:\n  {install_commands}\n  {self._command(self.app_label, self.target, fake=self.fake)}"
        )

    def _refuse_destructive_reversals(self, plan):
        problems = drift.reverse_problems(plan, self.database)
        destructive = [problem for problem in problems if problem.kind == "destructive"]
        if destructive:
            self._refuse(
                "Unapplying these package migrations would delete a graph that has "
                "resources, along with every resource and tile on it:\n  "
                + "\n  ".join(problem.message for problem in destructive)
                + "\nKeep the graph by unapplying only the migrations after the one that creates it."
            )
        orphans = [problem for problem in problems if problem.kind == "orphans"]
        if not orphans:
            return
        message = (
            "Unapplying these package migrations would delete nodegroups that hold "
            "tiles, leaving those tiles with nothing to belong to:\n  "
            + "\n  ".join(problem.message for problem in orphans)
        )
        if self.force:
            self._warn(message)
            return
        self._refuse(
            f"{message}\nUnapply them anyway by running the following:\n  {self._command(self.app_label, self.target, force=True)}"
        )

    def _refuse_discarding_unpublished_drafts(self, plan):
        slugs = sorted(
            models.GraphModel.objects.using(self.database)
            .filter(
                source_identifier_id__in=self._graphids(plan, scope="graph"),
                has_unpublished_changes=True,
            )
            .values_list("source_identifier__slug", flat=True)
        )
        if not slugs:
            return
        message = (
            "These graphs have changes in the Graph Designer that are not published, "
            "and this run would discard them:\n  " + "\n  ".join(slugs)
        )
        if self.force:
            self._warn(message)
            return
        self._refuse(
            f"{message}\nPublish or revert them in the Graph Designer, then run this command again, or discard them by running the following:\n  {self._command(self.app_label, self.target, force=True)}"
        )

    def _refuse_faking_work(self, plan):
        """Faking structural work is safe when the rows already exist: the end
        state matches. Faking data work is not, unless there is none to do here.
        Nothing else adds a key to a tile, and once the migration is recorded its
        content-addressed predicate is never consulted again, so the work is
        skipped in silence.
        """
        if plan[0][1]:
            with_data = [
                migration
                for migration, _backwards in plan
                if "data" in self._scopes(migration)
            ]
            if not with_data:
                return
            message = (
                "Recording these package migrations as unapplied would leave their "
                "business data changes in place:\n  "
                + "\n  ".join(self._label(migration) for migration in with_data)
            )
            if self.force:
                self._warn(message)
                return
            self._refuse(
                f"{message}\nUnapply them instead by running the following:\n  {self._command(self.app_label, self.target)}"
            )
            return

        reasons, commands = [], []
        for app_label, migrations in self._forward_migrations_by_app(plan).items():
            fit = self._fit(migrations)
            if fit.position is None:
                message = (
                    "This database does not match these package migrations, so they "
                    "cannot be recorded as applied:\n  "
                    + "\n  ".join(problem.message for problem in fit.problems)
                )
                if self.force:
                    self._warn(message)
                    continue
                self._refuse(message)
            steps = self._steps(migrations, fit.position)
            if all(action == "record" for action, _migration, _beyond in steps):
                continue
            reasons.extend(
                self._reason(migration, beyond)
                for action, migration, beyond in steps
                if action == "apply"
            )
            commands.extend(self._commands(app_label, steps))
        if not reasons:
            return
        if self.app_label is None:
            commands.append(self._command(fake=True, force=self.force))
        message = (
            "Some of these package migrations still have work to do in this "
            "database, so recording them without running them would skip it:\n  "
            + "\n  ".join(reasons)
        )
        if self.force:
            self._warn(message)
            return
        self._refuse(
            f"{message}\n{self._directions(commands)}\n  " + "\n  ".join(commands)
        )

    def _refuse_misfit_database(self, plan):
        """These migrations were generated from the database they were authored
        on, not from this one. If a curator has edited the graph since, an alter
        updates zero rows and reports success."""
        if plan[0][1]:
            return
        recorded, to_apply, commands = [], [], []
        for app_label, migrations in self._forward_migrations_by_app(plan).items():
            fit = self._fit(migrations)
            if fit.position == 0:
                continue
            if fit.position is None:
                self._refuse_diverged(fit.problems)
                continue
            steps = self._steps(migrations, fit.position)
            recorded.extend(
                self._label(migration)
                for action, migration, _beyond in steps
                if action == "record"
            )
            to_apply.extend(
                self._reason(migration, beyond)
                for action, migration, beyond in steps
                if action == "apply"
            )
            commands.extend(self._commands(app_label, steps))
        if not commands:
            return
        if self.app_label is None:
            commands.append(self._command(force=self.force))
        message = (
            "It looks like these package migrations have already been applied to "
            "this database but not recorded:\n  " + "\n  ".join(recorded)
        )
        if to_apply:
            message += (
                "\nThese still have changes to make here, so they must be applied:\n  "
                + "\n  ".join(to_apply)
            )
        self._refuse(
            f"{message}\n{self._directions(commands)}\n  " + "\n  ".join(commands)
        )

    def _refuse_diverged(self, problems):
        if all(problem.kind == "missing" for problem in problems):
            message = (
                "This database's graph has changed since these package migrations "
                "were made. Some rows they change or delete are no longer here, so "
                "those changes would be skipped:\n  "
                + "\n  ".join(problem.message for problem in problems)
            )
            if self.force:
                self._warn(message)
                return
            self._refuse(
                f"{message}\nRestore those rows in the Graph Designer and run this command again, or apply everything else anyway by running the following:\n  {self._command(self.app_label, self.target, force=True)}"
            )
        self._refuse(
            "This database's graph matches no point in these package migrations:\n  "
            + "\n  ".join(problem.message for problem in problems)
            + "\nUndo those edits in the Graph Designer so the graph matches, then run this command again."
        )

    def _fit(self, migrations):
        """Where several points fit, the operator says which: recording all of
        them with --fake, or running from the earliest with --force."""
        fit = drift.fit(migrations, self.database)
        if not fit.ambiguous:
            return fit
        if self.fake and len(migrations) in fit.ambiguous:
            return fit._replace(position=len(migrations), ambiguous=[])
        if self.force and not self.fake:
            return fit._replace(ambiguous=[])
        app_label = migrations[0].app_label
        candidates = []
        for position in fit.ambiguous:
            if position == 0:
                where = "before all of them"
            else:
                where = f"at {self._label(migrations[position - 1])}"
            commands = self._commands(
                app_label, self._steps(migrations, position), force=position == 0
            )
            candidates.append(f"If it is {where}:\n  " + "\n  ".join(commands))
        self._refuse(
            "This database fits more than one point in these package migrations, "
            "and the migrations between them delete and recreate the same rows, so "
            "running from the wrong one would destroy data. Run the commands for the "
            "point this database is actually at.\n" + "\n".join(candidates)
        )

    def _steps(self, migrations, position):
        """A data migration is recorded only when it has nothing to do here and
        nothing runs before it, since that could give it work. Data migrations
        write no rows the position can see, so they stay on the recorded side
        until the next graph migration."""
        steps = []
        applying = False
        beyond = False
        for index, migration in enumerate(migrations):
            scopes = self._scopes(migration)
            beyond = beyond or (index >= position and "graph" in scopes)
            if beyond:
                action = "apply"
            elif scopes == {"graph"}:
                action = "record"
            elif "graph" in scopes:
                if applying or self._has_pending_work(migration):
                    self._refuse(
                        f"{self._label(migration)} is already partly applied here: its graph changes are present, but it also has data work to do. It was written by hand, so resolve it by hand."
                    )
                action = "record"
            elif applying or self._has_pending_work(migration):
                action = "apply"
            else:
                action = "record"
            applying = applying or action == "apply"
            steps.append((action, migration, beyond))
        return steps

    def _commands(self, app_label, steps, force=False):
        runs = []
        for action, migration, _beyond in steps:
            if runs and runs[-1][0] == action:
                runs[-1] = (action, migration)
            else:
                runs.append((action, migration))
        commands = []
        for index, (action, migration) in enumerate(runs):
            last = index == len(runs) - 1
            if last and app_label == self.app_label:
                target = self.target
            else:
                target = migration.name
            commands.append(
                self._command(
                    app_label, target, fake=action == "record", force=force and last
                )
            )
        return commands

    def _command(self, app_label=None, target=None, fake=False, force=False):
        command = "python manage.py migratepkg"
        if app_label:
            command += f" {app_label}"
        if target:
            command += f" {target}"
        if fake:
            command += " --fake"
        if force:
            command += " --force"
        if self.database != DEFAULT_DB_ALIAS:
            command += f" --database {self.database}"
        return command

    def _directions(self, commands):
        if all(" --fake" in command for command in commands):
            return "Record them instead of applying them by running the following:"
        if any(" --fake" in command for command in commands):
            return "Record the ones already applied and apply the rest by running the following in order:"
        return "Apply them instead by running the following:"

    def _reason(self, migration, beyond):
        if beyond:
            return self._label(migration)
        pending = [
            operation
            for operation in migration.operations
            if operation.scope == "data" and operation.has_pending_work(self.database)
        ]
        if not pending:
            return self._label(migration)
        return f"{self._label(migration)}: {pending[0].describe()}"

    def _has_pending_work(self, migration):
        return any(
            operation.has_pending_work(self.database)
            for operation in migration.operations
            if operation.scope == "data"
        )

    def _scopes(self, migration):
        return {operation.scope for operation in migration.operations}

    def _label(self, migration):
        return f"{migration.app_label}.{migration.name}"

    def _forward_migrations_by_app(self, plan):
        migrations_by_app = {}
        for migration, _backwards in plan:
            migrations_by_app.setdefault(migration.app_label, []).append(migration)
        return migrations_by_app

    def _graphids(self, plan, scope=None):
        return sorted(
            {
                str(operation.graphid)
                for migration, _backwards in plan
                for operation in migration.operations
                if getattr(operation, "graphid", None)
                and scope in (None, operation.scope)
            }
        )

    def _refuse(self, message):
        raise CommandError(
            labels.humanize(message, labels.from_database(message, self.database))
        )

    def _warn(self, message):
        self.stderr.write(
            self.style.WARNING(
                labels.humanize(message, labels.from_database(message, self.database))
            )
        )

    def _discard_stale_drafts(self, plan):
        """A draft copied before this run would undo it on the next Designer
        publish, which rebuilds the live graph entirely from the draft. Dropping
        it is the whole fix: Draft a Model Update copies the migrated graph, which
        is the state a Designer publish leaves too.
        """
        for graphid in self._graphids(plan, scope="graph"):
            graph = Graph.objects.using(self.database).filter(pk=graphid).first()
            if graph is not None and graph.get_draft_graph():
                graph.delete_draft_graph()

    def _remind_to_reindex(self, plan):
        if self.verbosity < 1 or self.database != DEFAULT_DB_ALIAS:
            return
        if any(
            self._changes_untraceable_data(migration) for migration, _backwards in plan
        ):
            self.stdout.write(
                self.style.NOTICE(
                    "These package migrations changed data that cannot be traced to particular resource models. Reindex by running the following:\n  python manage.py es reindex_database"
                )
            )
            return
        resource_models = list(
            models.GraphModel.objects.filter(
                pk__in=self._graphids(plan),
                isresource=True,
                source_identifier__isnull=True,
            )
            .order_by("slug")
            .values_list("graphid", "slug")
        )
        if not resource_models:
            return
        slugs = "\n  ".join(slug for _graphid, slug in resource_models)
        graphids = ",".join(str(graphid) for graphid, _slug in resource_models)
        self.stdout.write(
            self.style.NOTICE(
                f"Search results for these resource models are now out of date:\n  {slugs}\nReindex them by running the following:\n  python manage.py es index_resources_by_type -rt {graphids}"
            )
        )

    def _changes_untraceable_data(self, migration):
        if any(
            isinstance(operation, RunPackagePython)
            for operation in migration.operations
        ):
            return True
        return "data" in self._scopes(migration) and not any(
            getattr(operation, "graphid", None) for operation in migration.operations
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
            marker = "[x]" if backwards else "[ ]"
            self.stdout.write(f"  {marker} {migration.app_label}.{migration.name}")
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
        if action in ("apply_success", "unapply_success"):
            self.completed.append(migration)
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
