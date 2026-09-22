"""Readable names for the ids an operation describes.

describe() stays in ids: an operation knows its own row and nothing else, and a
name copied into a migration file would be a lie the first time someone renames
the node. The commands resolve names at display time instead, from data they
already hold: makepkgmigrations from the committed JSON, migratepkg from the
database.

A nodegroup's id is its grouping node's id (node_groups.grouping_node_matches_pk_or_null),
so naming nodes names nodegroups too.
"""

import re

from arches.app.models import models

UUID = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.IGNORECASE
)


def from_graphs(graphs):
    """Names from committed graph JSON, keyed by id."""
    names = {}
    for graphid, graph in graphs.items():
        if graph.get("slug"):
            names[str(graphid).lower()] = graph["slug"]
        for nodeid, node in (graph.get("nodes") or {}).items():
            if node.get("alias"):
                names[str(nodeid).lower()] = node["alias"]
    return names


def from_database(text, using):
    """Names for the ids appearing in `text`, looked up once per kind."""
    ids = {match.lower() for match in UUID.findall(text)}
    if not ids:
        return {}
    names = {
        str(pk).lower(): slug
        for pk, slug in models.GraphModel.objects.using(using)
        .filter(pk__in=ids, slug__isnull=False)
        .values_list("graphid", "slug")
    }
    names.update(
        {
            str(pk).lower(): alias
            for pk, alias in models.Node.objects.using(using)
            .filter(pk__in=ids)
            .values_list("nodeid", "alias")
            if alias
        }
    )
    return names


def humanize(text, names):
    return UUID.sub(
        lambda match: names.get(match.group(0).lower(), match.group(0)), text
    )
