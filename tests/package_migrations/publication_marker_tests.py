"""Pins the behaviour that tile-data operations select on content, not on
resource_instances.graph_publication_id.

ResourceInstance.save() unconditionally re-stamps graph_publication to the
graph's CURRENT publication (models.py:1548), so between a modeler publishing and
ops running a migration, any record a curator touches is stamped as the new
version while its tile data is still the old shape. A migration that filtered on
that column would silently skip exactly those records.
"""

from unittest.mock import patch

from arches.app.models import models
from arches.app.models.resource import Resource

from tests.tasks_tests import UpdateResourceInstanceDataTaskTests


class PublicationMarkerTests(UpdateResourceInstanceDataTaskTests):
    @patch("arches.app.tasks.notify_completion")
    def test_ordinary_saves_restamp_the_publication_marker(self, mock_notify):
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
            "ResourceInstance.save() must re-stamp; if this ever stops being true, "
            "revisit D5 (content-addressed tile selection).",
        )

        models.ResourceInstance.objects.filter(pk=resource_instance.pk).update(
            graph_publication_id=old_publication_id
        )
        Resource.objects.get(pk=resource_instance.pk).save(index=False)
        resource_instance.refresh_from_db()
        self.assertEqual(
            str(resource_instance.graph_publication_id), new_publication_id
        )

    @patch("arches.app.tasks.notify_completion")
    def test_tile_save_does_not_restamp_the_resource(self, mock_notify):
        """Counterpart to the above: tile.save() does NOT reach
        ResourceInstance.save(), so the repoint loop in
        update_resource_instance_data_based_on_graph_diff is not defeated by it.
        """
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
