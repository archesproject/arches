"""makepkgmigrations: generate from committed JSON, then apply what was generated.

Generation reads only the repo (committed graph JSON on one side, replayed
migration state on the other), so these assertions hold regardless of what is in
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
        """Commit the graph in the shape `packages -o export_graphs` writes."""
        serialized = dict(self.graph.get_published_graph().serialized_graph)
        serialized.update(overrides)
        self._write_graph(serialized)
        return serialized

    def _write_graph(self, serialized):
        filename = "{}.json".format(serialized["graphid"])
        directory = self.package / "pkg" / "graphs" / "resource_models"
        (directory / filename).write_text(
            json.dumps({"graph": [serialized]}, indent=4, sort_keys=True)
        )

    def _migration_files(self):
        directory = self.package / "migrations" / "package_migrations"
        if not directory.is_dir():
            return []
        return sorted(p.name for p in directory.glob("[0-9]*.py"))

    def test_no_changes_when_json_matches_replayed_state(self):
        """The graph exists in the database but not in migration history, so the
        diff is against an empty replayed state: everything in the JSON is new."""
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
            # A graph created here has no tiles and no resources, so there is
            # nothing for a data migration to do.
            self.assertEqual(len(files), 1, files)
            self.assertIn("_graph_", files[0])
            self.assertTrue(files[0].startswith("0001_"))

            # The generated file must be importable and runnable, not just written.
            source = (
                self.package / "migrations" / "package_migrations" / files[0]
            ).read_text()
            self.assertIn("from arches.db.package_migrations.operations import", source)
            self.assertIn("CreateGraph(", source)

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

    def _adopt(self):
        """Generate 0001 and fake it, as the release notes instruct: the graph is
        already in the database, so the initial migration is recorded, not run."""
        call_command("makepkgmigrations", APP_NAME, verbosity=0)
        call_command("migratepkg", APP_NAME, fake=True, verbosity=0)

    def test_generated_migration_changes_what_the_application_reads(self):
        """Generating a file that imports is not enough: apply it and check the
        rows, the publication, the resources, the stale draft and the tiles."""
        from arches.app.models import models
        from arches.app.models.graph import Graph

        canonical = self._commit_graph()
        with self._installed():
            self._adopt()

            resource = models.ResourceInstance.objects.create(graph=self.graph)
            models.TileModel.objects.create(
                resourceinstance=resource,
                nodegroup_id=self.nodegroup_id,
                data={str(self.string_node.nodeid): None},
            )
            publication_before = models.GraphModel.objects.get(
                pk=self.graph.graphid
            ).publication_id

            # A real change: a new node, with the edge that joins it to the tree.
            new_nodeid = str(uuid.uuid4())
            new_edgeid = str(uuid.uuid4())
            # Rows are written whole, the way an export writes them: the
            # projection fills absent keys with None, not with model defaults.
            existing_node = [
                node
                for node in canonical["nodes"]
                if str(node["nodeid"]) == str(self.string_node.nodeid)
            ][0]
            canonical["nodes"].append(
                dict(
                    existing_node,
                    nodeid=new_nodeid,
                    name="Survey Date",
                    datatype="date",
                    alias="survey_date_generated",
                )
            )
            canonical["edges"].append(
                dict(
                    canonical["edges"][0],
                    edgeid=new_edgeid,
                    domainnode_id=str(self.nodegroup_id),
                    rangenode_id=new_nodeid,
                )
            )
            self._write_graph(canonical)

            call_command("makepkgmigrations", APP_NAME, verbosity=0)
            call_command("migratepkg", APP_NAME, verbosity=0)

            # 1. the structural change landed
            self.assertTrue(models.Node.objects.filter(pk=new_nodeid).exists())

            # 2. the graph was republished, so what the application reads changed
            graph = models.GraphModel.objects.get(pk=self.graph.graphid)
            self.assertIsNotNone(graph.publication_id)
            self.assertNotEqual(graph.publication_id, publication_before)
            published = Graph.objects.get(pk=graph.graphid).get_published_graph()
            self.assertIsNotNone(published)
            self.assertIn(
                new_nodeid,
                [node["nodeid"] for node in published.serialized_graph["nodes"]],
            )

            # 3. resources moved onto the new publication, so they stay editable
            resource.refresh_from_db()
            self.assertEqual(resource.graph_publication_id, graph.publication_id)

            # 4. no stale draft survives, so the next Designer publish cannot
            #    rebuild the live graph from a copy that predates this migration
            self.assertIsNone(Graph.objects.get(pk=graph.graphid).get_draft_graph())

            # 5. existing tiles carry the new node key
            tile = models.TileModel.objects.filter(
                nodegroup_id=self.nodegroup_id
            ).first()
            self.assertIn(new_nodeid, tile.data)

    def test_graph_and_data_operations_land_in_separate_migrations(self):
        """The file boundary is what makes the ordering true: the graph is
        published first, and resources stay on the old publication until the data
        migration has brought their tiles in line and moved them."""
        serialized = self._commit_graph()
        with self._installed():
            call_command("makepkgmigrations", APP_NAME, verbosity=0)
            adopted = set(self._migration_files())

            # A change to an existing graph is what implies tile work.
            new_nodeid = str(uuid.uuid4())
            existing = [
                node
                for node in serialized["nodes"]
                if str(node["nodeid"]) == str(self.string_node.nodeid)
            ][0]
            serialized["nodes"].append(
                dict(existing, nodeid=new_nodeid, alias="separation", name="Separation")
            )
            serialized["edges"].append(
                dict(
                    serialized["edges"][0],
                    edgeid=str(uuid.uuid4()),
                    domainnode_id=str(self.nodegroup_id),
                    rangenode_id=new_nodeid,
                )
            )
            self._write_graph(serialized)
            call_command("makepkgmigrations", APP_NAME, verbosity=0)

            scopes = []
            for name in sorted(set(self._migration_files()) - adopted):
                module = __import__(
                    "%s.migrations.package_migrations.%s" % (APP_NAME, name[:-3]),
                    fromlist=["Migration"],
                )
                operations = module.Migration.operations
                scopes.append({operation.scope for operation in operations})
                self.assertEqual(len(scopes[-1]), 1, name)
            self.assertEqual(scopes, [{"graph"}, {"data"}])

    def test_moving_a_node_between_nodegroups_warns_that_data_is_stranded(self):
        serialized = self._commit_graph()
        with self._installed():
            call_command("makepkgmigrations", APP_NAME, verbosity=0)

            for node in serialized["nodes"]:
                if str(node["nodeid"]) == str(self.string_node.nodeid):
                    node["nodegroup_id"] = str(uuid.uuid4())
            self._write_graph(serialized)

            err = StringIO()
            call_command("makepkgmigrations", APP_NAME, verbosity=0, stderr=err)
            self.assertIn("stranded", err.getvalue())
            self.assertIn(str(self.string_node.nodeid), err.getvalue())

    def test_changing_a_datatype_warns_that_stored_values_are_not_converted(self):
        serialized = self._commit_graph()
        with self._installed():
            call_command("makepkgmigrations", APP_NAME, verbosity=0)

            for node in serialized["nodes"]:
                if str(node["nodeid"]) == str(self.string_node.nodeid):
                    node["datatype"] = "concept"
            self._write_graph(serialized)

            err = StringIO()
            call_command("makepkgmigrations", APP_NAME, verbosity=0, stderr=err)
            self.assertIn("changing datatype to 'concept'", err.getvalue())
            self.assertIn("RunPackagePython", err.getvalue())

    def test_faking_a_data_migration_is_refused(self):
        """Faking structural work is safe when the rows are already there. Faking
        tile work skips the only thing that would ever do it, and the ledger then
        says it happened."""
        serialized = self._commit_graph()
        with self._installed():
            self._adopt()

            new_nodeid = str(uuid.uuid4())
            existing = [
                node
                for node in serialized["nodes"]
                if str(node["nodeid"]) == str(self.string_node.nodeid)
            ][0]
            serialized["nodes"].append(
                dict(existing, nodeid=new_nodeid, alias="faked", name="Faked")
            )
            serialized["edges"].append(
                dict(
                    serialized["edges"][0],
                    edgeid=str(uuid.uuid4()),
                    domainnode_id=str(self.nodegroup_id),
                    rangenode_id=new_nodeid,
                )
            )
            self._write_graph(serialized)
            call_command("makepkgmigrations", APP_NAME, verbosity=0)

            with self.assertRaises(CommandError) as refusal:
                call_command("migratepkg", APP_NAME, fake=True, verbosity=0)
            self.assertIn("change business data", str(refusal.exception))
