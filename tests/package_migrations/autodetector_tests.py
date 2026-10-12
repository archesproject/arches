"""Detecting what changed between two graph states. No database."""

import uuid

from django.test import SimpleTestCase

from arches.db.package_migrations.state import PackageState, canonical_graph
from arches.db.package_migrations.autodetector import changes_for_graph

GRAPH = str(uuid.uuid4())
NODEGROUP = str(uuid.uuid4())
NODE = str(uuid.uuid4())
PUBLICATION_ID = str(uuid.uuid4())


def _graph(nodes=(), nodegroups=(), **overrides):
    serialized = {
        "graphid": GRAPH,
        "name": {"en": "Heritage Asset"},
        "slug": "heritage-asset",
        "isresource": True,
        "nodes": list(nodes),
        "nodegroups": list(nodegroups),
    }
    serialized.update(overrides)
    return canonical_graph(serialized)


def _node(nodeid=NODE, **overrides):
    node = {
        "nodeid": nodeid,
        "name": {"en": "Survey Date"},
        "datatype": "date",
        "istopnode": False,
        "alias": "survey_date",
        "nodegroup_id": NODEGROUP,
    }
    node.update(overrides)
    return node


PUBLICATION = ("PublishGraph", "SetResourcePublication")


def _names(operations):
    return [type(op).__name__ for op in operations]


def _structural(operations):
    return [n for n in _names(operations) if n not in PUBLICATION]


class DiffGraphTests(SimpleTestCase):
    def test_no_change_produces_no_operations(self):
        graph = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        self.assertEqual(changes_for_graph(graph, graph, PUBLICATION_ID), [])

    def test_new_graph_emits_create_graph_first(self):
        operations = changes_for_graph(None, _graph(nodes=[_node()]), PUBLICATION_ID)
        self.assertEqual(_names(operations)[0], "CreateGraph")
        self.assertIn("CreateNode", _names(operations))

    def test_added_node_emits_create_node_with_every_field(self):
        before = _graph(nodegroups=[{"nodegroupid": NODEGROUP}])
        after = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        operations = changes_for_graph(before, after, PUBLICATION_ID)
        self.assertEqual(_structural(operations), ["CreateNode", "AddNodeToTiles"])
        self.assertEqual(operations[0].fields["alias"], "survey_date")
        self.assertEqual(operations[0].fields["datatype"], "date")

    def test_changed_field_emits_alter_with_only_that_field(self):
        before = _graph(nodes=[_node()])
        after = _graph(nodes=[_node(datatype="concept")])
        operations = changes_for_graph(before, after, PUBLICATION_ID)
        self.assertEqual(_structural(operations), ["AlterNode"])
        self.assertEqual(operations[0].changes, {"datatype": "concept"})

    def test_removed_node_emits_delete(self):
        before = _graph(nodes=[_node()])
        after = _graph()
        self.assertEqual(
            _structural(changes_for_graph(before, after, PUBLICATION_ID)),
            ["DeleteNode", "RemoveNodeFromTiles"],
        )

    def test_graph_metadata_change_emits_alter_graph(self):
        before = _graph()
        after = _graph(subtitle={"en": "new"})
        operations = changes_for_graph(before, after, PUBLICATION_ID)
        self.assertEqual(_structural(operations), ["AlterGraph"])
        self.assertNotIn("graphid", operations[0].changes)

    def test_creates_run_nodegroup_before_node(self):
        after = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        names = _structural(changes_for_graph(_graph(), after, PUBLICATION_ID))
        self.assertLess(names.index("CreateNodeGroup"), names.index("CreateNode"))

    def test_deletes_run_before_creates_and_in_reverse_order(self):
        other_node = str(uuid.uuid4())
        before = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        after = _graph(nodes=[_node(nodeid=other_node)])
        names = _structural(changes_for_graph(before, after, PUBLICATION_ID))
        self.assertLess(names.index("DeleteNode"), names.index("CreateNode"))
        self.assertLess(names.index("DeleteNode"), names.index("DeleteNodeGroup"))

    def test_a_key_the_to_state_omits_is_not_a_change(self):
        """Reading it as null would emit AlterNode(alias=None); alias is NOT NULL."""
        complete = _node(alias="survey_date", hascustomalias=True)
        partial = {
            key: value
            for key, value in complete.items()
            if key not in ("alias", "hascustomalias")
        }
        nodegroups = [{"nodegroupid": NODEGROUP}]
        before = _graph(nodes=[complete], nodegroups=nodegroups)
        after = _graph(nodes=[partial], nodegroups=nodegroups)
        self.assertEqual(changes_for_graph(before, after, PUBLICATION_ID), [])

    def test_diff_is_the_inverse_of_replaying_its_own_operations(self):
        before = _graph(nodegroups=[{"nodegroupid": NODEGROUP}])
        after = _graph(
            nodes=[_node()],
            nodegroups=[{"nodegroupid": NODEGROUP}],
            subtitle={"en": "v2"},
        )
        state = PackageState()
        state.add_graph(before)
        for operation in changes_for_graph(before, after, PUBLICATION_ID):
            operation.state_forwards("arches", state)
        replayed = state.graphs[GRAPH]
        # Replayed rows hold every column, so compare only the keys the graph gives.
        for key, expected in after.items():
            if key in ("nodes", "nodegroups", "edges", "cards", "widgets"):
                self.assertEqual(set(replayed[key]), set(expected), key)
                for pk, row in expected.items():
                    stored = replayed[key][pk]
                    self.assertEqual(
                        {field: stored[field] for field in row}, row, (key, pk)
                    )
            else:
                self.assertEqual(replayed[key], expected, key)


