import io
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core import management
from django.test import TestCase
from django.test.utils import captured_stdout
from django.core.management.base import CommandError

from arches.app.models.models import (
    Node,
    GraphModel,
    LoadErrors,
    ResourceInstance,
    TileModel,
    Value,
)
from arches.app.etl_modules.base_data_editor import MissingRequiredInputError

from arches.extensions.controlled_lists.models import List, ListItem, ListItemValue
from arches.extensions.controlled_lists.etl_modules.migrate_to_reference_datatype import (
    MigrateToReferenceDatatype,
)
from arches.extensions.controlled_lists.management.commands.controlled_lists import (
    Command as ControlledListsCommand,
)

from .constants import APP_ROOT, PROJECT_TEST_ROOT, TEST_PACKAGE_DIR

# these tests can be run from the command line via
# python manage.py test tests.extensions.controlled_lists.cli_tests --settings="tests.test_settings"


class PackageCommandTests(TestCase):

    def test_load_package(self):
        with captured_stdout() as stdout:
            management.call_command(
                "packages",
                [
                    "-o",
                    "load_package",
                    "-s",
                    TEST_PACKAGE_DIR,
                    "-y",
                ],
            )
        output = stdout.getvalue()
        self.assertIn("Importing controlled lists...", output)
        new_lists = List.objects.filter(name__startswith="Test Thesaurus")
        new_list = new_lists.first()
        new_list_items = new_list.list_items.filter(list_id=new_list.id)
        new_list_item_values = ListItemValue.objects.filter(
            list_item_id__in=new_list_items.all()
        )
        self.assertEqual(new_lists.count(), 1)
        self.assertEqual(new_list_items.count(), 17)
        self.assertEqual(new_list_item_values.count(), 21)


class ListExportPackageTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        from .test_views import ListTests

        return ListTests.setUpTestData()

    def test_export_controlled_list_xlsx(self):
        export_file_name = "list_xlsx_export"
        file_path = os.path.join(PROJECT_TEST_ROOT, f"{export_file_name}.xlsx")
        self.addCleanup(os.remove, file_path)
        output = io.StringIO()
        # packages command does not yet fully avoid print()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="export_controlled_lists",
                dest_dir=PROJECT_TEST_ROOT,
                file_name=export_file_name,
                controlled_lists="",
                format="xlsx",
                stdout=output,
            )
        self.assertTrue(os.path.exists(file_path))

    def test_export_controlled_single_list_skos(self):
        export_file_name = "lists_skos_export"
        file_path = os.path.join(PROJECT_TEST_ROOT, f"{export_file_name}.xml")
        self.addCleanup(os.remove, file_path)
        output = io.StringIO()
        # packages command does not yet fully avoid print()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="export_controlled_lists",
                dest_dir=PROJECT_TEST_ROOT,
                file_name=export_file_name,
                controlled_lists="list1",
                single_file=True,
                format="skos-rdf",
                stdout=output,
            )
        self.assertTrue(os.path.exists(file_path))

    def test_export_controlled_all_lists_skos(self):
        export_file_name = "all_lists_skos_export"
        file_path = os.path.join(PROJECT_TEST_ROOT, f"{export_file_name}.xml")
        self.addCleanup(os.remove, file_path)
        output = io.StringIO()
        # packages command does not yet fully avoid print()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="export_controlled_lists",
                dest_dir=PROJECT_TEST_ROOT,
                file_name=export_file_name,
                controlled_lists="",
                single_file=True,
                format="skos-rdf",
                stdout=output,
            )
        self.assertTrue(os.path.exists(file_path))

    def test_export_controlled_file_name_default_skos(self):
        file_path = os.path.join(PROJECT_TEST_ROOT, f"{'list1'}.xml")
        self.addCleanup(os.remove, file_path)
        output = io.StringIO()
        # packages command does not yet fully avoid print()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="export_controlled_lists",
                dest_dir=PROJECT_TEST_ROOT,
                file_name="list1",
                controlled_lists="",
                single_file=True,
                format="skos-rdf",
                stdout=output,
            )
        self.assertTrue(os.path.exists(file_path))

    def test_export_multi_lists_single_file_raises(self):
        output = io.StringIO()
        with captured_stdout():
            with self.assertRaises(CommandError):
                management.call_command(
                    "packages",
                    operation="export_controlled_lists",
                    dest_dir=PROJECT_TEST_ROOT,
                    file_name="invalid_export",
                    controlled_lists="list1,list2",
                    format="skos-rdf",
                    stdout=output,
                )

    def test_export_multi_lists_multi_file(self):
        output = io.StringIO()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="export_controlled_lists",
                dest_dir=PROJECT_TEST_ROOT,
                controlled_lists="list1,list2",
                format="skos-rdf",
                stdout=output,
            )
        file_path_list1 = os.path.join(PROJECT_TEST_ROOT, f"list1.xml")
        file_path_list2 = os.path.join(PROJECT_TEST_ROOT, f"list2.xml")
        self.assertTrue(os.path.exists(file_path_list1))
        self.assertTrue(os.path.exists(file_path_list2))
        self.addCleanup(os.remove, file_path_list1)
        self.addCleanup(os.remove, file_path_list2)


