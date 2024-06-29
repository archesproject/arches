import io
import os

from django.conf import settings
from django.core import management
from django.urls import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.utils import captured_stdout

from arches.controlledlists.models import List, ListItem, ListItemValue
from arches.app.utils.skos import SKOSReader
from tests.base_test import ArchesTestCase

# Change TEST_ROOT context for just Controlled Lists
from arches.settings import ROOT_DIR

TEST_ROOT = os.path.normpath(os.path.join(ROOT_DIR, "controlledlists/tests"))


# these tests can be run from the command line via
# python manage.py test arches.controlledlists.tests.cli_tests --settings="tests.test_settings"


class ListExportPackageTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        from arches.controlledlists.tests.view_tests import ListTests

        return ListTests.setUpTestData()

    def test_export_controlled_list(self):
        file_path = os.path.join(TEST_ROOT, "controlled_lists.xlsx")
        self.addCleanup(os.remove, file_path)
        output = io.StringIO()
        # packages command does not yet fully avoid print()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="export_controlled_lists",
                dest_dir=TEST_ROOT,
                stdout=output,
            )
        self.assertTrue(os.path.exists(file_path))


class ListImportPackageTests(TestCase):

    def test_import_controlled_list(self):
        input_file = os.path.join(TEST_ROOT, "data/controlled_lists.xlsx")
        output = io.StringIO()
        # packages command does not yet fully avoid print()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="import_controlled_lists",
                source=input_file,
                stdout=output,
            )
        list_pk = "e962bdaf-8243-4fbb-bd43-39bc1f54c168"
        self.assertTrue(List.objects.filter(pk=list_pk).exists())

    ### TODO Add test for creating new language if language code not in db but found in import file


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
            "controlled_lists",
            operation="migrate_collections_to_controlled_lists",
            collections_to_migrate=["Concept Label Import Test"],
            host="http://localhost:8000/plugins/controlled-list-manager/item/",
            preferred_sort_language="en",
            overwrite=False,
            stdout=output,
        )

        self.assertTrue(List.objects.filter(name="Concept Label Import Test").exists())
        self.assertTrue(
            ListItem.objects.filter(id="89ff530a-f350-44f0-ac88-bdd8904eb57e").exists()
        )
