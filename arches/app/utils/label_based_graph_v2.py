import copy

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from django.utils import translation
from types import SimpleNamespace


RESOURCE_ID_KEY = "@resource_id"
NODE_ID_KEY = "@node_id"
TILE_ID_KEY = "@tile_id"

NON_DATA_COLLECTING_NODE = "NON_DATA_COLLECTING_NODE"


class LabelBasedNode(object):
    def __init__(self, name, node_id, tile_id, value, cardinality=None):
        self.name = name
        self.node_id = node_id
        self.tile_id = tile_id
        self.cardinality = cardinality
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

    def as_json(
        self, compact=False, include_empty_nodes=True, include_hidden_nodes=True
    ):
        display_data = {}

        if not include_hidden_nodes:
            card = models.CardModel.objects.filter(nodegroup_id=self.node_id).first()
            try:
                if not card.visible:
                    return None
            except AttributeError:
                pass

        for child_node in self.child_nodes:
            formatted_node = child_node.as_json(
                compact=compact,
                include_empty_nodes=include_empty_nodes,
                include_hidden_nodes=include_hidden_nodes,
            )
            if formatted_node is not None:
                formatted_node_name, formatted_node_value = formatted_node.popitem()

                if include_empty_nodes or not child_node.is_empty():
                    previous_val = display_data.get(formatted_node_name)
                    cardinality = child_node.cardinality

                    # let's handle multiple identical node names
                    if not previous_val:
                        should_create_new_array = (
                            cardinality == "n" and self.tile_id != child_node.tile_id
                        )
                        display_data[formatted_node_name] = (
                            [formatted_node_value]
                            if should_create_new_array
                            else formatted_node_value
                        )
                    elif isinstance(previous_val, list):
                        display_data[formatted_node_name].append(formatted_node_value)
                    else:
                        display_data[formatted_node_name] = [
                            previous_val,
                            formatted_node_value,
                        ]

        val = self.value
        if compact and display_data:
            if self.value is not NON_DATA_COLLECTING_NODE:
                if self.value is not None:
                    display_data.update(self.value)
        elif compact and not display_data:  # if compact and no child nodes
            display_data = self.value
        elif not compact:
            display_data[NODE_ID_KEY] = self.node_id
            display_data[TILE_ID_KEY] = self.tile_id
            if self.value is not None and self.value is not NON_DATA_COLLECTING_NODE:
                display_data.update(self.value)

        return {self.name: display_data}


