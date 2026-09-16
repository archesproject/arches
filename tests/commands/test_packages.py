# these tests can be run from the command line via
# python manage.py test tests.commands.test_packages --settings="tests.test_settings"

import os
import tempfile

from django.test.utils import captured_stdout

from arches.app.models.graph import Graph
from arches.app.models.models import Node
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.data_management.resource_graphs.exporter import (
    get_graphs_for_export,
)
from arches.management.commands.packages import Command
from tests.base_test import ArchesTransactionTestCase


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
