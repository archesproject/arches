"""Reshape existing business data to match a graph change.

Extracted verbatim from ``arches.app.tasks.update_resource_instance_data_based_on_graph_diff``
so the interactive publish path and package migrations run the same code rather
than two implementations that drift.

Two deliberate differences from the original task body:

* It RAISES. The task swallowed every exception and notified the user, which is
  correct for a background job but would let a failed package migration be
  recorded as applied. Only the Celery wrapper may catch.
* It takes no user and sends no notifications. Migrations have no user.
"""

from django.db import DEFAULT_DB_ALIAS
from django.db.models import F, Q

from arches.app.models import models


def apply_graph_diff(initial_graph, updated_graph, using=DEFAULT_DB_ALIAS):
    """Bring resources on ``initial_graph``'s publication into line with
    ``updated_graph``.

    Both arguments are serialized graphs (``PublishedGraph.serialized_graph``).
    Returns a dict of what was touched, so callers can report progress and drive
    reindexing.
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
    orphaned_tiles_deleted, _ignored = (
        models.TileModel.objects.using(using)
        .filter(
            nodegroup_id__in=orphaned_nodegroup_ids,
            resourceinstance__graph_publication_id=initial_graph["publication_id"],
        )
        .delete()
    )

    # delete tiles whose parent tile's nodegroup_id does not match the expected
    # parent nodegroup_id
    misparented_tiles_deleted, _ignored = (
        models.TileModel.objects.using(using)
        .filter(
            parenttile__isnull=False,
            resourceinstance__graph_publication_id=initial_graph["publication_id"],
        )
        .filter(~Q(parenttile__nodegroup_id=F("nodegroup__parentnodegroup_id")))
        .delete()
    )

    # add/remove nodes and change default values
    resource_instances = models.ResourceInstance.objects.using(using).filter(
        graph_publication_id=initial_graph["publication_id"]
    )
    resource_instance_count = resource_instances.count()

    initial_node_ids_to_default_values = {
        node["nodeid"]: (node.get("config") or {}).get("defaultValue")
        for node in initial_graph["nodes"]
    }
    updated_node_ids_to_default_values = {
        node["nodeid"]: (node.get("config") or {}).get("defaultValue")
        for node in updated_graph["nodes"]
    }

    touched_resource_instance_ids = set()
    tiles_updated = 0

    for tile in models.TileModel.objects.using(using).filter(
        resourceinstance__in=resource_instances
    ):
        updated_node_ids = [
            node["nodeid"]
            for node in updated_graph["nodes"]
            if node["nodegroup_id"] == str(tile.nodegroup_id)
        ]

        # delete nodes not in updated graph
        for node_id in list(tile.data.keys()):
            if node_id not in updated_node_ids:
                del tile.data[node_id]

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
        tiles_updated += 1
        touched_resource_instance_ids.add(tile.resourceinstance_id)

    # update resource_instance publication_id
    for resource_instance in resource_instances:
        resource_instance.graph_publication_id = updated_graph["publication_id"]
        resource_instance.save()
        touched_resource_instance_ids.add(resource_instance.pk)

    return {
        "resource_instance_count": resource_instance_count,
        "orphaned_tiles_deleted": orphaned_tiles_deleted,
        "misparented_tiles_deleted": misparented_tiles_deleted,
        "tiles_updated": tiles_updated,
        "touched_resource_instance_ids": touched_resource_instance_ids,
    }
