from collections import ChainMap
from copy import deepcopy

from unittest import mock, TestCase

from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.utils.label_based_graph import LabelBasedGraph, LabelBasedNode, NODE_ID_KEY, TILE_ID_KEY, VALUE_KEY


class LabelBasedNodeTests(TestCase):
    @classmethod
    def setUp(cls):
        cls.test_node = LabelBasedNode(
            name="test_node_name",
            node_id="test_node_node_id",
            tile_id="test_node_tile_id",
            value="test_node_value"
        )

        cls.test_node_json_data = {
            NODE_ID_KEY: cls.test_node.node_id,
            TILE_ID_KEY: cls.test_node.tile_id,
            VALUE_KEY: cls.test_node.value,
        }

    def test_as_json_no_child_nodes(self):
        self.assertEqual(
            self.test_node.as_json(),
            {
                self.test_node.name: self.test_node_json_data
            }
        )
        
    def test_as_json_single_child_node(self):
        child_node = LabelBasedNode(
            name="child_node_val",
            node_id="child_node_node_id",
            tile_id="child_node_tile_id",
            value="child_node_value"
        )
        
        self.test_node.child_nodes.append(child_node)
        self.test_node_json_data[child_node.name] = {
            NODE_ID_KEY: child_node.node_id,
            TILE_ID_KEY: child_node.tile_id,
            VALUE_KEY: child_node.value,
        }

        self.assertEqual(
            self.test_node.as_json(),
            {
                self.test_node.name: self.test_node_json_data
            }
        )
        
    def test_as_json_two_child_nodes(self):
        child_node_1 = LabelBasedNode(
            name="child_node_val",
            node_id="child_node_node_id",
            tile_id="child_node_tile_id",
            value="child_node_value"
        )

        child_node_2 = LabelBasedNode(
            name="child_node_val",
            node_id="child_node_node_id",
            tile_id="child_node_tile_id",
            value="child_node_value"
        )

        self.test_node.child_nodes.append(child_node_1)
        self.test_node.child_nodes.append(child_node_2)

        self.test_node_json_data[child_node_1.name] = [
            {
                NODE_ID_KEY: child_node_1.node_id,
                TILE_ID_KEY: child_node_1.tile_id,
                VALUE_KEY: child_node_1.value,
            },
            {
                NODE_ID_KEY: child_node_2.node_id,
                TILE_ID_KEY: child_node_2.tile_id,
                VALUE_KEY: child_node_2.value,
            }
        ]
        
        self.assertEqual(
            self.test_node.as_json(),
            {
                self.test_node.name: self.test_node_json_data
            }
        )
        
    def test_as_json_many_child_nodes(self):
        child_node_1 = LabelBasedNode(
            name="child_node_val",
            node_id="child_node_node_id",
            tile_id="child_node_tile_id",
            value="child_node_value"
        )

        child_node_2 = LabelBasedNode(
            name="child_node_val",
            node_id="child_node_node_id",
            tile_id="child_node_tile_id",
            value="child_node_value"
        )

        child_node_3 = LabelBasedNode(
            name="child_node_val",
            node_id="child_node_node_id",
            tile_id="child_node_tile_id",
            value="child_node_value"
        )

        self.test_node.child_nodes.append(child_node_1)
        self.test_node.child_nodes.append(child_node_2)
        self.test_node.child_nodes.append(child_node_3)

        self.test_node_json_data[child_node_1.name] = [
            {
                NODE_ID_KEY: child_node_1.node_id,
                TILE_ID_KEY: child_node_1.tile_id,
                VALUE_KEY: child_node_1.value,
            },
            {
                NODE_ID_KEY: child_node_2.node_id,
                TILE_ID_KEY: child_node_2.tile_id,
                VALUE_KEY: child_node_2.value,
            },
            {
                NODE_ID_KEY: child_node_3.node_id,
                TILE_ID_KEY: child_node_3.tile_id,
                VALUE_KEY: child_node_3.value,
            }
        ]

        self.assertEqual(
            self.test_node.as_json(),
            {
                self.test_node.name: self.test_node_json_data
            }
        )


