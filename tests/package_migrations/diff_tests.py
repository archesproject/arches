"""Diffing two canonical graphs. No database."""

import uuid

from django.test import SimpleTestCase

from arches.db.package_migrations.canonical import canonical_graph
from arches.db.package_migrations.diff import diff_graph
from arches.db.package_migrations.state import PackageState

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


def _names(operations):
    return [type(op).__name__ for op in operations]


class DiffGraphTests(SimpleTestCase):
    def test_no_change_produces_no_operations(self):
        graph = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        self.assertEqual(diff_graph(graph, graph), [])

    def test_new_graph_emits_create_graph_first(self):
        operations = diff_graph(None, _graph(nodes=[_node()]))
        self.assertEqual(_names(operations)[0], "CreateGraph")
        self.assertIn("CreateNode", _names(operations))

    def test_added_node_emits_create_node_with_every_field(self):
        before = _graph(nodegroups=[{"nodegroupid": NODEGROUP}])
        after = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        operations = diff_graph(before, after)
        self.assertEqual(_names(operations), ["CreateNode"])
        self.assertEqual(operations[0].fields["alias"], "survey_date")
        self.assertEqual(operations[0].fields["datatype"], "date")

    def test_changed_field_emits_alter_with_only_that_field(self):
        before = _graph(nodes=[_node()])
        after = _graph(nodes=[_node(datatype="concept")])
        operations = diff_graph(before, after)
        self.assertEqual(_names(operations), ["AlterNode"])
        self.assertEqual(operations[0].changes, {"datatype": "concept"})

    def test_removed_node_emits_delete(self):
        before = _graph(nodes=[_node()])
        after = _graph()
        self.assertEqual(_names(diff_graph(before, after)), ["DeleteNode"])

    def test_graph_metadata_change_emits_alter_graph(self):
        before = _graph()
        after = _graph(subtitle={"en": "new"})
        operations = diff_graph(before, after)
        self.assertEqual(_names(operations), ["AlterGraph"])
        self.assertNotIn("graphid", operations[0].changes)

    def test_creates_run_nodegroup_before_node(self):
        """A node references its nodegroup, so the nodegroup must exist first."""
        after = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        names = _names(diff_graph(_graph(), after))
        self.assertLess(names.index("CreateNodeGroup"), names.index("CreateNode"))

    def test_deletes_run_before_creates_and_in_reverse_order(self):
        other_node = str(uuid.uuid4())
        before = _graph(nodes=[_node()], nodegroups=[{"nodegroupid": NODEGROUP}])
        after = _graph(nodes=[_node(nodeid=other_node)])
        names = _names(diff_graph(before, after))
        self.assertLess(names.index("DeleteNode"), names.index("CreateNode"))
        self.assertLess(names.index("DeleteNode"), names.index("DeleteNodeGroup"))

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
        for operation in diff_graph(before, after):
            operation.state_forwards("arches", state)
        self.assertEqual(state.graphs[GRAPH], after)
