"""Apply graph migrations, shaped like `manage.py migrate`."""

import os
from collections import Counter

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.exceptions import AmbiguityError

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.graph_migrations import drift, labels
from arches.db.graph_migrations.executor import GraphMigrationExecutor
from arches.db.graph_migrations.operations.base import GraphMigrationError
from arches.db.graph_migrations.operations.graph import PublishGraph
from arches.db.graph_migrations.operations.python import RunGraphPython
from arches.db.graph_migrations.operations.resource import SetResourcePublication


class Command(BaseCommand):
    help = "Applies graph migrations for Arches applications."

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
            help="Go ahead where a refusal offers --force: skip changes to what is no longer here, discard unpublished Graph Designer changes, unapply nodegroups that still have tiles, mark tile changes as applied without running them, or start from the earliest migration this database's graph matches.",
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

        executor = GraphMigrationExecutor(connection, progress_callback=self._progress)
        executor.loader.check_consistent_history(connection)

        conflicts = executor.loader.detect_conflicts()
        if conflicts:
            described = "; ".join(
                f"{app}: {', '.join(names)}" for app, names in conflicts.items()
            )
            raise CommandError(
                f"More than one graph migration is the latest in its app ({described}), usually because two branches each added one. Make one depend on the other, then run this command again."
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
                self.stdout.write("No graph migrations to apply.")
            return

        self._refuse_missing_references(plan)
        if self.fake:
            self._refuse_faking_work(plan)
        else:
            self._refuse_destructive_reversals(plan)
            self._refuse_discarding_unpublished_drafts(plan)
            self._refuse_misfit_database(plan)
            self._warn_about_unrestored_data(plan)

        self.completed = []
        try:
            executor.migrate(targets, plan=plan, fake=self.fake)
        except GraphMigrationError as error:
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
            raise CommandError(f"App '{app_label}' does not have graph migrations.")

        if migration_name is None:
            return graph.leaf_nodes(app_label)

        if migration_name == "zero":
            return [(app_label, None)]

        try:
            migration = executor.loader.get_migration_by_prefix(
                app_label, migration_name
            )
        except AmbiguityError:
            raise CommandError(
                f"More than one graph migration matches '{migration_name}' in app '{app_label}'. Give a more specific prefix."
            )
        except KeyError:
            raise CommandError(
                f"Cannot find a graph migration matching '{migration_name}' for app '{app_label}'."
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
                f"This database has applied these graph migrations, but their files are missing:\n  {missing_names}\nRestore them, for example by checking out the branch that has them."
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
            "These graph migrations use records this database does not have:\n  "
            + "\n  ".join(problem.message for problem in problems)
            + "\nGraph migrations do not create ontologies, widgets, card components and "
            "the like; installing the application's package does. To install it and try "
            f"again, run:\n  {install_commands}\n  {self._command(self.app_label, self.target, fake=self.fake)}"
        )

    def _refuse_destructive_reversals(self, plan):
        problems = drift.reverse_problems(plan, self.database)
        destructive = [problem for problem in problems if problem.kind == "destructive"]
        if destructive:
            self._refuse(
                "Unapplying these graph migrations would delete a graph that has "
                "resources, along with every resource and tile on it:\n  "
                + "\n  ".join(problem.message for problem in destructive)
                + "\nTo keep the graph, unapply only the migrations after the one that creates it."
            )
        orphans = [problem for problem in problems if problem.kind == "orphans"]
        if orphans:
            message = (
                "Unapplying these graph migrations would delete nodegroups that still "
                "have tiles, leaving those tiles orphaned:\n  "
                + "\n  ".join(problem.message for problem in orphans)
            )
            if not self.force:
                self._refuse(
                    f"{message}\nTo unapply them anyway, run:\n  {self._command(self.app_label, self.target, force=True)}"
                )
            self._warn(message)

    def _warn_about_unrestored_data(self, plan):
        unrestored = [
            problem
            for problem in drift.reverse_problems(plan, self.database)
            if problem.kind == "unrestored"
        ]
        if unrestored:
            self._warn(
                "Unapplying these graph migrations puts the graph back, but not "
                "the tiles or values they deleted:\n  "
                + "\n  ".join(problem.message for problem in unrestored)
            )

    def _refuse_discarding_unpublished_drafts(self, plan):
        slugs = sorted(
            models.GraphModel.objects.using(self.database)
            .filter(
                source_identifier_id__in=self._graphids(plan, scope="schema"),
                has_unpublished_changes=True,
            )
            .values_list("source_identifier__slug", flat=True)
        )
        if not slugs:
            return
        message = (
            "These graphs have unpublished changes in the Graph Designer, which this "
            "run would discard:\n  " + "\n  ".join(slugs)
        )
        if self.force:
            self._warn(message)
            return
        self._refuse(
            f"{message}\nPublish or revert them in the Graph Designer, then run this command again. To discard them instead, run:\n  {self._command(self.app_label, self.target, force=True)}"
        )

    def _refuse_faking_work(self, plan):
        # A faked data migration is never checked again, so its work is lost.
        if plan[0][1]:
            with_data = [
                migration
                for migration, _backwards in plan
                if "data" in self._scopes(migration)
            ]
            if not with_data:
                return
            message = (
                "Marking these graph migrations as unapplied without reversing them "
                "would leave the changes they made to tiles and resources in place:\n  "
                + "\n  ".join(self._label(migration) for migration in with_data)
            )
            if self.force:
                self._warn(message)
                return
            self._refuse(
                f"{message}\nTo undo those changes as well, run:\n  {self._command(self.app_label, self.target)}"
            )
            return

        reasons, commands = [], []
        for app_label, migrations in self._forward_migrations_by_app(plan).items():
            fit = self._fit(migrations)
            if fit.position is None:
                message = (
                    "This database's graph does not match the graph as it was after "
                    "any of these graph migrations, so they cannot be marked as applied "
                    "without running them:\n  "
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
            "Some of these graph migrations still have changes to make to this "
            "database. Marking them as applied without running them would skip those "
            "changes for good:\n  " + "\n  ".join(reasons)
        )
        if self.force:
            self._warn(message)
            return
        self._refuse(
            f"{message}\n{self._directions(commands)}\n  " + "\n  ".join(commands)
        )

    def _refuse_misfit_database(self, plan):
        # An alter on rows edited since updates nothing and still succeeds.
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
            "It looks like these graph migrations have already been applied to "
            "this database but not recorded:\n  " + "\n  ".join(recorded)
        )
        if to_apply:
            message += (
                "\nThese still have changes to make here, so they need to run:\n  "
                + "\n  ".join(to_apply)
            )
        self._refuse(
            f"{message}\n{self._directions(commands)}\n  " + "\n  ".join(commands)
        )

    def _refuse_diverged(self, problems):
        if all(problem.kind == "missing" for problem in problems):
            message = (
                "This database's graph has been edited since these graph migrations "
                "were made. Some of what they change or delete is no longer here, so "
                "those changes would be skipped:\n  "
                + "\n  ".join(problem.message for problem in problems)
            )
            if self.force:
                self._warn(message)
                return
            self._refuse(
                f"{message}\nRestore them in the Graph Designer, then run this command again. To apply everything else anyway, run:\n  {self._command(self.app_label, self.target, force=True)}"
            )
        self._refuse(
            "This database's graph has been edited since these graph migrations were "
            "made, and no longer matches the graph as it was after any of them:\n  "
            + "\n  ".join(problem.message for problem in problems)
            + "\nUndo those edits in the Graph Designer so the graph matches, then run this command again."
        )

    def _fit(self, migrations):
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
                where = "none of them"
            else:
                where = f"up to {self._label(migrations[position - 1])}"
            commands = self._commands(
                app_label, self._steps(migrations, position), force=position == 0
            )
            candidates.append(f"If it had {where}:\n  " + "\n  ".join(commands))
        self._refuse(
            "This database's graph matches the graph as it was after more than one of "
            "these graph migrations, because the ones in between delete and recreate "
            "the same rows. Running from the wrong one would destroy data, so run the "
            "commands for the last migration this database actually had.\n"
            + "\n".join(candidates)
        )

    def _steps(self, migrations, position):
        # Record a data migration only if it and every earlier step need no work.
        steps = []
        applying = False
        beyond = False
        for index, migration in enumerate(migrations):
            scopes = self._scopes(migration)
            beyond = beyond or (index >= position and "schema" in scopes)
            if beyond:
                action = "apply"
            elif scopes == {"schema"}:
                action = "record"
            elif "schema" in scopes:
                if applying or self._has_pending_work(migration):
                    self._refuse(
                        f"{self._label(migration)} is partly applied to this database: its graph changes are here, but its changes to tiles and resources are not. It mixes both, so it was written by hand; finish or undo it by hand."
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
        command = "python manage.py migrategraphs"
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
            return "To mark them as applied without running them, run:"
        if any(" --fake" in command for command in commands):
            return (
                "To mark the ones already applied and run the rest, run these in order:"
            )
        return "To apply them instead, run:"

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
        # Publishing a stale draft rebuilds the graph from it, undoing this run.
        for graphid in self._graphids(plan, scope="schema"):
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
                    "Search results may be out of date for any resource model: these graph migrations changed data that is not tied to particular ones. To reindex everything, run:\n  python manage.py es reindex_database"
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
                f"Search results for these resource models are now out of date:\n  {slugs}\nTo reindex them, run:\n  python manage.py es index_resources_by_type -rt {graphids}"
            )
        )

    def _changes_untraceable_data(self, migration):
        if any(
            isinstance(operation, RunGraphPython) for operation in migration.operations
        ):
            return True
        return "data" in self._scopes(migration) and not any(
            getattr(operation, "graphid", None) for operation in migration.operations
        )

    def _refuse_half_reversals(self, plan):
        # Django raises only at the irreversible one, after unapplying those before it.
        for migration, backwards in plan:
            if not backwards:
                continue
            irreversible = [
                operation
                for operation in migration.operations
                if not operation.reversible
            ]
            if not irreversible:
                continue
            operation = irreversible[0]
            message = f"{migration.app_label}.{migration.name} cannot be unapplied: {operation.describe()} is irreversible."
            if isinstance(operation, (PublishGraph, SetResourcePublication)):
                message += " Unapplying the migrations after it would leave the graph and its resources on different publications."
            elif isinstance(operation, RunGraphPython):
                message += " It has no reverse_code."
            raise CommandError(message)

    def _print_plan(self, plan):
        if not plan:
            self.stdout.write("No graph migrations to apply.")
            return
        self.stdout.write("Planned graph migrations:")
        for migration, backwards in plan:
            marker = "[x]" if backwards else "[ ]"
            self.stdout.write(f"  {marker} {migration.app_label}.{migration.name}")
            self._print_operations(migration.operations)

    def _print_operations(self, operations):
        described = [operation.describe() for operation in operations]
        if self.verbosity >= 2 or len(operations) <= self.PLAN_DETAIL_LIMIT:
            names = labels.from_database("\n".join(described), self.database)
            for description in described:
                self.stdout.write(f"      {labels.humanize(description, names)}")
            return

        counts = Counter(type(operation).__name__ for operation in operations)
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
        elif action == "unapply_start":
            self.stdout.write(f"  Unapplying {migration}...", ending="")
            self.stdout.flush()
        elif action in ("apply_success", "unapply_success"):
            self.stdout.write(self.style.SUCCESS(" FAKED" if fake else " OK"))
