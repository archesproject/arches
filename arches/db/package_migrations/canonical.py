"""Canonical projection of a graph.

Turns a serialized graph into exactly the shape ``PackageState.graphs`` holds, so
that "what the migrations say the graph looks like" and "what the graph actually
looks like" are directly comparable dicts.

The field set comes from the models rather than a list here, which is also
correct by construction: everything a serialized graph carries that is NOT
package content (is_collector, parentproperty, card constraints, spatial_views,
permissions, relatable_resource_model_ids) is a serializer addition rather than a
column, so none of it survives the projection and nobody has to remember to
exclude the next one.

Collections become keyed maps because Graph.serialize() assembles them from
querysets with no guaranteed ordering, so list position is not identity.
"""

from arches.app.models import models

# Real columns that are still not package content. Every entry needs a reason.
EXCLUDED_FIELDS = {
    # Implied by the graph that contains the row, and identical for every row in it.
    "graph_id",
    # Draft-graph linkage. Minted per install; says nothing about the package.
    "source_identifier_id",
    "sourcebranchpublication_id",
    # Publication state is owned by PublishGraph, not by the structural diff.
    "publication_id",
    "has_unpublished_changes",
}

# (state key, serialized_graph key, model, pk field)
COLLECTIONS = (
    ("nodes", "nodes", models.Node, "nodeid"),
    ("nodegroups", "nodegroups", models.NodeGroup, "nodegroupid"),
    ("edges", "edges", models.Edge, "edgeid"),
    ("cards", "cards", models.CardModel, "cardid"),
    ("widgets", "cards_x_nodes_x_widgets", models.CardXNodeXWidget, "id"),
)


STATE_COLLECTIONS = tuple(entry[0] for entry in COLLECTIONS)


def fields_for(model):
    """The package-content columns of a model, in declaration order."""
    return tuple(
        field.attname
        for field in model._meta.concrete_fields
        if field.attname not in EXCLUDED_FIELDS
    )


def _normalize(value):
    """Coerce to JSON-native shapes so equality and hashing are stable.

    Tuples and lists compare unequal, and a dict mixing UUID and str keys raises
    inside Django's migration serializer, so keys are stringified here rather
    than blowing up later at codegen time.
    """
    if isinstance(value, dict):
        return {str(key): _normalize(inner) for key, inner in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    return str(value)


def _project(source, fields):
    """Only the fields the source actually carries.

    An absent key is not the same as null. A package exported by an older Arches
    has no `alias`, `hascustomalias` or `grouping_node_id`; projecting those to
    None would make every diff emit AlterNode(alias=None), which is written to
    disk, shipped, and only fails on the customer's database -- alias is NOT NULL.
    Absent keys simply produce no change, and the create path fills them from the
    model's own defaults.
    """
    return {field: _normalize(source[field]) for field in fields if field in source}


def canonical_graph(serialized_graph):
    """Project a serialized graph into PackageState's shape."""
    canonical = _project(serialized_graph, fields_for(models.GraphModel))
    canonical["graphid"] = str(canonical["graphid"])
    for state_key, serialized_key, model, pk_field in COLLECTIONS:
        entries = serialized_graph.get(serialized_key) or []
        canonical[state_key] = {
            str(entry[pk_field]): _project(entry, fields_for(model))
            for entry in entries
            if entry.get(pk_field) is not None
        }
    return canonical