class ListImportPackageTests(TestCase):

    def test_import_controlled_list(self):
        input_file = os.path.join(
            PROJECT_TEST_ROOT, "fixtures", "data", "controlled_lists.xlsx"
        )
        output = io.StringIO()
        # packages command does not yet fully avoid print()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="import_controlled_lists",
                source=input_file,
                stdout=output,
            )

        self.assertEqual(List.objects.count(), 2)
        self.assertEqual(ListItem.objects.count(), 10)
        self.assertEqual(ListItemValue.objects.count(), 21)

    ### TODO Add test for creating new language if language code not in db but found in import file

    def test_import_from_skos(self):
        input_file = os.path.join(
            TEST_PACKAGE_DIR,
            "reference_data",
            "controlled_lists",
            "skos_rdf_import_example.xml",
        )
        output = io.StringIO()
        # packages command does not yet fully avoid print()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="import_controlled_lists",
                source=input_file,
                overwrite="ignore",
                stdout=output,
            )

        self.assertEqual(List.objects.count(), 1)
        self.assertEqual(ListItem.objects.count(), 17)
        self.assertEqual(ListItemValue.objects.count(), 21)
        # child1 list item should be duplicated
        child1_list_items = ListItem.objects.filter(
            uri="http://localhost:8000/fea17c9d-e9c2-4469-91f9-6519f6692625"
        )
        self.assertEqual(child1_list_items.count(), 2)
        # but those list items will have different parents
        child1_instance_1 = child1_list_items[0]
        child1_instance_2 = child1_list_items[1]
        self.assertNotEqual(child1_instance_1.parent, child1_instance_2.parent)

        # They should have distinct list item values
        self.assertNotEqual(
            child1_instance_1.list_item_values.first().pk,
            child1_instance_2.list_item_values.first().pk,
        )
        # but the values should be the same
        self.assertEqual(
            child1_instance_1.list_item_values.first().value,
            child1_instance_2.list_item_values.first().value,
        )

        # Re-run with overwrite
        with captured_stdout():
            management.call_command(
                "packages",
                operation="import_controlled_lists",
                source=input_file,
                overwrite="overwrite",
                stdout=output,
            )

        self.assertEqual(List.objects.count(), 1)
        self.assertEqual(ListItem.objects.count(), 17)
        self.assertEqual(ListItemValue.objects.count(), 21)

        # Re-run last time with duplicate
        with captured_stdout():
            management.call_command(
                "packages",
                operation="import_controlled_lists",
                source=input_file,
                overwrite="duplicate",
                stdout=output,
            )

        self.assertEqual(List.objects.count(), 2)
        self.assertEqual(ListItem.objects.count(), 34)
        self.assertEqual(ListItemValue.objects.count(), 42)

    def test_import_from_skos_via_directory(self):
        input_dir = os.path.join(
            TEST_PACKAGE_DIR,
        )
        output = io.StringIO()
        # packages command does not yet fully avoid print()
        with captured_stdout():
            management.call_command(
                "packages",
                operation="import_controlled_lists",
                source=input_dir,
                overwrite="ignore",
                stdout=output,
            )

        self.assertEqual(List.objects.count(), 3)
        self.assertEqual(ListItem.objects.count(), 17)
        self.assertEqual(ListItemValue.objects.count(), 21)

        # Test Thesaurus does not have searchable attribute in skos file
        test_thesaurus = List.objects.get(name="Test Thesaurus")
        self.assertEqual(test_thesaurus.searchable, False)

        # Searchable Thesaurus has searchable attribute in skos file
        searchable = List.objects.get(name="Searchable")
        self.assertEqual(searchable.searchable, True)

        not_searchable = List.objects.get(name="Not Searchable")
        self.assertEqual(not_searchable.searchable, False)


