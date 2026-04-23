"""Model Context Protocol (MCP) server for Arches.

Exposes read-only tools for browsing graphs, resource instances, tiles,
relationships, and concepts over the MCP stdio transport. The server is
launched via the ``mcp_server`` Django management command.
"""

from arches.mcp.server import build_server

__all__ = ["build_server"]
