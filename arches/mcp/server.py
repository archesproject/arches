"""MCP server exposing Arches data tools.

Core read-only tools cover graphs, resource instances, tiles, relationships,
and concepts.  A write tool (``set_tile_geojson``) is also provided for
updating ``geojson-feature-collection`` node values on existing tiles.

Extension packages (e.g. ``arches-controlled-lists``) add their own tools
by implementing one of the two hooks documented in :func:`register_extensions`.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from django.db.models import Q

from arches.app.models import models as arches_models
from arches.app.models.resource import Resource

from arches.mcp.helpers import (
    async_orm_tool,
    build_list_envelope,
    clamp_limit,
    coerce_uuid,
    i18n_to_str,
    DEFAULT_LIMIT,
)
from arches.mcp.serializers import (
    node_alias_map_for_graph,
    serialize_edge,
    serialize_graph,
    serialize_node,
    serialize_nodegroup,
    serialize_resource_instance,
    serialize_tile,
)

logger = logging.getLogger(__name__)


def register_extensions(mcp) -> None:
    """Discover and load MCP tools from installed Arches application packages.

    Called by :func:`build_server` after all core tools have been registered.
    Two hook styles are supported (tried in order):

    **1. AppConfig method hook** (preferred)::

        # mypackage/apps.py
        class MyPackageConfig(AppConfig):
            name = "mypackage"
            is_arches_application = True

            def register_mcp_tools(self, server) -> None:
                from mypackage.mcp import register
                register(server)

    **2. Module-level ``register`` function** (zero-config fallback)::

        # mypackage/mcp.py
        def register(server) -> None:
            from arches.mcp.helpers import async_orm_tool

            @server.tool()
            @async_orm_tool
            def my_tool(...) -> dict:
                ...

    Any exception raised by an extension is logged as an error and skipped so
    that a broken add-on never prevents the server from starting.
    """
    import importlib

    from django.apps import apps

    arches_apps = [
        ac
        for ac in apps.get_app_configs()
        if getattr(ac, "is_arches_application", False)
    ]
    logger.warning(
        "MCP register_extensions: found %d Arches application(s): %s",
        len(arches_apps),
        [ac.name for ac in arches_apps],
    )

    for app_config in arches_apps:
        # --- Hook 1: explicit AppConfig method ---
        if hasattr(app_config, "register_mcp_tools"):
            logger.warning("MCP: calling register_mcp_tools on %s", app_config.name)
            try:
                app_config.register_mcp_tools(mcp)
                logger.warning(
                    "MCP: registered tools from %s (AppConfig hook)",
                    app_config.name,
                )
            except Exception:
                logger.exception(
                    "MCP: FAILED to register tools from %s (AppConfig hook)",
                    app_config.name,
                )
            continue  # don't also try the module hook for the same app

        # --- Hook 2: <app_module>.mcp.register(server) ---
        mcp_module_path = f"{app_config.name}.mcp"
        logger.warning(
            "MCP: no register_mcp_tools on %s, trying module %s",
            app_config.name,
            mcp_module_path,
        )
        try:
            mod = importlib.import_module(mcp_module_path)
            if callable(getattr(mod, "register", None)):
                mod.register(mcp)
                logger.warning(
                    "MCP: registered tools from %s (module hook)",
                    mcp_module_path,
                )
            else:
                logger.warning(
                    "MCP: module %s has no callable register()", mcp_module_path
                )
        except ModuleNotFoundError as exc:
            # Only suppress if the missing module IS the top-level mcp module
            # itself.  A deeper ImportError (e.g. a missing dep inside mcp.py)
            # must be reported so it is not mistaken for "no mcp module".
            if exc.name == mcp_module_path:
                logger.warning("MCP: no module %s found, skipping", mcp_module_path)
            else:
                logger.exception(
                    "MCP: FAILED loading %s — ImportError inside the module "
                    "(missing dependency: %s)",
                    mcp_module_path,
                    exc.name,
                )
        except Exception:
            logger.exception(
                "MCP: FAILED to register tools from %s (module hook)",
                mcp_module_path,
            )


def build_server():
    """Build and return a configured FastMCP server with all tools registered.

    Imported lazily so the rest of the package does not require the optional
    ``mcp`` dependency at import time. After the core tools are registered,
    :func:`register_extensions` is called to load tools from installed Arches
    application packages.
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
            "Tools for browsing and editing an Arches cultural-heritage database. "
            "Use list_graphs to discover resource models, describe_graph to see "
            "the node/nodegroup schema for a graph, and search_resources or "
            "get_resource to inspect resource instances and their tiles. "
            "Use set_tile_geojson to update the geometry (geojson-feature-collection) "
            "on an existing tile — supply a valid GeoJSON FeatureCollection."
        ),
    )

    # ------------------------------------------------------------------ #
    #  Core tools                                                          #
    # ------------------------------------------------------------------ #

    @mcp.tool()
    @async_orm_tool
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
        _limit = clamp_limit(limit)
        qs = qs.order_by("name")[offset : offset + _limit]
        return build_list_envelope(
            total, offset, _limit, "graphs", [serialize_graph(g) for g in qs]
        )

    @mcp.tool()
    @async_orm_tool
    def describe_graph(graph_id: str) -> dict[str, Any]:
        """Return the full schema for a graph: nodes, nodegroups, and edges.

        ``graph_id`` is a UUID string. Use ``list_graphs`` first if you do
        not know the id.
        """
        gid = coerce_uuid(graph_id, "graph_id")
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
            "graph": serialize_graph(graph),
            "nodes": [serialize_node(n) for n in nodes],
            "nodegroups": [serialize_nodegroup(ng) for ng in nodegroups],
            "edges": [serialize_edge(e) for e in edges],
        }

    @mcp.tool()
    @async_orm_tool
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
                "graph_name": i18n_to_str(r["graph__name"]),
                "count": r["count"],
            }
            for r in rows
        ]

    @mcp.tool()
    @async_orm_tool
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
            qs = qs.filter(graph_id=coerce_uuid(graph_id, "graph_id"))
        if legacyid:
            qs = qs.filter(legacyid=legacyid)
        if name_contains:
            # ``name`` is an I18n_TextField stored as JSON; icontains over the
            # JSON text covers all languages without needing a per-language key.
            qs = qs.filter(name__icontains=name_contains)

        total = qs.count()
        _limit = clamp_limit(limit)
        qs = qs.order_by("-createdtime")[offset : offset + _limit]
        return build_list_envelope(
            total,
            offset,
            _limit,
            "resources",
            [serialize_resource_instance(r) for r in qs],
        )

    @mcp.tool()
    @async_orm_tool
    def get_resource(resource_id: str, include_tiles: bool = True) -> dict[str, Any]:
        """Fetch a resource instance and (optionally) all its tiles.

        Tiles are returned grouped by ``nodegroup_alias`` so consumers can
        navigate the resource by semantic field name rather than by UUID.
        """
        rid = coerce_uuid(resource_id, "resource_id")
        resource = arches_models.ResourceInstance.objects.select_related("graph").get(
            pk=rid
        )
        out: dict[str, Any] = {
            "resource": serialize_resource_instance(resource),
        }
        # Best-effort display name via the Resource proxy; it may return None
        # if no descriptor function is configured for the graph.
        try:
            out["display_name"] = Resource.objects.get(pk=rid).displayname()
        except Exception:
            out["display_name"] = None

        if include_tiles:
            alias_map = node_alias_map_for_graph(resource.graph_id)
            tiles = arches_models.TileModel.objects.filter(
                resourceinstance_id=rid
            ).order_by("nodegroup_id", "sortorder")

            grouped: dict[str, list[dict[str, Any]]] = {}
            ungrouped: list[dict[str, Any]] = []
            for tile in tiles:
                serialized = serialize_tile(tile, node_alias_map=alias_map)
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
    @async_orm_tool
    def list_resource_tiles(
        resource_id: str,
        nodegroup_alias: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List tiles for a resource, optionally filtered to one nodegroup
        (by its grouping-node alias)."""
        rid = coerce_uuid(resource_id, "resource_id")
        qs = arches_models.TileModel.objects.filter(resourceinstance_id=rid)

        if nodegroup_alias:
            qs = qs.filter(nodegroup__grouping_node__alias=nodegroup_alias)

        # Build alias map from this resource's graph for cheap value annotation.
        graph_id = arches_models.ResourceInstance.objects.values_list(
            "graph_id", flat=True
        ).get(pk=rid)
        alias_map = node_alias_map_for_graph(graph_id)

        total = qs.count()
        _limit = clamp_limit(limit)
        qs = qs.order_by("nodegroup_id", "sortorder")[offset : offset + _limit]
        return build_list_envelope(
            total,
            offset,
            _limit,
            "tiles",
            [serialize_tile(t, node_alias_map=alias_map) for t in qs],
        )

    @mcp.tool()
    @async_orm_tool
    def get_tile(tile_id: str) -> dict[str, Any]:
        """Fetch a single tile by id, with node aliases annotated."""
        tid = coerce_uuid(tile_id, "tile_id")
        tile = arches_models.TileModel.objects.select_related(
            "nodegroup__grouping_node", "resourceinstance"
        ).get(pk=tid)
        alias_map = node_alias_map_for_graph(tile.resourceinstance.graph_id)
        return serialize_tile(tile, node_alias_map=alias_map)

    @mcp.tool()
    @async_orm_tool
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
        rid = coerce_uuid(resource_id, "resource_id")
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
        _limit = clamp_limit(limit)
        qs = qs.order_by("-modified")[offset : offset + _limit]

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
                        i18n_to_str(rel.from_resource_graph.name)
                        if rel.from_resource_graph_id
                        else None
                    ),
                    "to_graph_name": (
                        i18n_to_str(rel.to_resource_graph.name)
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
        return build_list_envelope(total, offset, _limit, "relationships", rows)

    @mcp.tool()
    @async_orm_tool
    def get_concept_values(
        concept_id: str,
        language: Optional[str] = None,
    ) -> dict[str, Any]:
        """Return all Values attached to a Concept (labels, notes, etc.).

        Optionally filter to a single ``language`` code (e.g. ``"en"``).
        """
        cid = coerce_uuid(concept_id, "concept_id")
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
    @async_orm_tool
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
        qs = qs.select_related("concept", "valuetype").order_by("value")
        total = qs.count()
        _limit = clamp_limit(limit)
        qs = qs[offset : offset + _limit]
        return build_list_envelope(
            total,
            offset,
            _limit,
            "matches",
            [
                {
                    "conceptid": str(v.concept_id),
                    "value": v.value,
                    "valuetype": v.valuetype_id,
                    "language": v.language_id,
                }
                for v in qs
            ],
        )

    # ------------------------------------------------------------------ #
    #  Write tools                                                         #
    # ------------------------------------------------------------------ #

    @mcp.tool()
    @async_orm_tool
    def set_tile_geojson(
        tile_id: str,
        geojson: dict,
        node_alias: Optional[str] = None,
        node_id: Optional[str] = None,
        username: Optional[str] = None,
    ) -> dict[str, Any]:
        """Set the geojson-feature-collection value on a tile.

        **This tool writes to the database.** The GeoJSON is validated
        (geometry bbox, feature structure) before saving.

        Parameters
        ----------
        tile_id : str
            UUID of the tile to edit.
        geojson : dict
            A valid GeoJSON ``FeatureCollection`` object, e.g.::

                {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {"type": "Point", "coordinates": [-118.2, 34.0]},
                            "properties": {}
                        }
                    ]
                }

            Pass ``{"type": "FeatureCollection", "features": []}`` to clear
            the geometry.
        node_alias : str, optional
            Alias of the ``geojson-feature-collection`` node to update.
            Either ``node_alias`` or ``node_id`` must be supplied when the
            tile contains more than one geojson node.
        node_id : str, optional
            UUID of the ``geojson-feature-collection`` node to update.
            Alternative to ``node_alias``; ignored if ``node_alias`` is given.
        username : str, optional
            Django username to record in the edit log and use for permission
            checking.  If the user is not a resource reviewer the edit is
            stored as a *provisional edit* rather than committed directly.
            Omit to save without a user context (bypasses provisional-edit
            logic and saves directly — appropriate for system-level imports).

        Returns
        -------
        dict
            The serialised tile after saving, plus a ``"saved_node_id"`` key
            indicating which node was updated.
        """
        from django.contrib.auth.models import User

        from arches.app.datatypes.datatypes import DataTypeFactory
        from arches.app.models.tile import Tile

        # --- Validate geojson structure (surface-level) ---
        if not isinstance(geojson, dict) or geojson.get("type") != "FeatureCollection":
            raise ValueError(
                "geojson must be a GeoJSON FeatureCollection object "
                "(i.e. {'type': 'FeatureCollection', 'features': [...]})"
            )
        if "features" not in geojson or not isinstance(geojson["features"], list):
            raise ValueError("geojson must have a 'features' list")

        tid = coerce_uuid(tile_id, "tile_id")

        # --- Load the tile (proxy class, not the raw model) ---
        tile = Tile.objects.select_related("resourceinstance__graph", "nodegroup").get(
            pk=tid
        )

        # --- Resolve which node to update ---
        # Build a map of nodeid → alias for geojson nodes in this tile.
        geojson_nodes = {
            str(nodeid): alias or ""
            for nodeid, alias, datatype in arches_models.Node.objects.filter(
                graph_id=tile.resourceinstance.graph_id
            ).values_list("nodeid", "alias", "datatype")
            if datatype == "geojson-feature-collection"
        }

        # Only keep nodes whose data key is already present in the tile
        # (or any geojson node for the graph if the tile data is empty/new).
        tile_geojson_nodeids = {
            nid: alias
            for nid, alias in geojson_nodes.items()
            if nid in (tile.data or {})
        }

        if node_alias:
            # Find by alias.
            matched = [nid for nid, al in geojson_nodes.items() if al == node_alias]
            if not matched:
                raise ValueError(
                    f"No geojson-feature-collection node with alias {node_alias!r} "
                    f"found in graph for tile {tile_id}. "
                    f"Available geojson nodes: {list(geojson_nodes.values())}"
                )
            target_nodeid = matched[0]
        elif node_id:
            nid_str = str(coerce_uuid(node_id, "node_id"))
            if nid_str not in geojson_nodes:
                raise ValueError(
                    f"Node {node_id!r} is not a geojson-feature-collection node "
                    f"in graph for tile {tile_id}. "
                    f"Available geojson node ids: {list(geojson_nodes.keys())}"
                )
            target_nodeid = nid_str
        else:
            # Auto-detect: exactly one geojson node must exist in the tile data.
            if len(tile_geojson_nodeids) == 1:
                target_nodeid = next(iter(tile_geojson_nodeids))
            elif len(tile_geojson_nodeids) == 0:
                # Tile data has no geojson keys yet — look at all graph geojson nodes.
                if len(geojson_nodes) == 1:
                    target_nodeid = next(iter(geojson_nodes))
                elif len(geojson_nodes) == 0:
                    raise ValueError(
                        f"Tile {tile_id} belongs to a graph with no "
                        "geojson-feature-collection nodes."
                    )
                else:
                    raise ValueError(
                        "Multiple geojson-feature-collection nodes found. "
                        "Specify node_alias or node_id. "
                        f"Available: {list(geojson_nodes.values())}"
                    )
            else:
                raise ValueError(
                    "Multiple geojson-feature-collection nodes found in tile data. "
                    "Specify node_alias or node_id. "
                    f"Available aliases: {list(tile_geojson_nodeids.values())}"
                )

        # --- Run datatype validation (bbox, geometry structure) ---
        factory = DataTypeFactory()
        datatype = factory.get_instance("geojson-feature-collection")
        # check_geojson_value normalises multi-part geometries and assigns feature ids.
        normalised = datatype.check_geojson_value(geojson)
        errors = datatype.validate(normalised)
        if errors:
            messages = "; ".join(e.get("message", str(e)) for e in errors)
            raise ValueError(f"GeoJSON validation failed: {messages}")

        # --- Apply the new value ---
        if tile.data is None:
            tile.data = {}
        tile.data[target_nodeid] = normalised

        # --- Resolve user (optional) ---
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise ValueError(f"No Django user found with username {username!r}")

        # --- Save via the Tile proxy (triggers pre/post hooks and edit log) ---
        tile.save(user=user)

        # --- Return the updated tile ---
        alias_map = node_alias_map_for_graph(tile.resourceinstance.graph_id)
        return {
            "saved_node_id": target_nodeid,
            "saved_node_alias": alias_map.get(target_nodeid, ""),
            "tile": serialize_tile(tile, node_alias_map=alias_map),
        }

    # ------------------------------------------------------------------ #
    #  Extension tools from installed Arches application packages         #
    # ------------------------------------------------------------------ #
    register_extensions(mcp)

    return mcp