class RDMToControlledListsETLTests(TestCase):
    fixtures = ["polyhierarchical_collections"]

    def test_migrate_collections_to_controlled_lists(self):
        output = io.StringIO()
        management.call_command(
            "controlled_lists",
            operation="migrate_collections_to_controlled_lists",
            # Migrate all collections with empty string param
            collections_to_migrate=[""],
            host="http://localhost:8000/plugins/controlled-list-manager/item/",
            preferred_sort_language="en",
            overwrite=False,
            stdout=output,
        )

        list1 = List.objects.get(name="Polyhierarchical Collection Test")
        list1_items = (
            list1.list_items.all().with_list_item_labels().order_by("sortorder")
        )
        self.assertEqual(len(list1_items), 3)

        list1_item_values = ListItemValue.objects.filter(list_item__in=list1_items)
        self.assertQuerySetEqual(
            list1_item_values.values_list("value", flat=True).order_by("value"),
            [
                "French Test Concept 1",
                "French Test Concept 2",
                "French Test Concept 3",
                "Test Concept 1",
                "Test Concept 2",
                "Test Concept 3",
            ],
        )

        # Check that sortorder was calculated correctly based on sortorder value coming from RDM
        # Test Concept 3 has sortorder 0,
        # Test Concept 2 has sortorder 1,
        # and Test Concept 1 has no provided sortorder, so will fall back to alpha order
        # after those with a provided sortorder.
        self.assertIn(
            list1_items[0].list_item_labels[0].value,
            ["Test Concept 3", "French Test Concept 3"],
        )
        self.assertIn(
            list1_items[1].list_item_labels[0].value,
            ["Test Concept 2", "French Test Concept 2"],
        )
        self.assertIn(
            list1_items[2].list_item_labels[0].value,
            ["Test Concept 1", "French Test Concept 1"],
        )

        list2 = List.objects.get(name="Polyhierarchy Collection 2")
        list2_items = list2.list_items.all()
        self.assertEqual(len(list2_items), 3)
        list2_item_values = ListItemValue.objects.filter(list_item__in=list2_items)

        # Check that new uuids were generated for polyhierarchical concepts
        self.assertNotEqual(
            list1_item_values.filter(value="Test Concept 1"),
            list2_item_values.filter(value="Test Concept 1"),
        )

        # Check that items with multiple prefLabels in different languages have same listitemid
        self.assertEqual(
            list1_item_values.get(value="Test Concept 1").list_item_id,
            list1_item_values.get(value="French Test Concept 1").list_item_id,
        )

        # But that items with prefLabels in different languages have different listitemvalue ids
        self.assertNotEqual(
            list1_item_values.get(value="Test Concept 1").pk,
            list1_item_values.get(value="French Test Concept 1").pk,
        )

        # Nested Polyhierarchy contains Polyhierarchical Collection Test & Polyhierarchy Collection 2
        nested_list = List.objects.get(name="Nested Polyhierarchy")
        nested_list_items = (
            nested_list.list_items.all().with_list_item_labels().order_by("sortorder")
        )
        nested_list_item_values = ListItemValue.objects.filter(
            list_item__in=nested_list_items
        )
        self.assertEqual(len(nested_list_items), 8)

        # Check that two nested collections that became nested list items have
        # list_item_ids that differ from their list ids (correspond to original conceptids)
        nested_polyhierarchy_1 = nested_list_item_values.get(
            value="Polyhierarchical Collection Test"
        )
        nested_polyhierarchy_2 = nested_list_item_values.get(
            value="Polyhierarchy Collection 2"
        )
        self.assertNotEqual(nested_polyhierarchy_1.list_item_id, list1.id)
        self.assertNotEqual(nested_polyhierarchy_2.list_item_id, list2.id)

        # Check that a duplicated concept have the same URIs as their source concept
        test_concept_1 = ListItemValue.objects.filter(
            value="Test Concept 1"
        ).prefetch_related("list_item")
        for item in test_concept_1:
            self.assertEqual(
                item.list_item.uri,
                "http://www.archesproject.org/89ff530a-f350-44f0-ac88-bdd8904eb57e",
            )

    def test_no_matching_collection_error(self):
        expected_output = "Failed to find the following collections in the database: Collection That Doesn't Exist"
        output = io.StringIO()
        management.call_command(
            "controlled_lists",
            operation="migrate_collections_to_controlled_lists",
            collections_to_migrate=["Collection That Doesn't Exist"],
            host="http://localhost:8000/plugins/controlled-list-manager/item/",
            preferred_sort_language="en",
            overwrite=False,
            stderr=output,
        )
        self.assertIn(expected_output, output.getvalue().strip())

    def test_existing_controlled_list_raises_when_overwrite_false(self):
        List.objects.create(name="Polyhierarchical Collection Test")

        with self.assertRaises(CommandError) as error:
            management.call_command(
                "controlled_lists",
                operation="migrate_collections_to_controlled_lists",
                collections_to_migrate=["Polyhierarchical Collection Test"],
                host="http://localhost:8000/plugins/controlled-list-manager/item/",
                preferred_sort_language="en",
                overwrite=False,
            )

        self.assertIn("already exists", str(error.exception))

    def test_migrate_all_collections_warns_when_none_exist(self):
        Value.objects.filter(concept__nodetype="Collection").delete()
        error_output = io.StringIO()

        management.call_command(
            "controlled_lists",
            operation="migrate_collections_to_controlled_lists",
            collections_to_migrate=[""],
            host="http://localhost:8000/plugins/controlled-list-manager/item/",
            preferred_sort_language="en",
            overwrite=False,
            stderr=error_output,
        )

        stderr_text = error_output.getvalue()
        self.assertIn(
            "No collections were found in the database to migrate to controlled lists.",
            stderr_text,
        )
        self.assertIn(
            "No collections were found in the database for the provided collection names.",
            stderr_text,
        )

    def test_no_matching_language_error(self):
        expected_output = (
            "The preferred sort language, nonexistent, does not exist in the database."
        )
        output = io.StringIO()
        with self.assertRaises(CommandError) as e:
            management.call_command(
                "controlled_lists",
                operation="migrate_collections_to_controlled_lists",
                collections_to_migrate=["Polyhierarchical Collection Test"],
                host="http://localhost:8000/plugins/controlled-list-manager/item/",
                preferred_sort_language="nonexistent",
                overwrite=False,
                stderr=output,
            )
        self.assertEqual(expected_output, str(e.exception))


