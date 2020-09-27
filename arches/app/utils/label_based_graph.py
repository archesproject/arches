from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.models.resource import Resource  # avoids circular import

NODE_ID_KEY = "@node_id"
TILE_ID_KEY = "@tile_id"
VALUE_KEY = "@value"


class LabelBasedNode(object):
    def __init__(self, name, node_id, tile_id, value):
        self.name = name
        self.node_id = node_id
        self.tile_id = tile_id
        self.value = value
        self.child_nodes = []

    def as_json(self):
        display_data = {
            NODE_ID_KEY: self.node_id,
            TILE_ID_KEY: self.tile_id,
            VALUE_KEY: self.value,
        }

        for child_node in self.child_nodes:
            formatted_node = child_node.as_json()
            formatted_node_name, formatted_node_value = formatted_node.popitem()

            previous_val = display_data.get(formatted_node_name)

            # let's handle multiple identical node names
            if not previous_val:
                display_data[formatted_node_name] = formatted_node_value
            elif isinstance(previous_val, list):
                display_data[formatted_node_name].append(formatted_node_value)
            else:
                display_data[formatted_node_name] = [previous_val, formatted_node_value]

        return {self.name: display_data}


class LabelBasedGraph(object):
    datatype_factory = DataTypeFactory()

    @staticmethod
    def is_node_empty(node):
        """
        Discerns whether a LabelBasedNode either has a value,
        or children with values
        """
        is_empty = True

        if node.value:
            is_empty = False
        else:
            for child_node in node.child_nodes:
                if not LabelBasedGraph.is_node_empty(child_node):
                    is_empty = False

        return is_empty

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
    def from_tile(cls, tile, node_tile_reference=None, hide_empty_nodes=False, as_json=True):
        """
        Generates a label-based graph from a given tile
        """
        if not node_tile_reference:
            node_tile_reference = cls.generate_node_tile_reference(resource=Resource(tile.resourceinstance))

        graph = cls._build_graph(
            node=models.Node.objects.get(pk=tile.nodegroup_id),
            tile=tile,
            parent_tree=None,
            tile_reference=node_tile_reference,
            include_empty_nodes=bool(not hide_empty_nodes),
        )

        return graph.as_json() if as_json else graph

    @classmethod
    def from_resource(cls, resource, hide_empty_nodes, as_json=True):
        """
        Generates a label-based graph from a given resource
        """
        if not resource.tiles:
            resource.load_tiles()

        node_tile_reference = cls.generate_node_tile_reference(resource=resource)

        root_graph = LabelBasedNode(name=resource.displayname, node_id=None, tile_id=None, value=None,)

        for tile in resource.tiles:
            root_tile = tile.get_root_tile()

            if root_tile.data:
                label_based_graph = LabelBasedGraph.from_tile(
                    tile=root_tile, node_tile_reference=node_tile_reference, hide_empty_nodes=hide_empty_nodes, as_json=False,
                )

                if not cls.is_node_empty(node=label_based_graph):
                    root_graph.child_nodes.append(label_based_graph)

        return root_graph.as_json() if as_json else root_graph

    @classmethod
    def _get_display_value(cls, tile, node):
        display_value = None

        if tile.data:
            datatype = cls.datatype_factory.get_instance(node.datatype)

            # `get_display_value` varies between datatypes,
            # so let's handle errors here instead of nullguarding all models
            try:
                display_value = datatype.get_display_value(tile=tile, node=node)
            except:
                pass

        return display_value

    @classmethod
    def _build_graph(cls, node, tile, parent_tree, tile_reference, include_empty_nodes=True):
        # if a tile doesn't have any nodes, it should associate itself
        for associated_tile in tile_reference.get(str(node.pk), [tile]):
            if associated_tile == tile or associated_tile.parenttile == tile:
                label_based_node = LabelBasedNode(
                    name=node.name,
                    node_id=str(node.pk),
                    tile_id=str(associated_tile.pk),
                    value=cls._get_display_value(tile=associated_tile, node=node),
                )

                if parent_tree == None:  # if top node
                    parent_tree = label_based_node
                elif include_empty_nodes or not cls.is_node_empty(label_based_node):
                    parent_tree.child_nodes.append(label_based_node)

                for child_node in node.get_direct_child_nodes():
                    cls._build_graph(
                        node=child_node,
                        tile=associated_tile,
                        parent_tree=label_based_node,
                        tile_reference=tile_reference,
                        include_empty_nodes=include_empty_nodes,
                    )

        return parent_tree
