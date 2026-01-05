import os
import json

from django.test import RequestFactory, TestCase

from arches.app.models import models
from arches.app.tasks import package_load_complete
from arches.app.views.notifications import NotificationView


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


class NotificationViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = models.User.objects.get(username="admin")
        notifs = []
        user_x_notifs = []
        for idx in range(100):
            notif = models.Notification(
                message=f"Test notification {idx+1}",
                context={"index": idx + 1},
            )
            notifs.append(notif)
            user_x_notif = models.UserXNotification(
                recipient=cls.user,
                notif=notif,
                isread=(idx % 2 == 0),  # Mark even indexed notifications as read
            )
            user_x_notifs.append(user_x_notif)
        models.Notification.objects.bulk_create(notifs)
        models.UserXNotification.objects.bulk_create(user_x_notifs)

    def test_notification_pagination_unread(self):
        page_size = 25
        page = 1
        unread_only = True
        factory = RequestFactory()
        request = factory.get(
            "/get_notifications/",
            {
                "unread_only": unread_only,
                "page": page,
                "items": page_size,
            },
        )
        request.user = self.user
        response = NotificationView.as_view()(request)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("notifications", data)
        self.assertIn("paginator", data)
        paginator = data["paginator"]
        self.assertEqual(paginator["current_page"], page)
        self.assertEqual(paginator["results_per_page"], page_size)
        self.assertEqual(paginator["has_next"], True)
        self.assertEqual(
            paginator["total_pages"], 2
        )  # 50 unread notifications, 25 per page
        self.assertEqual(paginator["total_notifications"], 100)
        self.assertEqual(paginator["unread_notifications"], 50)

    def test_notification_pagination_all(self):
        page_size = 25
        page = 1
        factory = RequestFactory()
        request = factory.get(
            "/get_notifications/",
            {
                "page": page,
                "items": page_size,
                # No unread_only parameter to get all notifications
            },
        )
        request.user = self.user
        response = NotificationView.as_view()(request)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("notifications", data)
        self.assertIn("paginator", data)
        paginator = data["paginator"]
        self.assertEqual(paginator["current_page"], page)
        self.assertEqual(paginator["results_per_page"], page_size)
        self.assertEqual(paginator["has_next"], True)
        self.assertEqual(
            paginator["total_pages"], 4
        )  # 100 total notifications, 25 per page
        self.assertEqual(paginator["total_notifications"], 100)
        self.assertEqual(paginator["unread_notifications"], 50)

    def test_notification_no_pagination(self):
        factory = RequestFactory()
        request = factory.get("/get_notifications/")
        request.user = self.user
        response = NotificationView.as_view()(request)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("notifications", data)
        self.assertNotIn("paginator", data)
