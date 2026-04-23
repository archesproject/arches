"""MCP server exposing read-only Arches data tools.

Tools are intentionally read-only: the server reads from the active Django
database connection and returns plain JSON-serialisable dicts. Mutating
operations (create/update/delete) are deliberately omitted so the server
is safe to point at a production database.
"""

from __future__ import annotations

import functools
import uuid
from typing import Any, Optional

from asgiref.sync import sync_to_async
from django.db.models import Q

from arches.app.models import models as arches_models
from arches.app.models.resource import Resource


def _async_orm_tool(func):
    """Wrap a sync ORM function so FastMCP can call it from its event loop.

    FastMCP runs tool callables on the asyncio loop; Django's ORM refuses to
    run from an async context. ``sync_to_async`` with ``thread_sensitive=True``
    routes the call through the shared sync thread so DB connections remain
    consistent.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await sync_to_async(func, thread_sensitive=True)(*args, **kwargs)

    return wrapper


# A defensive ceiling so the server cannot return unbounded result sets.
MAX_LIMIT = 200
DEFAULT_LIMIT = 25


def _i18n_to_str(value: Any) -> Any:
    """Render an I18n_String / I18n_JSON / dict to a JSON-safe value.

    Falls back to ``str(value)`` for I18n field values, and returns the value
    unchanged for primitives. Returns ``None`` for ``None``.
    """
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    try:
        return str(value)
    except Exception:
        return None


def _coerce_uuid(value: str, field: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError(f"{field} must be a valid UUID, got: {value!r}") from exc


def _clamp_limit(limit: Optional[int]) -> int:
    if not limit or limit <= 0:
        return DEFAULT_LIMIT
    return min(int(limit), MAX_LIMIT)


def _serialize_graph(graph: arches_models.GraphModel) -> dict[str, Any]:
    return {
        "graphid": str(graph.graphid),
        "name": _i18n_to_str(graph.name),
        "slug": graph.slug,
        "description": _i18n_to_str(graph.description),
        "subtitle": _i18n_to_str(graph.subtitle),
        "isresource": graph.isresource,
        "is_active": graph.is_active,
        "author": graph.author,
        "version": graph.version,
        "iconclass": graph.iconclass,
        "color": graph.color,
        "ontology_id": str(graph.ontology_id) if graph.ontology_id else None,
        "publication_id": (str(graph.publication_id) if graph.publication_id else None),
    }


def _serialize_node(node: arches_models.Node) -> dict[str, Any]:
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


def _serialize_nodegroup(ng: arches_models.NodeGroup) -> dict[str, Any]:
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


def _serialize_edge(edge: arches_models.Edge) -> dict[str, Any]:
    return {
        "edgeid": str(edge.edgeid),
        "domainnodeid": str(edge.domainnode_id),
        "rangenodeid": str(edge.rangenode_id),
        "ontologyproperty": edge.ontologyproperty,
        "name": edge.name,
    }


def _serialize_resource_instance(
    resource: arches_models.ResourceInstance,
) -> dict[str, Any]:
    descriptors = resource.descriptors or {}
    name = _i18n_to_str(resource.name)
    return {
        "resourceinstanceid": str(resource.resourceinstanceid),
        "graphid": str(resource.graph_id),
        "graph_name": _i18n_to_str(resource.graph.name) if resource.graph_id else None,
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


def _serialize_tile(
    tile: arches_models.TileModel,
    *,
    node_alias_map: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """Serialize a tile. If a node_alias_map is provided, also annotate
    each value with the alias of the node it belongs to so consumers do
    not have to fetch the graph separately.
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


def _node_alias_map_for_graph(graph_id) -> dict[str, str]:
    return {
        str(nodeid): alias or ""
        for nodeid, alias in arches_models.Node.objects.filter(
            graph_id=graph_id
        ).values_list("nodeid", "alias")
    }


