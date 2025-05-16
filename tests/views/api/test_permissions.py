from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from arches.app.models.graph import Graph
from arches.app.models.models import ResourceInstance

from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.views.api.test_permissions --settings="tests.test_settings"


class InstancePermissionsAPITest(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.graph = Graph.objects.create_graph(
            name="INSTANCE_PERMISSIONS_TEST_GRAPH",
            is_resource=False,  # creates a nodegroup, will undo this below.
        )
        cls.graph.isresource = True
        cls.graph.resource_instance_lifecycle_id = (
            settings.DEFAULT_RESOURCE_INSTANCE_LIFECYCLE_ID
        )
        cls.graph.save(validate=False)

        cls.resource = ResourceInstance.objects.create(graph=cls.graph)

    def test_get_with_anonymous_user(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                reverse("api_instance_permissions"),
                QUERY_STRING=f"resourceinstanceid={self.resource.pk}",
            )
        resource_selects = [
            q for q in queries if q["sql"].startswith('SELECT "resource_instances"')
        ]
        self.assertEqual(len(resource_selects), 1, list(queries))
        self.assertEqual(
            response.content.decode(), '{"delete": true, "edit": true, "read": true}'
        )

    def test_get_with_resource_editor_role(self):
        editor_group = Group.objects.get(name="Resource Editor")
        test_user = User.objects.create()
        test_user.groups.add(editor_group)
        self.client.force_login(test_user)

        response = self.client.get(
            reverse("api_instance_permissions"),
            QUERY_STRING=f"resourceinstanceid={self.resource.pk}",
        )

        self.assertEqual(
            response.content.decode(), '{"delete": true, "edit": true, "read": true}'
        )
