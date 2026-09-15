"""Tests for arches.app.utils.graph_diff.apply_graph_diff."""

from unittest.mock import patch

from arches.app.models import models
from arches.app.utils.graph_diff import apply_graph_diff

from tests.tasks_tests import UpdateResourceInstanceDataTaskTests


class ApplyGraphDiffTests(UpdateResourceInstanceDataTaskTests):
    def _publish_with_node_deleted(self):
        """Delete the concept node and republish, returning (initial, updated)."""
        initial = models.PublishedGraph.objects.get(
            publication=self.test_graph.publication, language="en"
        ).serialized_graph

        draft_graph = self.test_graph.create_draft_graph()
        draft_graph.delete_node(
            models.Node.objects.get(source_identifier_id=self.concept_node_id)
        )
        updated_graph = self.test_graph.promote_draft_graph_to_active_graph()
        updated_graph.publish()

        updated = models.PublishedGraph.objects.get(
            publication=updated_graph.publication, language="en"
        ).serialized_graph
        return initial, updated

    @patch("arches.app.tasks.notify_completion")
    def test_reports_touched_resources_and_graphs(self, mock_notify):
        resource_instance = models.ResourceInstance.objects.create(
            graph=self.test_graph
        )
        models.TileModel.objects.create(
            resourceinstance=resource_instance,
            data={str(self.concept_node_id): "DUMMY DATA"},
            sortorder=0,
        )
        initial, updated = self._publish_with_node_deleted()

        result = apply_graph_diff(initial, updated)

        self.assertIn(resource_instance.pk, result["touched_resource_instance_ids"])
        self.assertIn(str(self.test_graph.graphid), result["touched_graph_ids"])

    @patch("arches.app.tasks.notify_completion")
    def test_prunes_deleted_node_from_provisionaledits(self, mock_notify):
        """provisionaledits is keyed by the same nodeids as data.

        If a deleted node's key survives there, approving the pending edit later
        writes it back into data, and Tile.save() then raises Node.DoesNotExist
        because the node is gone -- leaving a record no curator can fix from the UI.
        """
        resource_instance = models.ResourceInstance.objects.create(
            graph=self.test_graph
        )
        tile = models.TileModel.objects.create(
            resourceinstance=resource_instance,
            data={str(self.concept_node_id): "DUMMY DATA"},
            provisionaledits={
                str(self.user.pk): {
                    "value": {str(self.concept_node_id): "PENDING DATA"},
                    "status": "review",
                    "action": "update",
                    "reviewer": None,
                    "timestamp": "2024-01-01T00:00:00.000000Z",
                    "reviewtimestamp": None,
                }
            },
            sortorder=0,
        )
        initial, updated = self._publish_with_node_deleted()

        apply_graph_diff(initial, updated)

        tile.refresh_from_db()
        self.assertNotIn(str(self.concept_node_id), tile.data)
        self.assertNotIn(
            str(self.concept_node_id),
            tile.provisionaledits[str(self.user.pk)]["value"],
            "deleted node must be pruned from provisionaledits too",
        )
