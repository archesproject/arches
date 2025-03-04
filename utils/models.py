from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import F, OuterRef
from django.db.models.expressions import BaseExpression

from arches.app.models.models import ResourceInstance, TileModel
from arches.app.models.utils import field_names


def field_attnames(instance_or_class):
    return {f.attname for f in instance_or_class._meta.fields}


def generate_tile_annotations(nodes, *, defer, only, model):
    if defer and only and (overlap := defer.intersection(only)):
        raise ValueError(f"Got intersecting defer/only nodes: {overlap}")
    node_alias_annotations = {}
    invalid_names = field_names(model)

    for node in nodes:
        if node.datatype == "semantic":
            continue
        if node.nodegroup_id is None:
            continue
        if node.source_identifier_id:
            continue
        if (defer and node.alias in defer) or (only and node.alias not in only):
            continue
        if node.alias in invalid_names:
            raise ValueError(f'"{node.alias}" clashes with a model field name.')

        if issubclass(model, ResourceInstance):
            tile_values_query = get_tile_values_for_resource(
                nodegroup=node.nodegroup,
                base_lookup=f"data__{node.pk}",
            )
        elif issubclass(model, TileModel):
            tile_values_query = F(f"data__{node.pk}")
        else:
            raise ValueError
        node_alias_annotations[node.alias] = tile_values_query

    if not node_alias_annotations:
        raise ValueError("All fields were excluded.")

    return node_alias_annotations


def pop_arches_model_kwargs(kwargs, model_fields):
    arches_model_data = {}
    for kwarg, value in kwargs.items():
        if kwarg not in model_fields:
            arches_model_data[kwarg] = value
    without_model_data = {k: v for k, v in kwargs.items() if k not in arches_model_data}
    return arches_model_data, without_model_data


def get_tile_values_for_resource(*, nodegroup, base_lookup) -> BaseExpression:
    """Return a tile values query expression for use in a ResourceInstanceQuerySet."""
    tile_query = TileModel.objects.filter(
        nodegroup_id=nodegroup.pk, resourceinstance_id=OuterRef("resourceinstanceid")
    )
    if nodegroup.cardinality == "n":
        tile_query = tile_query.order_by("sortorder")
    tile_query = tile_query.values(base_lookup)
    return ArraySubquery(tile_query)


def get_nodegroups_here_and_below(start_nodegroup):
    accumulator = []

    def accumulate(nodegroup):
        nonlocal accumulator
        accumulator.append(nodegroup)
        for child_nodegroup in nodegroup.children.all():
            accumulate(child_nodegroup)

    accumulate(start_nodegroup)
    return accumulator


def filter_nodes_by_highest_parent(nodes, aliases):
    filtered_nodes = set()
    for alias in aliases:
        for node in nodes:
            if node.alias == alias:
                break
        else:
            raise ValueError("Node alias {alias} not found in nodes.")
        nodegroups = get_nodegroups_here_and_below(node.nodegroup)
        for nodegroup in nodegroups:
            filtered_nodes |= set(nodegroup.node_set.all())

    return filtered_nodes
