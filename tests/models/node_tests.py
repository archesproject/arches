from arches.app.models.graph import Graph
from arches.app.models.models import Node
from tests.base_test import ArchesTestCase


class NodeTests(ArchesTestCase):
    def test_missing_alias_supplied(self):
        new_graph = Graph.new(name="Missing alias test")
        new_node = Node(graph_id=new_graph.pk)
        new_node.clean()
        self.assertIsNotNone(new_node.alias)
