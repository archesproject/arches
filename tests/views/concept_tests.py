from django.urls import reverse
from django.test.client import Client
from arches.app.models.concept import get_preflabel_from_valueid

from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.views.concept_tests --settings="tests.test_settings"


class ConceptTests(ArchesTestCase):
    def test_get_collection(self):
        client = Client()
        client.login(username="admin", password="admin")

        collection_concept_id = "00000000-0000-0000-0000-000000000005"
        with self.assertLogs("django.request", level="WARNING"):
            response = client.get(
                reverse("concept", kwargs={"conceptid": collection_concept_id})
            )

        self.assertEqual(response.status_code, 404)

    def test_get_preflabel_from_valueid(self):
        # static is related to valueid
        value_id = "ac41d9be-79db-4256-b368-2f4559cfbe55"

        preflabel = get_preflabel_from_valueid(value_id, "en")["value"]

        self.assertEqual(preflabel, "is related to")
