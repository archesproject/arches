"""Package migration operations for the difference between two graph states.
Creates run in dependency order and deletes in reverse.
"""

from django.db.models import CASCADE

from arches.db.package_migrations.state import EXCLUDED_FIELDS, STATE_COLLECTIONS
from arches.db.package_migrations.operations.resource import SetResourcePublication
from arches.db.package_migrations.operations.tile import (
    AddNodeToTiles,
    DeleteMisparentedTiles,
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


COLLECTION_MODELS = {
    state_key: alter.model
    for state_key, _pk, _create, alter, _delete in COLLECTION_OPERATIONS
}
COLLECTION_ALTERS = {
    state_key: alter
    for state_key, _pk, _create, alter, _delete in COLLECTION_OPERATIONS
}


def _cascading_fields(state_key):
    collections_by_model = {
        model: collection for collection, model in COLLECTION_MODELS.items()
    }
    return {
        field.attname: collections_by_model[field.related_model]
        for field in COLLECTION_MODELS[state_key]._meta.concrete_fields
        if field.is_relation
        and field.related_model in collections_by_model
        and field.remote_field.on_delete is CASCADE
        and field.attname not in EXCLUDED_FIELDS
    }


def _deleted_ancestors(before_by_collection, deleted, state_key, key):
    found = set()
    pending = [(state_key, key)]
    while pending:
        collection, row_key = pending.pop()
        if row_key not in deleted[collection] or (collection, row_key) in found:
            continue
        found.add((collection, row_key))
        row = before_by_collection[collection][row_key]
        for field, target_collection in _cascading_fields(collection).items():
            if row.get(field) is not None:
                pending.append((target_collection, str(row[field])))
    return found


def _delete_operations(graphid, deleted, include):
    return [
        delete(graphid=graphid, pk=key)
        for state_key, _pk, _create, _alter, delete in reversed(COLLECTION_OPERATIONS)
        for key in sorted(deleted[state_key])
        if include((state_key, key))
    ]


def _placeholders(
    graphid,
    repoints,
    before_by_collection,
    after_by_collection,
    deleted,
    late_deletes,
    remaining_changes,
):
    # A node re-pointed into a nodegroup keeps its old name until its remaining alter,
    # so whichever node holds that name there gives it up first.
    placeholders = []
    nodes_before = before_by_collection["nodes"]
    for state_key, key, repoint in repoints:
        if state_key != "nodes" or "nodegroup_id" not in repoint:
            continue
        for holder_key, holder in sorted(nodes_before.items()):
            if holder_key == key:
                continue
            if str(holder.get("nodegroup_id")) != str(repoint["nodegroup_id"]):
                continue
            if holder.get("name") != nodes_before[key].get("name"):
                continue
            surviving = holder_key not in deleted["nodes"]
            if not surviving and ("nodes", holder_key) not in late_deletes:
                continue
            placeholders.append(
                AlterNode(
                    graphid=graphid,
                    pk=holder_key,
                    changes={"name": f"_placeholder_{holder_key}"},
                )
            )
            if surviving:
                remaining_changes[("nodes", holder_key)]["name"] = after_by_collection[
                    "nodes"
                ][holder_key]["name"]
    return placeholders


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
    before_by_collection = {key: from_graph.get(key) or {} for key in STATE_COLLECTIONS}
    after_by_collection = {key: to_graph.get(key) or {} for key in STATE_COLLECTIONS}
    deleted = {
        key: set(before_by_collection[key]) - set(after_by_collection[key])
        for key in STATE_COLLECTIONS
    }

    # Rows moving off a deleted row move before it is deleted, or its cascade takes them.
    repoints = []
    remaining_changes = {}
    late_deletes = set()
    for state_key, pk, _create, _alter, _delete in COLLECTION_OPERATIONS:
        before = before_by_collection[state_key]
        after = after_by_collection[state_key]
        cascading_fields = _cascading_fields(state_key)
        for key in sorted(set(after) & set(before)):
            changes = _changed_fields(before[key], after[key])
            changes.pop(pk, None)
            repoint = {}
            for field, target_collection in cascading_fields.items():
                previous_target = before[key].get(field)
                if field not in changes or previous_target is None:
                    continue
                if str(previous_target) not in deleted[target_collection]:
                    continue
                repoint[field] = changes.pop(field)
                late_deletes |= _deleted_ancestors(
                    before_by_collection,
                    deleted,
                    target_collection,
                    str(previous_target),
                )
            if repoint:
                repoints.append((state_key, key, repoint))
            remaining_changes[(state_key, key)] = changes

    operations.extend(
        _delete_operations(graphid, deleted, lambda row: row not in late_deletes)
    )
    operations.extend(
        _placeholders(
            graphid,
            repoints,
            before_by_collection,
            after_by_collection,
            deleted,
            late_deletes,
            remaining_changes,
        )
    )
    for state_key, key, repoint in repoints:
        operations.append(
            COLLECTION_ALTERS[state_key](graphid=graphid, pk=key, changes=repoint)
        )
    operations.extend(
        _delete_operations(graphid, deleted, lambda row: row in late_deletes)
    )

    for state_key, _pk, create, alter, _delete in COLLECTION_OPERATIONS:
        before = before_by_collection[state_key]
        after = after_by_collection[state_key]
        for key in sorted(set(after) - set(before)):
            operations.append(create(graphid=graphid, fields=after[key]))
        for key in sorted(set(after) & set(before)):
            changes = remaining_changes[(state_key, key)]
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

    for nodegroupid in sorted(set(before_nodegroups) & set(after_nodegroups)):
        changes = _changed_fields(
            before_nodegroups[nodegroupid], after_nodegroups[nodegroupid]
        )
        if "parentnodegroup_id" in changes:
            operations.append(DeleteMisparentedTiles(nodegroup_id=nodegroupid))

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
