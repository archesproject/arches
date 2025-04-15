import uuid

from unittest.mock import patch
from arches.app.models import models as arches_models
from arches.app.models.graph import Graph
from tests.base_test import ArchesTestCase


class GraphQuerySetTests(ArchesTestCase):
    def test_create_raises_not_implemented_for_create(self):
        """
        Calling create() should raise NotImplementedError.
        """
        with self.assertRaises(NotImplementedError):
            Graph.objects.create(name="test")

    @patch("uuid.uuid4")
    def test_create_graph_is_resource_false(self, mock_uuid4):
        """
        When is_resource is False:
         - A new GraphModel is created.
         - A NodeGroup is created with the fixed UUID.
         - A CardModel is created associated with the NodeGroup and Graph.
         - A Node is created as the root node linked to both the Graph and NodeGroup.
         - The graph's publish and create_draft_graph methods are called.
        """
        fixed_uuid = uuid.UUID("00000000-0000-0000-0000-000000000001")
        mock_uuid4.return_value = fixed_uuid

        with patch.object(Graph, "publish") as publish_mock:
            with patch.object(Graph, "create_draft_graph") as create_draft_mock:

                graph = Graph.objects.create_graph(name="Graph Test", is_resource=False)

                self.assertIsNotNone(graph)
                self.assertIsInstance(graph, Graph)

                self.assertTrue(
                    arches_models.NodeGroup.objects.filter(pk=fixed_uuid).exists()
                )
                nodegroup = arches_models.NodeGroup.objects.get(pk=fixed_uuid)

                self.assertTrue(
                    arches_models.CardModel.objects.filter(
                        nodegroup=nodegroup, name="Graph Test", graph=graph
                    ).exists()
                )

                self.assertTrue(
                    arches_models.Node.objects.filter(
                        pk=fixed_uuid,
                        name="Graph Test",
                        nodegroup=nodegroup,
                        graph=graph,
                    ).exists()
                )

                publish_mock.assert_called_once()
                create_draft_mock.assert_called_once()

    @patch("uuid.uuid4")
    def test_create_graph_is_resource_true(self, mock_uuid4):
        """
        When is_resource is True:
         - A new GraphModel is created.
         - No NodeGroup or CardModel is created.
         - A Node (root node) is still created with nodegroup set to None.
         - The graph's publish and create_draft_graph methods are called.
        """
        fixed_uuid = uuid.UUID("00000000-0000-0000-0000-000000000002")
        mock_uuid4.return_value = fixed_uuid

        with patch.object(Graph, "publish") as publish_mock:
            with patch.object(Graph, "create_draft_graph") as create_draft_mock:

                graph = Graph.objects.create_graph(
                    name="Resource Graph", is_resource=True
                )

                self.assertIsNotNone(graph)
                self.assertIsInstance(graph, Graph)

                self.assertFalse(arches_models.NodeGroup.objects.filter(pk=fixed_uuid))
                self.assertFalse(arches_models.CardModel.objects.exists())

                self.assertTrue(
                    arches_models.Node.objects.filter(
                        pk=fixed_uuid,
                        name="Resource Graph",
                        graph=graph,
                        nodegroup__isnull=True,
                    ).exists()
                )

                publish_mock.assert_called_once()
                create_draft_mock.assert_called_once()

    def test_create_graph_correctly_sets_has_unpublished_changes(self):
        """
        Neither the created graph nor the draft_graph should have unpublished changes.
        """
        graph = Graph.objects.create_graph(name="Resource Graph", is_resource=True)
        self.assertFalse(graph.has_unpublished_changes)

        draft_graph = Graph.objects.get(source_identifier=graph)
        self.assertFalse(draft_graph.has_unpublished_changes)