class PublicationTailTests(SimpleTestCase):
    def test_every_non_empty_diff_publishes_and_moves_resources(self):
        before = _graph()
        after = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        names = _names(changes_for_graph(before, after, PUBLICATION_ID))
        self.assertEqual(names[-2:], ["PublishGraph", "SetResourcePublication"])

    def test_the_publication_is_the_one_the_graph_was_read_from(self):
        previous_publication_id = str(uuid.uuid4())
        before = dict(_graph(), publication_id=previous_publication_id)
        after = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        publish, move = changes_for_graph(before, after, PUBLICATION_ID)[-2:]
        for operation in (publish, move):
            self.assertEqual(operation.publication_id, PUBLICATION_ID)
            self.assertEqual(operation.previous_publication_id, previous_publication_id)
        self.assertFalse(publish.updates_in_place)

    def test_an_unchanged_publication_id_updates_in_place(self):
        before = dict(_graph(), publication_id=PUBLICATION_ID)
        after = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        publish = changes_for_graph(before, after, PUBLICATION_ID)[-2]
        self.assertTrue(publish.updates_in_place)
        self.assertTrue(publish.reversible)


class DeleteNodeGroupStateTests(SimpleTestCase):
    def test_state_loses_everything_the_database_cascade_takes(self):
        from arches.db.package_migrations.operations.nodegroup import DeleteNodeGroup

        card = str(uuid.uuid4())
        edge = str(uuid.uuid4())
        widget = str(uuid.uuid4())
        state = PackageState()
        state.add_graph(
            _graph(
                nodes=[_node()],
                nodegroups=[{"nodegroupid": NODEGROUP}],
                cards=[{"cardid": card, "nodegroup_id": NODEGROUP}],
                edges=[{"edgeid": edge, "domainnode_id": NODE, "rangenode_id": NODE}],
                cards_x_nodes_x_widgets=[{"id": widget, "card_id": card}],
            )
        )

        DeleteNodeGroup(graphid=GRAPH, pk=NODEGROUP).state_forwards("arches", state)

        graph = state.graphs[GRAPH]
        for collection in ("nodegroups", "nodes", "cards", "edges", "widgets"):
            self.assertEqual(graph[collection], {}, collection)


class MisparentedTileTests(SimpleTestCase):
    def test_reparented_nodegroup_deletes_misparented_tiles(self):
        before = _graph(
            nodegroups=[
                {"nodegroupid": NODEGROUP, "parentnodegroup_id": str(uuid.uuid4())}
            ]
        )
        after = _graph(
            nodegroups=[
                {"nodegroupid": NODEGROUP, "parentnodegroup_id": str(uuid.uuid4())}
            ]
        )

        operation_names = _names(changes_for_graph(before, after, PUBLICATION_ID))

        self.assertIn("DeleteMisparentedTiles", operation_names)
        self.assertLess(
            operation_names.index("AlterNodeGroup"),
            operation_names.index("DeleteMisparentedTiles"),
        )

    def test_deleted_nodegroup_only_deletes_its_tiles(self):
        before = _graph(
            nodegroups=[
                {"nodegroupid": NODEGROUP, "parentnodegroup_id": str(uuid.uuid4())}
            ]
        )

        operation_names = _names(changes_for_graph(before, _graph(), PUBLICATION_ID))

        self.assertNotIn("DeleteMisparentedTiles", operation_names)
        self.assertIn("DeleteTilesForNodeGroup", operation_names)


