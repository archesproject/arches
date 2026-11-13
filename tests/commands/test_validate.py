# these tests can be run from the command line via
# python manage.py test tests.commands.test_validate --settings="tests.test_settings"

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command

from arches.app.const import IntegrityCheck
from arches.app.models.graph import Graph
from arches.app.models.models import (
    CardModel,
    CardXNodeXWidget,
    DDataType,
    Edge,
    Node,
    NodeGroup,
)
from tests.base_test import ArchesTestCase


class ValidateTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        """This will probably be moved to a helper somewhere importable
        by arches applications, but just getting started."""

        super().setUpTestData()

        cls.graph = Graph.objects.create_graph(
            name="Datatype Lookups", is_resource=True
        )
        draft_graph = cls.graph.get_draft_graph()
        draft_graph.slug = "datatype_lookups"
        draft_graph.save()

        cls.graph.promote_draft_graph_to_active_graph()

        cls.top_node = Node.objects.create(
            graph=cls.graph, istopnode=True, datatype="semantic"
        )

        cls.grouping_node_1 = Node(
            graph=cls.graph, alias="datatypes-1", istopnode=False, datatype="semantic"
        )
        cls.nodegroup_1 = NodeGroup.objects.create(
            pk=cls.grouping_node_1.pk, grouping_node=cls.grouping_node_1
        )
        cls.grouping_node_1.nodegroup = cls.nodegroup_1
        cls.grouping_node_1.save()

        cls.grouping_node_n = Node(
            graph=cls.graph, alias="datatypes-n", istopnode=False, datatype="semantic"
        )
        cls.nodegroup_n = NodeGroup.objects.create(
            pk=cls.grouping_node_n.pk,
            grouping_node=cls.grouping_node_n,
            cardinality="n",
        )
        cls.grouping_node_n.nodegroup = cls.nodegroup_n
        cls.grouping_node_n.save()

        datatypes = DDataType.objects.all()
        data_nodes_1 = [
            Node(
                datatype=datatype.pk,
                alias=datatype.pk,
                name=datatype.pk,
                istopnode=False,
                nodegroup=cls.nodegroup_1,
                graph=cls.graph,
            )
            for datatype in datatypes
        ]
        data_nodes_n = [
            Node(
                datatype=datatype.pk,
                alias=datatype.pk + "-n",
                name=datatype.pk + "-n",
                istopnode=False,
                nodegroup=cls.nodegroup_n,
                graph=cls.graph,
            )
            for datatype in datatypes
        ]
        nodes = Node.objects.bulk_create(data_nodes_1 + data_nodes_n)

        cards = [
            CardModel(
                graph=cls.graph,
                nodegroup=nodegroup,
            )
            for nodegroup in [cls.nodegroup_1, cls.nodegroup_n]
        ]
        cards = CardModel.objects.bulk_create(cards)
        for i, card in enumerate(cards):
            card.sortorder = i
        CardModel.objects.bulk_update(cards, ["sortorder"])

        node_widgets = [
            CardXNodeXWidget(
                node=node,
                widget_id=cls.find_default_widget_id(node, datatypes),
                card=node.nodegroup.cardmodel_set.all()[0],
            )
            for node in [n for n in nodes if n.datatype != "semantic"]
        ]
        node_widgets = CardXNodeXWidget.objects.bulk_create(node_widgets)
        widgets_by_card = {}
        for w in node_widgets:
            widgets_by_card.setdefault(w.card_id, []).append(w)
        for card_widgets in widgets_by_card.values():
            for i, w in enumerate(card_widgets):
                w.sortorder = i
        CardXNodeXWidget.objects.bulk_update(node_widgets, ["sortorder"])

    @classmethod
    def find_default_widget_id(cls, node, datatypes):
        for datatype in datatypes:
            if node.datatype == datatype.pk:
                return datatype.defaultwidget_id
        return None

    def test_too_many_widgets_pass(self):
        out = StringIO()
        call_command(
            "validate", codes=[IntegrityCheck.TOO_MANY_WIDGETS.value], stdout=out
        )
        self.assertEqual(out.getvalue().count("PASS"), 1)

    # --- 1017: NO_WIDGETS ---

    def test_no_widgets_pass(self):
        """Nodes whose datatypes have a default widget, and that already have a
        widget record, do not trigger the check."""
        out = StringIO()
        call_command("validate", codes=[IntegrityCheck.NO_WIDGETS.value], stdout=out)
        self.assertIn("PASS", out.getvalue())

    def test_no_widgets_reported(self):
        """Nodes missing a widget record are reported as failures."""
        card = CardModel.objects.get(graph=self.graph, nodegroup=self.nodegroup_1)
        CardXNodeXWidget.objects.filter(card=card).delete()
        out = StringIO()
        call_command("validate", codes=[IntegrityCheck.NO_WIDGETS.value], stdout=out)
        self.assertIn("FAIL", out.getvalue())

    def test_backfill_creates_widgets_with_correct_datatype(self):
        """Fix action creates a widget record using the datatype's default widget."""
        card = CardModel.objects.get(graph=self.graph, nodegroup=self.nodegroup_1)
        CardXNodeXWidget.objects.filter(card=card).delete()

        call_command(
            "validate", fix=[IntegrityCheck.NO_WIDGETS.value], stdout=StringIO()
        )

        datatypes_with_widgets = DDataType.objects.filter(
            defaultwidget__isnull=False
        ).select_related("defaultwidget")
        for dt in datatypes_with_widgets:
            node = Node.objects.filter(
                nodegroup=self.nodegroup_1, datatype=dt.pk, source_identifier=None
            ).first()
            if node is None:
                continue
            widget = CardXNodeXWidget.objects.filter(node=node, card=card).first()
            self.assertIsNotNone(
                widget, f"No widget created for node with datatype {dt.pk}"
            )
            self.assertEqual(widget.widget_id, dt.defaultwidget_id)

    def test_backfill_sortorder_sequential_from_zero(self):
        """When a card has no existing widgets, backfilled widgets get
        consecutive sortorders starting at 0."""
        card = CardModel.objects.get(graph=self.graph, nodegroup=self.nodegroup_1)
        CardXNodeXWidget.objects.filter(card=card).delete()

        call_command(
            "validate", fix=[IntegrityCheck.NO_WIDGETS.value], stdout=StringIO()
        )

        sortorders = sorted(
            CardXNodeXWidget.objects.filter(card=card).values_list(
                "sortorder", flat=True
            )
        )
        self.assertFalse(
            any(s is None for s in sortorders), "NULL sortorder after backfill"
        )
        self.assertEqual(sortorders, list(range(len(sortorders))))

    def test_backfill_sortorder_continues_after_existing(self):
        """When a card already has widgets with explicit sortorders, backfilled
        widgets are appended after the current maximum."""
        card = CardModel.objects.get(graph=self.graph, nodegroup=self.nodegroup_1)
        existing = list(CardXNodeXWidget.objects.filter(card=card))
        for i, widget in enumerate(existing):
            widget.sortorder = i
        CardXNodeXWidget.objects.bulk_update(existing, ["sortorder"])

        # Delete the last widget to create a gap to fill.
        deleted = existing[-1]
        deleted_node = deleted.node
        deleted.delete()
        expected_sortorder = len(existing) - 1  # max remaining + 1

        call_command(
            "validate", fix=[IntegrityCheck.NO_WIDGETS.value], stdout=StringIO()
        )

        new_widget = CardXNodeXWidget.objects.get(node=deleted_node, card=card)
        self.assertEqual(new_widget.sortorder, expected_sortorder)

    def test_backfill_suggests_reexport_without_export_flag(self):
        """Without --export, the fix outputs a message suggesting manual re-export."""
        card = CardModel.objects.get(graph=self.graph, nodegroup=self.nodegroup_1)
        CardXNodeXWidget.objects.filter(card=card).delete()
        out = StringIO()
        call_command("validate", fix=[IntegrityCheck.NO_WIDGETS.value], stdout=out)
        self.assertIn("modified in the database only", out.getvalue())
        self.assertIn("datatype_lookups", out.getvalue())

    def test_backfill_export_runs_regardless_of_verbosity(self):
        """Export suggestion appears even at --verbosity=0."""
        card = CardModel.objects.get(graph=self.graph, nodegroup=self.nodegroup_1)
        CardXNodeXWidget.objects.filter(card=card).delete()
        out = StringIO()
        call_command(
            "validate",
            fix=[IntegrityCheck.NO_WIDGETS.value],
            verbosity=0,
            stdout=out,
        )
        self.assertIn("modified in the database only", out.getvalue())

    def test_backfill_export_flag_triggers_export(self):
        """With --export, packages export_graphs is invoked for the modified graph."""
        card = CardModel.objects.get(graph=self.graph, nodegroup=self.nodegroup_1)
        CardXNodeXWidget.objects.filter(card=card).delete()
        with patch("arches.management.commands.validate.call_command") as mock_cc:
            call_command(
                "validate",
                fix=[IntegrityCheck.NO_WIDGETS.value],
                export=True,
                export_dir=".",
                stdout=StringIO(),
            )
        packages_calls = [
            c for c in mock_cc.call_args_list if c.args and c.args[0] == "packages"
        ]
        self.assertEqual(len(packages_calls), 1)
        self.assertEqual(packages_calls[0].kwargs["operation"], "export_graphs")

    # --- 1018: NULL_OR_DUPLICATE_CARD_SORTORDER ---

    def test_card_sortorder_pass(self):
        """Cards with unique non-null sortorders do not trigger the check."""
        out = StringIO()
        call_command(
            "validate",
            codes=[IntegrityCheck.NULL_OR_DUPLICATE_CARD_SORTORDER.value],
            stdout=out,
        )
        self.assertIn("PASS", out.getvalue())

    def test_null_card_sortorder_reported(self):
        """A card with a NULL sortorder is reported as a failure."""
        card = CardModel.objects.get(graph=self.graph, nodegroup=self.nodegroup_1)
        card.sortorder = None
        card.save()
        out = StringIO()
        call_command(
            "validate",
            codes=[IntegrityCheck.NULL_OR_DUPLICATE_CARD_SORTORDER.value],
            stdout=out,
        )
        self.assertIn("FAIL", out.getvalue())

    def test_duplicate_card_sortorder_reported(self):
        """Two sibling cards sharing the same sortorder are reported."""
        cards = list(CardModel.objects.filter(graph=self.graph, source_identifier=None))
        for card in cards:
            card.sortorder = 0
        CardModel.objects.bulk_update(cards, ["sortorder"])
        out = StringIO()
        call_command(
            "validate",
            codes=[IntegrityCheck.NULL_OR_DUPLICATE_CARD_SORTORDER.value],
            stdout=out,
        )
        self.assertIn("FAIL", out.getvalue())

    def test_fix_card_sortorders_assigns_sequential_values(self):
        """Fix action assigns consecutive non-null sortorders within each sibling group."""
        cards = list(CardModel.objects.filter(graph=self.graph, source_identifier=None))
        for card in cards:
            card.sortorder = None
        CardModel.objects.bulk_update(cards, ["sortorder"])

        call_command(
            "validate",
            fix=[IntegrityCheck.NULL_OR_DUPLICATE_CARD_SORTORDER.value],
            stdout=StringIO(),
        )

        sortorders = sorted(
            CardModel.objects.filter(
                graph=self.graph, source_identifier=None
            ).values_list("sortorder", flat=True)
        )
        self.assertFalse(any(s is None for s in sortorders), "NULL sortorder after fix")
        self.assertEqual(sortorders, list(range(len(sortorders))))

    # --- 1021: NULL_OR_DUPLICATE_WIDGET_SORTORDER ---

    def test_widget_sortorder_pass(self):
        """Widgets with unique non-null sortorders per card do not trigger the check."""
        out = StringIO()
        call_command(
            "validate",
            codes=[IntegrityCheck.NULL_OR_DUPLICATE_WIDGET_SORTORDER.value],
            stdout=out,
        )
        self.assertIn("PASS", out.getvalue())

    def test_null_widget_sortorder_reported(self):
        """A widget with a NULL sortorder is reported as a failure."""
        card = CardModel.objects.get(graph=self.graph, nodegroup=self.nodegroup_1)
        widget = CardXNodeXWidget.objects.filter(card=card).first()
        widget.sortorder = None
        widget.save()
        out = StringIO()
        call_command(
            "validate",
            codes=[IntegrityCheck.NULL_OR_DUPLICATE_WIDGET_SORTORDER.value],
            stdout=out,
        )
        self.assertIn("FAIL", out.getvalue())

    def test_duplicate_widget_sortorder_reported(self):
        """Two widgets in the same card sharing a sortorder are reported."""
        card = CardModel.objects.get(graph=self.graph, nodegroup=self.nodegroup_1)
        widgets = list(CardXNodeXWidget.objects.filter(card=card))
        for widget in widgets:
            widget.sortorder = 0
        CardXNodeXWidget.objects.bulk_update(widgets, ["sortorder"])
        out = StringIO()
        call_command(
            "validate",
            codes=[IntegrityCheck.NULL_OR_DUPLICATE_WIDGET_SORTORDER.value],
            stdout=out,
        )
        self.assertIn("FAIL", out.getvalue())

    def test_fix_widget_sortorders_assigns_sequential_values(self):
        """Fix action assigns consecutive non-null sortorders within each card."""
        card = CardModel.objects.get(graph=self.graph, nodegroup=self.nodegroup_1)
        widgets = list(CardXNodeXWidget.objects.filter(card=card))
        for widget in widgets:
            widget.sortorder = None
        CardXNodeXWidget.objects.bulk_update(widgets, ["sortorder"])

        call_command(
            "validate",
            fix=[IntegrityCheck.NULL_OR_DUPLICATE_WIDGET_SORTORDER.value],
            stdout=StringIO(),
        )

        sortorders = sorted(
            CardXNodeXWidget.objects.filter(card=card).values_list(
                "sortorder", flat=True
            )
        )
        self.assertFalse(any(s is None for s in sortorders), "NULL sortorder after fix")
        self.assertEqual(sortorders, list(range(len(sortorders))))