class LabelBasedGraphTests(TestCase):
    @classmethod
    def setUp(cls):
        cls.node_1 = LabelBasedNode(
            name="node_1_val",
            node_id="node_1_node_id",
            tile_id="node_1_tile_id",
            value="node_1_value"
        )

        cls.node_2 = LabelBasedNode(
            name="node_2_val",
            node_id="node_2_node_id",
            tile_id="node_2_tile_id",
            value=None
        )

    def test_is_node_empty(self):
        self.assertFalse(LabelBasedGraph.is_node_empty(self.node_1))

    def test_is_node_empty_with_node_with_child_nodes(self):
        child_node = LabelBasedNode(
            name="child_node_val",
            node_id="child_node_node_id",
            tile_id="child_node_tile_id",
            value="child_node_value"
        )

        self.node_2.child_nodes.append(child_node)
        self.assertFalse(LabelBasedGraph.is_node_empty(self.node_2))

    def test_is_node_empty_with_empty_node(self):
        self.assertTrue(LabelBasedGraph.is_node_empty(self.node_2))

    def test_generate_node_tile_reference(self):
        mock_tile = mock.Mock(
            data={
                self.node_1.node_id: 'test_val'
            }
        )

        node_tile_reference = LabelBasedGraph.generate_node_tile_reference(
            resource=mock.Mock(tiles=[mock_tile])
        )

        self.assertEqual(
            mock_tile,
            node_tile_reference.get(self.node_1.node_id)[0]
        )

    @mock.patch.object(LabelBasedGraph, "generate_node_tile_reference", side_effect=None)
    @mock.patch.object(LabelBasedGraph, "_build_graph", side_effect=None)
    def test_from_tile(self, mock__build_graph, mock_generate_node_tile_reference):
        with mock.patch("arches.app.utils.label_based_graph.models.Node", return_value=None):
            LabelBasedGraph.from_tile(tile=mock.Mock(nodegroup_id=1))

            mock_generate_node_tile_reference.assert_called_once()
            mock__build_graph.assert_called_once()

    @mock.patch.object(LabelBasedGraph, "_build_graph", side_effect=None)
    def test_from_tile_with_node_tile_reference(self, mock__build_graph):
        with mock.patch("arches.app.utils.label_based_graph.models.Node", return_value=None):
            LabelBasedGraph.from_tile(tile=mock.Mock(nodegroup_id=1), node_tile_reference=mock.Mock())
            mock__build_graph.assert_called_once()

    # @mock.patch.object(LabelBasedGraph, "generate_node_tile_reference", side_effect=None)
    # def test_from_resource(self, mock_generate_node_tile_reference):
    #     test_resource = mock.Mock(
    #         load_tiles=mock.Mock(
    #             display_name="test_resource_name",
    #             return_value=[
    #                 mock.Mock(wraps=Tile(nodegroup_id=1), data={"mock_node_1": None}),
    #                 mock.Mock(wraps=Tile(nodegroup_id=2), data={"mock_node_2": None}),
    #             ]
    #         ),
    #     )

    #     # always mock the RELATIVE path
    #     with mock.patch("arches.app.utils.label_based_graph.LabelBasedGraph", wraps=LabelBasedGraph) as mock_label_based_graph:
    #         child_name_graphs = [
    #             {"label_graph_1_name": "label_graph_1"},
    #             {"label_graph_2_name": "label_graph_2"},
    #         ]

    #         mock_label_based_graph.from_tile.side_effect = deepcopy(child_name_graphs)

    #         foo = LabelBasedGraph.from_resource(resource=test_resource, hide_empty_nodes=True),
    #         import pdb; pdb.set_trace()

    #         self.assertEqual(
    #             foo,
    #             dict(ChainMap(*child_name_graphs)),  # combines list of dicts into single dict
    #         )


            # self.assertEqual(mock_label_based_graph.from_tile.call_count, 2)

            # for mock_tile in test_resource.tiles:
            #     mock_tile.get_root_tile.assert_called_once()

            # self.assertEqual(mock_label_based_graph.add_node.call_count, 2)


