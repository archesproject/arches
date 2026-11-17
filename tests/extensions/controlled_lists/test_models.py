import hashlib
import time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from arches.app.models.models import DValueType, Language
from arches.app.search.elasticsearch_dsl_builder import Query
from arches.app.search.search_engine_factory import SearchEngineInstance
from arches.extensions.controlled_lists.models import List, ListItem, ListItemValue

# these tests can be run from the command line via
# python manage.py test tests.extensions.controlled_lists.test_models --settings="tests.test_settings"


class ListItemTests(TestCase):
    def test_uri_generation_guards_against_failure(self):
        # Don't bother setting up a list.
        item = ListItem(sortorder=0)
        item.id = None

        with self.assertRaises(RuntimeError):
            item.clean()

        item.full_clean(exclude={"list"})
        self.assertIsNotNone(item.uri)


class ListItemValueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_list = List(name="Test List")
        List.objects.bulk_create([test_list])
        cls.items = [
            ListItem(list=test_list, sortorder=index, uri=f"http://example.com/{index}")
            for index in range(2)
        ]
        ListItem.objects.bulk_create(cls.items)
        for language in ("en", "de"):
            Language.objects.get_or_create(code=language)
        cls.value_fields = {
            "list_item": cls.items[0],
            "valuetype": DValueType.objects.get(valuetype="note"),
            "language_id": "en",
        }
        # Varied text avoids compression hiding PostgreSQL's index-entry limit.
        cls.long_value = "".join(
            hashlib.sha256(str(index).encode()).hexdigest() for index in range(512)
        )

    def test_long_note_is_stored_without_truncation(self):
        value = ListItemValue(**self.value_fields, value=self.long_value)
        value.full_clean()
        ListItemValue.objects.bulk_create([value])
        value.refresh_from_db()
        self.assertEqual(value.value, self.long_value)

    def test_duplicate_long_note_is_rejected_by_database(self):
        ListItemValue.objects.bulk_create(
            [ListItemValue(**self.value_fields, value=self.long_value)]
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            ListItemValue.objects.bulk_create(
                [ListItemValue(**self.value_fields, value=self.long_value)]
            )

    def test_duplicate_long_note_is_rejected_by_validation(self):
        ListItemValue.objects.bulk_create(
            [ListItemValue(**self.value_fields, value=self.long_value)]
        )
        duplicate = ListItemValue(**self.value_fields, value=self.long_value)
        with self.assertRaisesMessage(
            ValidationError,
            "The same item value cannot be stored twice in the same language.",
        ):
            duplicate.full_clean()

    def test_different_values_items_types_and_languages_remain_allowed(self):
        ListItemValue.objects.bulk_create(
            [ListItemValue(**self.value_fields, value=self.long_value)]
        )
        alternatives = [
            {"value": self.long_value + "different"},
            {"list_item": self.items[1]},
            {"valuetype": DValueType.objects.get(valuetype="scopeNote")},
            {"language_id": "de"},
        ]
        for alternative in alternatives:
            with self.subTest(alternative=tuple(alternative)):
                fields = {
                    **self.value_fields,
                    "value": self.long_value,
                    **alternative,
                }
                value = ListItemValue(**fields)
                value.full_clean()
                ListItemValue.objects.bulk_create([value])


class ListItemGetChildUrisTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.list = List.objects.create(name="Test List")
        cls.parent_item = ListItem.objects.create(
            list=cls.list, sortorder=0, uri="http://example.com/parent"
        )
        cls.child_item_1 = ListItem.objects.create(
            list=cls.list,
            parent=cls.parent_item,
            sortorder=1,
            uri="http://example.com/child1",
        )
        cls.child_item_2 = ListItem.objects.create(
            list=cls.list,
            parent=cls.parent_item,
            sortorder=2,
            uri="http://example.com/child2",
        )

    def test_get_child_uris_includes_parent_and_children(self):
        uris = self.parent_item.get_child_uris()
        self.assertIn(self.parent_item.uri, uris)
        self.assertIn(self.child_item_1.uri, uris)
        self.assertIn(self.child_item_2.uri, uris)

    def test_get_child_uris_empty_for_item_without_children(self):
        uris = self.child_item_1.get_child_uris()
        self.assertEqual(uris, [self.child_item_1.uri])


class ListIndexTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.list = List.objects.create(name="Test List", searchable=True)
        cls.list_item = ListItem.objects.create(
            list=cls.list, sortorder=0, uri="http://example.com/item"
        )
        cls.preflabel_value = ListItemValue.objects.create(
            list_item=cls.list_item,
            valuetype=DValueType.objects.get(valuetype="prefLabel"),
            language_id="en",
            value="Test PrefLabel",
        )
        cls.altlabel_value = ListItemValue.objects.create(
            list_item=cls.list_item,
            valuetype=DValueType.objects.get(valuetype="altLabel"),
            language_id="en",
            value="Test AltLabel",
        )

    def test_index_list_called_on_save(self):
        self.list.save()
        time.sleep(2)  # Allow time for indexing to complete
        query = Query(SearchEngineInstance)
        count = query.se.count(index=settings.REFERENCES_INDEX_NAME)
        self.assertEqual(count, 2)

    def test_delete_list_index_called_on_delete(self):
        self.list.save()
        time.sleep(2)  # Allow time for indexing to complete
        query = Query(SearchEngineInstance)
        count = query.se.count(index=settings.REFERENCES_INDEX_NAME)
        self.assertEqual(count, 2)
        self.list.delete()
        time.sleep(2)  # Allow time for index deletion to complete
        query = Query(SearchEngineInstance)
        count = query.se.count(index=settings.REFERENCES_INDEX_NAME)
        self.assertEqual(count, 0)

    def test_delete_list_item_index_called_on_delete(self):
        self.list.save()
        time.sleep(2)  # Allow time for indexing to complete
        query = Query(SearchEngineInstance)
        count = query.se.count(index=settings.REFERENCES_INDEX_NAME)
        self.assertEqual(count, 2)
        self.list_item.delete()
        time.sleep(2)  # Allow time for index deletion to complete
        query = Query(SearchEngineInstance)
        count = query.se.count(index=settings.REFERENCES_INDEX_NAME)
        self.assertEqual(count, 0)

    def test_delete_list_item_value_index_called_on_delete(self):
        self.list.save()
        time.sleep(2)  # Allow time for indexing to complete
        query = Query(SearchEngineInstance)
        count = query.se.count(index=settings.REFERENCES_INDEX_NAME)
        self.assertEqual(count, 2)
        self.altlabel_value.delete()
        time.sleep(2)  # Allow time for index deletion to complete
        query = Query(SearchEngineInstance)
        count = query.se.count(index=settings.REFERENCES_INDEX_NAME)
        self.assertEqual(count, 1)
