import uuid
from django.test import TestCase
from unittest.mock import MagicMock

from arches.app.models.models import DValueType

from arches.extensions.controlled_lists.models import List, ListItem, ListItemValue
from arches.extensions.controlled_lists.search.references_es_mapping_modifier import (
    ReferencesEsMappingModifier,
)


class TestReferencesEsMappingModifier(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.list = List.objects.create(name="Test List", searchable=False)
        cls.list_item = ListItem.objects.create(
            list=cls.list, sortorder=0, uri="http://example.com/item"
        )

    def test_add_search_filter(self):
        search_query = MagicMock()

        term = {"type": "reference", "value": self.list_item.pk, "inverted": False}
        permitted_nodegroups = ["nodegroup1", "nodegroup2"]
        include_provisional = False

        ReferencesEsMappingModifier.add_search_filter(
            search_query, term, permitted_nodegroups, include_provisional
        )

        search_query.filter.assert_called()
        search_query.must_not.assert_not_called()

    def test_get_mapping_property(self):
        self.assertEqual(
            ReferencesEsMappingModifier.get_mapping_property(), "references"
        )

    def test_get_mapping_definition(self):
        expected_definition = {
            "type": "nested",
            "properties": {
                "id": {"type": "keyword"},
                "uri": {"type": "keyword"},
                "list_id": {"type": "keyword"},
                "nodegroup_id": {"type": "keyword"},
                "provisional": {"type": "boolean"},
            },
        }
        self.assertEqual(
            ReferencesEsMappingModifier.get_mapping_definition(), expected_definition
        )

    def test_add_search_filter_inverted(self):
        search_query = MagicMock()

        term = {"type": "reference", "value": self.list_item.pk, "inverted": True}
        permitted_nodegroups = ["nodegroup1", "nodegroup2"]
        include_provisional = False

        ReferencesEsMappingModifier.add_search_filter(
            search_query, term, permitted_nodegroups, include_provisional
        )

        search_query.must_not.assert_called()
        search_query.filter.assert_not_called()
