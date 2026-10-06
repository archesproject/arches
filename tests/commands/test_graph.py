# these tests can be run from the command line via
# python manage.py test tests.commands.test_graph --settings="tests.test_settings"

from django.core.management import call_command

from arches.app.models import models
from arches.app.models.graph import Graph
from tests.base_test import ArchesTestCase


class GraphCommandTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.graph = Graph.objects.create_graph(
            name="Graph Command Tests", is_resource=True
        )
        cls.graph.publish()
        cls.base_publication_id = cls.graph.publication_id

        cls.resource = models.ResourceInstance.objects.create(
            graph=cls.graph, graph_publication_id=cls.base_publication_id
        )

    def test_publish(self):
        graph = Graph.objects.get(pk=self.graph.graphid)
        graph.publish()
        new_publication_id = graph.publication_id
        self.assertNotEqual(new_publication_id, self.base_publication_id)

        with self.subTest("publish"):
            call_command("graph", "publish", graphs=str(graph.graphid))

            self.resource.refresh_from_db()

            # Test the graph has changed publication id
            self.assertNotEqual(self.base_publication_id, new_publication_id)
            # Test that the resources have not been updated and match the original publication id
            self.assertEqual(
                self.resource.graph_publication_id, self.base_publication_id
            )

        with self.subTest("publish with update_instances"):
            call_command(
                "graph",
                "publish",
                graphs=str(graph.graphid),
                update_instances=True,
            )

            self.resource.refresh_from_db()

            # Test that the resources now match the new publication id
            self.assertEqual(self.resource.graph_publication_id, new_publication_id)
