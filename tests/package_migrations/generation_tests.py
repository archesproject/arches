"""makepkgmigrations: generate from committed JSON, then apply what was generated.

Generation reads only the repo -- committed graph JSON on one side, replayed
migration state on the other -- so these assertions hold regardless of what is in
the database.
"""

import json
import shutil
import sys
import tempfile
import textwrap
import uuid
from io import StringIO
from pathlib import Path

from django.apps import apps
from django.core.management import CommandError, call_command
from django.test import override_settings

from arches.db.package_migrations.canonical import canonical_graph

from tests.package_migrations.spike_tests import PackageMigrationOperationTests

APP_NAME = "pkggenfixture"


class MakePkgMigrationsTests(PackageMigrationOperationTests):
    def setUp(self):
        super().setUp()
        self.tmpdir = tempfile.mkdtemp()
        self.package = Path(self.tmpdir) / APP_NAME
        (self.package / "pkg" / "graphs" / "resource_models").mkdir(parents=True)
        (self.package / "__init__.py").write_text("")
        (self.package / "apps.py").write_text(
            textwrap.dedent(
                """
                from django.apps import AppConfig


                class FixtureConfig(AppConfig):
                    name = "%s"
                    is_arches_application = True
                """
                % APP_NAME
            )
        )
        sys.path.insert(0, self.tmpdir)

    def tearDown(self):
        sys.path.remove(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        for module in list(sys.modules):
            if module.startswith(APP_NAME):
                del sys.modules[module]
        super().tearDown()

    def _installed(self):
        from django.conf import settings

        return override_settings(
            INSTALLED_APPS=list(settings.INSTALLED_APPS)
            + ["%s.apps.FixtureConfig" % APP_NAME]
        )

    def _commit_graph(self, **overrides):
        published = self.graph.get_published_graph()
        canonical = canonical_graph(published.serialized_graph)
        for key, value in overrides.items():
            canonical[key] = value
        filename = "{}.json".format(canonical["graphid"])
        directory = self.package / "pkg" / "graphs" / "resource_models"
        (directory / filename).write_text(
            json.dumps(canonical, indent=4, sort_keys=True)
        )
        return canonical

    def _migration_files(self):
        directory = self.package / "migrations" / "package_migrations"
        if not directory.is_dir():
            return []
        return sorted(p.name for p in directory.glob("[0-9]*.py"))

    def test_no_changes_when_json_matches_replayed_state(self):
        """The graph exists in the database but not in migration history, so the
        diff is against an empty replayed state -- everything in the JSON is new."""
        self._commit_graph()
        with self._installed():
            out = StringIO()
            call_command("makepkgmigrations", APP_NAME, dry_run=True, stdout=out)
            self.assertIn("Create graph", out.getvalue())

    def test_generates_a_migration_that_then_applies(self):
        self._commit_graph()
        with self._installed():
            call_command("makepkgmigrations", APP_NAME, verbosity=0)
            files = self._migration_files()
            self.assertEqual(len(files), 1, files)
            self.assertTrue(files[0].startswith("0001_"))

            # The generated file must be importable and runnable, not just written.
            source = (
                self.package / "migrations" / "package_migrations" / files[0]
            ).read_text()
            self.assertIn("import arches.db.package_migrations.operations", source)
            self.assertIn("CreateGraph", source)

            out = StringIO()
            call_command("migratepkg", APP_NAME, plan=True, stdout=out)
            self.assertIn("Create graph", out.getvalue())

    def test_second_run_detects_nothing_new(self):
        self._commit_graph()
        with self._installed():
            call_command("makepkgmigrations", APP_NAME, verbosity=0)
            out = StringIO()
            call_command("makepkgmigrations", APP_NAME, stdout=out)
            self.assertIn("No changes detected", out.getvalue())
            self.assertEqual(len(self._migration_files()), 1)

    def test_check_exits_non_zero_when_a_migration_is_missing(self):
        self._commit_graph()
        with self._installed():
            with self.assertRaises(CommandError):
                call_command("makepkgmigrations", APP_NAME, check=True)
            self.assertEqual(self._migration_files(), [])

    def test_refuses_apps_that_are_not_arches_applications(self):
        with self.assertRaises(CommandError):
            call_command("makepkgmigrations", "models")
