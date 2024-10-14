from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from arches.app.models.graph import Graph
from arches.app.models.models import ResourceInstance

# these tests can be run from the command line via
# python manage.py test tests.views.api.test_permissions --settings="tests.test_settings"


class InstancePermissionsAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.graph = Graph.new(
            name="INSTANCE_PERMISSIONS_TEST_GRAPH",
            is_resource=True,
            author="ARCHES TEST",
        )

    def test_get(self):
        resource = ResourceInstance.objects.create(graph=self.graph)
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                reverse("api_instance_permissions"),
                QUERY_STRING=f"resourceinstanceid={resource.pk}",
            )
        resource_selects = [
            q for q in queries if q["sql"].startswith('SELECT "resource_instances"')
        ]
        self.assertEqual(len(resource_selects), 1, list(queries))
        self.assertEqual(
            response.content.decode(), '{"delete": false, "edit": false, "read": false}'
        )
