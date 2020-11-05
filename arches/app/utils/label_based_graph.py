from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models

NODE_ID_KEY = "@node_id"
TILE_ID_KEY = "@tile_id"
VALUE_KEY = "@value"

NON_DATA_COLLECTING_NODE = "NON_DATA_COLLECTING_NODE"


class LabelBasedNode(object):
    def __init__(self, name, node_id, tile_id, value):
        self.name = name
        self.node_id = node_id
        self.tile_id = tile_id
        self.value = value
        self.child_nodes = []

    def is_empty(self):
        is_empty = True

        if self.value and self.value is not NON_DATA_COLLECTING_NODE:
            is_empty = False
        else:
            for child_node in self.child_nodes:
                if not child_node.is_empty():
                    is_empty = False

        return is_empty

    def as_json(self, compact=False, include_empty_nodes=True):
        display_data = {}

        for child_node in self.child_nodes:
            formatted_node = child_node.as_json(compact=compact, include_empty_nodes=include_empty_nodes)

            formatted_node_name, formatted_node_value = formatted_node.popitem()

            if include_empty_nodes or not child_node.is_empty():
                previous_val = display_data.get(formatted_node_name)

                # let's handle multiple identical node names
                if not previous_val:
                    display_data[formatted_node_name] = formatted_node_value
                elif isinstance(previous_val, list):
                    display_data[formatted_node_name].append(formatted_node_value)
                else:
                    display_data[formatted_node_name] = [previous_val, formatted_node_value]

        if compact and not display_data:  # if compact and no child nodes
            display_data = self.value
        elif not compact:
            display_data[NODE_ID_KEY] = self.node_id
            display_data[TILE_ID_KEY] = self.tile_id
            display_data[VALUE_KEY] = self.value

        return {self.name: display_data}


class LabelBasedGraph(object):
    @staticmethod
    def generate_node_tile_reference(resource):
        """
        Builds a reference of all nodes in a in a given resource,
        paired with a list of tiles in which they exist
        """
        node_tile_reference = {}

        for tile in resource.tiles:
            for node_id in tile.data.keys():
                tile_list = node_tile_reference.get(node_id, [])
                tile_list.append(tile)
                node_tile_reference[node_id] = tile_list

        return node_tile_reference

    @classmethod
    def from_tile(cls, tile, node_tile_reference, datatype_factory=None, compact=False, hide_empty_nodes=False, as_json=True):
        """
        Generates a label-based graph from a given tile
        """
        if not datatype_factory:
            datatype_factory = DataTypeFactory()

        graph = cls._build_graph(
            node=models.Node.objects.get(pk=tile.nodegroup_id),
            tile=tile,
            parent_tree=None,
            tile_reference=node_tile_reference,
            datatype_factory=datatype_factory,
        )

        return graph.as_json(include_empty_nodes=bool(not hide_empty_nodes)) if as_json else graph

    @classmethod
    def from_resource(cls, resource, compact, hide_empty_nodes, as_json=True):
        """
        Generates a label-based graph from a given resource
        """
        if not resource.tiles:
            resource.load_tiles()

        node_tile_reference = cls.generate_node_tile_reference(resource=resource)
        datatype_factory = DataTypeFactory()

        root_graph = LabelBasedNode(name=resource.displayname, node_id=None, tile_id=None, value=None)

        for tile in resource.tiles:
            label_based_graph = LabelBasedGraph.from_tile(
                tile=tile,
                node_tile_reference=node_tile_reference,
                datatype_factory=datatype_factory,
                compact=compact,
                hide_empty_nodes=hide_empty_nodes,
                as_json=False,
            )

            if label_based_graph:
                root_graph.child_nodes.append(label_based_graph)

        if as_json:
            root_graph_json = root_graph.as_json(compact=compact, include_empty_nodes=bool(not hide_empty_nodes))

            resource_name, resource_graph = root_graph_json.popitem()

            for key in [NODE_ID_KEY, TILE_ID_KEY, VALUE_KEY]:
                if key in resource_graph:
                    resource_graph.pop(key)  # removes unneccesary top-node values

            return {resource_name: resource_graph}
        else:  # pragma: no cover
            return root_graph

    @classmethod
    def _get_display_value(cls, tile, node, datatype_factory):
        display_value = None

        # if the node is unable to collect data, let's explicitly say so
        if datatype_factory.datatypes[node.datatype].defaultwidget is None:
            display_value = NON_DATA_COLLECTING_NODE
        elif tile.data:
            datatype = datatype_factory.get_instance(node.datatype)

            # `get_display_value` varies between datatypes,
            # so let's handle errors here instead of nullguarding all models
            try:
                display_value = datatype.get_display_value(tile=tile, node=node)
            except:  # pragma: no cover
                pass

        return display_value

    @classmethod
    def _build_graph(cls, node, tile, parent_tree, tile_reference, datatype_factory):
        # if a tile doesn't have any nodes, it should associate itself
        for associated_tile in tile_reference.get(str(node.pk), [tile]):
            if associated_tile == tile or associated_tile.parenttile == tile:
                label_based_node = LabelBasedNode(
                    name=node.name,
                    node_id=str(node.pk),
                    tile_id=str(associated_tile.pk),
                    value=cls._get_display_value(tile=associated_tile, node=node, datatype_factory=datatype_factory),
                )

                if not parent_tree:
                    if not associated_tile.parenttile:  # if not top node in separate card
                        parent_tree = label_based_node
                else:
                    parent_tree.child_nodes.append(label_based_node)

                for child_node in node.get_direct_child_nodes():
                    cls._build_graph(
                        node=child_node,
                        tile=associated_tile,
                        parent_tree=label_based_node,
                        tile_reference=tile_reference,
                        datatype_factory=datatype_factory,
                    )

        return parent_tree
