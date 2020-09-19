from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.models import resource  # avoids circular import


NODE_ID_KEY = '@node_id'
TILE_ID_KEY = '@tile_id'
VALUE_KEY = '@value'

class LabelBasedNode(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class LabelBasedGraph(object):
    datatype_factory = DataTypeFactory()

    @staticmethod
    def add_node(graph, node):
        """
        Adds a node to a graph, respecting non-unique node names
        """
        previous_val = graph.get(node.name)

        # let's handle multiple identical node names
        if not previous_val:
            graph[node.name] = node.value
        elif isinstance(previous_val, list):
            graph[node.name].append(node.value)
        else:
            graph[node.name] = [previous_val, node.value]   
        
    @staticmethod
    def is_node_empty(label_based_node):
        """
        Discerns whether a LabelBasedNode either has a value,
        or children with values
        """
        node_empty = True

        if isinstance(label_based_node.value, dict):
            if label_based_node.value[VALUE_KEY]:
                node_empty = False
            else:
                for key in label_based_node.value.keys():  
                    if key in [NODE_ID_KEY, TILE_ID_KEY, VALUE_KEY]:
                        pass
                    else:
                        node_empty = False

        if isinstance(label_based_node.value, list):
            for node in label_based_node.value:
                if not LabelBasedGraph.is_node_empty(
                    label_based_node=LabelBasedNode(
                        name=label_based_node.name,
                        value=node
                    )
                ):
                    node_empty = False

        return node_empty

    @classmethod
    def from_tile(cls, tile, node_tile_reference=None):
        """
        Generates a label-based graph from a given tile
        """
        if not node_tile_reference:
            node_tile_reference = cls._generate_node_tile_reference(
                self=cls,
                resource=resource.Resource(tile.resourceinstance),
            )

        return cls._build_graph(
            self=cls,
            node=models.Node.objects.get(pk=tile.nodegroup_id),
            tile=tile,
            parent_tree={},
            tile_reference=node_tile_reference,
        )

    @classmethod
    def from_resource(cls, resource):
        """
        Generates a label-based graph from a given resource
        """
        if not resource.tiles:
            resource.load_tiles()

        node_tile_reference = cls._generate_node_tile_reference(
            self=cls,
            resource=resource,
        )

        root_nodes = {}

        for tile in resource.tiles:
            root_tile = tile.get_root_tile()
            
            if not root_nodes.get(str(root_tile.nodegroup_id)):
                label_based_graph = LabelBasedGraph.from_tile(
                    tile=root_tile,
                    node_tile_reference=node_tile_reference,
                )

                if label_based_graph:
                    root_nodes[str(root_tile.nodegroup_id)] = label_based_graph

        root_graph = {}

        for label_based_graph in root_nodes.values():
            root_node_name, graph = label_based_graph.popitem()
            LabelBasedGraph.add_node(
                graph=root_graph, 
                node=LabelBasedNode(
                    name=root_node_name, 
                    value=graph,
                )
            )

        return root_graph
    
    def _generate_node_tile_reference(self, resource):
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

    def _build_graph(self, node, tile, parent_tree, tile_reference, include_empty_nodes=True):
        datatype = self.datatype_factory.get_instance(node.datatype)
        direct_child_nodes = node.get_direct_child_nodes()

        current_tree = {}

        # if a tile doesn't have any nodes, it should associate itself
        associated_tiles = tile_reference.get(str(node.pk), [tile])

        for associated_tile in associated_tiles:
            if associated_tile == tile or associated_tile.parenttile == tile:
                # `get_display_value` varies between datatypes, 
                #  so let's handle errors here instead of nullguarding all models
                try:
                    display_value = datatype.get_display_value(
                        tile=associated_tile,
                        node=node,
                    )
                except:
                    display_value = None

                label_based_node_data = {
                    NODE_ID_KEY: str(node.pk),
                    # TILE_ID_KEY: str(associated_tile.pk),
                    VALUE_KEY: display_value,
                }

                self.add_node(
                    graph=current_tree, 
                    node=LabelBasedNode(
                        name=node.name,
                        value=label_based_node_data,
                    ),
                )

                for child_node in direct_child_nodes:
                    self._build_graph(
                        self=self,
                        node=child_node, 
                        tile=associated_tile, 
                        parent_tree=label_based_node_data, 
                        tile_reference=tile_reference,
                    )

        root_node = LabelBasedNode(
            name=node.name,
            value=current_tree.get(node.name),
        )

        if include_empty_nodes or not self.is_node_empty(root_node):
            self.add_node(
                graph=parent_tree, 
                node=root_node,
            )

        return parent_tree 
