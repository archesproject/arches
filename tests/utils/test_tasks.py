import os

from django.test import TestCase

from arches.app.models import models
from arches.app.tasks import package_load_complete

# these tests can be run from the command line via
# python manage.py test tests.utils.test_tasks.TaskTests --settings="tests.test_settings"


class TaskTests(TestCase):
    def test_package_load_complete(self):
        resource_path = os.path.join(
            "tests", "fixtures", "data", "json", "example_source_business_data.json"
        )
        package_load_complete(valid_resource_paths=[resource_path])

        notif = models.Notification.objects.all().order_by("-created").first()
        self.assertIn("salutation", notif.context)
        notif_x_user = models.UserXNotification.objects.get(notif=notif)
        self.assertEqual(notif_x_user.recipient_id, 1)
