"""End-to-end: a real package migration, applied and reversed by migratepkg.

The fixture app lives in a temp directory: ArchesTestRunner discovers *.py, so a
migration module under tests/ would be imported as a test module.
"""

import shutil
import sys
import tempfile
import textwrap
import uuid
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.test import override_settings

from arches.app.models import models
from arches.db.package_migrations.recorder import PackageMigrationRecorder

from tests.package_migrations.spike_tests import PackageMigrationOperationTests

APP_NAME = "pkgmigfixture"


def _write_fixture_app(root, graphid, nodegroup_id, nodeid):
    package = Path(root) / APP_NAME
    migrations = package / "migrations" / "package_migrations"
    migrations.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "migrations" / "__init__.py").write_text("")
    (migrations / "__init__.py").write_text("")
    (package / "apps.py").write_text(textwrap.dedent(f"""
            from django.apps import AppConfig


            class FixtureConfig(AppConfig):
                name = "{APP_NAME}"
                is_arches_application = True
            """))
    edgeid = str(uuid.uuid4())
    (migrations / "0001_add_survey_date.py").write_text(textwrap.dedent(f"""
            from django.db import migrations

            from arches.db.package_migrations.operations.tile import AddNodeToTiles
            from arches.db.package_migrations.operations.edge import CreateEdge
            from arches.db.package_migrations.operations.node import CreateNode


            class Migration(migrations.Migration):
                initial = True
                dependencies = []
                operations = [
                    CreateNode(
                        graphid="{graphid}",
                        fields={{
                            "nodeid": "{nodeid}",
                            "name": "Survey Date",
                            "datatype": "date",
                            "alias": "survey_date_cmd",
                            "nodegroup_id": "{nodegroup_id}",
                            "istopnode": False,
                        }},
                    ),
                    CreateEdge(
                        graphid="{graphid}",
                        fields={{
                            "edgeid": "{edgeid}",
                            "domainnode_id": "{nodegroup_id}",
                            "rangenode_id": "{nodeid}",
                        }},
                    ),
                    AddNodeToTiles(
                        nodegroup_id="{nodegroup_id}",
                        nodeid="{nodeid}",
                        value=None,
                    ),
                ]
            """))
    return package


class MigratePkgCommandTests(PackageMigrationOperationTests):
    def setUp(self):
        super().setUp()
        self.nodeid = str(uuid.uuid4())
        self.tmpdir = tempfile.mkdtemp()
        _write_fixture_app(
            self.tmpdir, str(self.graph.graphid), str(self.nodegroup_id), self.nodeid
        )
        sys.path.insert(0, self.tmpdir)
        with connection.schema_editor() as schema_editor:
            if not PackageMigrationRecorder(connection).has_table():
                schema_editor.create_model(PackageMigrationRecorder.Migration)

    def tearDown(self):
        sys.path.remove(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        for module in list(sys.modules):
            if module.startswith(APP_NAME):
                del sys.modules[module]
        PackageMigrationRecorder(connection).migration_qs.filter(app=APP_NAME).delete()
        super().tearDown()

    def _installed(self):
        return override_settings(
            INSTALLED_APPS=list(settings.INSTALLED_APPS)
            + [f"{APP_NAME}.apps.FixtureConfig"]
        )

    def test_migratepkg_applies_and_reverses_a_real_migration(self):
        tile = models.TileModel.objects.create(
            resourceinstance=models.ResourceInstance.objects.create(graph=self.graph),
            nodegroup_id=self.nodegroup_id,
            data={str(self.string_node.nodeid): None},
        )

        with self._installed():
            out = StringIO()
            call_command("showpkgmigrations", APP_NAME, stdout=out)
            self.assertIn("[ ] 0001_add_survey_date", out.getvalue())

            call_command("migratepkg", APP_NAME, verbosity=0)

            self.assertTrue(models.Node.objects.filter(pk=self.nodeid).exists())
            tile.refresh_from_db()
            self.assertIn(self.nodeid, tile.data)

            out = StringIO()
            call_command("showpkgmigrations", APP_NAME, stdout=out)
            self.assertIn("[X] 0001_add_survey_date", out.getvalue())

            out = StringIO()
            call_command("migratepkg", APP_NAME, stdout=out)
            self.assertIn("No package migrations to apply", out.getvalue())

            call_command("migratepkg", APP_NAME, "zero", verbosity=0)

            self.assertFalse(models.Node.objects.filter(pk=self.nodeid).exists())
            tile.refresh_from_db()
            self.assertNotIn(self.nodeid, tile.data)

    def test_plan_describes_operations_without_applying(self):
        with self._installed():
            out = StringIO()
            call_command("migratepkg", APP_NAME, plan=True, stdout=out)
            output = out.getvalue()
            self.assertIn("Create node survey_date_cmd (date)", output)
            self.assertIn("to tiles in nodegroup", output)
            self.assertFalse(models.Node.objects.filter(pk=self.nodeid).exists())
