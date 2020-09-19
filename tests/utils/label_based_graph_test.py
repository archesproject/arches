from collections import ChainMap
from copy import deepcopy

from unittest import mock, TestCase

from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.utils.label_based_graph import LabelBasedGraph, LabelBasedNode, NODE_ID_KEY, TILE_ID_KEY, VALUE_KEY
class LabelBasedGraphTests(TestCase):
    # fine to skip setup/teardown as long as read-only
    node_1 = LabelBasedNode(
        name='name',
        value={
            VALUE_KEY: 'value',
        },
    )

    node_2 = LabelBasedNode(
        name='name',
        value={
            VALUE_KEY: None,
        },
    )

    def test_add_node_no_previous_values(self):
        graph = {}

        LabelBasedGraph.add_node(
            graph=graph,
            node=self.node_1,
        ),

        self.assertEqual(
            graph,
            {self.node_1.name: self.node_1.value},
        )

    def test_add_node_previous_value_list(self):
        graph = {
            self.node_1.name: [self.node_1.value],
        }

        LabelBasedGraph.add_node(
            graph=graph,
            node=self.node_2,
        ),

        self.assertEqual(
            graph,
            {
                self.node_1.name: [self.node_1.value, self.node_2.value]
            },
        )

    def test_add_node_previous_value_other_types(self):
        graph = {
            self.node_1.name: self.node_1.value,
        }

        LabelBasedGraph.add_node(
            graph=graph,
            node=self.node_2,
        ),

        self.assertEqual(
            graph,
            {
                self.node_1.name: [self.node_1.value, self.node_2.value]
            },
        )

    def test_is_node_empty(self):
        self.assertFalse(
            LabelBasedGraph.is_node_empty(self.node_1)  
        )

    def test_is_node_empty_with_empty_node(self):
        self.assertTrue(
            LabelBasedGraph.is_node_empty(self.node_2)  # empty node
        )

    @mock.patch.object(LabelBasedGraph, '_generate_node_tile_reference', side_effect=None)
    @mock.patch.object(LabelBasedGraph, '_build_graph', side_effect=None)
    def test_from_tile(self, mock__build_graph, mock__generate_node_tile_reference):
        with mock.patch('arches.app.utils.label_based_graph.models.Node', return_value = None):
                LabelBasedGraph.from_tile(
                    tile=mock.Mock(nodegroup_id=1),
                )

                mock__generate_node_tile_reference.assert_called_once()
                mock__build_graph.assert_called_once()

    @mock.patch.object(LabelBasedGraph, '_build_graph', side_effect=None)
    def test_from_tile_with_node_tile_reference(self, mock__build_graph):
        with mock.patch('arches.app.utils.label_based_graph.models.Node', return_value=None):
                LabelBasedGraph.from_tile(
                    tile=mock.Mock(nodegroup_id=1),
                    node_tile_reference=mock.Mock(),
                )

                mock__build_graph.assert_called_once()

    @mock.patch.object(LabelBasedGraph, '_generate_node_tile_reference', side_effect=None)
    def test_from_resource(self, mock__generate_node_tile_reference):
        test_resource = mock.Mock(
            load_tiles=mock.Mock(),
            tiles=[
                mock.Mock(
                    wraps=Tile(nodegroup_id=1),
                    data={
                        'mock_node_1': None,
                    },
                ),
                mock.Mock(
                    wraps=Tile(nodegroup_id=2),
                    data={
                        'mock_node_2': None,
                    },
                ),
                mock.Mock(
                    wraps=Tile(nodegroup_id=2),  # tests that idential root tiles only have graph built once
                    data={
                        'mock_node_3': None,
                    },
                ),
            ],
        )

        # always mock the RELATIVE path
        with mock.patch('arches.app.utils.label_based_graph.LabelBasedGraph', wraps=LabelBasedGraph) as mock_label_based_graph:
            child_name_graphs = [
                {'label_graph_1_name': 'label_graph_1'}, 
                {'label_graph_2_name': 'label_graph_2'},
            ]

            mock_label_based_graph.from_tile.side_effect = deepcopy(child_name_graphs)

            self.assertEqual(
                LabelBasedGraph.from_resource(test_resource),
                dict(ChainMap(*child_name_graphs)),  # combines list of dicts into single dict
            )

            self.assertEqual(mock_label_based_graph.from_tile.call_count, 2)

            for mock_tile in test_resource.tiles:
                mock_tile.get_root_tile.assert_called_once()

            self.assertEqual(mock_label_based_graph.add_node.call_count, 2)


