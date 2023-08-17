from django.urls import reverse
from django.test.client import Client

from tests.base_test import ArchesTestCase


class ConceptTests(ArchesTestCase):
    def test_get_collection(self):
        client = Client()
        client.login(username="admin", password="admin")

        collection_concept_id = "00000000-0000-0000-0000-000000000005"
        response = client.get(reverse("concept", kwargs={"conceptid": collection_concept_id}))

        self.assertEqual(response.status_code, 404)