class LabelBasedGraph(object):
    @staticmethod
    def generate_node_ids_to_tiles_reference_and_nodegroup_cardinality_reference(
        resource,
    ):
        """
        Builds a reference of all nodes in a in a given resource,
        paired with a list of tiles in which they exist
        """
        node_ids_to_tiles_reference = {}
        nodegroupids = set()

        for tile in resource.tiles:
            nodegroupids.add(str(tile.nodegroup_id))
            node_ids = list(tile.data.keys())

            if str(tile.nodegroup_id) not in node_ids:
                node_ids.append(str(tile.nodegroup_id))

            for node_id in node_ids:
                tile_list = node_ids_to_tiles_reference.get(node_id, [])
                tile_list.append(tile)
                node_ids_to_tiles_reference[node_id] = tile_list

        nodegroup_cardinality = models.NodeGroup.objects.filter(
            pk__in=nodegroupids
        ).values("nodegroupid", "cardinality")
        nodegroup_cardinality_reference = {
            str(nodegroup["nodegroupid"]): nodegroup["cardinality"]
            for nodegroup in nodegroup_cardinality
        }

        return node_ids_to_tiles_reference, nodegroup_cardinality_reference

    @classmethod
    def is_valid_semantic_node(
        cls,
        node,
        tile,
        node_ids_to_tiles_reference,
        edge_domain_node_ids_to_range_nodes,
    ):
        if node["datatype"] == "semantic":
            child_nodes = edge_domain_node_ids_to_range_nodes.get(node["nodeid"], [])

            semantic_child_nodes = [
                child_node
                for child_node in child_nodes
                if child_node["datatype"] == "semantic"
            ]
            non_semantic_child_nodes = [
                child_node
                for child_node in child_nodes
                if child_node["datatype"] != "semantic"
            ]

            for non_semantic_child_node in non_semantic_child_nodes:
                if (
                    str(non_semantic_child_node["nodeid"]) in tile.data
                    or str(non_semantic_child_node["nodeid"])
                    in node_ids_to_tiles_reference
                ):
                    return True

            has_valid_child_semantic_node = False

            for semantic_child_node in semantic_child_nodes:
                if cls.is_valid_semantic_node(
                    semantic_child_node,
                    tile,
                    node_ids_to_tiles_reference,
                    edge_domain_node_ids_to_range_nodes,
                ):
                    has_valid_child_semantic_node = True

            return has_valid_child_semantic_node

    @classmethod
    def from_tile(
        cls,
        tile,
        node_ids_to_tiles_reference,
        nodegroup_cardinality_reference=None,
        datatype_factory=None,
        node_ids_to_serialized_nodes=None,
        edge_domain_node_ids_to_range_nodes=None,
        hide_empty_nodes=False,
        serialized_graph=None,
        as_json=True,
    ):
        """
        Generates a label-based graph from a given tile
        """
        if not datatype_factory:
            datatype_factory = DataTypeFactory()

        if not serialized_graph:
            node = models.Node.objects.get(pk=tile.nodegroup_id)
            graph = models.GraphModel.objects.get(pk=node.graph_id)

            user_language = translation.get_language()
            published_graph = models.PublishedGraph.objects.get(
                publication=graph.publication, language=user_language
            )
            serialized_graph = published_graph.serialized_graph

        if not node_ids_to_serialized_nodes or not edge_domain_node_ids_to_range_nodes:
            node_ids_to_serialized_nodes = {
                serialized_node["nodeid"]: serialized_node
                for serialized_node in serialized_graph["nodes"]
            }

            edge_domain_node_ids_to_range_nodes = {}
            for serialized_edge in serialized_graph["edges"]:
                if (
                    edge_domain_node_ids_to_range_nodes.get(
                        serialized_edge["domainnode_id"]
                    )
                    is None
                ):
                    edge_domain_node_ids_to_range_nodes[
                        serialized_edge["domainnode_id"]
                    ] = []

                range_node = [
                    serialized_node
                    for serialized_node in serialized_graph["nodes"]
                    if serialized_node["nodeid"] == serialized_edge["rangenode_id"]
                ][0]
                edge_domain_node_ids_to_range_nodes[
                    serialized_edge["domainnode_id"]
                ].append(range_node)

        graph = cls._build_graph(
            input_node=node_ids_to_serialized_nodes[str(tile.nodegroup_id)],
            input_tile=tile,
            parent_tree=None,
            node_ids_to_tiles_reference=node_ids_to_tiles_reference,
            nodegroup_cardinality_reference=nodegroup_cardinality_reference,
            serialized_graph=serialized_graph,
            datatype_factory=datatype_factory,
            node_ids_to_serialized_nodes=node_ids_to_serialized_nodes,
            edge_domain_node_ids_to_range_nodes=edge_domain_node_ids_to_range_nodes,
        )

        return (
            graph.as_json(include_empty_nodes=bool(not hide_empty_nodes))
            if as_json
            else graph
        )

    @classmethod
    def from_resource(
        cls,
        resource,
        datatype_factory=None,
        compact=False,
        hide_empty_nodes=False,
        as_json=True,
        user=None,
        perm=None,
        hide_hidden_nodes=False,
    ):
        """
        Generates a label-based graph from a given resource
        """
        if not datatype_factory:
            datatype_factory = DataTypeFactory()

        if not resource.tiles:
            resource.load_tiles(user, perm)

        (
            node_ids_to_tiles_reference,
            nodegroup_cardinality_reference,
        ) = cls.generate_node_ids_to_tiles_reference_and_nodegroup_cardinality_reference(
            resource=resource
        )

        user_language = translation.get_language()
        published_graph = models.PublishedGraph.objects.get(
            publication=resource.graph.publication, language=user_language
        )
        serialized_graph = published_graph.serialized_graph

        node_ids_to_serialized_nodes = {
            serialized_node["nodeid"]: serialized_node
            for serialized_node in serialized_graph["nodes"]
        }

        edge_domain_node_ids_to_range_nodes = {}
        for serialized_edge in serialized_graph["edges"]:
            if (
                edge_domain_node_ids_to_range_nodes.get(
                    serialized_edge["domainnode_id"]
                )
                is None
            ):
                edge_domain_node_ids_to_range_nodes[
                    serialized_edge["domainnode_id"]
                ] = []

            range_node = [
                serialized_node
                for serialized_node in serialized_graph["nodes"]
                if serialized_node["nodeid"] == serialized_edge["rangenode_id"]
            ][0]
            edge_domain_node_ids_to_range_nodes[
                serialized_edge["domainnode_id"]
            ].append(range_node)

        root_label_based_node = LabelBasedNode(
            name=None, node_id=None, tile_id=None, value=None, cardinality=None
        )

        for tile in resource.tiles:
            label_based_graph = LabelBasedGraph.from_tile(
                tile=tile,
                node_ids_to_tiles_reference=node_ids_to_tiles_reference,
                nodegroup_cardinality_reference=nodegroup_cardinality_reference,
                datatype_factory=datatype_factory,
                node_ids_to_serialized_nodes=node_ids_to_serialized_nodes,
                edge_domain_node_ids_to_range_nodes=edge_domain_node_ids_to_range_nodes,
                hide_empty_nodes=hide_empty_nodes,
                serialized_graph=serialized_graph,
                as_json=False,
            )

            if label_based_graph:
                root_label_based_node.child_nodes.append(label_based_graph)

        if as_json:
            root_label_based_node_json = root_label_based_node.as_json(
                compact=compact,
                include_empty_nodes=bool(not hide_empty_nodes),
                include_hidden_nodes=bool(not hide_hidden_nodes),
            )

            _dummy_resource_name, resource_graph = root_label_based_node_json.popitem()

            # removes unneccesary ( None ) top-node values
            if resource_graph:
                for key in [NODE_ID_KEY, TILE_ID_KEY]:
                    resource_graph.pop(key, None)

            # adds metadata that was previously only accessible via API
            return {
                "displaydescription": resource.displaydescription(),
                "displayname": resource.displayname(),
                "graph_id": resource.graph_id,
                "legacyid": resource.legacyid,
                "map_popup": resource.map_popup(),
                "resourceinstanceid": resource.resourceinstanceid,
                "resource": resource_graph,
            }
        else:  # pragma: no cover
            return root_label_based_node

    @classmethod
    def from_resources(
        cls, resources, compact=False, hide_empty_nodes=False, as_json=True
    ):
        """
        Generates a list of label-based graph from given resources
        """

        datatype_factory = DataTypeFactory()

        resource_label_based_graphs = []

        for resource in resources:
            resource_label_based_graph = cls.from_resource(
                resource=resource,
                datatype_factory=datatype_factory,
                compact=compact,
                hide_empty_nodes=hide_empty_nodes,
                as_json=as_json,
            )

            resource_label_based_graph[RESOURCE_ID_KEY] = str(resource.pk)
            resource_label_based_graphs.append(resource_label_based_graph)

        return resource_label_based_graphs

    @classmethod
    def _get_display_value(cls, tile, serialized_node, datatype_factory):
        display_value = None

        # if the serialized_node is unable to collect data, let's explicitly say so
        if (
            datatype_factory.datatypes[serialized_node["datatype"]].defaultwidget
            is None
        ):
            display_value = NON_DATA_COLLECTING_NODE
        elif tile.data or tile.provisionaledits:
            datatype = datatype_factory.get_instance(serialized_node["datatype"])

            node_copy = copy.deepcopy(serialized_node)

            # `get_display_value` varies between datatypes,
            # so let's handle errors here instead of nullguarding all models
            try:
                display_value = datatype.to_json(
                    tile=tile, node=SimpleNamespace(**node_copy)
                )
            except:  # pragma: no cover
                pass

        return display_value

    @classmethod
    def _build_graph(
        cls,
        input_node,
        input_tile,
        parent_tree,
        node_ids_to_tiles_reference,
        nodegroup_cardinality_reference,
        serialized_graph,
        datatype_factory,
        node_ids_to_serialized_nodes,
        edge_domain_node_ids_to_range_nodes,
    ):
        for associated_tile in node_ids_to_tiles_reference.get(
            input_node["nodeid"], [input_tile]
        ):
            parent_tile = associated_tile.parenttile

            if associated_tile == input_tile or parent_tile == input_tile:
                if (
                    cls.is_valid_semantic_node(
                        node=input_node,
                        tile=associated_tile,
                        node_ids_to_tiles_reference=node_ids_to_tiles_reference,
                        edge_domain_node_ids_to_range_nodes=edge_domain_node_ids_to_range_nodes,
                    )
                    or input_node["nodeid"] in associated_tile.data
                ):

                    label_based_node = LabelBasedNode(
                        name=input_node["name"],
                        node_id=input_node["nodeid"],
                        tile_id=str(associated_tile.pk),
                        value=cls._get_display_value(
                            tile=associated_tile,
                            serialized_node=input_node,
                            datatype_factory=datatype_factory,
                        ),
                        cardinality=nodegroup_cardinality_reference.get(
                            str(associated_tile.nodegroup_id)
                        ),
                    )

                    if not parent_tree:  # if top node and
                        if not parent_tile:  # if not top node in separate card
                            parent_tree = label_based_node
                    else:
                        parent_tree.child_nodes.append(label_based_node)

                    for child_node in edge_domain_node_ids_to_range_nodes.get(
                        input_node["nodeid"], []
                    ):
                        cls._build_graph(
                            input_node=child_node,
                            input_tile=associated_tile,
                            parent_tree=label_based_node,
                            node_ids_to_tiles_reference=node_ids_to_tiles_reference,
                            nodegroup_cardinality_reference=nodegroup_cardinality_reference,
                            serialized_graph=serialized_graph,
                            datatype_factory=datatype_factory,
                            node_ids_to_serialized_nodes=node_ids_to_serialized_nodes,
                            edge_domain_node_ids_to_range_nodes=edge_domain_node_ids_to_range_nodes,
                        )

        return parent_tree
