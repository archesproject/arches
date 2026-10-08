"""Bring existing business data into line with a republished graph.

Reshape the tiles first, then move the resources: a resource's publication says
its data matches that published graph.
"""

from django.db.models import F, Q

from arches.app.models import models


def reshape_tiles(initial_graph, updated_graph):
    updated_nodegroup_ids = {
        nodegroup["nodegroupid"] for nodegroup in updated_graph["nodegroups"]
    }
    orphaned_nodegroup_ids = {
        nodegroup["nodegroupid"]
        for nodegroup in initial_graph["nodegroups"]
        if nodegroup["nodegroupid"] not in updated_nodegroup_ids
    }

    # delete tiles whose nodegroups are no longer in the updated graph
    models.TileModel.objects.filter(
        nodegroup_id__in=orphaned_nodegroup_ids,
        resourceinstance__graph_publication_id=initial_graph["publication_id"],
    ).delete()

    # delete tiles whose parent tile's nodegroup_id does not match the expected
    # parent nodegroup_id
    models.TileModel.objects.filter(
        parenttile__isnull=False,
        resourceinstance__graph_publication_id=initial_graph["publication_id"],
    ).filter(~Q(parenttile__nodegroup_id=F("nodegroup__parentnodegroup_id"))).delete()

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

    tiles = models.TileModel.objects.filter(
        resourceinstance__graph_publication_id=initial_graph["publication_id"]
    )
    for tile in tiles.iterator():
        updated_node_ids = updated_node_ids_by_nodegroup.get(str(tile.nodegroup_id), [])

        # delete nodes not in updated graph
        for node_id in list(tile.data.keys()):
            if node_id not in updated_node_ids:
                del tile.data[node_id]

        # A stale key in a provisional edit is written back into data on approval,
        # and Tile.save() then raises Node.DoesNotExist.
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


def move_resources_to_publication(initial_graph, updated_graph):
    resource_instances = models.ResourceInstance.objects.filter(
        graph_publication_id=initial_graph["publication_id"]
    )
    moved = 0
    for resource_instance in resource_instances.iterator():
        resource_instance.graph_publication_id = updated_graph["publication_id"]
        resource_instance.save()
        moved += 1
    return moved
