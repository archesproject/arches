"""Package migration operations for the difference between two graph states.
Creates run in dependency order and deletes in reverse.
"""

from arches.db.package_migrations.state import STATE_COLLECTIONS
from arches.db.package_migrations.operations.resource import SetResourcePublication
from arches.db.package_migrations.operations.tile import (
    AddNodeToTiles,
    DeleteTilesForNodeGroup,
    RemoveNodeFromTiles,
)
from arches.db.package_migrations.operations.card import (
    AlterCard,
    CreateCard,
    DeleteCard,
)
from arches.db.package_migrations.operations.edge import (
    AlterEdge,
    CreateEdge,
    DeleteEdge,
)
from arches.db.package_migrations.operations.graph import (
    AlterGraph,
    CreateGraph,
    PublishGraph,
)
from arches.db.package_migrations.operations.node import (
    AlterNode,
    CreateNode,
    DeleteNode,
)
from arches.db.package_migrations.operations.nodegroup import (
    AlterNodeGroup,
    CreateNodeGroup,
    DeleteNodeGroup,
)
from arches.db.package_migrations.operations.widget import (
    AlterCardXNodeXWidget,
    CreateCardXNodeXWidget,
    DeleteCardXNodeXWidget,
)

# (state key, pk field, Create, Alter, Delete), in creation order.
COLLECTION_OPERATIONS = (
    ("nodegroups", "nodegroupid", CreateNodeGroup, AlterNodeGroup, DeleteNodeGroup),
    ("nodes", "nodeid", CreateNode, AlterNode, DeleteNode),
    ("edges", "edgeid", CreateEdge, AlterEdge, DeleteEdge),
    ("cards", "cardid", CreateCard, AlterCard, DeleteCard),
    (
        "widgets",
        "id",
        CreateCardXNodeXWidget,
        AlterCardXNodeXWidget,
        DeleteCardXNodeXWidget,
    ),
)


def _scalar_fields(graph):
    return {key: value for key, value in graph.items() if key not in STATE_COLLECTIONS}


def _changed_fields(before, after):
    return {
        field: value for field, value in after.items() if before.get(field) != value
    }


def changes_for_graph(from_graph, to_graph, publication_id):
    """Operations that turn ``from_graph`` (None if new) into ``to_graph``."""
    operations = []

    creating = from_graph is None
    if creating:
        operations.append(CreateGraph(fields=_scalar_fields(to_graph)))
        from_graph = {"graphid": to_graph["graphid"]}
        from_graph.update({key: {} for key in STATE_COLLECTIONS})
    else:
        changes = _changed_fields(_scalar_fields(from_graph), _scalar_fields(to_graph))
        changes.pop("graphid", None)
        if changes:
            operations.append(AlterGraph(graphid=to_graph["graphid"], changes=changes))

    graphid = to_graph["graphid"]

    for state_key, _pk, _create, _alter, delete in reversed(COLLECTION_OPERATIONS):
        before = from_graph.get(state_key) or {}
        after = to_graph.get(state_key) or {}
        for key in sorted(set(before) - set(after)):
            operations.append(delete(graphid=graphid, pk=key))

    for state_key, pk, create, alter, _delete in COLLECTION_OPERATIONS:
        before = from_graph.get(state_key) or {}
        after = to_graph.get(state_key) or {}
        for key in sorted(set(after) - set(before)):
            operations.append(create(graphid=graphid, fields=after[key]))
        for key in sorted(set(after) & set(before)):
            changes = _changed_fields(before[key], after[key])
            changes.pop(pk, None)
            if changes:
                operations.append(alter(graphid=graphid, pk=key, changes=changes))

    if not operations:
        return []

    if not creating:
        operations.extend(_data_operations(from_graph, to_graph))
    operations.extend(
        _publication_operations(from_graph, to_graph, creating, publication_id)
    )
    return operations


def _data_operations(from_graph, to_graph):
    # Must run after DeleteNode: TileModel.save() re-adds keys for existing nodes.
    operations = []

    before_nodegroups = from_graph.get("nodegroups") or {}
    after_nodegroups = to_graph.get("nodegroups") or {}
    deleted_nodegroups = set(before_nodegroups) - set(after_nodegroups)

    before_nodes = from_graph.get("nodes") or {}
    after_nodes = to_graph.get("nodes") or {}
    for nodeid in sorted(set(after_nodes) - set(before_nodes)):
        node = after_nodes[nodeid]
        if node.get("nodegroup_id"):
            operations.append(
                AddNodeToTiles(
                    nodegroup_id=node["nodegroup_id"],
                    nodeid=nodeid,
                    value=(node.get("config") or {}).get("defaultValue"),
                )
            )
    for nodeid in sorted(set(before_nodes) - set(after_nodes)):
        node = before_nodes[nodeid]
        if str(node.get("nodegroup_id")) in deleted_nodegroups:
            continue
        if node.get("nodegroup_id"):
            operations.append(
                RemoveNodeFromTiles(nodegroup_id=node["nodegroup_id"], nodeid=nodeid)
            )

    for nodegroupid in sorted(deleted_nodegroups):
        # TileModel.nodegroup is DO_NOTHING, so tiles outlive their nodegroup.
        operations.append(DeleteTilesForNodeGroup(nodegroup_id=nodegroupid))

    return operations


def _publication_operations(from_graph, to_graph, creating, publication_id):
    graphid = to_graph["graphid"]
    previous_publication_id = from_graph.get("publication_id")
    operations = [
        PublishGraph(
            graphid=graphid,
            publication_id=publication_id,
            previous_publication_id=previous_publication_id,
        )
    ]
    if not creating:
        operations.append(
            SetResourcePublication(
                graphid=graphid,
                publication_id=publication_id,
                previous_publication_id=previous_publication_id,
            )
        )
    return operations


def changes_for_package(from_state_graphs, to_state_graphs, publication_ids):
    """Operations for every graph in a package."""
    operations = []
    for graphid in sorted(to_state_graphs):
        operations.extend(
            changes_for_graph(
                from_state_graphs.get(graphid),
                to_state_graphs[graphid],
                publication_ids[graphid],
            )
        )
    return operations
