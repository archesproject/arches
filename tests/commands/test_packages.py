# these tests can be run from the command line via
# python manage.py test tests.commands.test_packages --settings="tests.test_settings"

import os
import tempfile
from unittest.mock import patch

from django.test.utils import captured_stdout

from arches.app.models.graph import Graph
from arches.app.models.models import Node, PublishedGraph
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.data_management.resource_graphs.exporter import (
    get_graphs_for_export,
)
from arches.management.commands.packages import Command
from tests.base_test import ArchesTestCase, ArchesTransactionTestCase


class LoadPackageGraphsTests(ArchesTestCase):
    def load_package_graph_dirs(self, **kwargs):
        with tempfile.TemporaryDirectory() as package_dir:
            branches = os.path.join(package_dir, "graphs", "branches")
            resource_models = os.path.join(package_dir, "graphs", "resource_models")
            os.makedirs(branches)
            os.makedirs(resource_models)

            with (
                patch(
                    "arches.management.commands.packages.task_management.check_if_celery_available",
                    return_value=False,
                ),
                patch.object(Command, "load_concepts"),
                patch.object(Command, "update_resource_geojson_geometries"),
                patch.object(Command, "import_graphs") as import_graphs,
                captured_stdout(),
            ):
                Command().load_package(
                    package_dir, yes=True, defer_indexing=False, **kwargs
                )

            imported = [call.args[0] for call in import_graphs.call_args_list]
            return imported, branches, resource_models

    def test_load_package_loads_branches_then_resource_models(self):
        imported, branches, resource_models = self.load_package_graph_dirs()
        self.assertEqual(imported, [branches, resource_models])

    def test_load_package_skip_branches(self):
        imported, _, resource_models = self.load_package_graph_dirs(skip_branches=True)
        self.assertEqual(imported, [resource_models])


class ImportGraphsTests(ArchesTransactionTestCase):
    serialized_rollback = True

    def test_import_graph_referencing_publication_of_later_graph(self):
        source = Graph.objects.create_graph(name="Source Branch")
        dependent = Graph.objects.create_graph(name="Dependent Branch")

        source_id, dependent_id = source.pk, dependent.pk
        source_publication_id = source.publication_id

        source_json = get_graphs_for_export(graphids=[str(source_id)])["graph"][0]
        dependent_json = get_graphs_for_export(graphids=[str(dependent_id)])["graph"][0]
        for node in dependent_json["nodes"]:
            node["sourcebranchpublication_id"] = str(source_publication_id)

        dependent.delete()
        source.delete()

        with tempfile.TemporaryDirectory() as directory:
            # "aa" sorts before "zz", so the dependent graph is imported before
            # the graph whose publication its nodes reference.
            for filename, graph_json in (
                ("aa_dependent.json", dependent_json),
                ("zz_source.json", source_json),
            ):
                with open(os.path.join(directory, filename), "w") as f:
                    f.write(JSONSerializer().serialize({"graph": [graph_json]}))

            with captured_stdout():
                Command().import_graphs(directory)

        self.assertTrue(Graph.objects.filter(pk=source_id).exists())
        self.assertTrue(Graph.objects.filter(pk=dependent_id).exists())
        self.assertEqual(
            Node.objects.filter(
                graph_id=dependent_id,
                sourcebranchpublication_id=source_publication_id,
            ).count(),
            len(dependent_json["nodes"]),
        )

    def test_import_graph_referencing_missing_publication(self):
        source = Graph.objects.create_graph(name="Source Branch")
        dependent = Graph.objects.create_graph(name="Dependent Branch")

        dependent_id = dependent.pk
        source_publication_id = source.publication_id

        dependent_json = get_graphs_for_export(graphids=[str(dependent_id)])["graph"][0]
        for node in dependent_json["nodes"]:
            node["sourcebranchpublication_id"] = str(source_publication_id)

        dependent.delete()
        source.delete()

        with tempfile.TemporaryDirectory() as directory:
            # The source branch is never imported, as with --skip_branches.
            with open(os.path.join(directory, "dependent.json"), "w") as f:
                f.write(JSONSerializer().serialize({"graph": [dependent_json]}))

            with captured_stdout():
                Command().import_graphs(directory)

        self.assertTrue(Graph.objects.filter(pk=dependent_id).exists())
        self.assertFalse(
            Node.objects.filter(
                graph_id=dependent_id, sourcebranchpublication__isnull=False
            ).exists()
        )
        for published_graph in PublishedGraph.objects.filter(
            publication__graph_id=dependent_id
        ):
            for node in published_graph.serialized_graph["nodes"]:
                self.assertIsNone(node["sourcebranchpublication_id"])
