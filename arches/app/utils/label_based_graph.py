from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models


class LabelBasedGraph(object):
    datatype_factory = DataTypeFactory()

    @staticmethod
    def _add_node(graph, node_name, node_val):
        previous_val = graph.get(node_name)

        # let's handle multiple identical node_names
        if not previous_val:
            graph[node_name] = node_val
        elif isinstance(previous_val, list):
            graph[node_name].append(node_val)
        else:
            graph[node_name] = [previous_val, node_val]   

    @classmethod
    def from_tile(cls, tile, **kwargs):
        return cls._build_graph(
            self=cls,
            node=models.Node.objects.get(pk=tile.nodegroup_id),
            tile=tile,
            parent_tree={},
            tile_reference=kwargs.get('node_tile_reference', {}),
        )

    def _build_graph(self, node, tile, parent_tree, tile_reference):
        datatype = self.datatype_factory.get_instance(node.datatype)
        direct_child_nodes = node.get_direct_child_nodes()

        current_tree = {}

        for associated_tile in tile_reference.get(str(node.pk), [tile]):
            if associated_tile == tile or associated_tile.parenttile == tile:
                display_value = {
                    '@node_id': str(node.pk),
                    '@tile_id': str(associated_tile.pk),
                    '@value': datatype.get_display_value(
                        tile=associated_tile,
                        node=node,
                    ),
                }

                self._add_node(
                    graph=current_tree, 
                    node_name=node.name, 
                    node_val=display_value,
                )

                for child_node in direct_child_nodes:
                    self._build_graph(
                        self=self,
                        node=child_node, 
                        tile=associated_tile, 
                        parent_tree=display_value, 
                        tile_reference=tile_reference,
                    )

        self._add_node(
            graph=parent_tree, 
            node_name=node.name, 
            node_val=current_tree.get(node.name)
        )

        return parent_tree 