from itertools import chain

from django.contrib.auth.models import User
from django.contrib.postgres.expressions import ArraySubquery
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    Case,
    ExpressionWrapper,
    F,
    JSONField,
    OuterRef,
    TextField,
    UUIDField,
    Value,
    When,
)
from django.db.models.functions import Cast, NullIf
from django.db.models.fields.json import KT
from django.http import HttpRequest
from django.utils.functional import cached_property

from arches import VERSION as arches_version
from arches.app.models.models import ResourceInstance, TileModel

from arches_querysets.datatypes.datatypes import DataTypeFactory
from arches_querysets.fields import (
    CardinalityNConceptListField,
    CardinalityNJSONField,
    CardinalityNResourceInstanceField,
    CardinalityNResourceInstanceListField,
    CardinalityNLocalizedStringField,
    CardinalityNTextField,
    CardinalityNUUIDField,
    ConceptListField,
    LocalizedStringField,
    ResourceInstanceField,
    ResourceInstanceListField,
)


DATATYPES_NEEDING_KEY_TEXT_TRANSFORM = {
    "non-localized-string",
    "date",
    "concept",
    "concept-list",
    "node-value",
}
DATATYPES_NEEDING_CAST = {"boolean", "concept-list", "date", "number"}


class CardinalityNSubquery(ArraySubquery):
    @cached_property
    def output_field(self):
        match self.query.output_field:
            case ResourceInstanceField():
                array_wrapper = CardinalityNResourceInstanceField
            case ResourceInstanceListField():
                array_wrapper = CardinalityNResourceInstanceListField
            case LocalizedStringField():
                array_wrapper = CardinalityNLocalizedStringField
            case UUIDField():
                array_wrapper = CardinalityNUUIDField
            case ConceptListField():
                array_wrapper = CardinalityNConceptListField
            case JSONField():  # e.g. url
                array_wrapper = CardinalityNJSONField
            case TextField():
                array_wrapper = CardinalityNTextField
            case _:
                array_wrapper = ArrayField
        return array_wrapper(self.query.output_field)


def field_attnames(instance_or_class):
    return {f.attname for f in instance_or_class._meta.fields}


def get_invalid_aliases(instance_or_class):
    # From QuerySet._annotate() in Django
    return set(
        chain.from_iterable(
            (
                (field.name, field.attname)
                if hasattr(field, "attname")
                else (field.name,)
            )
            for field in instance_or_class._meta.get_fields()
        )
    )


def generate_node_alias_expressions(model, nodes):
    alias_expressions = {}
    invalid_names = get_invalid_aliases(model)

    for node in nodes:
        alias = node.alias
        if node.alias in invalid_names:
            # TODO (Arches 8.1): determine reserved namespace for node aliases
            alias = "_arches_querysets_" + alias

        if issubclass(model, ResourceInstance):
            tile_values_query = get_tile_values_for_resource(node, nodes)
        elif issubclass(model, TileModel):
            tile_values_query = get_node_value_expression(node, False)
        else:
            raise ValueError
        alias_expressions[alias] = tile_values_query

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


def get_tile_values_for_resource(node, graph_nodes):
    """
    Return a tile values query expression for use in a ResourceTileTreeQuerySet.

    Allows shallow filtering, e.g. concepts.filter(uri_content...
    even if `uri_content` is not in the top nodegroup. For this reason,
    multiple tiles for cardinality-1 nodegroups might appear if there
    are cardinality-N parents anywhere.
    """
    many = any_nodegroup_in_hierarchy_is_cardinality_n(node.nodegroup, graph_nodes)
    expression = get_node_value_expression(node, many)
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
        # None is a better representation than [None] for this subquery.
        # The python representation on aliased_data will still be [].
        return NullIf(
            CardinalityNSubquery(tile_query),
            Value([None]),
        )
    else:
        return tile_query


def get_node_value_expression(node, many: bool):
    node_lookup = f"data__{node.pk}"
    factory = DataTypeFactory()
    instance = factory.get_instance(node.datatype)
    output_field = factory.get_model_field(instance)
    if node.datatype in DATATYPES_NEEDING_KEY_TEXT_TRANSFORM:
        default = KT(node_lookup)
    else:
        default = F(node_lookup)
    if node.datatype in DATATYPES_NEEDING_CAST or many:
        default = Cast(default, output_field=output_field)
    else:
        default = ExpressionWrapper(default, output_field=output_field)
    return Case(When(**{node_lookup: None}, then=Value(None)), default=default)


def get_nodegroups_here_and_below(start_nodegroup):
    accumulator = []

    def accumulate(nodegroup):
        nonlocal accumulator
        accumulator.append(nodegroup)
        # arches_version==9.0.0
        if arches_version >= (8, 0):
            children_attr = nodegroup.children
        else:
            children_attr = nodegroup.nodegroup_set
        for child_nodegroup in children_attr.prefetch_related("node_set__nodegroup"):
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


def any_nodegroup_in_hierarchy_is_cardinality_n(nodegroup, graph_nodes):
    # Avoid verbose prefetching by just building a lookup locally.
    parent_nodegroup_lookup = {
        node.nodegroup.parentnodegroup_id: node.nodegroup.parentnodegroup
        for node in graph_nodes
        if node.nodegroup
    }
    cardinality_n_found = False
    breaker = 0
    while not cardinality_n_found and nodegroup and breaker < 1000:
        if nodegroup.cardinality == "n":
            cardinality_n_found = True
        if nodegroup.parentnodegroup_id:
            nodegroup = parent_nodegroup_lookup[nodegroup.parentnodegroup_id]
        else:
            nodegroup = None
        breaker += 1

    return cardinality_n_found


def get_recursive_prefetches(lookup_str, *, recursive_part="children", depth):
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


def append_tiles_recursively(resource_or_tile):
    from arches_querysets.models import TileTree

    if not vars(resource_or_tile.aliased_data):
        raise RuntimeError("aliased_data is empty")

    for alias, maybe_tiles in vars(resource_or_tile.aliased_data).items():
        if maybe_tiles in (None, []):
            try:
                resource_or_tile.append_tile(alias)
            except (ValueError, RuntimeError):  # not a nodegroup or alias not found
                continue

            maybe_tiles = getattr(resource_or_tile.aliased_data, alias)
        if not isinstance(maybe_tiles, list):
            maybe_tiles = [maybe_tiles]
        for tile in maybe_tiles:
            if isinstance(tile, TileTree):
                tile.fill_blanks()


def ensure_request(request, force_admin=False):
    """Allow server-side usage when not going through middleware."""
    if not request:
        request = HttpRequest()
        username = "admin" if force_admin else "anonymous"
        request.user = (
            User.objects.filter(username=username).select_related("userprofile").get()
        )

    # arches_version==9.0.0: remove & fix call sites to check .viewable_nodegroups
    try:
        request.user.userprofile.cached_viewable_nodegroups
    except AttributeError:
        request.user.userprofile.cached_viewable_nodegroups = (
            # This property is not cached by core until Arches 8.1
            request.user.userprofile.viewable_nodegroups
        )

    return request
