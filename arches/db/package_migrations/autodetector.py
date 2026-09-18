"""Work out what changed between two graph states, as package migration operations.

The original GraphPublicationComparator had eight hand-written ``check_*``
methods, one per kind of change, and could only detect what someone had
remembered to write a check for: it saw 2 of ~20 top-level keys and was blind
to all 97 edges of a real resource model.

None of that is needed once both sides are canonical projections of the same
model-derived shape: added keys are creates, missing keys are deletes, and
differing values are alters. Coverage becomes a property of the projection rather
than of how many checks exist, so a field added to a model is diffed the day it
is added.

Emission order matters and is fixed here rather than left to the caller:

* creates run graph -> nodegroup -> node -> edge -> card -> widget, because each
  references the one before it;
* deletes run in the exact reverse;
* a non-collector node is always paired with the edge that joins it to the tree,
  because ``Graph.copy()`` rebuilds nodegroup membership by walking edges and a
  stranded node makes the graph uncopyable.
"""

import uuid

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

# state key -> (pk field, Create, Alter, Delete). Creation order; deletion is the
# reverse.
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


def changes_for_graph(from_graph, to_graph):
    """Operations that turn ``from_graph`` into ``to_graph``.

    Both are canonical projections. ``from_graph`` may be None, meaning the graph
    does not exist yet.
    """
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

    # Deletes first, in reverse dependency order, so a row is never orphaned by
    # the removal of the thing it points at.
    for state_key, _pk, _create, _alter, delete in reversed(COLLECTION_OPERATIONS):
        before = from_graph.get(state_key) or {}
        after = to_graph.get(state_key) or {}
        for key in sorted(set(before) - set(after)):
            operations.append(delete(graphid=graphid, pk=key))

    # Then creates and alters, in dependency order.
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

    # A graph being created here has no tiles to backfill and no resources to
    # move: everything in it is new. Emitting them anyway wrote one operation per
    # node that could only ever match zero rows, and left the data migration
    # irreversible for want of a previous publication.
    if not creating:
        operations.extend(_data_operations(from_graph, to_graph))
    operations.extend(_publication_operations(from_graph, to_graph, creating))
    return operations


def _data_operations(from_graph, to_graph):
    """Tile data that a structural change leaves inconsistent.

    Ordering is load-bearing in one direction: RemoveNodeFromTiles must follow
    DeleteNode, because TileModel.save() -> set_missing_keys_to_none() re-adds a
    key for any Node still in the nodegroup. makepkgmigrations puts these in their
    own migration, which runs after the structural one.
    """
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
        # A node in a nodegroup that is going away needs no key removal: every
        # tile holding it is deleted below.
        if str(node.get("nodegroup_id")) in deleted_nodegroups:
            continue
        if node.get("nodegroup_id"):
            operations.append(
                RemoveNodeFromTiles(nodegroup_id=node["nodegroup_id"], nodeid=nodeid)
            )

    for nodegroupid in sorted(deleted_nodegroups):
        # TileModel.nodegroup is db_constraint=False / on_delete=DO_NOTHING, so a
        # deleted nodegroup leaves its tiles behind with nothing to reference.
        operations.append(DeleteTilesForNodeGroup(nodegroup_id=nodegroupid))

    return operations


def _publication_operations(from_graph, to_graph, creating=False):
    """Publish, then move resources onto the publication. Always last.

    Without these a migration mutates node/card/edge rows and nothing the
    application reads ever changes: the published snapshot still holds the old
    graph, resources stay on the old publication and go read-only, and the stale
    draft reverts the whole migration on the next Graph Designer publish.
    """
    graphid = to_graph["graphid"]
    publication_id = str(uuid.uuid4())
    previous_publication_id = from_graph.get("publication_id")
    operations = [
        PublishGraph(
            graphid=graphid,
            publication_id=publication_id,
            previous_publication_id=previous_publication_id,
        )
    ]
    # Nothing to move onto a publication for a graph created in this same diff.
    if not creating:
        operations.append(
            SetResourcePublication(
                graphid=graphid,
                publication_id=publication_id,
                previous_publication_id=previous_publication_id,
            )
        )
    return operations


def changes_for_package(from_state_graphs, to_state_graphs):
    """Operations for every graph in a package, keyed by graphid."""
    operations = []
    for graphid in sorted(to_state_graphs):
        operations.extend(
            changes_for_graph(from_state_graphs.get(graphid), to_state_graphs[graphid])
        )
    return operations
