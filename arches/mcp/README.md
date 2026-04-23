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

Pagination uses `limit` (default 25, max 200) and `offset`.

### Read-only tools

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

### Write tools

| Tool | What it does |
|------|--------------|
| `set_tile_geojson(tile_id, geojson)` | Replace the `geojson-feature-collection` value on a tile. Target a specific node with `node_alias` or `node_id` (auto-detected when only one geojson node exists). Optional `username` for permission checking and edit-log attribution. |

## Example session

> "What kinds of resources are in this Arches instance, and how many of each?"

The model would call `count_resources_by_graph`, then `list_graphs` to show
human-readable names alongside the counts.

> "Show me the data on heritage site abc123."

→ `get_resource(resource_id="abc123...")` returns the resource plus all of
its tiles keyed by nodegroup alias (e.g. `name`, `location`, `description`),
so the model can answer questions about the record without knowing any UUIDs.

> "Update the location of resource abc123 to a point at -118.2, 34.0."

→ `get_resource` first to find the tile containing the location nodegroup,
then `set_tile_geojson(tile_id="...", geojson={"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-118.2,34.0]},"properties":{}}]})`.

## Safety notes

- **`set_tile_geojson` writes to the database.** All other tools are read-only.
  GeoJSON is validated (geometry structure and bbox) before any save occurs.
  The existing tile value is replaced — there is no partial-feature merge.
- **Edit log.** Every `set_tile_geojson` call produces an Arches edit-log entry.
  Pass `username` to attribute the edit to a specific Django user; omit it
  to save without user context (bypasses provisional-edit workflow).
- **Result caps.** Every list-returning tool clamps `limit` to
  `MAX_LIMIT = 200` to keep responses bounded.
- **No authentication on the stdio transport.** stdio is meant for local
  subprocess use. If you expose the server over `sse`/`streamable-http`,
  put it behind your own auth proxy — the MCP server itself does not
  authenticate callers.

## Extending

The MCP server is designed to be extended by any installed Arches application
package. When `build_server()` finishes registering its core tools it calls
`register_extensions(mcp)`, which walks every installed Django app and invites
each Arches application package to register its own tools.

Two hook styles are supported — choose whichever fits your package layout.

### Option A — `AppConfig.register_mcp_tools` (recommended)

Add the method to your `AppConfig` subclass:

```python
# mypackage/apps.py
class MyPackageConfig(AppConfig):
    name = "mypackage"
    is_arches_application = True   # required

    def register_mcp_tools(self, server) -> None:
        from mypackage.mcp import register
        register(server)
```

Then implement `register` in `mypackage/mcp.py`:

```python
# mypackage/mcp.py
from arches.mcp.helpers import async_orm_tool, build_list_envelope, clamp_limit, DEFAULT_LIMIT
from arches.mcp.serializers import serialize_graph   # use the public serialisers

def register(server) -> None:
    @server.tool()
    @async_orm_tool
    def my_tool(arg: str) -> dict:
        """One-line description shown to the model."""
        from mypackage.models import MyModel
        obj = MyModel.objects.get(pk=arg)
        return {"id": str(obj.pk), "name": obj.name}
```

### Option B — module-level `register` function (zero-config fallback)

If your package does *not* declare `register_mcp_tools` on its `AppConfig`,
`register_extensions` will look for `<app_name>.mcp` and call its `register`
function automatically — the same function signature as Option A.

### Public helper API

| Symbol | Module | Purpose |
|--------|--------|---------|
| `async_orm_tool` | `arches.mcp.helpers` | Decorator: wraps sync ORM functions for the async MCP event loop |
| `coerce_uuid(value, field)` | `arches.mcp.helpers` | Parse & validate a UUID string with a clear error message |
| `clamp_limit(limit)` | `arches.mcp.helpers` | Clamp a user-supplied `limit` to `[1, MAX_LIMIT]` |
| `build_list_envelope(total, offset, limit, key, items)` | `arches.mcp.helpers` | Build the standard `{total, offset, limit, <key>: [...]}` response |
| `serialize_graph(graph)` | `arches.mcp.serializers` | Serialise a `GraphModel` |
| `serialize_node(node)` | `arches.mcp.serializers` | Serialise a `Node` |
| `serialize_nodegroup(ng)` | `arches.mcp.serializers` | Serialise a `NodeGroup` |
| `serialize_edge(edge)` | `arches.mcp.serializers` | Serialise an `Edge` |
| `serialize_resource_instance(r)` | `arches.mcp.serializers` | Serialise a `ResourceInstance` |
| `serialize_tile(tile, *, node_alias_map)` | `arches.mcp.serializers` | Serialise a `TileModel` (pass `node_alias_map` to annotate values with aliases) |
| `node_alias_map_for_graph(graph_id)` | `arches.mcp.serializers` | Build `{nodeid_str: alias}` map for a graph |

Keep all return values JSON-serialisable (dicts, lists, strings, numbers,
bools, `None`).  All list-returning tools should use `build_list_envelope` so
the envelope shape is consistent across packages.

### Reference implementation

`arches-controlled-lists` ships the canonical reference extension.  Its
`ArchesControlledListsConfig.register_mcp_tools` delegates to
`arches_controlled_lists/mcp.py::register`, which adds three tools:

| Tool | What it does |
|------|-------------|
| `list_controlled_lists` | Paginated list of all controlled lists |
| `get_controlled_list(list_id)` | One list with its full item hierarchy |
| `search_list_items(text)` | Find items by label substring; filter by `list_id`, `language`, `valuetype` |

### Error handling

Any exception raised during extension registration is logged at `ERROR` level
and skipped — a broken add-on will never prevent the server from starting.

