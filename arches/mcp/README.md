# Arches MCP Server

A read-only [Model Context Protocol](https://modelcontextprotocol.io) server
that exposes the core data of an Arches instance — graphs (resource models),
resource instances, tiles, resource-to-resource relationships, and concepts —
to MCP-compatible clients such as Claude Desktop, Claude Code, and the MCP
Inspector.

Because the server runs inside a Django process, it uses your project's normal
settings, database connection, and migrations. Nothing is exposed that your
Django user could not already read.

## Installation

The MCP SDK is an optional dependency:

```bash
pip install 'arches[mcp]'
```

If you are working from a checkout:

```bash
pip install -e '.[mcp]'
```

## Running the server

From the directory that contains your Arches project's `manage.py`:

```bash
# stdio transport (default) — used by Claude Desktop / Claude Code
python manage.py mcp_server

# HTTP/SSE transport — for remote clients
python manage.py mcp_server --transport sse --host 127.0.0.1 --port 8765
```

The process stays in the foreground; stop it with `Ctrl+C`.

## Connecting Claude Desktop

Add an entry under `mcpServers` in
`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or
`%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "arches": {
      "command": "/absolute/path/to/your/venv/bin/python",
      "args": ["/absolute/path/to/your/project/manage.py", "mcp_server"],
      "env": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings"
      }
    }
  }
}
```

Restart Claude Desktop. The Arches tools will appear in the tools menu.

## Connecting Claude Code

```bash
claude mcp add arches \
  --command /absolute/path/to/venv/bin/python \
  --args /absolute/path/to/project/manage.py mcp_server
```

Or edit `~/.claude.json` directly with the same shape as the Claude Desktop
config above.

## Available tools

All tools are read-only. Pagination uses `limit` (default 25, max 200) and
`offset`.

| Tool | What it does |
|------|--------------|
| `list_graphs` | List resource models (graphs). Filters: `resource_models_only`, `active_only`. |
| `describe_graph(graph_id)` | Full schema for one graph: nodes, nodegroups, edges. |
| `count_resources_by_graph` | Resource-instance counts per graph. |
| `search_resources` | Search instances by `graph_id`, `name_contains`, or `legacyid`. |
| `get_resource(resource_id)` | A single resource with display name and tiles grouped by nodegroup alias. |
| `list_resource_tiles(resource_id)` | Tiles for one resource, optionally filtered by `nodegroup_alias`. |
| `get_tile(tile_id)` | One tile with values annotated by node alias. |
| `list_resource_relationships(resource_id)` | `ResourceXResource` rows; `direction` ∈ `from`/`to`/`both`. |
| `get_concept_values(concept_id)` | All `Value` rows for a concept (labels, notes), optional `language`. |
| `search_concepts(text)` | Find concepts by label substring. |

## Example session

> "What kinds of resources are in this Arches instance, and how many of each?"

The model would call `count_resources_by_graph`, then `list_graphs` to show
human-readable names alongside the counts.

> "Show me the data on heritage site abc123."

→ `get_resource(resource_id="abc123...")` returns the resource plus all of
its tiles keyed by nodegroup alias (e.g. `name`, `location`, `description`),
so the model can answer questions about the record without knowing any UUIDs.

## Safety notes

- **Read-only by design.** No tool writes to the database. To extend the
  server with mutating operations, edit `arches/mcp/server.py` — but
  remember that an MCP client controls which tools to call, so any mutating
  tool will eventually be invoked.
- **Result caps.** Every list-returning tool clamps `limit` to
  `MAX_LIMIT = 200` to keep responses bounded.
- **No authentication on the stdio transport.** stdio is meant for local
  subprocess use. If you expose the server over `sse`/`streamable-http`,
  put it behind your own auth proxy — the MCP server itself does not
  authenticate callers.

## Extending

Tools live in `arches/mcp/server.py`. To add a tool:

```python
@mcp.tool()
def my_tool(arg: str) -> dict:
    """One-line description shown to the model."""
    ...
```

Keep return values JSON-serializable (dicts, lists, strings, numbers, bools,
None). Use the `_i18n_to_str` helper for `I18n_TextField` values and
`_coerce_uuid` for UUID arguments.
