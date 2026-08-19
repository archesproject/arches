# these tests can be run from the command line via
# python manage.py test tests.commands.test_resources --settings="tests.test_settings"

import uuid
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from tests.base_test import ArchesTestCase

PRIMARY_DESCRIPTORS_FUNCTION_ID = "60000000-0000-0000-0000-000000000001"


def _make_descriptor_graph(name="Descriptor Test Graph"):
    """
    Create a published graph with a string node and a primary-descriptors
    function configured to use that node.  Returns (graph, node_group, string_node).
    """
    graph = Graph.objects.create_graph(name=name, is_resource=True)
    node_group = models.NodeGroup.objects.create()
    string_node = models.Node.objects.create(
        graph=graph,
        nodegroup=node_group,
        name="String Node",
        datatype="string",
        istopnode=False,
    )
    graph.add_node(string_node)
    edge = models.Edge.objects.create(
        graph=graph, domainnode=graph.root, rangenode=string_node
    )
    graph.add_edge(edge)
    graph.add_card(
        models.CardModel(
            graph=graph,
            nodegroup=node_group,
            description="Test Card",
        )
    )
    models.FunctionXGraph.objects.create(
        graph=graph,
        function_id=PRIMARY_DESCRIPTORS_FUNCTION_ID,
        config={
            "descriptor_types": {
                "name": {
                    "nodegroup_id": str(node_group.nodegroupid),
                    "string_template": "<String Node>",
                },
                "map_popup": {
                    "nodegroup_id": str(node_group.nodegroupid),
                    "string_template": "<String Node>",
                },
                "description": {
                    "nodegroup_id": str(node_group.nodegroupid),
                    "string_template": "<String Node>",
                },
            },
        },
    )
    user = User.objects.get(username="admin")
    graph.save(validate=False)
    graph.publish(user=user)
    return graph, node_group, string_node


def _save_resource_with_tile(graph, node_group, string_node, value="test value"):
    resource = Resource(graph=graph)
    tile = Tile(
        nodegroup=node_group,
        resourceinstance=resource,
        data={
            str(string_node.pk): {
                "en": {"value": value, "direction": "ltr"},
            }
        },
        sortorder=0,
    )
    resource.tiles.append(tile)
    resource.save(index=False)
    return resource


class CalculateDescriptorsCommandTest(ArchesTestCase):
    """Tests for `python manage.py resources calculate_descriptors`."""

    def test_descriptors_recalculated_with_force_flag(self):
        graph, node_group, string_node = _make_descriptor_graph()
        resource = _save_resource_with_tile(graph, node_group, string_node)

        # Blank out the descriptors to confirm the command repopulates them.
        Resource.objects.filter(pk=resource.pk).update(descriptors={}, name={})

        out = StringIO()
        call_command(
            "resources",
            "calculate_descriptors",
            graph=str(graph.pk),
            yes=True,
            stdout=out,
        )

        resource.refresh_from_db()
        output = out.getvalue()
        self.assertIn("Successfully recalculated", output)

        # At least the English descriptor should be populated.
        en_name = resource.descriptors.get("en", {}).get("name")
        self.assertEqual(en_name, "test value")

    def test_descriptors_recalculated_filtered_by_graph(self):
        """
        Passing --graph should restrict updates to that graph only.
        Other resources must not be modified.
        """
        graph_a, node_group_a, string_node_a = _make_descriptor_graph("Graph A")
        graph_b, node_group_b, string_node_b = _make_descriptor_graph("Graph B")

        resource_a = _save_resource_with_tile(
            graph_a, node_group_a, string_node_a, value="value A"
        )
        resource_b = _save_resource_with_tile(
            graph_b, node_group_b, string_node_b, value="value B"
        )

        # Clear both.
        Resource.objects.filter(pk__in=[resource_a.pk, resource_b.pk]).update(
            descriptors={}, name={}
        )

        call_command(
            "resources",
            "calculate_descriptors",
            graph=str(graph_a.pk),
            yes=True,
            stdout=StringIO(),
        )

        resource_a.refresh_from_db()
        resource_b.refresh_from_db()

        # Only graph_a resource should have been updated.
        self.assertEqual(resource_a.descriptors.get("en", {}).get("name"), "value A")
        self.assertEqual(resource_b.descriptors, {})

    def test_descriptors_recalculated_filtered_by_transaction(self):
        """
        Passing --transaction should restrict updates to resources that appear
        in the edit log under that transaction id.
        """
        graph, node_group, string_node = _make_descriptor_graph("Transaction Graph")
        resource = _save_resource_with_tile(graph, node_group, string_node)

        transaction_id = uuid.uuid4()
        models.EditLog.objects.create(
            resourceinstanceid=str(resource.pk),
            resourceclassid=str(graph.pk),
            transactionid=transaction_id,
            edittype="update",
        )

        # An unrelated resource that should NOT be touched.
        other_resource = _save_resource_with_tile(graph, node_group, string_node)

        Resource.objects.filter(pk__in=[resource.pk, other_resource.pk]).update(
            descriptors={}, name={}
        )

        call_command(
            "resources",
            "calculate_descriptors",
            transaction=str(transaction_id),
            yes=True,
            stdout=StringIO(),
        )

        resource.refresh_from_db()
        other_resource.refresh_from_db()

        self.assertEqual(resource.descriptors.get("en", {}).get("name"), "test value")
        self.assertEqual(other_resource.descriptors, {})

    def test_resources_without_descriptor_function_get_null_descriptors(self):
        """
        Resources whose graph has no primary-descriptors function should have
        their descriptor fields set to None for each key.
        """
        bare_graph = Graph.objects.create_graph(name="Bare Graph", is_resource=True)
        user = User.objects.get(username="admin")
        bare_graph.save(validate=False)
        bare_graph.publish(user=user)

        resource = Resource(graph=bare_graph)
        resource.save(index=False)

        Resource.objects.filter(pk=resource.pk).update(
            descriptors={
                "en": {"name": "stale", "description": "stale", "map_popup": "stale"}
            },
        )

        out = StringIO()
        call_command(
            "resources",
            "calculate_descriptors",
            graph=str(bare_graph.pk),
            yes=True,
            stdout=out,
        )

        resource.refresh_from_db()
        self.assertIn("Successfully recalculated", out.getvalue())
        en_descriptors = resource.descriptors.get("en", {})
        for key in ("name", "description", "map_popup"):
            with self.subTest(descriptor=key):
                self.assertIsNone(en_descriptors.get(key))
