from unittest import mock, TestCase

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
        with mock.patch.object(LabelBasedGraph, '_build_graph', return_value=None) as mock_graph:
            with mock.patch('arches.app.utils.label_based_graph.models.Node', return_value=None):

                LabelBasedGraph.from_tile(
                    tile=mock.Mock(nodegroup_id=1),
                    node_tile_reference='node_tile_reference',
                )

                mock_graph.assert_called_once()

class build_graph(TestCase):
    