class LabelBasedGraph_BuildGraphTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_LabelBasedGraph = LabelBasedGraph()

        cls.grouping_node = models.Node(
            datatype='semantic',
            name="Test Node Grouping",
        )

        cls.string_node = models.Node(
            datatype='string',
            name="Test Node",
        )

        cls.test_tile = models.TileModel(
            data={
                str(cls.string_node.pk): 'value',
            },
        )

    def test_handles_node_with_single_value(self):
        self.assertEqual(
            self.test_LabelBasedGraph._build_graph(
                node=self.string_node,
                tile=self.test_tile,
                parent_tree={},
                tile_reference={},
            ),
            {
                self.string_node.name: {
                    NODE_ID_KEY: str(self.string_node.pk),
                    VALUE_KEY: self.test_tile.data[str(self.string_node.pk)]
                }
            }
        )

    def test_handles_node_with_multiple_values(self):
        string_node_id = str(self.string_node.pk)

        parent_tile = models.TileModel(
            data={
                string_node_id: 'test_val_1'
            }
        )

        self.test_tile.parenttile = parent_tile

        self.assertEqual(
            self.test_LabelBasedGraph._build_graph(
                node=self.string_node,
                tile=parent_tile,
                parent_tree={},
                tile_reference={
                    string_node_id: [parent_tile, self.test_tile],
                },
            ),
            {
                self.string_node.name: [
                    {
                        NODE_ID_KEY: string_node_id,
                        VALUE_KEY: parent_tile.data[string_node_id],
                    }, {
                        NODE_ID_KEY: string_node_id,
                        VALUE_KEY: self.test_tile.data[string_node_id],
                    }
                ],
            }
        )

    
    def test_handles_empty_semantic_node(self):
        self.assertEqual(
            LabelBasedGraph._build_graph(
                self=LabelBasedGraph,
                node=self.grouping_node,
                tile=self.test_tile,
                parent_tree={},
                tile_reference={},
            ),
            {
                self.grouping_node.name: {
                    NODE_ID_KEY: str(self.grouping_node.pk), 
                    VALUE_KEY: None, 
                },
            },
        )

    def test_semantic_node_with_child(self):
        self.grouping_node.get_direct_child_nodes = mock.Mock(
            return_value=[self.string_node]
        )

        self.assertEqual(
            LabelBasedGraph._build_graph(
                self=LabelBasedGraph,
                node=self.grouping_node,
                tile=self.test_tile,
                parent_tree={},
                tile_reference={},
            ),
            {
                self.grouping_node.name: {
                    NODE_ID_KEY: str(self.grouping_node.pk), 
                    VALUE_KEY: None, 
                    self.string_node.name: {
                        NODE_ID_KEY: str(self.string_node.pk), 
                        VALUE_KEY: self.test_tile.data[str(self.string_node.pk)]
                    },
                },
            },
        )

    def test_handles_node_grouped_in_separate_card(self):
        separate_card_node = models.Node(
            datatype='semantic',
            name='Test Node Separate Card'
        )

        self.grouping_node.get_direct_child_nodes = mock.Mock(
            return_value=[separate_card_node],
        )

        separate_card_node.get_direct_child_nodes = mock.Mock(
            return_value=[self.string_node],
        )

        self.assertEqual(
            LabelBasedGraph._build_graph(
                self=LabelBasedGraph,
                node=self.grouping_node,
                tile=self.test_tile,
                parent_tree={},
                tile_reference={},
            ),
            {
                self.grouping_node.name: {
                    NODE_ID_KEY: str(self.grouping_node.pk), 
                    VALUE_KEY: None, 
                    separate_card_node.name: {
                        NODE_ID_KEY: str(separate_card_node.pk),
                        VALUE_KEY: None,
                        self.string_node.name: {
                            NODE_ID_KEY: str(self.string_node.pk), 
                            VALUE_KEY: self.test_tile.data[str(self.string_node.pk)]
                        },
                    }
                },
            },
        )