class MigrateConceptNodesToReferenceDatatypeTests(TestCase):
    # Test data has three models:
    # - `Concept Node Migration Test`, with four concept nodes
    # - `Collection Not Migrated`, with one concept node but the collection hasn't been migrated
    # - `No concept nodes`, only has a string and a number node
    # Contains a Collection "Top Concept", which has been migrated to a controlled list

    # To create test fixtures run:
    # python manage.py dumpdata models.CardModel models.CardComponent models.CardXNodeXWidget models.Concept models.Edge models.GraphModel models.GraphXPublishedGraph models.PublishedGraphEdit models.Language models.NodeGroup models.Node models.Relation models.ResourceXResource models.ResourceInstance models.TileModel models.Value models.Widget arches_controlled_lists.List arches_controlled_lists.ListItem arches_controlled_lists.ListItemValue --format json --output concept_node_migration_test_fixture.json
    fixtures = ["concept_node_migration_test_fixture"]

    def test_migrate_concept_nodes_to_reference_datatype(self):
        output = io.StringIO()
        TEST_GRAPH_ID = "8f7cfa3c-d0e0-4a66-8608-43dd726a1b81"

        management.call_command(
            "controlled_lists",
            operation="migrate_concept_nodes_to_reference_datatype",
            graph=TEST_GRAPH_ID,
            stdout=output,
        )

        nodes = Node.objects.filter(graph_id=TEST_GRAPH_ID).prefetch_related(
            "cardxnodexwidget_set"
        )
        reference_nodes = nodes.filter(datatype="reference")

        self.assertEqual(len(nodes.filter(datatype__in=["concept", "concept-list"])), 0)
        self.assertEqual(len(reference_nodes), 4)

        expected_node_config_keys = set(["multiValue", "controlledList"])
        expected_widget_config_keys = set(
            [
                "label",
                "placeholder",
                "i18n_properties",
                "defaultValue",
            ]
        )
        for node in reference_nodes:
            self.assertEqual(expected_node_config_keys, set(node.config.keys()))
            for widget in node.cardxnodexwidget_set.all():
                self.assertEqual(expected_widget_config_keys, set(widget.config.keys()))

    def test_no_matching_graph_error(self):
        output = io.StringIO()
        expected_output = "Graph matching query does not exist."

        with self.assertRaises(CommandError) as e:
            management.call_command(
                "controlled_lists",
                operation="migrate_concept_nodes_to_reference_datatype",
                graph="00000000-0000-0000-0000-000000000000",
                stderr=output,
            )
        self.assertEqual(str(e.exception), expected_output)

    def test_no_concept_nodes_error(self):
        output = io.StringIO()
        expected_output = (
            "No concept/concept-list nodes found for the No concept nodes graph"
        )

        with self.assertRaises(CommandError) as e:
            management.call_command(
                "controlled_lists",
                operation="migrate_concept_nodes_to_reference_datatype",
                graph="fc46b399-c824-45e5-86e2-5b992b8fa619",
                stderr=output,
            )
        self.assertEqual(str(e.exception), expected_output)

    def test_collections_not_migrated_error(self):
        output = io.StringIO()
        expected_output = "The following collections for the associated nodes have not been migrated to controlled lists:\nNode alias: concept_not_migrated, Collection ID: 00000000-0000-0000-0000-000000000005"

        management.call_command(
            "controlled_lists",
            operation="migrate_concept_nodes_to_reference_datatype",
            graph="b974103f-73bb-4f2a-bffb-8303227ba0da",
            stderr=output,
        )
        self.assertEqual(output.getvalue().strip(), expected_output)


