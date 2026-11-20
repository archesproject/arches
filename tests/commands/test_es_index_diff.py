# these tests can be run from the command line via
# python manage.py test tests.commands.test_es_index_diff --settings="tests.test_settings"

import csv
import tempfile
import uuid
from io import StringIO
from pathlib import Path
from unittest import TestCase, mock

from elasticsearch import ApiError, ConnectionTimeout
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.management.commands.es_index_diff import Command
from tests.base_test import ArchesTestCase


def _ids(path):
    with open(path, newline="") as f:
        return {row[0] for row in list(csv.reader(f))[1:]}


class EsIndexDiffCommandTest(ArchesTestCase):
    """Tests for `python manage.py es_index_diff`."""

    def clear_index(self):
        self.se.delete(index=RESOURCES_INDEX, query={"query": {"match_all": {}}})
        self.se.refresh(index=RESOURCES_INDEX)

    def setUp(self):
        self.se = SearchEngineFactory().create()

    def tearDown(self):
        self.clear_index()

    def build_fixtures(self):
        self.clear_index()
        graph = Graph.objects.create_graph(name="ES Diff Graph", is_resource=True)
        self.resources = [Resource(graph=graph) for _ in range(3)]
        for resource in self.resources:
            resource.save(index=False)
            resource.index()
        self.missing_id = str(self.resources[0].pk)
        self.se.delete(index=RESOURCES_INDEX, id=self.missing_id)
        self.orphan_id = str(uuid.uuid4())
        self.se.index_data(
            index=RESOURCES_INDEX,
            body={"resourceinstanceid": self.orphan_id, "graph_id": str(graph.pk)},
            id=self.orphan_id,
        )
        self.se.refresh(index=RESOURCES_INDEX)

    def run_command(self, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            out = StringIO()
            call_command("es_index_diff", output_dir=tmp, stdout=out, **kwargs)
            tmp = Path(tmp)
            return (
                _ids(tmp / "missing_from_es.csv"),
                _ids(tmp / "orphaned_in_es.csv"),
                (tmp / "summary.txt").read_text(),
            )

    def test_reports_missing_and_orphaned(self):
        self.build_fixtures()
        missing, orphaned, summary = self.run_command()
        self.assertEqual(missing, {self.missing_id})
        self.assertEqual(orphaned, {self.orphan_id})
        self.assertIn("Missing by graphid:", summary)

    def test_partitions_and_slices_give_same_results(self):
        self.build_fixtures()
        baseline = self.run_command()[:2]
        self.assertEqual(self.run_command(partitions=1)[:2], baseline)
        self.assertEqual(self.run_command(partitions=256, slices=1)[:2], baseline)

    @override_settings(ELASTICSEARCH_ENABLED=False)
    def test_requires_elasticsearch(self):
        with self.assertRaises(CommandError):
            call_command("es_index_diff", stdout=StringIO())

    def test_rejects_invalid_batch_size(self):
        for batch_size in (0, 20000):
            with self.assertRaises(CommandError):
                call_command("es_index_diff", batch_size=batch_size, stdout=StringIO())


class EsIndexDiffTuningTest(TestCase):
    """Auto-tuning and retry logic; mocks Elasticsearch."""

    def make_command(self, shards=4, stats=None):
        cmd = Command(stdout=StringIO(), stderr=StringIO())
        cmd.index = "test_resources"
        cmd.batch_size = 10000
        cmd.es = mock.MagicMock()
        cmd.es.search.return_value = {"_shards": {"total": shards}}
        if stats is None:
            cmd.es.cluster.stats.side_effect = ApiError(
                "forbidden", mock.Mock(status=403), {}
            )
        else:
            cmd.es.cluster.stats.return_value = stats
        return cmd

    def test_auto_slices_without_cpu_stats(self):
        self.assertEqual(self.make_command(shards=4).auto_slices(), 2)
        self.assertEqual(self.make_command(shards=1).auto_slices(), 1)

    def test_auto_slices_uses_cpus(self):
        stats = {"nodes": {"os": {"allocated_processors": 3}}}
        self.assertEqual(self.make_command(4, stats).auto_slices(), 3)
        self.assertEqual(self.make_command(2, stats).auto_slices(), 2)

    @mock.patch("arches.management.commands.es_index_diff.time.sleep")
    def test_timeout_retries_with_half_batch_size(self, _sleep):
        cmd = self.make_command()
        cmd.fetch_es = mock.Mock(side_effect=[ConnectionTimeout("slow"), ({}, 0)])
        self.assertEqual(cmd.fetch_es_with_retry("a"), ({}, 0))
        self.assertEqual(cmd.batch_size, 5000)
        self.assertEqual(cmd.fetch_es.call_count, 2)
