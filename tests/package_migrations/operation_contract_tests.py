"""Contract tests covering every package migration operation at once.

No database. These catch the class of defect that shipped in the first attempt:
a codegen kwarg that is not an __init__ parameter is silently dropped by
OperationWriter, producing a migration file that imports cleanly and does
nothing.
"""

import uuid

from django.db.migrations.writer import OperationWriter
from django.test import SimpleTestCase
from django.utils.inspect import get_func_args

from arches.db.package_migrations import operations as ops
from arches.db.package_migrations.operations.base import PackageOperation

GRAPH = str(uuid.uuid4())
NODE = str(uuid.uuid4())
NODEGROUP = str(uuid.uuid4())
EDGE = str(uuid.uuid4())
CARD = str(uuid.uuid4())
WIDGET = str(uuid.uuid4())
PUB = str(uuid.uuid4())


def _noop(value, tile):
    return value


SAMPLES = [
    ops.CreateGraph(fields={"graphid": GRAPH, "name": {"en": "G"}, "slug": "g"}),
    ops.AlterGraph(graphid=GRAPH, changes={"subtitle": {"en": "s"}}),
    ops.CreateNodeGroup(graphid=GRAPH, fields={"nodegroupid": NODEGROUP}),
    ops.AlterNodeGroup(
        graphid=GRAPH, nodegroupid=NODEGROUP, changes={"cardinality": "n"}
    ),
    ops.DeleteNodeGroup(graphid=GRAPH, pk=NODEGROUP),
    ops.CreateNode(
        graphid=GRAPH,
        fields={
            "nodeid": NODE,
            "name": {"en": "N"},
            "datatype": "string",
            "istopnode": False,
            "alias": "n",
        },
    ),
    ops.AlterNode(graphid=GRAPH, nodeid=NODE, changes={"datatype": "concept"}),
    ops.DeleteNode(graphid=GRAPH, pk=NODE),
    ops.CreateEdge(
        graphid=GRAPH,
        fields={"edgeid": EDGE, "domainnode_id": NODE, "rangenode_id": NODE},
    ),
    ops.AlterEdge(graphid=GRAPH, edgeid=EDGE, changes={"ontologyproperty": "P1"}),
    ops.DeleteEdge(graphid=GRAPH, pk=EDGE),
    ops.CreateCard(graphid=GRAPH, fields={"cardid": CARD, "nodegroup_id": NODEGROUP}),
    ops.AlterCard(graphid=GRAPH, cardid=CARD, changes={"visible": False}),
    ops.DeleteCard(graphid=GRAPH, pk=CARD),
    ops.CreateCardXNodeXWidget(
        graphid=GRAPH,
        fields={"id": WIDGET, "card_id": CARD, "node_id": NODE, "widget_id": WIDGET},
    ),
    ops.AlterCardXNodeXWidget(graphid=GRAPH, id=WIDGET, changes={"visible": False}),
    ops.DeleteCardXNodeXWidget(graphid=GRAPH, pk=WIDGET),
    ops.BackfillNodeData(nodegroup_id=NODEGROUP, nodeid=NODE),
    ops.RemoveNodeData(nodegroup_id=NODEGROUP, nodeid=NODE),
    ops.CoerceNodeData(nodegroup_id=NODEGROUP, nodeid=NODE, converter=_noop),
    ops.DeleteTilesForNodeGroup(nodegroup_id=NODEGROUP),
    ops.PublishGraph(graphid=GRAPH, publication_id=PUB),
    ops.RepointResourceInstances(
        graphid=GRAPH, from_publication_id=PUB, to_publication_id=PUB
    ),
    ops.RefreshDraftGraph(graphid=GRAPH),
    ops.RunPackagePython(code=_noop),
]


class OperationContractTests(SimpleTestCase):
    def test_every_exported_operation_has_a_sample(self):
        exported = {n for n in ops.__all__ if n != "PackageOperation"}
        covered = {type(op).__name__ for op in SAMPLES}
        self.assertEqual(
            exported,
            covered,
            "every exported operation needs a sample in this contract test",
        )

    def test_deconstruct_kwargs_are_all_init_parameters(self):
        """OperationWriter silently drops any kwarg that is not an __init__
        parameter, so a mismatch produces a migration file that does nothing."""
        for op in SAMPLES:
            with self.subTest(op=type(op).__name__):
                _name, args, kwargs = op.deconstruct()
                init_params = set(get_func_args(op.__init__))
                self.assertEqual(args, [])
                self.assertTrue(
                    set(kwargs) <= init_params,
                    "%s emits %s which are not __init__ parameters"
                    % (type(op).__name__, set(kwargs) - init_params),
                )

    def test_deconstruct_emits_every_parameter(self):
        """Including defaulted ones, so a committed migration is self-describing."""
        for op in SAMPLES:
            with self.subTest(op=type(op).__name__):
                _name, _args, kwargs = op.deconstruct()
                expected = set(get_func_args(op.__init__))
                self.assertEqual(set(kwargs), expected)

    def test_operations_serialize(self):
        for op in SAMPLES:
            with self.subTest(op=type(op).__name__):
                rendered, imports = OperationWriter(op, indentation=0).serialize()
                self.assertIn(type(op).__name__, rendered)
                self.assertTrue(
                    any("package_migrations.operations" in i for i in imports),
                    imports,
                )

    def test_reversible_operations_implement_database_backwards(self):
        for op in SAMPLES:
            with self.subTest(op=type(op).__name__):
                if not op.reversible:
                    continue
                self.assertIsNot(
                    type(op).database_backwards,
                    PackageOperation.database_backwards,
                    "%s claims reversible but inherits the raising base"
                    % type(op).__name__,
                )

    def test_describe_and_name_fragment(self):
        for op in SAMPLES:
            with self.subTest(op=type(op).__name__):
                self.assertTrue(op.describe())
                self.assertTrue(op.migration_name_fragment)

    def test_no_operation_branches_on_a_datatype(self):
        """Datatype behaviour belongs to DDataType and the datatype factory.

        An operation branching on a datatype name hardcodes that knowledge in the
        migration layer and rots when a datatype gains post-save behaviour.
        """
        import pathlib

        package = pathlib.Path(ops.__file__).parent
        offenders = []
        for path in sorted(package.glob("*.py")):
            for lineno, line in enumerate(path.read_text().splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#") or '"""' in stripped:
                    continue
                if "datatype ==" in stripped or "datatype in (" in stripped:
                    offenders.append("%s:%s" % (path.name, lineno))
        self.assertEqual(offenders, [])
