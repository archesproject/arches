from unittest import mock, TestCase

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.utils.label_based_graph import LabelBasedGraph

class add_node(TestCase):
    def test_no_previous_values(self):
        graph = {}

        LabelBasedGraph._add_node(
            graph=graph,
            node_name='test_name',
            node_val='test_val',
        ),

        self.assertEqual(
            graph,
            {'test_name': 'test_val'},
        )

    def test_previous_value_list(self):
        graph = {
            'test_name': ['test_val']
        }

        LabelBasedGraph._add_node(
            graph=graph,
            node_name='test_name',
            node_val='test_val_2',
        ),

        self.assertEqual(
            graph,
            {'test_name': ['test_val', 'test_val_2']},
        )

    def test_previous_value_other_types(self):
        graph = {
            'test_name': 'test_val',
        }

        LabelBasedGraph._add_node(
            graph=graph,
            node_name='test_name',
            node_val='test_val_2',
        ),

        self.assertEqual(
            graph,
            {'test_name': ['test_val', 'test_val_2']},
        )

class from_tile(TestCase):
    def test_smoke(self):
        with mock.patch('arches.app.utils.label_based_graph.models.Node', return_value=None): # always mock the RELATIVE path
            with mock.patch.object(LabelBasedGraph, '_build_graph', return_value=None) as mock_graph:
                LabelBasedGraph.from_tile(
                    tile=mock.Mock(nodegroup_id=1),
                    node_tile_reference='node_tile_reference',
                )

                mock_graph.assert_called_once()

@mock.patch('arches.app.utils.label_based_graph.models.Node', wraps=models.Node)  # always mock the RELATIVE path
class build_graph(TestCase):
    def test_handles_single_node(self, mock_Node):
        mock_Node.get_direct_child_nodes.return_value = []
        print('foo')

    def test_handles_grouped_node(self, mock_Node):
        print('foo')

    def test_handles_empty_semantic_node(self, mock_Node):
        print('foo')

    def test_handles_node_grouped_in_separate_card(self, mock_Node):
        print('foo')

    def test_handles_empty_semantic_node_grouped_in_separate_card(self, mock_Node):
        print('foo')

    def test_handles_node_with_multiple_values(self, mock_Node):
        print('foo')

    def test_handles_node_with_multiple_values_grouped_in_separate_card(self, mock_Node):
        print('foo')

    def test_handles_node_with_multiple_associated_tiles(self, mock_Node):
        print('foo')