class ExtractDomainValuesToControlledListsTests(TestCase):
    # Domain-Node-Migration-Test model has four domain nodes:
    #   domain          (domain-value)      — options 1, 2, 3, 4
    #   domain_radio    (domain-value)      — same option IDs as `domain`
    #   domain_list     (domain-value-list) — options A, B, C, D
    #   domain_checkbox (domain-value-list) — same option IDs as `domain_list`
    #
    # The shared-ID pairs exercise the duplicate-ID guard rails.

    GRAPH_ID = "c86c9176-b41d-4a57-aeaa-d37928f7989b"
    HOST = "http://localhost:8000/plugins/controlled-list-manager/item/"

    DOMAIN_LIST = "domain_19da2f83-ddaa-442e-b7b6-caee0eb3ab7e"
    DOMAIN_RADIO_LIST = "domain_radio_937fec95-81f6-4396-871e-d99b9249579b"
    DOMAIN_LIST_LIST = "domain_list_1341e31d-2fe4-4e89-960d-143049315f3f"
    DOMAIN_CHECKBOX_LIST = "domain_checkbox_504f3271-ac1e-48bb-aba6-df3220405046"
    EXPECTED_LIST_NAMES = {
        DOMAIN_LIST,
        DOMAIN_RADIO_LIST,
        DOMAIN_LIST_LIST,
        DOMAIN_CHECKBOX_LIST,
    }

    DOMAIN_OPTION_IDS = {
        "cba2cbab-7e49-4248-985e-053f24fdf8eb",
        "ce55a9d7-2ec6-45e2-b8b8-0314ebe80109",
        "a7556098-28bf-4eff-93df-542dc746a45e",
        "77f312cb-5b17-4a02-8d1f-37def9599938",
    }
    DOMAIN_LIST_OPTION_IDS = {
        "2e440bf6-4f0c-465c-8348-99d9be3cc148",
        "2f53ffee-f7a2-48cd-850c-804cfd916e37",
        "3d955540-8d06-4f3d-aad0-75b008549d3c",
        "d249178e-c146-4adc-9eaf-dc0d6c9cf032",
    }

    @classmethod
    def setUpTestData(cls):
        fixture_path = os.path.join(
            TEST_PACKAGE_DIR,
            "graphs",
            "resource_models",
            "Domain Node Migration Test.json",
        )
        with captured_stdout():
            management.call_command(
                "packages",
                ["-o", "import_graphs", "-s", fixture_path],
            )

    def _run_migrate(self, node_aliases=None, overwrite=True):
        output = io.StringIO()
        kwargs = dict(
            operation="extract_domain_values_to_controlled_lists",
            graph=self.GRAPH_ID,
            host=self.HOST,
            overwrite=overwrite,
            stdout=output,
        )
        if node_aliases is not None:
            kwargs["node_aliases"] = node_aliases
        management.call_command("controlled_lists", **kwargs)
        return output.getvalue()

    def test_migrate_single_domain_value_node(self):
        self._run_migrate(node_aliases=["domain"])

        controlled_list = List.objects.get(name=self.DOMAIN_LIST)
        list_items = controlled_list.list_items.all()
        self.assertEqual(list_items.count(), 4)

        item_ids = {str(item.id) for item in list_items}
        self.assertEqual(item_ids, self.DOMAIN_OPTION_IDS)

        for item in list_items:
            self.assertEqual(item.uri, f"{self.HOST.rstrip('/')}/{item.id}")

        label_texts = set(
            ListItemValue.objects.filter(list_item__list=controlled_list).values_list(
                "value", flat=True
            )
        )
        self.assertEqual(label_texts, {"1", "2", "3", "4"})

    def test_migrate_single_domain_value_list_node(self):
        self._run_migrate(node_aliases=["domain_list"])

        controlled_list = List.objects.get(name=self.DOMAIN_LIST_LIST)
        list_items = controlled_list.list_items.all()
        self.assertEqual(list_items.count(), 4)

        item_ids = {str(item.id) for item in list_items}
        self.assertEqual(item_ids, self.DOMAIN_LIST_OPTION_IDS)

        label_texts = set(
            ListItemValue.objects.filter(list_item__list=controlled_list).values_list(
                "value", flat=True
            )
        )
        self.assertEqual(label_texts, {"A", "B", "C", "D"})

    def test_migrate_all_domain_nodes_in_graph(self):
        self._run_migrate()

        all_aliases = {
            self.DOMAIN_LIST,
            self.DOMAIN_RADIO_LIST,
            self.DOMAIN_LIST_LIST,
            self.DOMAIN_CHECKBOX_LIST,
        }
        self.assertEqual(List.objects.filter(name__in=all_aliases).count(), 4)

        for alias in all_aliases:
            self.assertEqual(List.objects.get(name=alias).list_items.count(), 4)

        # domain and domain_radio share the same original option IDs; whichever
        # is processed second gets reminted IDs — assert no overlap between them.
        domain_ids = {
            str(lst.id)
            for lst in List.objects.get(name=self.DOMAIN_LIST).list_items.all()
        }
        domain_radio_ids = {
            str(lst.id)
            for lst in List.objects.get(name=self.DOMAIN_RADIO_LIST).list_items.all()
        }
        self.assertTrue(domain_ids.isdisjoint(domain_radio_ids))
        self.assertEqual(len(domain_ids | domain_radio_ids), 8)

        # Same disjointness check for the domain_list / domain_checkbox pair.
        domain_list_ids = {
            str(lst.id)
            for lst in List.objects.get(name=self.DOMAIN_LIST_LIST).list_items.all()
        }
        domain_checkbox_ids = {
            str(lst.id)
            for lst in List.objects.get(name=self.DOMAIN_CHECKBOX_LIST).list_items.all()
        }
        self.assertTrue(domain_list_ids.isdisjoint(domain_checkbox_ids))
        self.assertEqual(len(domain_list_ids | domain_checkbox_ids), 8)

        # All lists should carry the correct text labels regardless of ID reminting.
        for alias, expected_labels in [
            (self.DOMAIN_LIST, {"1", "2", "3", "4"}),
            (self.DOMAIN_RADIO_LIST, {"1", "2", "3", "4"}),
            (self.DOMAIN_LIST_LIST, {"A", "B", "C", "D"}),
            (self.DOMAIN_CHECKBOX_LIST, {"A", "B", "C", "D"}),
        ]:
            labels = set(
                ListItemValue.objects.filter(
                    list_item__list=List.objects.get(name=alias)
                ).values_list("value", flat=True)
            )
            self.assertEqual(labels, expected_labels, f"labels mismatch for {alias}")

    def test_extract_domain_values_partial_alias_match_raises(self):
        with self.assertRaises(CommandError) as error:
            self._run_migrate(node_aliases=["domain", "missing_alias"])

        self.assertIn("Could not find domain nodes with aliases", str(error.exception))

    def test_extract_domain_values_existing_list_conflict_raises(self):
        node = Node.objects.get(graph_id=self.GRAPH_ID, alias="domain")
        List.objects.create(name=f"{node.alias}_{node.nodeid}")

        with self.assertRaises(CommandError) as error:
            self._run_migrate(node_aliases=["domain"], overwrite=False)

        self.assertIn("already exists", str(error.exception))

    def test_extract_domain_values_skips_node_without_options(self):
        node = Node.objects.get(graph_id=self.GRAPH_ID, alias="domain")
        node_config = dict(node.config or {})
        node_config["options"] = []
        node.config = node_config
        node.save()

        output = self._run_migrate(node_aliases=["domain"])
        self.assertIn("has no options, skipping", output)
        self.assertFalse(
            List.objects.filter(name=f"{node.alias}_{node.nodeid}").exists()
        )


