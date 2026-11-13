# these tests can be run from the command line via
# python manage.py test tests.commands.test_validate --settings="tests.test_settings"

from io import StringIO

from django.core.management import call_command

from arches.app.const import IntegrityCheck
from arches.app.models.graph import Graph
from arches.app.models.models import (
    CardModel,
    CardXNodeXWidget,
    DDataType,
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

        node_widgets = [
            CardXNodeXWidget(
                node=node,
                widget_id=cls.find_default_widget_id(node, datatypes),
                card=node.nodegroup.cardmodel_set.all()[0],
            )
            for node in [n for n in nodes if n.datatype != "semantic"]
        ]
        CardXNodeXWidget.objects.bulk_create(node_widgets)

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
        call_command(
            "validate", codes=[IntegrityCheck.NO_WIDGETS.value], stdout=out
        )
        self.assertIn("PASS", out.getvalue())

    def test_no_widgets_reported(self):
        """Nodes missing a widget record are reported as failures."""
        card = CardModel.objects.get(graph=self.graph, nodegroup=self.nodegroup_1)
        CardXNodeXWidget.objects.filter(card=card).delete()
        out = StringIO()
        call_command(
            "validate", codes=[IntegrityCheck.NO_WIDGETS.value], stdout=out
        )
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
            self.assertIsNotNone(widget, f"No widget created for node with datatype {dt.pk}")
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
            CardXNodeXWidget.objects.filter(card=card).values_list("sortorder", flat=True)
        )
        self.assertFalse(any(s is None for s in sortorders), "NULL sortorder after backfill")
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
