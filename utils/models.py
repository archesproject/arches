from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import F, OuterRef
from django.db.models.expressions import BaseExpression

from arches import __version__ as arches_version
from arches.app.models.models import ResourceInstance, TileModel
from arches.app.models.utils import field_names
from arches.app.utils.permission_backend import get_nodegroups_by_perm


def field_attnames(instance_or_class):
    return {f.attname for f in instance_or_class._meta.fields}


def generate_node_alias_expressions(nodes, *, defer, only, model):
    if defer and only and (overlap := defer.intersection(only)):
        raise ValueError(f"Got intersecting defer/only nodes: {overlap}")
    alias_expressions = {}
    invalid_names = field_names(model)

    for node in nodes:
        if node.datatype == "semantic":
            continue
        if node.nodegroup_id is None:
            continue
        if getattr(node, "source_identifier_id", None):
            continue
        if (defer and node.alias in defer) or (only and node.alias not in only):
            continue
        # TODO: solution here, either bump to aliased_data or rewrite as JSON
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
        alias_expressions[node.alias] = tile_values_query

    if not alias_expressions:
        raise ValueError("All fields were excluded.")

    return alias_expressions


def pop_arches_model_kwargs(kwargs, model_fields):
    arches_model_data = {}
    # Combine these sets to get both "nodegroup" and "nodegroup_id"
    model_field_names = {f.name for f in model_fields} | {
        getattr(f, "attname", None) for f in model_fields
    }
    for kwarg, value in kwargs.items():
        if kwarg not in model_field_names:
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


def get_nodegroups_here_and_below(start_nodegroup, user=None):
    accumulator = []
    if user:
        permitted_nodegroups = get_nodegroups_by_perm(user, "models.read_nodegroup")

    def accumulate(nodegroup):
        nonlocal accumulator
        nonlocal permitted_nodegroups
        nonlocal user
        if user and nodegroup.pk not in permitted_nodegroups:
            return

        accumulator.append(nodegroup)
        if arches_version >= "8":
            children_attr = nodegroup.children
        else:
            children_attr = nodegroup.nodegroup_set
        for child_nodegroup in children_attr.all():
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


def get_recursive_prefetches(lookup_str, *, recursive_part, depth):
    """
    Future: see various solutions mentioned here for avoiding
    "magic number" depth traversal (but the magic number is harmless,
    causes no additional queries beyond actual depth):
    https://forum.djangoproject.com/t/prefetching-relations-to-arbitrary-depth/39328
    """
    prefetches = []
    for i in range(1, depth + 1):
        recursive_lookup = "__".join([recursive_part] * i)
        prefetches.append(lookup_str.replace(recursive_part, recursive_lookup))
    return prefetches