class MigrateDomainNodesToReferenceDatatypeTests(
    ExtractDomainValuesToControlledListsTests
):
    # Subclassed to re-use setupdata method

    def _run_migrate_to_reference(self, node_aliases=None):
        output = io.StringIO()
        kwargs = dict(
            operation="migrate_domain_nodes_to_reference_datatype",
            graph=self.GRAPH_ID,
            stdout=output,
        )
        if node_aliases is not None:
            kwargs["node_aliases"] = node_aliases
        management.call_command("controlled_lists", **kwargs)
        return output.getvalue()

    def test_migrate_all_domain_nodes_to_reference_datatype(self):
        self._run_migrate()
        self._run_migrate_to_reference()

        reference_nodes = Node.objects.filter(
            graph_id=self.GRAPH_ID,
            alias__in=["domain", "domain_radio", "domain_list", "domain_checkbox"],
            datatype="reference",
        )
        self.assertEqual(reference_nodes.count(), 4)

        expected_node_config_keys = set(
            ["multiValue", "controlledList", "options", "i18n_config"]
        )
        expected_widget_config_keys = set(
            [
                "label",
                "placeholder",
                "i18n_properties",
                "defaultValue",
            ]
        )

        for node in reference_nodes:
            config = node.config
            self.assertEqual(expected_node_config_keys, set(config.keys()))
            for widget in node.cardxnodexwidget_set.all():
                self.assertEqual(expected_widget_config_keys, set(widget.config.keys()))
                if node.alias in ("domain", "domain_list"):
                    default_value = widget.config.get("defaultValue")
                    self.assertTrue(isinstance(default_value, list))
                    self.assertTrue(bool(default_value[0].get("uri")))
            if node.alias in ("domain", "domain_radio"):
                self.assertFalse(config["multiValue"])
            else:
                self.assertTrue(config["multiValue"])

        list_id_by_alias = {
            "domain": self.DOMAIN_LIST,
            "domain_radio": self.DOMAIN_RADIO_LIST,
            "domain_list": self.DOMAIN_LIST_LIST,
            "domain_checkbox": self.DOMAIN_CHECKBOX_LIST,
        }
        for node in reference_nodes:
            expected_list_name = list_id_by_alias[node.alias]
            expected_list_id = str(List.objects.get(name=expected_list_name).pk)
            self.assertEqual(node.config["controlledList"], expected_list_id)

    def test_migrate_domain_node_by_alias_to_reference_datatype(self):
        self._run_migrate()
        self._run_migrate_to_reference(node_aliases=["domain"])

        domain_node = Node.objects.get(graph_id=self.GRAPH_ID, alias="domain")
        self.assertEqual(domain_node.datatype, "reference")
        self.assertFalse(domain_node.config["multiValue"])
        expected_list_id = str(List.objects.get(name=self.DOMAIN_LIST).pk)
        self.assertEqual(domain_node.config["controlledList"], expected_list_id)

        unchanged_nodes = Node.objects.filter(
            graph_id=self.GRAPH_ID,
            alias__in=["domain_radio", "domain_list", "domain_checkbox"],
        )
        for node in unchanged_nodes:
            self.assertIn(node.datatype, ["domain-value", "domain-value-list"])

    def test_migrate_domain_nodes_to_reference_no_matching_aliases_error(self):
        with self.assertRaises(CommandError) as error:
            self._run_migrate_to_reference(node_aliases=["missing_alias"])

        self.assertIn("No domain/domain-list nodes found", str(error.exception))

    def test_migrate_domain_nodes_to_reference_reports_missing_lists(self):
        error_output = io.StringIO()

        management.call_command(
            "controlled_lists",
            operation="migrate_domain_nodes_to_reference_datatype",
            graph=self.GRAPH_ID,
            stderr=error_output,
        )

        self.assertIn(
            "have not been migrated to controlled lists",
            error_output.getvalue(),
        )


