from collections import ChainMap
from copy import deepcopy

from unittest import mock, TestCase

from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.models.resource import Resource
from arches.app.utils.label_based_graph import (
    LabelBasedGraph,
    LabelBasedNode,
    NODE_ID_KEY,
    TILE_ID_KEY,
    VALUE_KEY,
    NON_DATA_COLLECTING_NODE,
)


class LabelBasedNodeTests(TestCase):
    @classmethod
    def setUp(cls):
        cls.test_node = LabelBasedNode(
            name="test_node_name", node_id="test_node_node_id", tile_id="test_node_tile_id", value="test_node_value"
        )

        cls.test_node_json_data = {
            NODE_ID_KEY: cls.test_node.node_id,
            TILE_ID_KEY: cls.test_node.tile_id,
            VALUE_KEY: cls.test_node.value,
        }

        cls.empty_node = LabelBasedNode(name="empty_node_name", node_id="empty_node_node_id", tile_id="empty_node_tile_id", value=None)

        cls.child_node_1 = LabelBasedNode(
            name="child_node_val", node_id="child_node_node_id", tile_id="child_node_tile_id", value="child_node_value"
        )

        cls.child_node_2 = LabelBasedNode(
            name="child_node_val", node_id="child_node_node_id", tile_id="child_node_tile_id", value="child_node_value"
        )

        cls.child_node_3 = LabelBasedNode(
            name="child_node_val", node_id="child_node_node_id", tile_id="child_node_tile_id", value="child_node_value"
        )

    def test_is_empty_with_node_with_child_nodes(self):
        self.empty_node.child_nodes.append(self.test_node)
        self.assertFalse(self.empty_node.is_empty())

    def test_is_node_empty_with_empty_node(self):
        self.assertTrue(self.empty_node.is_empty())

    def test_as_json(self):
        self.assertEqual(self.test_node.as_json(), {self.test_node.name: self.test_node_json_data})

    def test_as_json_compact(self):
        self.assertEqual(self.test_node.as_json(compact=True), {self.test_node.name: self.test_node.value})

    def test_as_json_compact_data_collecting_node_with_child(self):
        self.test_node.child_nodes.append(self.child_node_1)

        self.assertEqual(
            self.test_node.as_json(compact=True),
            {self.test_node.name: {self.child_node_1.name: self.child_node_1.value, VALUE_KEY: self.test_node.value}},
        )

    def test_as_json_single_child_node(self):
        self.test_node.child_nodes.append(self.child_node_1)

        self.test_node_json_data[self.child_node_1.name] = {
            NODE_ID_KEY: self.child_node_1.node_id,
            TILE_ID_KEY: self.child_node_1.tile_id,
            VALUE_KEY: self.child_node_1.value,
        }

        self.assertEqual(self.test_node.as_json(), {self.test_node.name: self.test_node_json_data})

    def test_as_json_two_child_nodes(self):
        self.test_node.child_nodes.append(self.child_node_1)
        self.test_node.child_nodes.append(self.child_node_2)

        self.test_node_json_data[self.child_node_1.name] = [
            {NODE_ID_KEY: self.child_node_1.node_id, TILE_ID_KEY: self.child_node_1.tile_id, VALUE_KEY: self.child_node_1.value},
            {NODE_ID_KEY: self.child_node_2.node_id, TILE_ID_KEY: self.child_node_2.tile_id, VALUE_KEY: self.child_node_2.value},
        ]

        self.assertEqual(self.test_node.as_json(), {self.test_node.name: self.test_node_json_data})

    def test_as_json_many_child_nodes(self):
        self.test_node.child_nodes.append(self.child_node_1)
        self.test_node.child_nodes.append(self.child_node_2)
        self.test_node.child_nodes.append(self.child_node_3)

        self.test_node_json_data[self.child_node_1.name] = [
            {NODE_ID_KEY: self.child_node_1.node_id, TILE_ID_KEY: self.child_node_1.tile_id, VALUE_KEY: self.child_node_1.value},
            {NODE_ID_KEY: self.child_node_2.node_id, TILE_ID_KEY: self.child_node_2.tile_id, VALUE_KEY: self.child_node_2.value},
            {NODE_ID_KEY: self.child_node_3.node_id, TILE_ID_KEY: self.child_node_3.tile_id, VALUE_KEY: self.child_node_3.value},
        ]

        self.assertEqual(self.test_node.as_json(), {self.test_node.name: self.test_node_json_data})


class LabelBasedGraphTests(TestCase):
    @classmethod
    def setUp(cls):
        cls.node_1 = LabelBasedNode(name="node_1_val", node_id="node_1_node_id", tile_id="node_1_tile_id", value="node_1_value")
        cls.node_2 = LabelBasedNode(name="node_2_val", node_id="node_2_node_id", tile_id="node_2_tile_id", value=None)

    def test_generate_node_ids_to_tiles_reference(self):
        mock_tile = mock.Mock(data={self.node_1.node_id: "test_val"})
        node_ids_to_tiles_reference = LabelBasedGraph.generate_node_ids_to_tiles_reference(resource=mock.Mock(tiles=[mock_tile]))

        self.assertEqual(mock_tile, node_ids_to_tiles_reference.get(self.node_1.node_id)[0])

    @mock.patch.object(LabelBasedGraph, "_build_graph", side_effect=None)
    def test_from_tile(self, mock__build_graph):
        with mock.patch("arches.app.utils.label_based_graph.models.Node", return_value=None):
            LabelBasedGraph.from_tile(tile=mock.Mock(nodegroup_id=1), node_ids_to_tiles_reference=mock.Mock())
            mock__build_graph.assert_called_once()


