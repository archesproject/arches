"""ORM-coupled serialisers for Arches MCP tools.

These are the *public* serialisation functions that both core tools and
extension tools should use so that wire shapes stay consistent.

Unlike ``arches.mcp.helpers``, this module **does** import Django models and
may only be used from within a fully-configured Django context (i.e. after
``django.setup()`` has been called, which the ``mcp_server`` management
command guarantees).
"""

from __future__ import annotations

from typing import Any, Optional

from arches.app.models import models as arches_models

from arches.mcp.helpers import i18n_to_str


def serialize_graph(graph: arches_models.GraphModel) -> dict[str, Any]:
    """Serialise a :class:`~arches.app.models.models.GraphModel` to a plain dict."""
    return {
        "graphid": str(graph.graphid),
        "name": i18n_to_str(graph.name),
        "slug": graph.slug,
        "description": i18n_to_str(graph.description),
        "subtitle": i18n_to_str(graph.subtitle),
        "isresource": graph.isresource,
        "is_active": graph.is_active,
        "author": graph.author,
        "version": graph.version,
        "iconclass": graph.iconclass,
        "color": graph.color,
        "ontology_id": str(graph.ontology_id) if graph.ontology_id else None,
        "publication_id": (str(graph.publication_id) if graph.publication_id else None),
    }


def serialize_node(node: arches_models.Node) -> dict[str, Any]:
    """Serialise a :class:`~arches.app.models.models.Node` to a plain dict."""
    return {
        "nodeid": str(node.nodeid),
        "name": node.name,
        "alias": node.alias,
        "datatype": node.datatype,
        "description": node.description,
        "istopnode": node.istopnode,
        "issearchable": node.issearchable,
        "isrequired": node.isrequired,
        "nodegroupid": str(node.nodegroup_id) if node.nodegroup_id else None,
        "graphid": str(node.graph_id),
        "ontologyclass": node.ontologyclass,
    }


def serialize_nodegroup(ng: arches_models.NodeGroup) -> dict[str, Any]:
    """Serialise a :class:`~arches.app.models.models.NodeGroup` to a plain dict."""
    return {
        "nodegroupid": str(ng.nodegroupid),
        "cardinality": ng.cardinality,
        "parentnodegroupid": (
            str(ng.parentnodegroup_id) if ng.parentnodegroup_id else None
        ),
        "alias": (
            ng.grouping_node.alias
            if getattr(ng, "grouping_node", None) is not None
            else None
        ),
    }


def serialize_edge(edge: arches_models.Edge) -> dict[str, Any]:
    """Serialise a :class:`~arches.app.models.models.Edge` to a plain dict."""
    return {
        "edgeid": str(edge.edgeid),
        "domainnodeid": str(edge.domainnode_id),
        "rangenodeid": str(edge.rangenode_id),
        "ontologyproperty": edge.ontologyproperty,
        "name": edge.name,
    }


def serialize_resource_instance(
    resource: arches_models.ResourceInstance,
) -> dict[str, Any]:
    """Serialise a :class:`~arches.app.models.models.ResourceInstance`."""
    descriptors = resource.descriptors or {}
    name = i18n_to_str(resource.name)
    return {
        "resourceinstanceid": str(resource.resourceinstanceid),
        "graphid": str(resource.graph_id),
        "graph_name": (i18n_to_str(resource.graph.name) if resource.graph_id else None),
        "name": name,
        "descriptors": descriptors,
        "createdtime": (
            resource.createdtime.isoformat() if resource.createdtime else None
        ),
        "legacyid": resource.legacyid,
        "lifecycle_state_id": (
            str(resource.resource_instance_lifecycle_state_id)
            if resource.resource_instance_lifecycle_state_id
            else None
        ),
    }


def node_alias_map_for_graph(graph_id) -> dict[str, str]:
    """Return a ``{nodeid_str: alias}`` map for all nodes in *graph_id*.

    Used by tile serialisers to annotate raw node-keyed data with human-
    readable aliases so callers don't need a separate graph lookup.
    """
    return {
        str(nodeid): alias or ""
        for nodeid, alias in arches_models.Node.objects.filter(
            graph_id=graph_id
        ).values_list("nodeid", "alias")
    }


def serialize_tile(
    tile: arches_models.TileModel,
    *,
    node_alias_map: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """Serialise a :class:`~arches.app.models.models.TileModel`.

    If *node_alias_map* is provided (keyed by nodeid string), each data entry
    is annotated with ``"alias"`` so consumers can navigate by field name.
    Build the map with :func:`node_alias_map_for_graph`.
    """
    raw_data = tile.data or {}
    data_with_aliases: dict[str, Any] = {}
    for nodeid_str, value in raw_data.items():
        entry: dict[str, Any] = {"value": value}
        if node_alias_map and nodeid_str in node_alias_map:
            entry["alias"] = node_alias_map[nodeid_str]
        data_with_aliases[nodeid_str] = entry

    return {
        "tileid": str(tile.tileid),
        "resourceinstanceid": str(tile.resourceinstance_id),
        "nodegroupid": str(tile.nodegroup_id) if tile.nodegroup_id else None,
        "nodegroup_alias": tile.find_nodegroup_alias(),
        "parenttileid": str(tile.parenttile_id) if tile.parenttile_id else None,
        "sortorder": tile.sortorder,
        "data": data_with_aliases,
    }
