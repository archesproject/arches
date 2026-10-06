"""makepkgmigrations: generate from the graphs in the database, then apply what was
generated."""

import json
import shutil
import sys
import tempfile
import textwrap
import uuid
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import CommandError, call_command
from django.db import connection
from django.test import override_settings

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.system_settings import settings as arches_settings
from arches.db.package_migrations.operations.graph import CreateGraph
from arches.db.package_migrations.recorder import PackageMigrationRecorder
from arches.db.package_migrations.state import canonical_graph
from arches.management.commands.makepkgmigrations import (
    Command as MakePkgMigrationsCommand,
)

from tests.package_migrations.spike_tests import PackageMigrationOperationTests

APP_NAME = "pkggenfixture"
OTHER_APP_NAME = "pkggenother"


def _write_app(root, app_name):
    package = Path(root) / app_name
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "apps.py").write_text(textwrap.dedent(f"""
            from django.apps import AppConfig


            class FixtureConfig(AppConfig):
                name = "{app_name}"
                is_arches_application = True
            """))
    return package


class MakePkgMigrationsTests(PackageMigrationOperationTests):
    def setUp(self):
        super().setUp()
        self.tmpdir = tempfile.mkdtemp()
        self.package = _write_app(self.tmpdir, APP_NAME)
        sys.path.insert(0, self.tmpdir)
        with connection.schema_editor() as schema_editor:
            if not PackageMigrationRecorder(connection).has_table():
                schema_editor.create_model(PackageMigrationRecorder.Migration)

    def tearDown(self):
        sys.path.remove(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        for module in list(sys.modules):
            if module.startswith((APP_NAME, OTHER_APP_NAME)):
                del sys.modules[module]
        super().tearDown()

    def _installed(self, *other_app_names):
        return override_settings(
            INSTALLED_APPS=list(settings.INSTALLED_APPS)
            + [
                f"{app_name}.apps.FixtureConfig"
                for app_name in (APP_NAME, *other_app_names)
            ]
        )

    def _make(self, **options):
        stdout, stderr = StringIO(), StringIO()
        call_command(
            "makepkgmigrations", APP_NAME, stdout=stdout, stderr=stderr, **options
        )
        return stdout.getvalue(), stderr.getvalue()

    def _adopt(self):
        return self._make(graphs=[str(self.graph.graphid)])

    def _migration_files(self):
        directory = self.package / "migrations" / "package_migrations"
        if not directory.is_dir():
            return []
        return sorted(
            migration_path.name for migration_path in directory.glob("[0-9]*.py")
        )

    def _migration(self, filename):
        module = __import__(
            f"{APP_NAME}.migrations.package_migrations.{filename[:-3]}",
            fromlist=["Migration"],
        )
        return module.Migration

    def _recorded(self):
        return set(
            PackageMigrationRecorder(connection)
            .migration_qs.filter(app=APP_NAME)
            .values_list("name", flat=True)
        )

    def _publication_id(self):
        return str(models.GraphModel.objects.get(pk=self.graph.graphid).publication_id)

    def _add_node(self, alias):
        nodeid = str(uuid.uuid4())
        models.Node.objects.create(
            nodeid=nodeid,
            graph_id=self.graph.graphid,
            nodegroup_id=self.nodegroup_id,
            name=alias,
            datatype="date",
            alias=alias,
            hascustomalias=True,
            istopnode=False,
        )
        models.Edge.objects.create(
            edgeid=uuid.uuid4(),
            graph_id=self.graph.graphid,
            domainnode_id=self.nodegroup_id,
            rangenode_id=nodeid,
            ontologyproperty="http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
        )
        return nodeid

    def _publish_a_new_node(self, alias="survey_date"):
        """What a Graph Designer publish leaves behind: new rows on the source
        graph, on a new publication."""
        nodeid = self._add_node(alias)
        Graph.objects.get(pk=self.graph.graphid).publish()
        return nodeid

    def test_refuses_apps_that_are_not_arches_applications(self):
        with self.assertRaises(CommandError):
            call_command("makepkgmigrations", "models")

    def test_an_app_with_no_history_must_name_its_graphs(self):
        with self._installed():
            with self.assertRaises(CommandError) as refusal:
                self._make()
        self.assertIn("--graph", str(refusal.exception))

    def test_adopting_a_graph_describes_it_whole_and_records_it(self):
        publication_count = models.GraphXPublishedGraph.objects.count()
        with self._installed():
            stdout, _stderr = self._adopt()
            files = self._migration_files()
            self.assertEqual(len(files), 1, files)
            self.assertTrue(files[0].startswith("0001_graph_"))
            migration = self._migration(files[0])
            self.assertEqual(type(migration.operations[0]).__name__, "CreateGraph")
            publish = migration.operations[-1]
            self.assertEqual(type(publish).__name__, "PublishGraph")
            self.assertEqual(str(publish.publication_id), self._publication_id())
            self.assertEqual(self._recorded(), {files[0][:-3]})
            self.assertIn("Recorded", stdout)
        self.assertEqual(models.GraphXPublishedGraph.objects.count(), publication_count)

    def test_a_graph_can_be_named_by_slug(self):
        with self._installed():
            self._make(graphs=[self.graph.slug])
            self.assertEqual(len(self._migration_files()), 1)

    def test_second_run_detects_nothing_new(self):
        with self._installed():
            self._adopt()
            stdout, _stderr = self._make()
            self.assertIn("No changes detected", stdout)
            self.assertEqual(len(self._migration_files()), 1)

    def test_a_designer_change_is_recorded_here_and_its_data_migration_runs(self):
        with self._installed():
            self._adopt()
            adoption_publication_id = self._publication_id()
            resource = models.ResourceInstance.objects.create(graph=self.graph)
            tile = models.TileModel.objects.create(
                resourceinstance=resource,
                nodegroup_id=self.nodegroup_id,
                data={str(self.string_node.nodeid): None},
            )
            nodeid = self._publish_a_new_node()
            designer_publication_id = self._publication_id()
            publication_count = models.GraphXPublishedGraph.objects.count()

            stdout, _stderr = self._make()
            files = self._migration_files()
            self.assertEqual(len(files), 3, files)
            graph_file, data_file = files[1], files[2]
            self.assertIn("_graph_", graph_file)
            self.assertIn("_data_", data_file)
            for filename in (graph_file, data_file):
                scopes = {
                    operation.scope
                    for operation in self._migration(filename).operations
                }
                self.assertEqual(len(scopes), 1, filename)
            publish = self._migration(graph_file).operations[-1]
            self.assertEqual(str(publish.publication_id), designer_publication_id)
            self.assertEqual(
                str(publish.previous_publication_id), adoption_publication_id
            )
            self.assertEqual(self._recorded(), {files[0][:-3], graph_file[:-3]})
            self.assertEqual(
                models.GraphXPublishedGraph.objects.count(), publication_count
            )
            self.assertIn(f"python manage.py migratepkg {APP_NAME}", stdout)

            output = StringIO()
            call_command("migratepkg", APP_NAME, stdout=output)
            tile.refresh_from_db()
            self.assertIn(nodeid, tile.data)
            resource.refresh_from_db()
            self.assertEqual(
                str(resource.graph_publication_id), designer_publication_id
            )
            self.assertEqual(self._recorded(), {name[:-3] for name in files})
            self.assertIn(
                f"index_resources_by_type -rt {self.graph.graphid}", output.getvalue()
            )

    def test_check_exits_non_zero_and_writes_nothing(self):
        with self._installed():
            self._adopt()
            self._publish_a_new_node()
            with self.assertRaises(CommandError):
                self._make(check=True)
            self.assertEqual(len(self._migration_files()), 1)
            self.assertEqual(len(self._recorded()), 1)

    def test_dry_run_writes_and_records_nothing(self):
        with self._installed():
            stdout, _stderr = self._make(graphs=[str(self.graph.graphid)], dry_run=True)
            self.assertIn("Create graph", stdout)
            self.assertEqual(self._migration_files(), [])
            self.assertEqual(self._recorded(), set())

    def test_refuses_while_a_migration_of_the_app_is_unapplied(self):
        """A new migration depends on the leaf, so recording it while the leaf is
        unapplied leaves an applied migration whose parent is not."""
        with self._installed():
            self._adopt()
            self._publish_a_new_node()
            self._make()
            data_migration = self._migration_files()[-1][:-3]
            self._publish_a_new_node(alias="second_node")

            with self.assertRaises(CommandError) as refusal:
                self._make()
            self.assertIn(data_migration, str(refusal.exception))
            self.assertIn(
                f"python manage.py migratepkg {APP_NAME}", str(refusal.exception)
            )

            _stdout, stderr = self._make(dry_run=True)
            self.assertIn(data_migration, stderr)

    def test_refuses_when_a_recorded_migration_file_is_missing(self):
        with self._installed():
            self._adopt()
            adoption_file = self._migration_files()[0]
            (
                self.package / "migrations" / "package_migrations" / adoption_file
            ).unlink()
            with self.assertRaises(CommandError) as refusal:
                self._make()
            self.assertIn(adoption_file[:-3], str(refusal.exception))

    def test_refuses_unpublished_designer_changes(self):
        with self._installed():
            self._adopt()
            self._add_node("unpublished")
            with self.assertRaises(CommandError) as refusal:
                self._make()
            self.assertIn("not published", str(refusal.exception))

            _stdout, stderr = self._make(dry_run=True)
            self.assertIn("not published", stderr)

    def test_reads_the_source_graph_not_its_draft(self):
        with self._installed():
            self._adopt()
            source = Graph.objects.get(pk=self.graph.graphid)
            draft = source.get_draft_graph() or source.create_draft_graph()
            models.Node.objects.filter(
                graph_id=draft.graphid, datatype="string"
            ).update(alias="draft_only")
            stdout, _stderr = self._make()
            self.assertIn("No changes detected", stdout)

    def test_refuses_graphs_that_cannot_belong_to_an_application(self):
        with self._installed():
            with self.assertRaises(CommandError) as unknown:
                self._make(graphs=["all"])
            self.assertIn("'all'", str(unknown.exception))

            source = Graph.objects.get(pk=self.graph.graphid)
            draft = source.get_draft_graph() or source.create_draft_graph()
            with self.assertRaises(CommandError) as drafted:
                self._make(graphs=[str(draft.graphid)])
            self.assertIn(self.graph.slug, str(drafted.exception))

            CreateGraph(
                fields={
                    "graphid": arches_settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID,
                    "name": "System Settings",
                    "slug": "system_settings_fixture",
                    "isresource": True,
                }
            ).database_forwards(
                "arches", self.schema_editor, self._state(), self._state()
            )
            with self.assertRaises(CommandError) as system_settings:
                self._make(graphs=[arches_settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID])
            self.assertIn("System Settings", str(system_settings.exception))
            self.assertEqual(self._migration_files(), [])

    def test_refuses_a_graph_another_application_owns(self):
        other_package = _write_app(self.tmpdir, OTHER_APP_NAME)
        migrations_directory = other_package / "migrations" / "package_migrations"
        migrations_directory.mkdir(parents=True)
        (other_package / "migrations" / "__init__.py").write_text("")
        (migrations_directory / "__init__.py").write_text("")
        (migrations_directory / "0001_graph_owned.py").write_text(textwrap.dedent(f"""
                from django.db import migrations

                from arches.db.package_migrations.operations import AlterGraph


                class Migration(migrations.Migration):
                    initial = True
                    dependencies = []
                    operations = [
                        AlterGraph(graphid="{self.graph.graphid}", changes={{"subtitle": None}}),
                    ]
                """))
        with self._installed(OTHER_APP_NAME):
            with self.assertRaises(CommandError) as refusal:
                self._adopt()
        self.assertIn(OTHER_APP_NAME, str(refusal.exception))

    def test_created_graphs_get_a_graph_migration_of_their_own(self):
        """A site that already has the new graph from load_package records that
        migration and applies the change to the existing graph."""
        with self._installed():
            self._adopt()
            self._publish_a_new_node()
            new_graph = self.create_test_graph()
            self._make(graphs=[str(new_graph.graphid)])

            files = self._migration_files()
            self.assertEqual(len(files), 4, files)
            created = self._migration(files[1])
            self.assertEqual(type(created.operations[0]).__name__, "CreateGraph")
            self.assertEqual(
                {str(operation.graphid) for operation in created.operations},
                {str(new_graph.graphid)},
            )
            changed = self._migration(files[2])
            self.assertEqual(
                {str(operation.graphid) for operation in changed.operations},
                {str(self.graph.graphid)},
            )
            self.assertIn("_data_", files[3])
            self.assertEqual(self._recorded(), {name[:-3] for name in files[:3]})

    def test_moving_a_node_between_nodegroups_warns_that_data_is_stranded(self):
        """Nodegroup membership follows the edge tree, so the node moves the way
        the Designer moves it: under another collector."""
        with self._installed():
            self._adopt()
            collector_id = uuid.uuid4()
            models.NodeGroup.objects.create(nodegroupid=collector_id, cardinality="n")
            models.Node.objects.create(
                nodeid=collector_id,
                graph_id=self.graph.graphid,
                nodegroup_id=collector_id,
                name="Second Group",
                datatype="semantic",
                alias="second_group",
                hascustomalias=True,
                istopnode=False,
            )
            models.NodeGroup.objects.filter(pk=collector_id).update(
                grouping_node_id=collector_id
            )
            models.Edge.objects.create(
                edgeid=uuid.uuid4(),
                graph_id=self.graph.graphid,
                domainnode_id=self.graph.root.nodeid,
                rangenode_id=collector_id,
                ontologyproperty="http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            )
            models.Edge.objects.filter(rangenode_id=self.string_node.nodeid).update(
                domainnode_id=collector_id
            )
            models.Node.objects.filter(pk=self.string_node.nodeid).update(
                nodegroup_id=collector_id
            )
            _stdout, stderr = self._make(dry_run=True)
            self.assertIn("stranded", stderr)
            self.assertIn(str(self.string_node.nodeid), stderr)

    def test_changing_a_datatype_warns_that_stored_values_are_not_converted(self):
        with self._installed():
            self._adopt()
            models.Node.objects.filter(pk=self.string_node.nodeid).update(
                datatype="concept"
            )
            _stdout, stderr = self._make(dry_run=True)
            self.assertIn("changing datatype to 'concept'", stderr)
            self.assertIn("RunPackagePython", stderr)

    def test_refuses_a_name_that_is_not_an_identifier(self):
        with self._installed():
            with self.assertRaises(CommandError):
                self._make(graphs=[str(self.graph.graphid)], name="my-fix")
            self.assertEqual(self._migration_files(), [])

    def test_reads_exactly_what_export_graphs_writes(self):
        """Histories made from exported files diff cleanly against the database."""
        export_directory = Path(self.tmpdir) / "export"
        export_directory.mkdir()
        call_command(
            "packages",
            operation="export_graphs",
            dest_dir=str(export_directory),
            graphs=str(self.graph.graphid),
        )
        exported_file = list(export_directory.glob("*.json"))[0]
        exported = json.loads(exported_file.read_text())["graph"][0]
        from_database = MakePkgMigrationsCommand()._database_graphs(
            {str(self.graph.graphid)}
        )
        self.assertEqual(
            from_database[str(self.graph.graphid)], canonical_graph(exported)
        )
