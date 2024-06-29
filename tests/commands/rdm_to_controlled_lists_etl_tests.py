import io
from django.core import management
from django.urls import reverse
from django.test.client import Client

from arches.app.models.models import (
    ControlledList,
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    ControlledListItemValue,
    DValueType,
    Language,
)
from arches.app.utils.skos import SKOSReader

from tests.base_test import ArchesTestCase


# these tests can be run from the command line via
# python manage.py test tests.commands.rdm_to_controlled_lists_etl_tests --settings="tests.test_settings"


class RDMToControlledListsETLTests(ArchesTestCase):

    @classmethod
    def setUpTestData(cls):

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/data/concept_label_test_collection.xml")
        ret = skos.save_concepts_from_skos(rdf)

        client = Client()
        client.login(username="admin", password="admin")
        response = client.get(
            reverse(
                "make_collection",
                kwargs={"conceptid": "7c90899a-dbe9-4574-9175-e69481a80b3c"},
            )
        )

    def test_migrate_collections_to_controlled_lists(self):
        output = io.StringIO()
        management.call_command(
            "etl_processes",
            operation="migrate_collections_to_controlled_lists",
            collections_to_migrate=["Concept Label Import Test"],
            host="http://localhost:8000/plugins/controlled-list-manager/item/",
            preferred_sort_language="en",
            overwrite=False,
            stdout=output,
        )

        self.assertTrue(
            ControlledList.objects.filter(name="Concept Label Import Test").exists()
        )
        self.assertTrue(
            ControlledListItem.objects.filter(
                id="89ff530a-f350-44f0-ac88-bdd8904eb57e"
            ).exists()
        )
