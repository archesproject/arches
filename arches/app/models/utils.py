from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import OuterRef, Subquery
from django.db.models.expressions import BaseExpression


def add_to_update_fields(kwargs, field_name):
    """
    Update the `update_field` arg inside `kwargs` (if present) in-place
    with `field_name`.
    """
    if (update_fields := kwargs.get("update_fields")) is not None:
        if isinstance(update_fields, set):
            # Django sends a set from update_or_create()
            update_fields.add(field_name)
        else:
            # Arches sends a list from tile POST view
            new = set(update_fields)
            new.add(field_name)
            kwargs["update_fields"] = new


def field_names(instance_or_class):
    return {f.name for f in instance_or_class._meta.fields}


def generate_tile_annotations(nodes, *, defer, only, model, lhs=None, outer_ref):
    from arches.app.datatypes.datatypes import DataTypeFactory
    from arches.app.models.models import ResourceInstance, TileModel

    if defer and only and (overlap := set(defer).intersection(set(only))):
        raise ValueError(f"Got intersecting defer/only args: {overlap}")
    datatype_factory = DataTypeFactory()
    node_alias_annotations = {}
    invalid_names = field_names(model)
    is_resource = True
    if ResourceInstance in model.mro():
        is_resource = True
    elif TileModel in model.mro():
        is_resource = False
    else:
        raise ValueError(model)
    for node in nodes:
        if node.datatype == "semantic":
            continue
        if node.nodegroup_id is None:
            continue
        if is_resource:
            root = find_root_node(node.nodegroup.node_set.all(), node.nodegroup_id)
            if (defer and root.alias in defer) or (only and root.alias not in only):
                continue
        else:
            if (defer and node.alias in defer) or (only and node.alias not in only):
                continue
        if node.alias in invalid_names:
            raise ValueError(f'"{node.alias}" clashes with a model field name.')

        datatype_instance = datatype_factory.get_instance(node.datatype)
        tile_values_query = get_values_query(
            nodegroup=node.nodegroup,
            base_lookup=datatype_instance.get_base_orm_lookup(node),
            lhs=lhs,
            outer_ref=outer_ref,
        )
        node_alias_annotations[node.alias] = tile_values_query

    if not node_alias_annotations:
        raise ValueError("All fields were excluded.")
    if not is_resource:
        for given_alias in only or []:
            if given_alias not in node_alias_annotations:
                raise ValueError(f'"{given_alias}" is not a valid node alias.')

    return node_alias_annotations


def pop_arches_model_kwargs(kwargs, model_fields):
    arches_model_data = {}
    for kwarg, value in kwargs.items():
        if kwarg not in model_fields:
            arches_model_data[kwarg] = value
    without_model_data = {k: v for k, v in kwargs.items() if k not in arches_model_data}
    return arches_model_data, without_model_data


def find_root_node(prefetched_siblings, nodegroup_id):
    for sibling_node in prefetched_siblings:
        if sibling_node.pk == nodegroup_id:
            return sibling_node


def get_values_query(*, nodegroup, base_lookup, lhs=None, outer_ref) -> BaseExpression:
    """Return a tile values query expression for use in a
    ResourceInstanceQuerySet or TileQuerySet.

    lhs: the left-hand side (field_name) of the tile query.
        If absent, the query will be filtered by nodegroup and resourceinstance.
    """
    from arches.app.models.models import TileModel

    if lhs:
        tile_query = TileModel.objects.filter(**{lhs: OuterRef(outer_ref)})
    else:
        tile_query = TileModel.objects.filter(
            nodegroup_id=nodegroup.pk, resourceinstance_id=OuterRef(outer_ref)
        )
    if nodegroup.cardinality == "n":
        tile_query = tile_query.order_by("sortorder")

    tile_query = tile_query.values(base_lookup)

    if outer_ref == "tileid":
        return Subquery(tile_query)
    else:
        return ArraySubquery(tile_query)
