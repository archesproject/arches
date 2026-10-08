"""Contract tests covering every package migration operation at once. No database."""

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
    ops.AlterNodeGroup(graphid=GRAPH, pk=NODEGROUP, changes={"cardinality": "n"}),
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
    ops.AlterNode(graphid=GRAPH, pk=NODE, changes={"datatype": "concept"}),
    ops.DeleteNode(graphid=GRAPH, pk=NODE),
    ops.CreateEdge(
        graphid=GRAPH,
        fields={"edgeid": EDGE, "domainnode_id": NODE, "rangenode_id": NODE},
    ),
    ops.AlterEdge(graphid=GRAPH, pk=EDGE, changes={"ontologyproperty": "P1"}),
    ops.DeleteEdge(graphid=GRAPH, pk=EDGE),
    ops.CreateCard(graphid=GRAPH, fields={"cardid": CARD, "nodegroup_id": NODEGROUP}),
    ops.AlterCard(graphid=GRAPH, pk=CARD, changes={"visible": False}),
    ops.DeleteCard(graphid=GRAPH, pk=CARD),
    ops.CreateCardXNodeXWidget(
        graphid=GRAPH,
        fields={"id": WIDGET, "card_id": CARD, "node_id": NODE, "widget_id": WIDGET},
    ),
    ops.AlterCardXNodeXWidget(graphid=GRAPH, pk=WIDGET, changes={"visible": False}),
    ops.DeleteCardXNodeXWidget(graphid=GRAPH, pk=WIDGET),
    ops.AddNodeToTiles(nodegroup_id=NODEGROUP, nodeid=NODE),
    ops.RemoveNodeFromTiles(nodegroup_id=NODEGROUP, nodeid=NODE),
    ops.DeleteTilesForNodeGroup(nodegroup_id=NODEGROUP),
    ops.PublishGraph(graphid=GRAPH, publication_id=PUB),
    ops.SetResourcePublication(graphid=GRAPH, publication_id=PUB),
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

    def test_deconstruct_emits_exactly_the_init_parameters(self):
        """OperationWriter silently drops a kwarg that is not an __init__ parameter."""
        for op in SAMPLES:
            with self.subTest(op=type(op).__name__):
                _name, args, kwargs = op.deconstruct()
                self.assertEqual(args, [])
                self.assertEqual(set(kwargs), set(get_func_args(op.__init__)))

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
                    f"{type(op).__name__} claims reversible but inherits the raising base",
                )

    def test_describe_and_name_fragment(self):
        for op in SAMPLES:
            with self.subTest(op=type(op).__name__):
                self.assertTrue(op.describe())
                self.assertTrue(op.migration_name_fragment)

    def test_no_operation_branches_on_a_datatype(self):
        """Datatype behaviour belongs to the datatype factory, not operations."""
        import pathlib

        package = pathlib.Path(ops.__file__).parent
        offenders = []
        for path in sorted(package.glob("*.py")):
            for lineno, line in enumerate(path.read_text().splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#") or '"""' in stripped:
                    continue
                if "datatype ==" in stripped or "datatype in (" in stripped:
                    offenders.append(f"{path.name}:{lineno}")
        self.assertEqual(offenders, [])
