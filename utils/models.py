from django.contrib.postgres.expressions import ArraySubquery
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    BooleanField,
    DateTimeField,
    F,
    FloatField,
    OuterRef,
    TextField,
    UUIDField,
)
from django.db.models import JSONField
from django.db.models.functions import Cast
from django.db.models.fields.json import KT

from arches import __version__ as arches_version
from arches.app.models.models import ResourceInstance, TileModel
from arches.app.models.utils import field_names
from arches.app.utils.permission_backend import get_nodegroups_by_perm

from arches_querysets.fields import (
    Cardinality1DateTimeField,
    Cardinality1JSONField,
    Cardinality1ResourceInstanceField,
    Cardinality1ResourceInstanceListField,
    Cardinality1TextField,
    CardinalityNField,
    ResourceInstanceField,
    ResourceInstanceListField,
)


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
            tile_values_query = get_tile_values_for_resource(node)
        elif issubclass(model, TileModel):
            # TODO: Investigate consistency with prior branch.
            if node.datatype in {"non-localized-string"}:
                tile_values_query = KT(f"data__{node.pk}")
            else:
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


def get_tile_values_for_resource(node):
    """
    Return a tile values query expression for use in a ResourceInstanceQuerySet.

    Allows shallow filtering, e.g. concepts.filter(uri_content...
    even if `uri_content` is not in the top nodegroup. For this reason,
    multiple tiles for cardinality-1 nodegroups might appear if there
    are cardinality-N parents anywhere.
    """
    many = any_nodegroup_in_hierarchy_is_cardinality_n(node.nodegroup)
    expression, field = get_node_value_expression_and_output_field(node)
    tile_query = (
        TileModel.objects.filter(
            nodegroup_id=node.nodegroup_id,
            resourceinstance_id=OuterRef("resourceinstanceid"),
        )
        .annotate(node_value=expression)
        .values("node_value")
        .order_by("parenttile", "sortorder")
    )

    if many:
        return ArraySubquery(
            tile_query, output_field=CardinalityNField(base_field=field)
        )

    match field:
        case BooleanField() | FloatField() | ArrayField():
            output_field = field
        case DateTimeField():
            output_field = Cardinality1DateTimeField()
        case ResourceInstanceField():
            output_field = Cardinality1ResourceInstanceField()
        case ResourceInstanceListField():
            output_field = Cardinality1ResourceInstanceListField()
        case JSONField():
            output_field = Cardinality1JSONField()
        case _:
            output_field = Cardinality1TextField()
    return Cast(tile_query, output_field=output_field)


def get_node_value_expression_and_output_field(node):
    match node.datatype:
        case "boolean":
            return F(f"data__{node.pk}"), BooleanField()
        case "number":
            return F(f"data__{node.pk}"), FloatField()
        case "non-localized-string":
            return KT(f"data__{node.pk}"), TextField()
        case "date":
            return (
                Cast(KT(f"data__{node.pk}"), output_field=DateTimeField()),
                DateTimeField(),
            )
        case "string" | "url":
            return F(f"data__{node.pk}"), JSONField()
        case "resource-instance":
            return F(f"data__{node.pk}"), ResourceInstanceField()
        case "resource-instance-list":
            return F(f"data__{node.pk}"), ResourceInstanceListField()
        case "concept":
            return KT(f"data__{node.pk}"), UUIDField()
        case "concept-list":
            return F(f"data__{node.pk}"), JSONField()
        case _:
            return F(f"data__{node.pk}"), TextField()


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


def filter_nodes_by_highest_parent(nodes, aliases, user=None):
    filtered_nodes = set()
    for alias in aliases:
        for node in nodes:
            if node.alias == alias:
                break
        else:
            raise ValueError("Node alias {alias} not found in nodes.")
        nodegroups = get_nodegroups_here_and_below(node.nodegroup, user=user)
        for nodegroup in nodegroups:
            filtered_nodes |= set(nodegroup.node_set.all())

    return filtered_nodes


def any_nodegroup_in_hierarchy_is_cardinality_n(nodegroup):
    cardinality_n_found = False
    breaker = 0
    test_nodegroup = nodegroup
    while not cardinality_n_found and test_nodegroup and breaker < 1000:
        if nodegroup.cardinality == "n":
            cardinality_n_found = True
        test_nodegroup = nodegroup.parentnodegroup
        breaker += 1

    return cardinality_n_found


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
