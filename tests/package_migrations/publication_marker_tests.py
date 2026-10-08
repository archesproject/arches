"""Why tile-data operations select on content rather than graph_publication_id:
ResourceInstance.save() re-stamps it to the current publication, whatever shape
the tile data is in."""

from arches.app.models import models
from arches.app.models.resource import Resource

from tests.tasks_tests import ResourceInstanceDataTestCase


class PublicationMarkerTests(ResourceInstanceDataTestCase):
    def test_ordinary_saves_restamp_the_publication_marker(self):
        resource_instance = models.ResourceInstance.objects.create(
            graph=self.test_graph
        )
        old_publication_id = str(self.test_graph.publication_id)
        self.test_graph.publish()
        new_publication_id = str(
            models.GraphModel.objects.get(pk=self.test_graph.graphid).publication_id
        )

        resource_instance.refresh_from_db()
        self.assertEqual(
            str(resource_instance.graph_publication_id), old_publication_id
        )

        models.ResourceInstance.objects.get(pk=resource_instance.pk).save()
        resource_instance.refresh_from_db()
        self.assertEqual(
            str(resource_instance.graph_publication_id),
            new_publication_id,
            "ResourceInstance.save() must re-stamp",
        )

        models.ResourceInstance.objects.filter(pk=resource_instance.pk).update(
            graph_publication_id=old_publication_id
        )
        Resource.objects.get(pk=resource_instance.pk).save(index=False)
        resource_instance.refresh_from_db()
        self.assertEqual(
            str(resource_instance.graph_publication_id), new_publication_id
        )

    def test_tile_save_does_not_restamp_the_resource(self):
        resource_instance = models.ResourceInstance.objects.create(
            graph=self.test_graph
        )
        tile = models.TileModel.objects.create(
            resourceinstance=resource_instance,
            data={str(self.concept_node_id): "DUMMY DATA"},
            sortorder=0,
        )
        old_publication_id = str(self.test_graph.publication_id)
        self.test_graph.publish()

        tile.save()

        resource_instance.refresh_from_db()
        self.assertEqual(
            str(resource_instance.graph_publication_id), old_publication_id
        )
