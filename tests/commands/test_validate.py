# these tests can be run from the command line via
# python manage.py test tests.commands.test_validate --settings="tests.test_settings"

from io import StringIO

from django.core.management import call_command

from arches.app.const import IntegrityCheck
from arches.app.models.graph import Graph
from arches.app.models.models import (
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
        cls.graph.slug = "datatype_lookups"
        cls.graph.save()
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
                datatype=datatype,
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
                datatype=datatype,
                alias=datatype.pk + "-n",
                name=datatype.pk + "-n",
                istopnode=False,
                nodegroup=cls.nodegroup_n,
                graph=cls.graph,
            )
            for datatype in datatypes
        ]
        Node.objects.bulk_create(data_nodes_1 + data_nodes_n)

    def test_too_few_widget_configs(self):
        out = StringIO()
        call_command(
            "validate", codes=[IntegrityCheck.TOO_FEW_WIDGET_CONFIGS.value], stdout=out
        )
        self.assertEqual(out.getvalue().count("FAIL"), 1)
