"""migratepkg: where a database sits in a plan, the commands it is told to run,
and what a reversal leaves behind."""

import shutil
import sys
import tempfile
import textwrap
import uuid
from io import StringIO
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management import CommandError, call_command
from django.db import connection
from django.test import override_settings

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.package_migrations.recorder import PackageMigrationRecorder

from tests.package_migrations.spike_tests import PackageMigrationOperationTests

APP_NAME = "pkgmigratefixture"
ONTOLOGY_PROPERTY = "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by"


class MigratePkgTests(PackageMigrationOperationTests):
    def setUp(self):
        super().setUp()
        self.tmpdir = tempfile.mkdtemp()
        package = Path(self.tmpdir) / APP_NAME
        self.migrations_directory = package / "migrations" / "package_migrations"
        self.migrations_directory.mkdir(parents=True)
        for init in (
            package / "__init__.py",
            package / "migrations" / "__init__.py",
            self.migrations_directory / "__init__.py",
        ):
            init.write_text("")
        (package / "apps.py").write_text(textwrap.dedent(f"""
                from django.apps import AppConfig


                class FixtureConfig(AppConfig):
                    name = "{APP_NAME}"
                    is_arches_application = True
                """))
        sys.path.insert(0, self.tmpdir)
        with connection.schema_editor() as schema_editor:
            if not PackageMigrationRecorder(connection).has_table():
                schema_editor.create_model(PackageMigrationRecorder.Migration)
        self.graphid = str(self.graph.graphid)
        self.nodeid = str(uuid.uuid4())
        self.edgeid = str(uuid.uuid4())

    def tearDown(self):
        sys.path.remove(self.tmpdir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        for module in list(sys.modules):
            if module.startswith(APP_NAME):
                del sys.modules[module]
        super().tearDown()

    def _installed(self):
        return override_settings(
            INSTALLED_APPS=list(settings.INSTALLED_APPS)
            + [f"{APP_NAME}.apps.FixtureConfig"]
        )

    def _write_migrations(self, *migrations):
        previous_name = None
        for name, atomic, operations in migrations:
            if previous_name:
                dependencies = f'[("{APP_NAME}", "{previous_name}")]'
            else:
                dependencies = "[]"
            atomic_line = "" if atomic else "    atomic = False\n"
            (self.migrations_directory / f"{name}.py").write_text(
                "from django.db import migrations\n\n"
                "from arches.db.package_migrations.operations import *\n\n\n"
                "class Migration(migrations.Migration):\n"
                f"    dependencies = {dependencies}\n"
                f"{atomic_line}"
                f"    operations = [{', '.join(operations)}]\n"
            )
            previous_name = name

    def _migratepkg(self, *arguments, **options):
        stdout, stderr = StringIO(), StringIO()
        call_command("migratepkg", *arguments, stdout=stdout, stderr=stderr, **options)
        return stdout.getvalue(), stderr.getvalue()

    def _recorded(self):
        return set(
            PackageMigrationRecorder(connection)
            .migration_qs.filter(app=APP_NAME)
            .values_list("name", flat=True)
        )

    def _graph_row(self):
        return models.GraphModel.objects.get(pk=self.graphid)

    def _create_node(self, nodeid=None, alias="survey_date", datatype="date"):
        nodeid = nodeid or self.nodeid
        return f'CreateNode(graphid="{self.graphid}", fields={{"nodeid": "{nodeid}", "name": "{alias}", "datatype": "{datatype}", "alias": "{alias}", "nodegroup_id": "{self.nodegroup_id}", "istopnode": False}})'

    def _create_edge(self):
        return f'CreateEdge(graphid="{self.graphid}", fields={{"edgeid": "{self.edgeid}", "domainnode_id": "{self.nodegroup_id}", "rangenode_id": "{self.nodeid}", "ontologyproperty": "{ONTOLOGY_PROPERTY}"}})'

    def _publish(self, publication_id, previous_publication_id):
        return f'PublishGraph(graphid="{self.graphid}", publication_id="{publication_id}", previous_publication_id="{previous_publication_id}")'

    def _move_resources(self, publication_id, previous_publication_id):
        return f'SetResourcePublication(graphid="{self.graphid}", publication_id="{publication_id}", previous_publication_id="{previous_publication_id}")'

    def _add_node_to_tiles(self):
        return f'AddNodeToTiles(nodegroup_id="{self.nodegroup_id}", nodeid="{self.nodeid}")'

    def _add_node_rows(self):
        models.Node.objects.create(
            nodeid=self.nodeid,
            graph_id=self.graphid,
            nodegroup_id=self.nodegroup_id,
            name="survey_date",
            datatype="date",
            alias="survey_date",
            istopnode=False,
        )
        models.Edge.objects.create(
            edgeid=self.edgeid,
            graph_id=self.graphid,
            domainnode_id=self.nodegroup_id,
            rangenode_id=self.nodeid,
            ontologyproperty=ONTOLOGY_PROPERTY,
        )

    def _write_node_addition(self):
        self._write_migrations(
            ("0001_graph_add", True, [self._create_node(), self._create_edge()]),
            ("0002_data_add", False, [self._add_node_to_tiles()]),
        )

    def test_a_row_created_then_altered_applies_on_a_fresh_database(self):
        self._write_migrations(
            ("0001_graph_add", True, [self._create_node(), self._create_edge()]),
            (
                "0002_graph_rename",
                True,
                [
                    f'AlterNode(graphid="{self.graphid}", pk="{self.nodeid}", changes={{"name": "Renamed"}})'
                ],
            ),
        )
        with self._installed():
            self._migratepkg(APP_NAME, verbosity=0)
        self.assertEqual(models.Node.objects.get(pk=self.nodeid).name, "Renamed")

    def test_already_applied_with_tile_work_gives_the_exact_commands(self):
        self._write_node_addition()
        tile = self._make_tile()
        self._add_node_rows()
        with self._installed():
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME)
            message = str(refusal.exception)
            self.assertIn(
                "already been applied to this database but not recorded", message
            )
            self.assertIn(
                f"python manage.py migratepkg {APP_NAME} 0001_graph_add --fake\n  python manage.py migratepkg {APP_NAME}",
                message,
            )
            self.assertNotIn("--force", message)

            self._migratepkg(APP_NAME, "0001_graph_add", fake=True, verbosity=0)
            self._migratepkg(APP_NAME, verbosity=0)
        tile.refresh_from_db()
        self.assertIn(self.nodeid, tile.data)
        self.assertEqual(self._recorded(), {"0001_graph_add", "0002_data_add"})

    def test_already_applied_with_nothing_to_do_says_to_record_it_all(self):
        self._write_node_addition()
        self._add_node_rows()
        with self._installed():
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME)
            message = str(refusal.exception)
            self.assertIn("Record them instead of applying them", message)
            self.assertIn(f"python manage.py migratepkg {APP_NAME} --fake", message)

            self._migratepkg(APP_NAME, fake=True, verbosity=0)
        self.assertEqual(self._recorded(), {"0001_graph_add", "0002_data_add"})

    def test_fake_refuses_to_record_what_this_database_does_not_have(self):
        self._write_node_addition()
        with self._installed():
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME, fake=True)
        message = str(refusal.exception)
        self.assertIn("Apply them instead", message)
        self.assertIn(f"python manage.py migratepkg {APP_NAME}", message)
        self.assertNotIn("--fake", message)
        self.assertEqual(self._recorded(), set())

    def test_fake_refuses_data_work_and_says_what_to_run(self):
        self._write_node_addition()
        self._make_tile()
        self._add_node_rows()
        with self._installed():
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME, fake=True)
        message = str(refusal.exception)
        self.assertIn("still have work to do", message)
        self.assertIn(
            "0002_data_add: Add node survey_date to tiles in nodegroup spike_group",
            message,
        )
        self.assertIn(
            f"python manage.py migratepkg {APP_NAME} 0001_graph_add --fake\n  python manage.py migratepkg {APP_NAME}",
            message,
        )

    def test_missing_rows_are_skipped_only_with_force(self):
        missing_nodeid = str(uuid.uuid4())
        self._write_migrations(
            (
                "0001_graph_rename",
                True,
                [
                    f'AlterNode(graphid="{self.graphid}", pk="{missing_nodeid}", changes={{"name": "Renamed"}})'
                ],
            ),
        )
        with self._installed():
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME)
            self.assertIn(f"migratepkg {APP_NAME} --force", str(refusal.exception))

            _stdout, stderr = self._migratepkg(APP_NAME, force=True, verbosity=0)
        self.assertIn("no longer here", stderr)
        self.assertEqual(self._recorded(), {"0001_graph_rename"})

    def test_a_diverged_database_is_refused_without_offering_force(self):
        self._add_node_rows()
        self._write_migrations(
            (
                "0001_graph_mixed",
                True,
                [
                    self._create_node(),
                    f'AlterNode(graphid="{self.graphid}", pk="{uuid.uuid4()}", changes={{"name": "Renamed"}})',
                ],
            ),
        )
        with self._installed():
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME)
        message = str(refusal.exception)
        self.assertIn("matches no point", message)
        self.assertNotIn("--force", message)

    def test_reversal_leaves_the_graph_as_a_designer_publish_would(self):
        previous_publication_id = str(self._graph_row().publication_id)
        publication_id = str(uuid.uuid4())
        self._write_migrations(
            (
                "0001_graph_add",
                True,
                [
                    self._create_node(),
                    self._create_edge(),
                    self._publish(publication_id, previous_publication_id),
                ],
            ),
            (
                "0002_data_add",
                False,
                [
                    self._add_node_to_tiles(),
                    self._move_resources(publication_id, previous_publication_id),
                ],
            ),
        )
        resource = models.ResourceInstance.objects.create(graph=self.graph)
        with self._installed():
            self._migratepkg(APP_NAME, verbosity=0)
            self.assertEqual(str(self._graph_row().publication_id), publication_id)
            resource.refresh_from_db()
            self.assertEqual(str(resource.graph_publication_id), publication_id)

            self._migratepkg(APP_NAME, "zero", verbosity=0)

        graph_row = self._graph_row()
        self.assertEqual(str(graph_row.publication_id), previous_publication_id)
        self.assertFalse(graph_row.has_unpublished_changes)
        self.assertFalse(
            models.GraphXPublishedGraph.objects.filter(pk=publication_id).exists()
        )
        self.assertTrue(
            models.PublishedGraph.objects.filter(
                publication_id=previous_publication_id
            ).exists()
        )
        self.assertIsNone(Graph.objects.get(pk=self.graphid).get_draft_graph())
        self.assertFalse(models.Node.objects.filter(pk=self.nodeid).exists())
        resource.refresh_from_db()
        self.assertEqual(str(resource.graph_publication_id), previous_publication_id)

    def test_reversal_keeps_edits_that_were_never_published(self):
        previous_publication_id = str(self._graph_row().publication_id)
        publication_id = str(uuid.uuid4())
        self._write_migrations(
            (
                "0001_graph_add",
                True,
                [
                    self._create_node(),
                    self._create_edge(),
                    self._publish(publication_id, previous_publication_id),
                ],
            ),
        )
        with self._installed():
            self._migratepkg(APP_NAME, verbosity=0)
            models.GraphModel.objects.filter(pk=self.graphid).update(
                has_unpublished_changes=True
            )
            self._migratepkg(APP_NAME, "zero", verbosity=0)
        self.assertTrue(self._graph_row().has_unpublished_changes)

    def test_reversing_an_in_place_publication_snapshots_the_reverted_rows(self):
        publication_id = str(self._graph_row().publication_id)
        self._write_migrations(
            (
                "0001_graph_add",
                True,
                [
                    self._create_node(),
                    self._create_edge(),
                    self._publish(publication_id, publication_id),
                ],
            ),
        )

        def published_nodeids():
            published_graph = models.PublishedGraph.objects.filter(
                publication_id=publication_id
            ).first()
            return {
                str(node["nodeid"])
                for node in published_graph.serialized_graph["nodes"]
            }

        with self._installed():
            self._migratepkg(APP_NAME, verbosity=0)
            self.assertIn(self.nodeid, published_nodeids())

            self._migratepkg(APP_NAME, "zero", verbosity=0)
        self.assertNotIn(self.nodeid, published_nodeids())
        graph_row = self._graph_row()
        self.assertEqual(str(graph_row.publication_id), publication_id)
        self.assertFalse(graph_row.has_unpublished_changes)

    def test_a_draft_with_unpublished_edits_is_kept_unless_forced(self):
        self._write_migrations(
            ("0001_graph_add", True, [self._create_node(), self._create_edge()]),
        )
        source = Graph.objects.get(pk=self.graphid)
        draft = source.get_draft_graph() or source.create_draft_graph()
        models.GraphModel.objects.filter(pk=draft.graphid).update(
            has_unpublished_changes=True
        )
        with self._installed():
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME)
            self.assertIn(self.graph.slug, str(refusal.exception))
            self.assertIsNotNone(Graph.objects.get(pk=self.graphid).get_draft_graph())

            self._migratepkg(APP_NAME, force=True, verbosity=0)
        self.assertIsNone(Graph.objects.get(pk=self.graphid).get_draft_graph())

    def test_a_run_says_how_to_reindex_what_it_touched(self):
        self._write_migrations(
            ("0001_graph_add", True, [self._create_node(), self._create_edge()]),
        )
        with self._installed():
            stdout, _stderr = self._migratepkg(APP_NAME, plan=True)
            self.assertNotIn("index_resources_by_type", stdout)
            stdout, _stderr = self._migratepkg(APP_NAME)
        self.assertIn(
            f"python manage.py es index_resources_by_type -rt {self.graphid}", stdout
        )

    def test_reversing_a_graph_that_has_resources_is_refused(self):
        graphid = str(uuid.uuid4())
        self._write_migrations(
            (
                "0001_graph_create",
                True,
                [
                    f'CreateGraph(fields={{"graphid": "{graphid}", "name": "Throwaway", "slug": "throwaway_{graphid[:8]}", "isresource": True}})'
                ],
            ),
        )
        with self._installed():
            self._migratepkg(APP_NAME, verbosity=0)
            models.ResourceInstance.objects.create(graph_id=graphid)
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME, "zero", verbosity=0)
        self.assertIn("has resources", str(refusal.exception))
        self.assertTrue(models.GraphModel.objects.filter(pk=graphid).exists())

    def test_reversing_a_nodegroup_that_holds_tiles_needs_force(self):
        nodegroup_id = str(uuid.uuid4())
        self._write_migrations(
            (
                "0001_graph_nodegroup",
                True,
                [
                    f'CreateNodeGroup(graphid="{self.graphid}", fields={{"nodegroupid": "{nodegroup_id}", "cardinality": "n"}})'
                ],
            ),
        )
        with self._installed():
            self._migratepkg(APP_NAME, verbosity=0)
            models.TileModel.objects.create(
                resourceinstance=models.ResourceInstance.objects.create(
                    graph=self.graph
                ),
                nodegroup_id=nodegroup_id,
                data={},
            )
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME, "zero", verbosity=0)
            self.assertIn("1 tiles", str(refusal.exception))
            self.assertIn("--force", str(refusal.exception))

            self._migratepkg(APP_NAME, "zero", force=True, verbosity=0)
        self.assertFalse(models.NodeGroup.objects.filter(pk=nodegroup_id).exists())

    def test_missing_reference_data_names_the_package_to_install(self):
        graphid = str(uuid.uuid4())
        ontology_id = str(uuid.uuid4())
        self._write_migrations(
            (
                "0001_graph_create",
                True,
                [
                    f'CreateGraph(fields={{"graphid": "{graphid}", "name": "Needs Ontology", "slug": "needs_ontology_{graphid[:8]}", "isresource": True, "ontology_id": "{ontology_id}"}})'
                ],
            ),
        )
        with self._installed():
            package_path = Path(apps.get_app_config(APP_NAME).path) / "pkg"
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME)
        message = str(refusal.exception)
        self.assertIn(ontology_id, message)
        self.assertIn(
            f"python manage.py packages -o load_package -s {package_path}", message
        )
        self.assertNotIn(" -y", message)
        self.assertTrue(message.endswith(f"python manage.py migratepkg {APP_NAME}"))

    def test_publish_graph_refuses_a_previous_publication_this_database_never_had(
        self,
    ):
        publication_id = str(uuid.uuid4())
        self._write_migrations(
            (
                "0001_graph_add",
                True,
                [
                    self._create_node(),
                    self._create_edge(),
                    self._publish(publication_id, str(uuid.uuid4())),
                ],
            ),
        )
        with self._installed():
            self._migratepkg(APP_NAME, verbosity=0)
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME, "zero", verbosity=0)
        self.assertIn("never had it", str(refusal.exception))
        self.assertEqual(self._recorded(), {"0001_graph_add"})
        self.assertTrue(models.Node.objects.filter(pk=self.nodeid).exists())

    def test_publish_graph_refuses_while_resources_are_still_on_its_publication(self):
        previous_publication_id = str(self._graph_row().publication_id)
        publication_id = str(uuid.uuid4())
        self._write_migrations(
            (
                "0001_graph_add",
                True,
                [
                    self._create_node(),
                    self._create_edge(),
                    self._publish(publication_id, previous_publication_id),
                ],
            ),
        )
        with self._installed():
            self._migratepkg(APP_NAME, verbosity=0)
            resource = models.ResourceInstance.objects.create(graph=self.graph)
            models.ResourceInstance.objects.filter(pk=resource.pk).update(
                graph_publication_id=publication_id
            )
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME, "zero", verbosity=0)
        self.assertIn("still on publication", str(refusal.exception))
        self.assertEqual(str(self._graph_row().publication_id), publication_id)

    def test_a_fake_run_prints_no_reindex_advice(self):
        self._write_node_addition()
        self._add_node_rows()
        with self._installed():
            stdout, _stderr = self._migratepkg(APP_NAME, fake=True)
        self.assertNotIn("index_resources_by_type", stdout)
        self.assertNotIn("reindex_database", stdout)

    def test_custom_code_is_reindexed_in_full(self):
        (self.migrations_directory / "0001_data_custom.py").write_text(
            textwrap.dedent("""
                from django.db import migrations

                from arches.db.package_migrations.operations import RunPackagePython


                def forwards(schema_editor, state):
                    pass


                class Migration(migrations.Migration):
                    dependencies = []
                    atomic = False
                    operations = [RunPackagePython(forwards)]
                """)
        )
        with self._installed():
            stdout, _stderr = self._migratepkg(APP_NAME)
        self.assertIn("python manage.py es reindex_database", stdout)
        self.assertNotIn("index_resources_by_type", stdout)

    def test_the_command_suggested_for_an_ambiguous_position_runs(self):
        string_nodeid = str(self.string_node.nodeid)
        self._write_migrations(
            (
                "0001_graph_delete",
                True,
                [f'DeleteNode(graphid="{self.graphid}", pk="{string_nodeid}")'],
            ),
            (
                "0002_graph_recreate",
                True,
                [self._create_node(string_nodeid, "spike_string", "string")],
            ),
        )
        with self._installed():
            with self.assertRaises(CommandError) as refusal:
                self._migratepkg(APP_NAME)
            message = str(refusal.exception)
            self.assertIn("fits more than one point", message)
            self.assertIn("If it is before all of them", message)
            self.assertIn(
                f"If it is at {APP_NAME}.0002_graph_recreate:\n  python manage.py migratepkg {APP_NAME} --fake",
                message,
            )
            self.assertIn(f"python manage.py migratepkg {APP_NAME} --force", message)
            self._migratepkg(APP_NAME, fake=True, verbosity=0)
        self.assertEqual(self._recorded(), {"0001_graph_delete", "0002_graph_recreate"})
        self.assertTrue(models.Node.objects.filter(pk=string_nodeid).exists())

    def test_creating_a_row_and_later_deleting_it_is_not_ambiguous(self):
        self._write_migrations(
            ("0001_graph_add", True, [self._create_node(), self._create_edge()]),
            (
                "0002_graph_remove",
                True,
                [
                    f'DeleteEdge(graphid="{self.graphid}", pk="{self.edgeid}")',
                    f'DeleteNode(graphid="{self.graphid}", pk="{self.nodeid}")',
                ],
            ),
        )
        with self._installed():
            self._migratepkg(APP_NAME, verbosity=0)
        self.assertEqual(self._recorded(), {"0001_graph_add", "0002_graph_remove"})
        self.assertFalse(models.Node.objects.filter(pk=self.nodeid).exists())

    def test_unrecording_with_fake_deletes_nothing(self):
        nodegroup_id = str(uuid.uuid4())
        self._write_migrations(
            (
                "0001_graph_nodegroup",
                True,
                [
                    f'CreateNodeGroup(graphid="{self.graphid}", fields={{"nodegroupid": "{nodegroup_id}", "cardinality": "n"}})'
                ],
            ),
        )
        with self._installed():
            self._migratepkg(APP_NAME, verbosity=0)
            models.TileModel.objects.create(
                resourceinstance=models.ResourceInstance.objects.create(
                    graph=self.graph
                ),
                nodegroup_id=nodegroup_id,
                data={},
            )
            self._migratepkg(APP_NAME, "zero", fake=True, verbosity=0)
        self.assertEqual(self._recorded(), set())
        self.assertTrue(models.NodeGroup.objects.filter(pk=nodegroup_id).exists())