class ChangeUrlBaseTests(TestCase):

    def setUp(self):
        self.list = List.objects.create(name="Test List")
        self.item1 = ListItem.objects.create(
            list=self.list,
            uri="http://localhost:8000/plugins/controlled-list-manager/item/item-1",
            sortorder=0,
        )
        self.item2 = ListItem.objects.create(
            list=self.list,
            uri="http://localhost:8000/plugins/controlled-list-manager/item/item-2",
            sortorder=1,
        )
        self.item3 = ListItem.objects.create(
            list=self.list,
            uri="http://localhost:8080/plugins/controlled-list-manager/item/item-3",
            sortorder=2,
        )

    def test_change_url_base_all_lists(self):
        output = io.StringIO()
        management.call_command(
            "controlled_lists",
            operation="change_url_base",
            host="https://example.com",
            stdout=output,
        )

        self.item1.refresh_from_db()
        self.item2.refresh_from_db()
        self.item3.refresh_from_db()

        self.assertEqual(
            self.item1.uri,
            "https://example.com/plugins/controlled-list-manager/item/item-1",
        )
        self.assertEqual(
            self.item2.uri,
            "https://example.com/plugins/controlled-list-manager/item/item-2",
        )
        self.assertEqual(
            self.item3.uri,
            "https://example.com/plugins/controlled-list-manager/item/item-3",
        )
        self.assertIn("Successfully changed URL base.", output.getvalue())

    def test_change_url_base_specific_list(self):
        second_list = List.objects.create(name="Second List")
        second_item = ListItem.objects.create(
            list=second_list,
            uri="http://localhost:8000/plugins/controlled-list-manager/item/second-item",
            sortorder=0,
        )

        output = io.StringIO()
        management.call_command(
            "controlled_lists",
            operation="change_url_base",
            host="https://production.org:443",
            lists=str(second_list.id),
            stdout=output,
        )

        second_item.refresh_from_db()

        self.assertEqual(
            self.item1.uri,
            "http://localhost:8000/plugins/controlled-list-manager/item/item-1",
        )

        self.assertEqual(
            second_item.uri,
            "https://production.org/plugins/controlled-list-manager/item/second-item",
        )

    def test_change_url_base_preserves_port(self):
        output = io.StringIO()
        management.call_command(
            "controlled_lists",
            operation="change_url_base",
            host="https://newdomain.com:8080",
            stdout=output,
        )

        self.item3.refresh_from_db()
        self.assertEqual(
            self.item3.uri,
            "https://newdomain.com:8080/plugins/controlled-list-manager/item/item-3",
        )

    def test_change_url_base_normalizes_url(self):
        output = io.StringIO()
        management.call_command(
            "controlled_lists",
            operation="change_url_base",
            host="example.org",
            stdout=output,
        )

        self.item1.refresh_from_db()
        self.assertTrue(self.item1.uri.startswith("https://"))
        self.assertIn("example.org", self.item1.uri)

        management.call_command(
            "controlled_lists",
            operation="change_url_base",
            host="http://test.org:80",
            stdout=output,
        )

        self.item1.refresh_from_db()
        self.assertTrue(self.item1.uri.startswith("http://"))
        self.assertIn("test.org", self.item1.uri)
        self.assertNotIn(":80", self.item1.uri)


