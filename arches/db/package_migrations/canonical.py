"""Canonical projection of a graph.

Turns a serialized graph into exactly the shape ``PackageState.graphs`` holds, so
that "what the migrations say the graph looks like" and "what the graph actually
looks like" are directly comparable dicts.

The field set is derived from the Django models rather than listed here. That is
not just DRY -- it is also correct by construction, because everything a
serialized graph carries that is NOT package content happens to be a serializer
addition rather than a column:

* ``is_collector`` and ``parentproperty`` on nodes, and ``constraints`` /
  ``is_editable`` on cards, are derived and are stripped by
  ``restore_state_from_serialized_graph`` before it rebuilds anything.
* ``spatial_views``, ``functions_x_graphs``, ``domain_connections``,
  ``relatable_resource_model_ids`` and the guardian ``user_permissions`` /
  ``group_permissions`` blocks are install-local.

None of those are concrete fields, so none of them survive the projection, and
nobody has to remember to exclude them when Arches adds another.

Collections are keyed maps rather than lists because ``Graph.serialize()``
assembles them from querysets with no guaranteed ordering, so list position is
not identity.
"""

import hashlib
import json

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
    if isinstance(value, (set, frozenset)):
        return sorted(_normalize(item) for item in value)
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    return str(value)


def _project(source, fields):
    return {field: _normalize(source.get(field)) for field in fields}


def canonical_graph(serialized_graph):
    """Project a serialized graph into PackageState's shape."""
    canonical = _project(serialized_graph, fields_for(models.GraphModel))
    canonical["graphid"] = str(canonical["graphid"])
    for state_key, serialized_key, model, pk_field in COLLECTIONS:
        # Accept either shape: a serialized graph stores collections as lists,
        # a canonical one as keyed maps. Taking both makes this idempotent, so
        # committed JSON can be re-projected without special-casing.
        entries = serialized_graph.get(serialized_key)
        if entries is None:
            entries = serialized_graph.get(state_key) or []
        if isinstance(entries, dict):
            entries = list(entries.values())
        canonical[state_key] = {
            str(entry[pk_field]): _project(entry, fields_for(model))
            for entry in entries
            if entry.get(pk_field) is not None
        }
    return canonical


def graph_hash(canonical):
    """Stable digest of a canonical graph.

    Distinguishes "this site never touched the package's graph" from "this site
    customized it", which is the difference between a safe upgrade and clobbering
    someone's work.
    """
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