# --- 1019: NULL_OR_DUPLICATE_NODE_SORTORDER ---


class NodeSortorderTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        """Create a graph with two sibling non-root nodes connected via Edges,
        both initially having valid unique sortorders."""

        super().setUpTestData()

        cls.node_graph = Graph.objects.create_graph(
            name="Node Sortorder Test", is_resource=True
        )
        draft = cls.node_graph.get_draft_graph()
        draft.slug = "node_sortorder_test"
        draft.save()
        cls.node_graph.promote_draft_graph_to_active_graph()

        # Root node (no Edge points to it, so NULL/duplicate sortorder is not an issue)
        cls.parent_node = Node.objects.create(
            graph=cls.node_graph,
            alias="ns-parent",
            name="ns-parent",
            datatype="semantic",
            istopnode=True,
        )

        # Two sibling child nodes with valid, unique sortorders.
        # Non-top nodes require a nodegroup (constraint: has_nodegroup_or_istopnode),
        # so create each NodeGroup first using the node's PK, then assign and save.
        cls.child_node_a = Node(
            graph=cls.node_graph,
            alias="ns-child-a",
            name="ns-child-a",
            datatype="semantic",
            istopnode=False,
            sortorder=0,
        )
        cls.nodegroup_a = NodeGroup.objects.create(
            pk=cls.child_node_a.pk, grouping_node=cls.child_node_a
        )
        cls.child_node_a.nodegroup = cls.nodegroup_a
        cls.child_node_a.save()

        cls.child_node_b = Node(
            graph=cls.node_graph,
            alias="ns-child-b",
            name="ns-child-b",
            datatype="semantic",
            istopnode=False,
            sortorder=1,
        )
        cls.nodegroup_b = NodeGroup.objects.create(
            pk=cls.child_node_b.pk, grouping_node=cls.child_node_b
        )
        cls.child_node_b.nodegroup = cls.nodegroup_b
        cls.child_node_b.save()

        # Edges make child_a and child_b siblings (same domainnode = parent)
        Edge.objects.create(
            domainnode=cls.parent_node,
            rangenode=cls.child_node_a,
            graph=cls.node_graph,
        )
        Edge.objects.create(
            domainnode=cls.parent_node,
            rangenode=cls.child_node_b,
            graph=cls.node_graph,
        )

    def test_node_sortorder_pass(self):
        """Non-root sibling nodes with unique non-null sortorders do not trigger the check."""
        out = StringIO()
        call_command(
            "validate",
            codes=[IntegrityCheck.NULL_OR_DUPLICATE_NODE_SORTORDER.value],
            stdout=out,
        )
        self.assertIn("PASS", out.getvalue())

    def test_null_node_sortorder_reported(self):
        """A non-root node with a NULL sortorder is reported as a failure."""
        Node.objects.filter(pk=self.child_node_a.pk).update(sortorder=None)
        out = StringIO()
        call_command(
            "validate",
            codes=[IntegrityCheck.NULL_OR_DUPLICATE_NODE_SORTORDER.value],
            stdout=out,
        )
        self.assertIn("FAIL", out.getvalue())

    def test_duplicate_node_sortorder_reported(self):
        """Sibling nodes sharing a sortorder are reported."""
        Node.objects.filter(pk__in=[self.child_node_a.pk, self.child_node_b.pk]).update(
            sortorder=0
        )
        out = StringIO()
        call_command(
            "validate",
            codes=[IntegrityCheck.NULL_OR_DUPLICATE_NODE_SORTORDER.value],
            stdout=out,
        )
        self.assertIn("FAIL", out.getvalue())

    def test_fix_node_sortorders_assigns_sequential_values(self):
        """Fix action assigns consecutive non-null sortorders within each sibling group."""
        Node.objects.filter(pk__in=[self.child_node_a.pk, self.child_node_b.pk]).update(
            sortorder=None
        )

        call_command(
            "validate",
            fix=[IntegrityCheck.NULL_OR_DUPLICATE_NODE_SORTORDER.value],
            stdout=StringIO(),
        )

        sortorders = sorted(
            Node.objects.filter(
                pk__in=[self.child_node_a.pk, self.child_node_b.pk]
            ).values_list("sortorder", flat=True)
        )
        self.assertFalse(any(s is None for s in sortorders), "NULL sortorder after fix")
        self.assertEqual(sortorders, list(range(len(sortorders))))