# class LabelBasedGraph_BuildGraphTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.test_LabelBasedGraph = LabelBasedGraph()
#         cls.grouping_node = models.Node(datatype="semantic", name="Test Node Grouping")
#         cls.string_node = models.Node(datatype="string", name="Test Node")
#         cls.test_tile = models.TileModel(data={str(cls.string_node.pk): "value"})

#     def test_handles_node_with_single_value(self):
#         self.assertEqual(
#             self.test_LabelBasedGraph._build_graph(node=self.string_node, tile=self.test_tile, parent_tree={}, tile_reference={}),
#             {self.string_node.name: {NODE_ID_KEY: str(self.string_node.pk), VALUE_KEY: self.test_tile.data[str(self.string_node.pk)]}},
#         )

#     def test_handles_node_with_multiple_values(self):
#         string_node_id = str(self.string_node.pk)
#         parent_tile = models.TileModel(data={string_node_id: "test_val_1"})

#         self.test_tile.parenttile = parent_tile

#         self.assertEqual(
#             self.test_LabelBasedGraph._build_graph(
#                 node=self.string_node, tile=parent_tile, parent_tree={}, tile_reference={string_node_id: [parent_tile, self.test_tile]},
#             ),
#             {
#                 self.string_node.name: [
#                     {NODE_ID_KEY: string_node_id, VALUE_KEY: parent_tile.data[string_node_id]},
#                     {NODE_ID_KEY: string_node_id, VALUE_KEY: self.test_tile.data[string_node_id]},
#                 ],
#             },
#         )

#     def test_handles_empty_semantic_node(self):
#         self.assertEqual(
#             LabelBasedGraph._build_graph(
#                 node=self.grouping_node, tile=self.test_tile, parent_tree={}, tile_reference={}
#             ),
#             {self.grouping_node.name: {NODE_ID_KEY: str(self.grouping_node.pk), VALUE_KEY: None}},
#         )

#     def test_semantic_node_with_child(self):
#         self.grouping_node.get_direct_child_nodes = mock.Mock(return_value=[self.string_node])

#         self.assertEqual(
#             LabelBasedGraph._build_graph(
#                 node=self.grouping_node, tile=self.test_tile, parent_tree={}, tile_reference={},
#             ),
#             {
#                 self.grouping_node.name: {
#                     NODE_ID_KEY: str(self.grouping_node.pk),
#                     VALUE_KEY: None,
#                     self.string_node.name: {
#                         NODE_ID_KEY: str(self.string_node.pk),
#                         VALUE_KEY: self.test_tile.data[str(self.string_node.pk)],
#                     },
#                 },
#             },
#         )

#     def test_handles_node_grouped_in_separate_card(self):
#         separate_card_node = models.Node(datatype="semantic", name="Test Node Separate Card")

#         self.grouping_node.get_direct_child_nodes = mock.Mock(return_value=[separate_card_node])
#         separate_card_node.get_direct_child_nodes = mock.Mock(return_value=[self.string_node])

#         self.assertEqual(
#             LabelBasedGraph._build_graph(
#                 node=self.grouping_node, tile=self.test_tile, parent_tree={}, tile_reference={}
#             ),
#             {
#                 self.grouping_node.name: {
#                     NODE_ID_KEY: str(self.grouping_node.pk),
#                     VALUE_KEY: None,
#                     separate_card_node.name: {
#                         NODE_ID_KEY: str(separate_card_node.pk),
#                         VALUE_KEY: None,
#                         self.string_node.name: {
#                             NODE_ID_KEY: str(self.string_node.pk),
#                             VALUE_KEY: self.test_tile.data[str(self.string_node.pk)],
#                         },
#                     },
#                 },
#             },
#         )