class MigrateTileDataToReferenceDatatypeTests(TestCase):
    """
    Tile tests fixtures have two models:
    - `Concept Value Migration Test`, with four concept origin nodes
    - `Domain Value Migration Test`, with four domain origin nodes
    Each model has a resource instance with tiles created with concept & domain values, repectively.
    The collections/domain values used by those nodes were migrated to controlled lists (see `MigrateCollectionsToControlledListsTests` and `MigrateDomainNodesToControlledListsTests`).
    Then the nodes were migrated to reference datatype (see `MigrateConceptNodesToReferenceDatatypeTests` and `MigrateDomainNodesToReferenceDatatypeTests`).

    The fixture mocks the state of an Arches instance just before tile data need to be migrated to the reference datatype.

    To create test fixtures run:
    python manage.py dumpdata models.CardModel models.CardComponent models.CardXNodeXWidget models.Concept models.Edge models.GraphModel models.GraphXPublishedGraph models.PublishedGraph models.PublishedGraphEdit models.Language models.NodeGroup models.Node models.Relation models.ResourceXResource models.ResourceInstance models.TileModel models.Value models.Widget arches_controlled_lists.List arches_controlled_lists.ListItem arches_controlled_lists.ListItemValue --format json --output tile_migration_test_data.json
    """

    fixtures = ["tile_migration_test_data"]

    CONCEPT_GRAPH_SLUG = "concept-node-migration-test"
    DOMAIN_GRAPH_SLUG = "domain-node-migration-test"

    @classmethod
    def _register_etl_module(cls, module_name):
        from arches.management.commands.etl_module import Command as ETLModuleCommand

        cmd = ETLModuleCommand()
        cmd.register(source=str(Path(APP_ROOT) / "etl_modules" / module_name))

    def setUp(cls):
        """setUpClass doesn't work because the rollback fixture is applied after that."""
        cls._register_etl_module("migrate_to_reference_datatype.py")

    def _run_migration(self, graph, origin):
        with (
            captured_stdout(),
            patch("arches.app.etl_modules.save.disable_tile_triggers"),
            patch("arches.app.etl_modules.save.reenable_tile_triggers"),
        ):
            management.call_command(
                "controlled_lists",
                operation="migrate_tile_data_to_reference_datatype",
                graph=graph,
                origin=origin,
            )

    def _assert_reference_shape(self, node_val):
        self.assertIsInstance(node_val, list)
        for entry in node_val:
            self.assertEqual(set(entry.keys()), {"uri", "labels", "list_id"})
            self.assertIsInstance(entry["labels"], list)
            self.assertTrue(entry["labels"])

    def test_migrate_domain_tile_data_to_reference_datatype(self):
        self._run_migration(self.DOMAIN_GRAPH_SLUG, "domain")

        domain_graph = GraphModel.objects.get(slug=self.DOMAIN_GRAPH_SLUG)
        domain_node = Node.objects.get(graph=domain_graph, alias="domain")
        domain_list_node = Node.objects.get(graph=domain_graph, alias="domain_list")
        resource = ResourceInstance.objects.filter(graph=domain_graph).first()

        tile1 = TileModel.objects.filter(
            resourceinstance=resource,
            nodegroup=domain_node.nodegroup,
        ).first()
        node_val = tile1.data[str(domain_node.pk)]
        self._assert_reference_shape(node_val)

        tile2 = TileModel.objects.filter(
            resourceinstance=resource,
            nodegroup=domain_list_node.nodegroup,
        ).first()
        node_val = tile2.data[str(domain_list_node.pk)]
        self._assert_reference_shape(node_val)

    def test_migrate_concept_tile_data_to_reference_datatype(self):
        self._run_migration(self.CONCEPT_GRAPH_SLUG, "concept")

        concept_graph = GraphModel.objects.get(slug=self.CONCEPT_GRAPH_SLUG)
        concept_node = Node.objects.get(
            graph=concept_graph, alias="concept_n1_w_default"
        )
        concept_list_node = Node.objects.get(
            graph=concept_graph, alias="concept_list_w_default"
        )
        resource = ResourceInstance.objects.filter(graph=concept_graph).first()

        tile = TileModel.objects.filter(
            resourceinstance=resource,
            nodegroup=concept_node.nodegroup,
        ).first()
        node_val = tile.data[str(concept_node.pk)]
        self._assert_reference_shape(node_val)
        node_val = tile.data[str(concept_list_node.pk)]
        self._assert_reference_shape(node_val)

    def test_missing_list_items_during_migration(self):
        concept_graph = GraphModel.objects.get(slug=self.CONCEPT_GRAPH_SLUG)
        concept_node = Node.objects.get(
            graph=concept_graph, alias="concept_n1_w_default"
        )
        controlled_list = concept_node.config["controlledList"]
        ListItem.objects.filter(list_id=controlled_list).delete()
        self._run_migration(self.CONCEPT_GRAPH_SLUG, "concept")

        load_errors = LoadErrors.objects.all()
        self.assertEqual(load_errors.count(), 2)
        for error in load_errors:
            self.assertIn("Could not resolve legacy concept id(s)", error.message)

    def test_validate_inputs(self):
        etl_module = MigrateToReferenceDatatype()
        with self.assertRaises(MissingRequiredInputError) as error:
            graph_id = None
            origin = None
            etl_module.validate_inputs(graph_id, origin)

        with self.assertRaises(MissingRequiredInputError) as error:
            graph_id = "c86c9176-b41d-4a57-aeaa-d37928f7989b"
            origin = None
            etl_module.validate_inputs(graph_id, origin)
            self.assertEqual(
                str(error.exception), "Missing required value: Origin Datatype"
            )

        with self.assertRaises(MissingRequiredInputError) as error:
            graph_id = None
            origin = "concept"
            etl_module.validate_inputs(graph_id, origin)
            self.assertEqual(str(error.exception), "Missing required value: Graph ID")

        with self.assertRaises(MissingRequiredInputError) as error:
            graph_id = "c86c9176-b41d-4a57-aeaa-d37928f7989b"
            origin = "string"
            etl_module.validate_inputs(graph_id, origin)
            self.assertEqual(
                str(error.exception), "Origin must be either 'concept' or 'domain'."
            )

    def test_get_candidate_nodes(self):
        etl_module = MigrateToReferenceDatatype()
        graph_id = "8f7cfa3c-d0e0-4a66-8608-43dd726a1b81"
        origin = "concept"
        request = MagicMock(POST={"graph_id": graph_id, "origin": origin})
        response = etl_module.get_candidate_nodes(request)
        self.assertTrue(response["success"])
        data = response["data"]
        self.assertEqual(len(data), 4)
        expected_keys = set(
            ["nodeid", "alias", "name", "nodegroup", "list_name", "tile_count"]
        )
        for node in data:
            self.assertEqual(set(node.keys()), expected_keys)

    def test_write_missing_input_payload(self):
        etl_module = MigrateToReferenceDatatype()
        response = etl_module.write(request=MagicMock(POST={}))
        self.assertFalse(response["success"])
        self.assertEqual(response["data"]["title"], "Missing input error")


class BulkChangeURLTests(TestCase):

    def setUp(self):
        self.command = ControlledListsCommand()

    def test_handle_change_url_base_requires_host(self):
        with self.assertRaises(CommandError):
            self.command.handle(operation="change_url_base", host=None, lists=False)

    def test_bulk_change_url_base_handles_update_errors(self):
        self.command.stderr.write = MagicMock()
        with patch(
            "arches.extensions.controlled_lists.management.commands.controlled_lists.ListItem.objects.bulk_update",
            side_effect=Exception("update failed"),
        ):
            self.command.bulk_change_url_base(
                target_hostname="https://example.org",
                list_ids=[],
            )
        self.command.stderr.write.assert_called_once()
        self.assertIn(
            "Could not change base url: update failed",
            self.command.stderr.write.call_args[0][0],
        )

    def test_replace_hostname_handles_invalid_url(self):
        bad_url = "no-netloc-path-only"
        with patch("builtins.print") as mock_print:
            result = self.command._replace_hostname(bad_url, "https://example.org")
        self.assertEqual(result, bad_url)
        mock_print.assert_called_once()

    def test_replace_hostname_handles_parse_exception(self):
        original_url = "https://localhost/item/1"
        with patch(
            "arches.extensions.controlled_lists.management.commands.controlled_lists.urlparse",
            side_effect=Exception("parse error"),
        ):
            with patch("builtins.print") as mock_print:
                result = self.command._replace_hostname(
                    original_url,
                    "https://example.org",
                )
        self.assertEqual(result, original_url)
        mock_print.assert_called_once()

    def test_resolve_graph_requires_value(self):
        with self.assertRaises(CommandError) as error:
            self.command._resolve_graph(None)

        self.assertIn("Please provide a valid graph id or slug", str(error.exception))
