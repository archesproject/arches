from arches.app.models import models
from arches.app.utils.resource_instance_data import (
    move_resources_to_publication,
    reshape_tiles,
)

from tests.tasks_tests import ResourceInstanceDataTestCase


class ResourceInstanceDataTests(ResourceInstanceDataTestCase):
    def _publish_with_node_deleted(self):
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

    def test_moves_resources_onto_the_new_publication(self):
        resource_instance = models.ResourceInstance.objects.create(
            graph=self.test_graph
        )
        models.TileModel.objects.create(
            resourceinstance=resource_instance,
            data={str(self.concept_node_id): "DUMMY DATA"},
            sortorder=0,
        )
        initial, updated = self._publish_with_node_deleted()

        reshape_tiles(initial, updated)
        moved = move_resources_to_publication(initial, updated)

        self.assertEqual(moved, 1)
        resource_instance.refresh_from_db()
        self.assertEqual(
            str(resource_instance.graph_publication_id), updated["publication_id"]
        )

    def test_prunes_deleted_node_from_provisionaledits(self):
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

        reshape_tiles(initial, updated)

        tile.refresh_from_db()
        self.assertNotIn(str(self.concept_node_id), tile.data)
        self.assertNotIn(
            str(self.concept_node_id),
            tile.provisionaledits[str(self.user.pk)]["value"],
            "deleted node must be pruned from provisionaledits too",
        )
