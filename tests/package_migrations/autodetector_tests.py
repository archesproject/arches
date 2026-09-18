"""Detecting what changed between two graph states. No database."""

import uuid

from django.test import SimpleTestCase

from arches.db.package_migrations.state import PackageState, canonical_graph
from arches.db.package_migrations.autodetector import changes_for_graph

GRAPH = str(uuid.uuid4())
NODEGROUP = str(uuid.uuid4())
NODE = str(uuid.uuid4())


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
    """Names minus the publication tail every non-empty diff appends."""
    return [n for n in _names(operations) if n not in PUBLICATION]


class DiffGraphTests(SimpleTestCase):
    def test_no_change_produces_no_operations(self):
        graph = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        self.assertEqual(changes_for_graph(graph, graph), [])

    def test_new_graph_emits_create_graph_first(self):
        operations = changes_for_graph(None, _graph(nodes=[_node()]))
        self.assertEqual(_names(operations)[0], "CreateGraph")
        self.assertIn("CreateNode", _names(operations))

    def test_added_node_emits_create_node_with_every_field(self):
        before = _graph(nodegroups=[{"nodegroupid": NODEGROUP}])
        after = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        operations = changes_for_graph(before, after)
        self.assertEqual(_structural(operations), ["CreateNode", "AddNodeToTiles"])
        self.assertEqual(operations[0].fields["alias"], "survey_date")
        self.assertEqual(operations[0].fields["datatype"], "date")

    def test_changed_field_emits_alter_with_only_that_field(self):
        before = _graph(nodes=[_node()])
        after = _graph(nodes=[_node(datatype="concept")])
        operations = changes_for_graph(before, after)
        self.assertEqual(_structural(operations), ["AlterNode"])
        self.assertEqual(operations[0].changes, {"datatype": "concept"})

    def test_removed_node_emits_delete(self):
        before = _graph(nodes=[_node()])
        after = _graph()
        self.assertEqual(
            _structural(changes_for_graph(before, after)),
            ["DeleteNode", "RemoveNodeFromTiles"],
        )

    def test_graph_metadata_change_emits_alter_graph(self):
        before = _graph()
        after = _graph(subtitle={"en": "new"})
        operations = changes_for_graph(before, after)
        self.assertEqual(_structural(operations), ["AlterGraph"])
        self.assertNotIn("graphid", operations[0].changes)

    def test_creates_run_nodegroup_before_node(self):
        """A node references its nodegroup, so the nodegroup must exist first."""
        after = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        names = _structural(changes_for_graph(_graph(), after))
        self.assertLess(names.index("CreateNodeGroup"), names.index("CreateNode"))

    def test_deletes_run_before_creates_and_in_reverse_order(self):
        other_node = str(uuid.uuid4())
        before = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        after = _graph(nodes=[_node(nodeid=other_node)])
        names = _structural(changes_for_graph(before, after))
        self.assertLess(names.index("DeleteNode"), names.index("CreateNode"))
        self.assertLess(names.index("DeleteNode"), names.index("DeleteNodeGroup"))

    def test_a_key_the_committed_file_omits_is_not_a_change(self):
        """Packages exported by an older Arches carry no alias or hascustomalias.
        Reading an absent key as null emitted AlterNode(alias=None), which is
        written to disk, shipped, and only fails on the customer's database --
        Node.alias is NOT NULL."""
        complete = _node(alias="survey_date", hascustomalias=True)
        partial = {
            key: value
            for key, value in complete.items()
            if key not in ("alias", "hascustomalias")
        }
        nodegroups = [{"nodegroupid": NODEGROUP}]
        before = _graph(nodes=[complete], nodegroups=nodegroups)
        after = _graph(nodes=[partial], nodegroups=nodegroups)
        self.assertEqual(changes_for_graph(before, after), [])

    def test_diff_is_the_inverse_of_replaying_its_own_operations(self):
        """The property that makes the autodetector trustworthy: applying the
        emitted operations to the from-state must produce the to-state."""
        before = _graph(nodegroups=[{"nodegroupid": NODEGROUP}])
        after = _graph(
            nodes=[_node()],
            nodegroups=[{"nodegroupid": NODEGROUP}],
            subtitle={"en": "v2"},
        )
        state = PackageState()
        state.add_graph(before)
        for operation in changes_for_graph(before, after):
            operation.state_forwards("arches", state)
        replayed = state.graphs[GRAPH]
        # Replayed state holds every column, because that is what the rows hold
        # once created; the committed graph holds only what its author wrote, and
        # PublishGraph adds a publication the file never carries. The property
        # that matters is that the two agree wherever the file speaks. Anywhere
        # they disagree, the next diff invents a change nobody made.
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
        """Without this tail a migration mutates rows and nothing the application
        reads changes: the published snapshot keeps the old graph, resources stay
        pinned to the old publication, and the stale draft reverts the migration on
        the next Graph Designer publish."""
        before = _graph()
        after = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        names = _names(changes_for_graph(before, after))
        self.assertEqual(names[-2:], ["PublishGraph", "SetResourcePublication"])


class DeleteNodeGroupStateTests(SimpleTestCase):
    def test_state_loses_everything_the_database_cascade_takes(self):
        """The row cascade reaches nodes, cards, the widgets on those cards and the
        edges joining those nodes. State that keeps them makes the next diff emit
        deletes for rows that are already gone."""
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
