from arches.app.models.models import DValueType
from arches.app.utils.resource_relationship_utils import (
    get_resource_relationship_type_label,
)
from django.apps import apps
from django.test import TestCase
import unittest
import uuid

# these tests can be run from the command line via
# python manage.py test tests.utils.test_resource_relationship_utils --settings="tests.test_settings"

CONTROLLED_LISTS_INSTALLED = apps.is_installed("arches_controlled_lists")


class ResourceRelationshipUtilsTests(TestCase):

    def test_get_resource_relationship_type_label(self):
        is_related_to = uuid.UUID("ac41d9be-79db-4256-b368-2f4559cfbe55")
        labels = get_resource_relationship_type_label({is_related_to})
        with self.subTest(labels=labels):
            self.assertEqual(labels[str(is_related_to)], "is related to")

    def test_ontology_property_has_no_label(self):
        labels = get_resource_relationship_type_label({"P1_is_identified_by"})
        self.assertEqual(labels, {})


@unittest.skipUnless(
    CONTROLLED_LISTS_INSTALLED, "requires the arches_controlled_lists application"
)
class ReferenceRelationshipTypeLabelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        from arches_controlled_lists.models import List, ListItem, ListItemValue

        cls.list = List.objects.create(name="Relationship Types")
        # a uri that doesn't end in the item id, as imported vocabularies have
        cls.list_item = ListItem.objects.create(
            list=cls.list, sortorder=0, uri="http://vocab.getty.edu/aat/300129361"
        )
        ListItemValue.objects.create(
            list_item=cls.list_item,
            valuetype=DValueType.objects.get(valuetype="prefLabel"),
            language_id="en",
            value="is depicted by",
        )
        ListItemValue.objects.create(
            list_item=cls.list_item,
            valuetype=DValueType.objects.get(valuetype="altLabel"),
            language_id="en",
            value="depicted by",
        )

    def test_label_by_uri(self):
        labels = get_resource_relationship_type_label({self.list_item.uri})
        self.assertEqual(labels[self.list_item.uri], "is depicted by")

    def test_label_by_item_id(self):
        """A generated uri ends in the item id, and a stale one still resolves."""
        stale_uri = (
            "http://elsewhere.example.com/plugins/controlled-list-manager/item/"
            f"{self.list_item.pk}"
        )
        labels = get_resource_relationship_type_label(
            {str(self.list_item.pk), stale_uri}
        )
        self.assertEqual(labels[str(self.list_item.pk)], "is depicted by")
        self.assertEqual(labels[stale_uri], "is depicted by")

    def test_concepts_and_references_together(self):
        is_related_to = uuid.UUID("ac41d9be-79db-4256-b368-2f4559cfbe55")
        labels = get_resource_relationship_type_label(
            {is_related_to, self.list_item.uri, "P1_is_identified_by"}
        )
        self.assertEqual(
            labels,
            {
                str(is_related_to): "is related to",
                self.list_item.uri: "is depicted by",
            },
        )
