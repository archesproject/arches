"""Run the Arches MCP (Model Context Protocol) server.

Default transport is ``stdio``, which is what local MCP clients (Claude
Desktop, Claude Code, the MCP Inspector) connect to. Pass ``--transport
sse`` to expose the server over HTTP/SSE for remote clients.
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Run the Arches MCP server (read-only access to graphs, resources, tiles, concepts)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--transport",
            choices=["stdio", "sse", "streamable-http"],
            default="stdio",
            help=(
                "Transport for the MCP server. 'stdio' (default) is for local "
                "clients launched as subprocesses. 'sse' or 'streamable-http' "
                "expose the server over HTTP for remote clients."
            ),
        )
        parser.add_argument(
            "--host",
            default="127.0.0.1",
            help="Host to bind when using sse/streamable-http transport.",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=8765,
            help="Port to bind when using sse/streamable-http transport.",
        )

    def handle(self, *args, **options):
        try:
            from arches.mcp import build_server
        except ImportError as exc:
            raise CommandError(str(exc))

        server = build_server()
        transport = options["transport"]

        if transport in {"sse", "streamable-http"}:
            server.settings.host = options["host"]
            server.settings.port = options["port"]

        # FastMCP.run is blocking. stdio is the right default; the other
        # transports are opt-in for remote use.
        server.run(transport=transport)
