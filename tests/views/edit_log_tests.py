from http import HTTPStatus

from django.urls import reverse

from tests.base_test import ArchesTestCase


class EditLogTests(ArchesTestCase):
    def test_resource_history_view_logged_out(self):
        response = self.client.get(reverse("edit_history"))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
