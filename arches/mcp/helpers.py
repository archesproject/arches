"""Public helpers for Arches MCP server extensions.

External Arches add-ons (e.g. ``arches-controlled-lists``) register tools by
calling ``@server.tool()`` on the FastMCP instance handed to their
``register_mcp_tools(server)`` AppConfig method or ``<app>.mcp.register(server)``
module-level function.

The utilities below are the stable public API extensions should use when
serialising Arches data so output stays consistent across all tools.

This module deliberately has *no* Django-model imports so extensions can pull
helpers in at module-load time without triggering Django's app registry.
"""

from __future__ import annotations

import functools
import logging
import uuid
from typing import Any, Optional

from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

# A defensive ceiling so list tools cannot return unbounded result sets.
MAX_LIMIT = 200
DEFAULT_LIMIT = 25


def async_orm_tool(func):
    """Wrap a sync ORM function so FastMCP can call it from its event loop.

    FastMCP runs tool callables on the asyncio event loop; Django's ORM
    refuses to run from an async context.  ``sync_to_async`` with
    ``thread_sensitive=True`` routes the call through the shared sync thread
    so DB connections remain consistent across calls.

    Usage::

        from arches.mcp.helpers import async_orm_tool

        @server.tool()
        @async_orm_tool
        def my_tool(some_id: str) -> dict:
            ...
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await sync_to_async(func, thread_sensitive=True)(*args, **kwargs)

    return wrapper


def i18n_to_str(value: Any) -> Any:
    """Render an I18n_String / I18n_JSON / dict to a JSON-safe value.

    Returns ``str(value)`` for I18n field values, the value unchanged for
    dicts and primitives, and ``None`` for ``None``.
    """
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    try:
        return str(value)
    except Exception:
        return None


def coerce_uuid(value: str, field: str) -> uuid.UUID:
    """Validate and convert a string into a UUID, raising a clear error.

    Raises :class:`ValueError` with a human-readable message so MCP clients
    see a useful error rather than a raw Python traceback.
    """
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError(f"{field} must be a valid UUID, got: {value!r}") from exc


def clamp_limit(limit: Optional[int]) -> int:
    """Clamp a user-supplied *limit* into ``[1, MAX_LIMIT]`` with a default.

    Always call this before slicing a queryset so individual tools cannot
    accidentally return unbounded result sets.
    """
    if not limit or limit <= 0:
        return DEFAULT_LIMIT
    return min(int(limit), MAX_LIMIT)


def build_list_envelope(
    total: int,
    offset: int,
    limit: int,
    items_key: str,
    items: list,
) -> dict[str, Any]:
    """Return the standard pagination envelope used by every list-returning tool.

    Extensions should call this instead of constructing the dict by hand so the
    envelope shape stays consistent across core and add-on tools::

        return build_list_envelope(total, offset, limit, "lists", serialized_rows)

    Returns::

        {
            "total": <int>,
            "offset": <int>,
            "limit": <int>,
            "<items_key>": [...]
        }
    """
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        items_key: items,
    }