class CascadeOrderTests(SimpleTestCase):
    def _positions(self, operations):
        return [
            (type(operation).__name__, str(getattr(operation, "pk", "")))
            for operation in operations
        ]

    def test_a_child_moved_off_a_deleted_parent_moves_before_the_delete(self):
        parent_id, child_id, new_parent_id = (
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        )
        before = _graph(
            nodegroups=[
                {"nodegroupid": parent_id},
                {"nodegroupid": child_id, "parentnodegroup_id": parent_id},
                {"nodegroupid": new_parent_id},
            ]
        )
        after = _graph(
            nodegroups=[
                {"nodegroupid": child_id, "parentnodegroup_id": new_parent_id},
                {"nodegroupid": new_parent_id},
            ]
        )

        positions = self._positions(changes_for_graph(before, after, PUBLICATION_ID))

        self.assertLess(
            positions.index(("AlterNodeGroup", child_id)),
            positions.index(("DeleteNodeGroup", parent_id)),
        )

    def test_an_edge_moved_onto_a_deleted_edges_pair_waits_for_that_delete(self):
        deleted_node_id, kept_node_id, range_node_id = (
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        )
        deleted_edge_id, moved_edge_id = str(uuid.uuid4()), str(uuid.uuid4())
        nodes = [
            _node(nodeid=deleted_node_id, alias="deleted", name="deleted"),
            _node(nodeid=kept_node_id, alias="kept", name="kept"),
            _node(nodeid=range_node_id, alias="range", name="range"),
        ]
        before = _graph(
            nodes=nodes,
            edges=[
                {
                    "edgeid": deleted_edge_id,
                    "domainnode_id": kept_node_id,
                    "rangenode_id": range_node_id,
                },
                {
                    "edgeid": moved_edge_id,
                    "domainnode_id": deleted_node_id,
                    "rangenode_id": range_node_id,
                },
            ],
        )
        after = _graph(
            nodes=nodes[1:],
            edges=[
                {
                    "edgeid": moved_edge_id,
                    "domainnode_id": kept_node_id,
                    "rangenode_id": range_node_id,
                }
            ],
        )

        positions = self._positions(changes_for_graph(before, after, PUBLICATION_ID))

        self.assertLess(
            positions.index(("DeleteEdge", deleted_edge_id)),
            positions.index(("AlterEdge", moved_edge_id)),
        )
        self.assertLess(
            positions.index(("AlterEdge", moved_edge_id)),
            positions.index(("DeleteNode", deleted_node_id)),
        )

    def test_a_node_moving_into_a_taken_name_gets_the_holder_out_of_the_way(self):
        deleted_nodegroup_id, target_nodegroup_id, other_nodegroup_id = (
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        )
        moving_node_id, holder_node_id = str(uuid.uuid4()), str(uuid.uuid4())
        nodegroups = [
            {"nodegroupid": target_nodegroup_id},
            {"nodegroupid": other_nodegroup_id},
        ]
        before = _graph(
            nodegroups=nodegroups + [{"nodegroupid": deleted_nodegroup_id}],
            nodes=[
                _node(
                    nodeid=moving_node_id,
                    name="Survey Date",
                    alias="moving",
                    nodegroup_id=deleted_nodegroup_id,
                ),
                _node(
                    nodeid=holder_node_id,
                    name="Survey Date",
                    alias="holder",
                    nodegroup_id=target_nodegroup_id,
                ),
            ],
        )
        after = _graph(
            nodegroups=nodegroups,
            nodes=[
                _node(
                    nodeid=moving_node_id,
                    name="Survey Date",
                    alias="moving",
                    nodegroup_id=target_nodegroup_id,
                ),
                _node(
                    nodeid=holder_node_id,
                    name="Survey Date",
                    alias="holder",
                    nodegroup_id=other_nodegroup_id,
                ),
            ],
        )

        operations = changes_for_graph(before, after, PUBLICATION_ID)
        holder_alters = [
            operation.changes
            for operation in operations
            if type(operation).__name__ == "AlterNode"
            and str(operation.pk) == holder_node_id
        ]
        positions = self._positions(operations)
        moving_alter = positions.index(("AlterNode", moving_node_id))

        self.assertEqual(
            holder_alters,
            [
                {"name": f"_placeholder_{holder_node_id}"},
                {"nodegroup_id": other_nodegroup_id, "name": "Survey Date"},
            ],
        )
        self.assertLess(positions.index(("AlterNode", holder_node_id)), moving_alter)
        self.assertLess(
            moving_alter,
            positions.index(("DeleteNodeGroup", deleted_nodegroup_id)),
        )

    def test_a_moved_and_renamed_node_renames_after_the_deletes(self):
        deleted_nodegroup_id = str(uuid.uuid4())
        before = _graph(
            nodegroups=[
                {"nodegroupid": NODEGROUP},
                {"nodegroupid": deleted_nodegroup_id},
            ],
            nodes=[_node(nodegroup_id=deleted_nodegroup_id)],
        )
        after = _graph(
            nodegroups=[{"nodegroupid": NODEGROUP}],
            nodes=[_node(alias="renamed")],
        )

        operations = changes_for_graph(before, after, PUBLICATION_ID)
        node_alters = [
            operation.changes
            for operation in operations
            if type(operation).__name__ == "AlterNode"
        ]
        positions = self._positions(operations)

        alias_alter = [
            index
            for index, operation in enumerate(operations)
            if getattr(operation, "changes", None) == {"alias": "renamed"}
        ][0]
        delete = positions.index(("DeleteNodeGroup", deleted_nodegroup_id))

        self.assertEqual(
            node_alters, [{"nodegroup_id": NODEGROUP}, {"alias": "renamed"}]
        )
        self.assertLess(positions.index(("AlterNode", NODE)), delete)
        self.assertLess(delete, alias_alter)