def build_server():
    """Build and return a configured FastMCP server.

    Imported lazily so the rest of the package does not require the optional
    ``mcp`` dependency at import time.
    """
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise ImportError(
            "The 'mcp' package is required to run the Arches MCP server. "
            "Install it with: pip install 'arches[mcp]'"
        ) from exc

    mcp = FastMCP(
        name="arches",
        instructions=(
            "Read-only tools for browsing an Arches cultural-heritage database. "
            "Use list_graphs to discover resource models, describe_graph to see "
            "the node/nodegroup schema for a graph, and search_resources or "
            "get_resource to inspect resource instances and their tiles."
        ),
    )

    @mcp.tool()
    @_async_orm_tool
    def list_graphs(
        resource_models_only: bool = True,
        active_only: bool = True,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List graphs (resource models) defined in the Arches instance.

        A *graph* is the schema for a class of resource (e.g. "Heritage Site").
        By default returns only resource models that are active.
        """
        qs = arches_models.GraphModel.objects.all()
        if resource_models_only:
            qs = qs.filter(isresource=True)
        if active_only:
            qs = qs.filter(is_active=True)
        # Exclude unpublished drafts (rows with a source_identifier are drafts).
        qs = qs.filter(source_identifier__isnull=True)

        total = qs.count()
        qs = qs.order_by("name")[offset : offset + _clamp_limit(limit)]
        return {
            "total": total,
            "offset": offset,
            "limit": _clamp_limit(limit),
            "graphs": [_serialize_graph(g) for g in qs],
        }

    @mcp.tool()
    @_async_orm_tool
    def describe_graph(graph_id: str) -> dict[str, Any]:
        """Return the full schema for a graph: nodes, nodegroups, and edges.

        ``graph_id`` is a UUID string. Use ``list_graphs`` first if you do
        not know the id.
        """
        gid = _coerce_uuid(graph_id, "graph_id")
        graph = arches_models.GraphModel.objects.get(pk=gid)

        nodes = list(arches_models.Node.objects.filter(graph_id=gid))
        nodegroup_ids = {n.nodegroup_id for n in nodes if n.nodegroup_id}
        nodegroups = list(
            arches_models.NodeGroup.objects.filter(
                nodegroupid__in=nodegroup_ids
            ).select_related("grouping_node")
        )
        edges = list(arches_models.Edge.objects.filter(graph_id=gid))

        return {
            "graph": _serialize_graph(graph),
            "nodes": [_serialize_node(n) for n in nodes],
            "nodegroups": [_serialize_nodegroup(ng) for ng in nodegroups],
            "edges": [_serialize_edge(e) for e in edges],
        }

    @mcp.tool()
    @_async_orm_tool
    def count_resources_by_graph() -> list[dict[str, Any]]:
        """Return the resource instance count per graph (resource models only)."""
        from django.db.models import Count

        rows = (
            arches_models.ResourceInstance.objects.filter(graph__isresource=True)
            .values("graph_id", "graph__name")
            .annotate(count=Count("resourceinstanceid"))
            .order_by("-count")
        )
        return [
            {
                "graphid": str(r["graph_id"]),
                "graph_name": _i18n_to_str(r["graph__name"]),
                "count": r["count"],
            }
            for r in rows
        ]

    @mcp.tool()
    @_async_orm_tool
    def search_resources(
        graph_id: Optional[str] = None,
        name_contains: Optional[str] = None,
        legacyid: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search resource instances.

        Filter by ``graph_id`` (resource model), free-text ``name_contains``
        match against the cached display name, and/or ``legacyid``. Results
        are ordered by creation time (newest first).
        """
        qs = arches_models.ResourceInstance.objects.select_related("graph")
        if graph_id:
            qs = qs.filter(graph_id=_coerce_uuid(graph_id, "graph_id"))
        if legacyid:
            qs = qs.filter(legacyid=legacyid)
        if name_contains:
            # ``name`` is an I18n_TextField stored as JSON. icontains over the
            # JSON text covers all languages without needing a per-language key.
            qs = qs.filter(name__icontains=name_contains)

        total = qs.count()
        qs = qs.order_by("-createdtime")[offset : offset + _clamp_limit(limit)]
        return {
            "total": total,
            "offset": offset,
            "limit": _clamp_limit(limit),
            "resources": [_serialize_resource_instance(r) for r in qs],
        }

    @mcp.tool()
    @_async_orm_tool
    def get_resource(resource_id: str, include_tiles: bool = True) -> dict[str, Any]:
        """Fetch a resource instance and (optionally) all its tiles.

        Tiles are returned grouped by ``nodegroup_alias`` so consumers can
        navigate the resource by semantic field name rather than by UUID.
        """
        rid = _coerce_uuid(resource_id, "resource_id")
        resource = arches_models.ResourceInstance.objects.select_related("graph").get(
            pk=rid
        )
        out: dict[str, Any] = {
            "resource": _serialize_resource_instance(resource),
        }
        # Best-effort display name via the Resource proxy; it may return None
        # if no descriptor function is configured for the graph.
        try:
            out["display_name"] = Resource.objects.get(pk=rid).displayname()
        except Exception:
            out["display_name"] = None

        if include_tiles:
            alias_map = _node_alias_map_for_graph(resource.graph_id)
            tiles = arches_models.TileModel.objects.filter(
                resourceinstance_id=rid
            ).order_by("nodegroup_id", "sortorder")

            grouped: dict[str, list[dict[str, Any]]] = {}
            ungrouped: list[dict[str, Any]] = []
            for tile in tiles:
                serialized = _serialize_tile(tile, node_alias_map=alias_map)
                key = serialized["nodegroup_alias"]
                if key:
                    grouped.setdefault(key, []).append(serialized)
                else:
                    ungrouped.append(serialized)
            out["tiles_by_nodegroup"] = grouped
            if ungrouped:
                out["tiles_without_alias"] = ungrouped

        return out

    @mcp.tool()
    @_async_orm_tool
    def list_resource_tiles(
        resource_id: str,
        nodegroup_alias: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List tiles for a resource, optionally filtered to one nodegroup
        (by its grouping-node alias)."""
        rid = _coerce_uuid(resource_id, "resource_id")
        qs = arches_models.TileModel.objects.filter(resourceinstance_id=rid)

        if nodegroup_alias:
            qs = qs.filter(nodegroup__grouping_node__alias=nodegroup_alias)

        # Build alias map from this resource's graph for cheap value annotation.
        graph_id = arches_models.ResourceInstance.objects.values_list(
            "graph_id", flat=True
        ).get(pk=rid)
        alias_map = _node_alias_map_for_graph(graph_id)

        total = qs.count()
        qs = qs.order_by("nodegroup_id", "sortorder")[
            offset : offset + _clamp_limit(limit)
        ]
        return {
            "total": total,
            "offset": offset,
            "limit": _clamp_limit(limit),
            "tiles": [_serialize_tile(t, node_alias_map=alias_map) for t in qs],
        }

    @mcp.tool()
    @_async_orm_tool
    def get_tile(tile_id: str) -> dict[str, Any]:
        """Fetch a single tile by id, with node aliases annotated."""
        tid = _coerce_uuid(tile_id, "tile_id")
        tile = arches_models.TileModel.objects.select_related(
            "nodegroup__grouping_node", "resourceinstance"
        ).get(pk=tid)
        alias_map = _node_alias_map_for_graph(tile.resourceinstance.graph_id)
        return _serialize_tile(tile, node_alias_map=alias_map)

    @mcp.tool()
    @_async_orm_tool
    def list_resource_relationships(
        resource_id: str,
        direction: str = "both",
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List ResourceXResource relationships for a resource.

        ``direction`` is one of ``"from"``, ``"to"``, or ``"both"`` (default).
        Each row includes the related resource id, its graph, and the
        relationship type.
        """
        rid = _coerce_uuid(resource_id, "resource_id")
        if direction not in {"from", "to", "both"}:
            raise ValueError("direction must be one of: from, to, both")

        if direction == "from":
            q = Q(from_resource_id=rid)
        elif direction == "to":
            q = Q(to_resource_id=rid)
        else:
            q = Q(from_resource_id=rid) | Q(to_resource_id=rid)

        qs = arches_models.ResourceXResource.objects.filter(q).select_related(
            "from_resource_graph", "to_resource_graph"
        )
        total = qs.count()
        qs = qs.order_by("-modified")[offset : offset + _clamp_limit(limit)]

        rows = []
        for rel in qs:
            rows.append(
                {
                    "resourcexid": str(rel.resourcexid),
                    "from_resource_id": (
                        str(rel.from_resource_id) if rel.from_resource_id else None
                    ),
                    "to_resource_id": (
                        str(rel.to_resource_id) if rel.to_resource_id else None
                    ),
                    "from_graph_name": (
                        _i18n_to_str(rel.from_resource_graph.name)
                        if rel.from_resource_graph_id
                        else None
                    ),
                    "to_graph_name": (
                        _i18n_to_str(rel.to_resource_graph.name)
                        if rel.to_resource_graph_id
                        else None
                    ),
                    "relationshiptype": rel.relationshiptype,
                    "inverserelationshiptype": rel.inverserelationshiptype,
                    "notes": rel.notes,
                    "tileid": str(rel.tile_id) if rel.tile_id else None,
                    "nodeid": str(rel.node_id) if rel.node_id else None,
                    "modified": rel.modified.isoformat() if rel.modified else None,
                }
            )
        return {
            "total": total,
            "offset": offset,
            "limit": _clamp_limit(limit),
            "relationships": rows,
        }

    @mcp.tool()
    @_async_orm_tool
    def get_concept_values(
        concept_id: str,
        language: Optional[str] = None,
    ) -> dict[str, Any]:
        """Return all Values attached to a Concept (labels, notes, etc.).

        Optionally filter to a single ``language`` code (e.g. ``"en"``).
        """
        cid = _coerce_uuid(concept_id, "concept_id")
        qs = arches_models.Value.objects.filter(concept_id=cid).select_related(
            "valuetype", "language"
        )
        if language:
            qs = qs.filter(language_id=language)

        return {
            "concept_id": str(cid),
            "values": [
                {
                    "valueid": str(v.valueid),
                    "value": v.value,
                    "valuetype": v.valuetype_id,
                    "valuetype_category": v.valuetype.category,
                    "language": v.language_id,
                }
                for v in qs
            ],
        }

    @mcp.tool()
    @_async_orm_tool
    def search_concepts(
        text: str,
        language: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search concepts by label text (case-insensitive substring match)."""
        qs = arches_models.Value.objects.filter(value__icontains=text)
        if language:
            qs = qs.filter(language_id=language)
        # Prefer prefLabel-type values when present.
        qs = qs.select_related("concept", "valuetype").order_by("value")
        total = qs.count()
        qs = qs[offset : offset + _clamp_limit(limit)]
        return {
            "total": total,
            "offset": offset,
            "limit": _clamp_limit(limit),
            "matches": [
                {
                    "conceptid": str(v.concept_id),
                    "value": v.value,
                    "valuetype": v.valuetype_id,
                    "language": v.language_id,
                }
                for v in qs
            ],
        }

    return mcp
