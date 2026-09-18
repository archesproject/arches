"""Bring existing business data into line with a republished graph.

Two separate changes, in this order:

* ``reshape_tiles`` rewrites the tiles of resources still on the old publication,
  so their data matches the new graph.
* ``move_resources_to_publication`` then points those resources at the new
  publication, which is what marks them current.

The order is the point. A resource's publication says "this record matches the
published graph", so moving it before its tiles are reshaped would claim
something untrue.

Both raise rather than swallowing: only the Celery wrapper in arches.app.tasks
may catch, or a failure here would be reported as success.
"""

from django.db import DEFAULT_DB_ALIAS
from django.db.models import F, Q

from arches.app.models import models


def reshape_tiles(initial_graph, updated_graph, using=DEFAULT_DB_ALIAS):
    """Rewrite the tiles of resources on ``initial_graph``'s publication.

    Tiles gain keys for nodes the new graph adds, lose keys for nodes it removes,
    and are deleted when their nodegroup is gone. Both arguments are serialized
    graphs (``PublishedGraph.serialized_graph``). Returns the number of tiles
    deleted or rewritten.
    """
    updated_nodegroup_ids = {
        nodegroup["nodegroupid"] for nodegroup in updated_graph["nodegroups"]
    }
    orphaned_nodegroup_ids = {
        nodegroup["nodegroupid"]
        for nodegroup in initial_graph["nodegroups"]
        if nodegroup["nodegroupid"] not in updated_nodegroup_ids
    }

    # delete tiles whose nodegroups are no longer in the updated graph
    orphaned, _ = (
        models.TileModel.objects.using(using)
        .filter(
            nodegroup_id__in=orphaned_nodegroup_ids,
            resourceinstance__graph_publication_id=initial_graph["publication_id"],
        )
        .delete()
    )

    # delete tiles whose parent tile's nodegroup_id does not match the expected
    # parent nodegroup_id
    misparented, _ = (
        models.TileModel.objects.using(using)
        .filter(
            parenttile__isnull=False,
            resourceinstance__graph_publication_id=initial_graph["publication_id"],
        )
        .filter(~Q(parenttile__nodegroup_id=F("nodegroup__parentnodegroup_id")))
        .delete()
    )

    initial_node_ids_to_default_values = {
        node["nodeid"]: (node.get("config") or {}).get("defaultValue")
        for node in initial_graph["nodes"]
    }
    updated_node_ids_to_default_values = {
        node["nodeid"]: (node.get("config") or {}).get("defaultValue")
        for node in updated_graph["nodes"]
    }
    updated_node_ids_by_nodegroup = {}
    for node in updated_graph["nodes"]:
        updated_node_ids_by_nodegroup.setdefault(node["nodegroup_id"], []).append(
            node["nodeid"]
        )

    rewritten = 0
    tiles = models.TileModel.objects.using(using).filter(
        resourceinstance__graph_publication_id=initial_graph["publication_id"]
    )
    for tile in tiles.iterator():
        updated_node_ids = updated_node_ids_by_nodegroup.get(str(tile.nodegroup_id), [])

        # delete nodes not in updated graph
        for node_id in list(tile.data.keys()):
            if node_id not in updated_node_ids:
                del tile.data[node_id]

        # ...and from any pending provisional edit, which is keyed by the same
        # nodeids. A stale key there is written back into data when a reviewer
        # approves the edit, and Tile.save() then raises Node.DoesNotExist because
        # the node is gone, leaving a record no curator can fix from the UI.
        for provisional_edit in (tile.provisionaledits or {}).values():
            for node_id in list(provisional_edit.get("value", {})):
                if node_id not in updated_node_ids:
                    del provisional_edit["value"][node_id]

        # add nodes that only exist in updated graph
        # or update nodes default value if changed
        for node_id in updated_node_ids:
            initial_default_value = initial_node_ids_to_default_values.get(node_id)

            if (
                node_id not in tile.data.keys()
                or tile.data[node_id] == initial_default_value
            ):
                tile.data[node_id] = updated_node_ids_to_default_values.get(node_id)

        tile.save()
        rewritten += 1

    return orphaned + misparented + rewritten


def move_resources_to_publication(initial_graph, updated_graph, using=DEFAULT_DB_ALIAS):
    """Point resources on ``initial_graph``'s publication at ``updated_graph``'s.

    Run this after reshape_tiles: the publication is what says a resource matches
    the published graph. Returns the number of resources moved.
    """
    resource_instances = models.ResourceInstance.objects.using(using).filter(
        graph_publication_id=initial_graph["publication_id"]
    )
    moved = 0
    for resource_instance in resource_instances.iterator():
        resource_instance.graph_publication_id = updated_graph["publication_id"]
        resource_instance.save()
        moved += 1
    return moved