@mock.patch("arches.app.utils.label_based_graph.models.Node")
class LabelBasedGraph_FromResourceTests(TestCase):
    @classmethod
    def setUp(cls):
        cls.grouping_node = models.Node(datatype="semantic", name="Test Node Grouping")
        cls.string_node = models.Node(datatype="string", name="Test Node")

        cls.grouping_tile = models.TileModel(data={}, nodegroup_id=str(cls.grouping_node.pk))
        cls.string_tile = models.TileModel(data={str(cls.string_node.pk): "value_1"}, nodegroup_id=str(cls.string_node.pk))

        # le'ts mock Resource since it's minimally used
        # and complex to get `displayname`
        cls.test_resource = mock.Mock(displayname="Test Resource", tiles=[])

    def test_smoke(self, mock_Node):
        label_based_graph = LabelBasedGraph.from_resource(resource=self.test_resource, compact=False, hide_empty_nodes=False)

        self.assertEqual(label_based_graph, {})

    def test_handles_node_with_single_value(self, mock_Node):
        mock_Node.objects.get.return_value = self.string_node

        self.test_resource.tiles.append(self.string_tile)

        label_based_graph = LabelBasedGraph.from_resource(resource=self.test_resource, compact=False, hide_empty_nodes=False)

        self.assertEqual(
            label_based_graph,
            {
                self.string_node.name: {
                    NODE_ID_KEY: str(self.string_node.pk),
                    TILE_ID_KEY: str(self.string_tile.pk),
                    VALUE_KEY: self.string_tile.data[str(self.string_node.pk)],
                },
            },
        )

    def test_handles_node_with_multiple_values(self, mock_Node):
        mock_Node.objects.get.return_value = self.string_node

        duplicate_node_tile = models.TileModel(data={str(self.string_node.pk): "value_2"}, nodegroup_id=str(self.string_node.pk))

        self.test_resource.tiles.append(self.string_tile)
        self.test_resource.tiles.append(duplicate_node_tile)

        label_based_graph = LabelBasedGraph.from_resource(resource=self.test_resource, compact=False, hide_empty_nodes=False)

        self.assertEqual(
            label_based_graph,
            {
                self.string_node.name: [
                    {
                        NODE_ID_KEY: str(self.string_node.pk),
                        TILE_ID_KEY: str(self.string_tile.pk),
                        VALUE_KEY: self.string_tile.data[str(self.string_node.pk)],
                    },
                    {
                        NODE_ID_KEY: str(self.string_node.pk),
                        TILE_ID_KEY: str(duplicate_node_tile.pk),
                        VALUE_KEY: duplicate_node_tile.data[str(self.string_node.pk)],
                    },
                ],
            },
        )

    def test_handles_empty_semantic_node(self, mock_Node):
        mock_Node.objects.get.return_value = self.grouping_node

        self.test_resource.tiles.append(self.grouping_tile)

        label_based_graph = LabelBasedGraph.from_resource(resource=self.test_resource, compact=False, hide_empty_nodes=False)

        self.assertEqual(
            label_based_graph,
            {
                self.grouping_node.name: {
                    NODE_ID_KEY: str(self.grouping_node.pk),
                    TILE_ID_KEY: str(self.grouping_tile.pk),
                    VALUE_KEY: NON_DATA_COLLECTING_NODE,
                },
            },
        )

    def test_semantic_node_with_child(self, mock_Node):
        mock_Node.objects.get.return_value = self.grouping_node

        self.grouping_node.get_direct_child_nodes = mock.Mock(return_value=[self.string_node])

        self.grouping_tile.data = {str(self.string_node.pk): "value_2"}
        self.test_resource.tiles.append(self.grouping_tile)

        label_based_graph = LabelBasedGraph.from_resource(resource=self.test_resource, compact=False, hide_empty_nodes=False)

        self.assertEqual(
            label_based_graph,
            {
                self.grouping_node.name: {
                    NODE_ID_KEY: str(self.grouping_node.pk),
                    TILE_ID_KEY: str(self.grouping_tile.pk),
                    VALUE_KEY: NON_DATA_COLLECTING_NODE,
                    self.string_node.name: {
                        NODE_ID_KEY: str(self.string_node.pk),
                        TILE_ID_KEY: str(self.grouping_tile.pk),
                        VALUE_KEY: self.grouping_tile.data[str(self.string_node.pk)],
                    },
                },
            },
        )

    def test_handles_node_grouped_in_separate_card(self, mock_Node):
        mock_Node.objects.get.side_effect = [self.grouping_node, self.string_node]

        self.grouping_node.get_direct_child_nodes = mock.Mock(return_value=[self.string_node])

        self.string_tile.parenttile = self.grouping_tile

        self.test_resource.tiles.append(self.grouping_tile)
        self.test_resource.tiles.append(self.string_tile)

        label_based_graph = LabelBasedGraph.from_resource(resource=self.test_resource, compact=False, hide_empty_nodes=False)

        self.assertEqual(
            label_based_graph,
            {
                self.grouping_node.name: {
                    NODE_ID_KEY: str(self.grouping_node.pk),
                    TILE_ID_KEY: str(self.grouping_tile.pk),
                    VALUE_KEY: NON_DATA_COLLECTING_NODE,
                    self.string_node.name: {
                        NODE_ID_KEY: str(self.string_node.pk),
                        TILE_ID_KEY: str(self.string_tile.pk),
                        VALUE_KEY: self.string_tile.data[str(self.string_node.pk)],
                    },
                },
            },
        )
