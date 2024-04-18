import uuid
import datetime

from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.test.client import Client

from arches.app.models.models import WorkflowHistory
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.views.workflow_tests --settings="tests.test_settings"


class WorkflowHistoryTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.admin = User.objects.get(username="admin")
        cls.anonymous = User.objects.get(username="anonymous")
        cls.editor = User.objects.create_user(username="editor", email="editor@resources.com", password="Test12345!")
        group = Group.objects.get(name="Resource Editor")
        group.user_set.add(cls.editor)
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.history = WorkflowHistory.objects.create(
            workflowid=str(uuid.uuid1()),
            workflowname='test-name',
            user=cls.admin,
            created=datetime.datetime.now(),
            completed=False,
            stepdata={
                "set-project-name": {
                    "componentIdLookup": {
                        "project-name": "84d0578f-6061-4015-a44d-c7b64cdb0551",
                    },
                    "stepId": "d0d644c2-3bbb-4f9c-aa52-4a4c1c544d07",
                    "locked": False,
                },
                # etc...
            },
            componentdata={
                "84d0578f-6061-4015-a44d-c7b64cdb0551": {
                    "value": {
                        "name": {
                            "tileid": str(uuid.uuid1()),
                            "value": {
                                "en": {
                                    "direction": "ltr",
                                    "value": "sample name",
                                },
                            },
                        },
                        "projectResourceId": str(uuid.uuid1()),
                        "type": {
                            "tileid": str(uuid.uuid1()),
                            "value": str(uuid.uuid1()),
                        },
                    },
                },
                # etc...
            },
        )

    def test_get_nonexistent_workflow_history(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("workflow_history", kwargs={"workflowid": uuid.uuid1()}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"{}")

    def test_get_workflow_history(self):
        self.client.force_login(self.anonymous)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.get(reverse("workflow_history", kwargs={"workflowid": str(self.history.workflowid)}))

        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Forbidden", response.content)

        self.client.force_login(self.admin)
        response = self.client.get(reverse("workflow_history", kwargs={"workflowid": str(self.history.workflowid)}))

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"sample name", response.content)

    def test_post_workflow_history(self):
        """Partial updates of componentdata and stepdata are allowed."""
        post_data = {
            "workflowid": str(self.history.workflowid),  # required
            "workflowname": 'test-name',
            "stepdata": {
                # Add a second step.
                "set-project-statement": {
                    "componentIdLookup": {
                        "project-statement": "ae8f2027-f2e1-447c-8763-125e65d4b666",
                    },
                    "stepId": "8a9d8ea7-9430-4732-9cc4-6efacf6b43b7",
                    "locked": False,
                },
            },
            "componentdata": {
                # Add a second component. Realistically these would be
                # separate requests, but test the ability of the view
                # to patch in whatever it's given.
                "ae8f2027-f2e1-447c-8763-125e65d4b666": {
                    "value": {
                        "name": {
                            "tileid": str(uuid.uuid1()),
                            "value": {
                                "en": {
                                    "direction": "ltr",
                                    "value": "sample description",
                                },
                            },
                        },
                        "projectResourceId": str(uuid.uuid1()),
                        "type": {
                            "tileid": str(uuid.uuid1()),
                            "value": str(uuid.uuid1()),
                        },
                    },
                }
            },
        }

        # Non-superuser cannot update someone else's workflow.
        self.client.force_login(self.editor)
        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(
                reverse("workflow_history", kwargs={"workflowid": str(self.history.workflowid)}),
                post_data,
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Forbidden", response.content)

        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("workflow_history", kwargs={"workflowid": str(self.history.workflowid)}),
            post_data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        # Both steps and components are present.
        self.history.refresh_from_db()
        self.assertEqual(len(self.history.stepdata), 2)
        self.assertEqual(len(self.history.componentdata), 2)

    def test_complete_workflow_history(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("workflow_history", kwargs={"workflowid": str(self.history.workflowid)}),
            {"workflowid": str(self.history.workflowid), "workflowname": 'test-name', "completed": True},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        self.history.refresh_from_db()
        self.assertTrue(self.history.completed)

    def test_no_edits_after_completed(self):
        self.history.completed = True
        self.history.save()
        self.client.force_login(self.admin)

        with self.assertLogs("django.request", level="WARNING"):
            response = self.client.post(
                reverse("workflow_history", kwargs={"workflowid": str(self.history.workflowid)}),
                {"workflowid": str(self.history.workflowid), "workflowname": "test-name", "completed": False},
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 400)
