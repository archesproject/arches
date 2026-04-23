"""Model Context Protocol (MCP) server for Arches.

Exposes read-only tools for browsing graphs, resource instances, tiles,
relationships, and concepts over the MCP stdio transport. The server is
launched via the ``mcp_server`` Django management command.

Public extension API
--------------------
* :mod:`arches.mcp.helpers` — Django-free utilities (``async_orm_tool``,
  ``coerce_uuid``, ``clamp_limit``, ``i18n_to_str``, ``build_list_envelope``).
* :mod:`arches.mcp.serializers` — ORM-coupled serialisers (``serialize_graph``,
  ``serialize_node``, ``serialize_tile``, etc.).
* :func:`~arches.mcp.server.register_extensions` — hook discovery logic.
"""

from arches.mcp.server import build_server, register_extensions

__all__ = ["build_server", "register_extensions"]
