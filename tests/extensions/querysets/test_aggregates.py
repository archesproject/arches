from django.db.models import Max, Min

from arches.extensions.querysets.models import ResourceTileTree
from arches.extensions.querysets.utils.tests import GraphTestCase


class AggregateTests(GraphTestCase):
    def test_number(self):
        self.resources = ResourceTileTree.get_tiles("datatype_lookups")

        # Edit the resource that usually has None in all nodes to have a value of 43.
        # Fetch it since cls.resource_none was not fetched via get_tiles() :/
        resource2 = self.resources.get(pk=self.resource_none.pk)
        resource2.aliased_data.datatypes_1.aliased_data.number_alias = 43
        resource2.aliased_data.datatypes_n[0].aliased_data.number_alias_n = 43
        resource2.save(force_admin=True)

        # Per-table aggregate on cardinality-1 value
        query = self.resources.aggregate(Min("number_alias"), Max("number_alias"))
        self.assertEqual(query["number_alias__min"], 42.0)
        self.assertEqual(query["number_alias__max"], 43.0)

        # Per-table aggregate on arrays, e.g. [43] > [42], but [43, 42] < [43, 44]
        query = self.resources.aggregate(Min("number_alias_n"), Max("number_alias_n"))
        self.assertEqual(query["number_alias_n__min"], [42.0])
        self.assertEqual(query["number_alias_n__max"], [43.0])
