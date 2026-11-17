import uuid

from arches.app.models.graph import Graph
from arches.app.models.models import Node
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.models.node_tests --settings="tests.test_settings"


class NodeTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.graph = Graph.objects.create_graph(name="Node Tests Graph")

    def test_missing_alias_supplied(self):
        new_node = Node(graph_id=self.graph.pk)
        new_node.clean()
        self.assertIsNotNone(new_node.alias)

    def test_empty_custom_alias_regenerated(self):
        """One dubiously empty alias per graph is currently allowed at the
        database level. Ensure it is regenerated via the application."""
        new_node = Node(
            graph_id=self.graph.pk, name="Test node", alias="", hascustomalias=True
        )
        new_node.clean()
        self.assertEqual(new_node.alias, "test_node")
        self.assertIs(new_node.hascustomalias, False)

    def test_slugify_node_aliases(self):
        aliases = ["time-span", "time_span", "-edge-", "valid_alias", ""]
        graph = Graph()
        graph.nodes = {uuid.uuid4(): Node(alias=alias) for alias in aliases}

        graph.slugify_node_aliases()

        self.assertEqual(
            [node.alias for node in graph.nodes.values()],
            ["time_span_n1", "time_span", "edge", "valid_alias", ""],
        )
