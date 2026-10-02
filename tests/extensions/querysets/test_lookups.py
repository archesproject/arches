import uuid

from arches.extensions.querysets.models import ResourceTileTree, TileTree
from arches.extensions.querysets.utils.tests import GraphTestCase


class LookupTestCase(GraphTestCase):
    def setUp(self):
        self.resources = ResourceTileTree.get_tiles("datatype_lookups")
        self.tiles_1 = TileTree.get_tiles(
            "datatype_lookups", nodegroup_alias="datatypes_1"
        )
        self.tiles_n = TileTree.get_tiles(
            "datatype_lookups", nodegroup_alias="datatypes_n"
        )


class GenericLookupTests(LookupTestCase):
    def test_cardinality_1(self):
        # Exact
        for lookup, value in [
            ("boolean_alias", True),
            ("number_alias", 42.0),  # Use a float so that stringifying causes failure.
            ("url_alias__url_label", "42.com"),
            ("non_localized_string_alias", "forty-two"),
            ("string_alias__en__value", "forty-two"),
            ("date_alias", "2042-04-02"),
            # More natural lookups in ResourceInstanceLookupTests
            ("resource_instance_alias__0__resourceId", str(self.resource_42.pk)),
            ("resource_instance_list_alias__0__resourceId", str(self.resource_42.pk)),
            ("concept_alias", self.concept_value.pk),
            ("concept_list_alias", [str(self.concept_value.pk)]),
            ("node_value_alias", self.cardinality_1_tile.pk),
        ]:
            with self.subTest(lookup=lookup, value=value):
                self.assertTrue(self.resources.filter(**{lookup: value}))
                self.assertTrue(self.tiles_1.filter(**{lookup: value}))

    def test_cardinality_n(self):
        # Contains
        for lookup, value in [
            ("boolean_alias_n__contains", [True]),
            ("number_alias_n__contains", [42.0]),
            ("url_alias_n__0__url_label", "42.com"),
            ("non_localized_string_alias_n__contains", ["forty-two"]),
            ("date_alias_n__contains", ["2042-04-02"]),
            # better lookups for RI{list} below.
            ("resource_instance_alias_n__0__0__resourceId", str(self.resource_42.pk)),
            # you likely want ids_contain, below.
            (
                "resource_instance_list_alias_n__0__0__resourceId",
                str(self.resource_42.pk),
            ),
            ("concept_alias_n__contains", [self.concept_value.pk]),
            # you likely want any_contains, below.
            ("concept_list_alias_n__0__contains", str(self.concept_value.pk)),
            ("node_value_alias_n__contains", [self.cardinality_n_tile.pk]),
        ]:
            with self.subTest(lookup=lookup, value=value):
                self.assertTrue(self.resources.filter(**{lookup: value}))

    def test_cardinality_1_values(self):
        for node in self.data_nodes_1:
            with self.subTest(alias=node.alias):
                self.assertTrue(self.resources.values(node.alias))
                self.assertTrue(self.tiles_1.values(node.alias))
                self.assertTrue(self.resources.values_list(node.alias))
                self.assertTrue(self.tiles_1.values_list(node.alias))

    def test_cardinality_n_values(self):
        for node in self.data_nodes_n:
            with self.subTest(alias=node.alias):
                self.assertTrue(self.resources.values(node.alias))
                self.assertTrue(self.tiles_n.values(node.alias))
                self.assertTrue(self.resources.values_list(node.alias))
                self.assertTrue(self.tiles_n.values_list(node.alias))

    def test_values_path_transforms(self):
        resources = self.resources.exclude(resource_instance_list_alias=None)
        values = resources.values("resource_instance_list_alias__0__resourceId")
        uuid_val = values[0]["resource_instance_list_alias__0__resourceId"]
        # Implicitly test the result is a uuid
        uuid.UUID(uuid_val)

        values = resources.values_list(
            "resource_instance_list_alias__0__resourceId", flat=True
        )
        uuid_val = values[0]
        uuid.UUID(uuid_val)


class NonLocalizedStringLookupTests(LookupTestCase):
    def test_cardinality_1(self):
        self.assertTrue(
            self.resources.filter(non_localized_string_alias__contains="forty")
        )

    def test_cardinality_n(self):
        self.assertTrue(
            self.resources.filter(non_localized_string_alias_n__contains=["forty-two"])
        )
        self.assertFalse(
            self.resources.filter(non_localized_string_alias_n__contains=["forty"])
        )
        self.assertTrue(
            self.resources.filter(non_localized_string_alias_n__any_contains="forty")
        )
        self.assertFalse(
            self.resources.filter(non_localized_string_alias_n__any_contains="FORTY")
        )
        self.assertTrue(
            self.resources.filter(non_localized_string_alias_n__any_icontains="FORTY")
        )


class LocalizedStringLookupTests(LookupTestCase):
    def test_cardinality_1(self):
        for lookup, value in [
            ("string_alias__any_lang_startswith", "forty"),
            ("string_alias__any_lang_istartswith", "FORTY"),
            ("string_alias__any_lang_contains", "fort"),
            ("string_alias__any_lang_icontains", "FORT"),
        ]:
            with self.subTest(lookup=lookup, value=value):
                self.assertTrue(self.resources.filter(**{lookup: value}))

        # Negatives
        for lookup, value in [
            ("string_alias__any_lang_startswith", "orty-two"),
            ("string_alias__any_lang_istartswith", "ORTY-TWO"),
            ("string_alias__any_lang_contains", "orty-three"),
            ("string_alias__any_lang_icontains", "ORTY-THREE"),
        ]:
            with self.subTest(lookup=lookup, value=value):
                self.assertFalse(self.resources.filter(**{lookup: value}))

    def test_cardinality_n(self):
        for lookup, value in [
            ("string_alias_n__any_lang_startswith", "forty"),
            ("string_alias_n__any_lang_istartswith", "FORTY"),
            ("string_alias_n__any_lang_contains", "fort"),
            ("string_alias_n__any_lang_icontains", "FORT"),
        ]:
            with self.subTest(lookup=lookup, value=value):
                self.assertTrue(self.resources.filter(**{lookup: value}))

        # Negatives
        for lookup, value in [
            ("string_alias_n__any_lang_startswith", "orty-two"),
            ("string_alias_n__any_lang_istartswith", "ORTY-TWO"),
            ("string_alias_n__any_lang_contains", "orty-three"),
            ("string_alias_n__any_lang_icontains", "ORTY-THREE"),
        ]:
            with self.subTest(lookup=lookup, value=value):
                self.assertFalse(self.resources.filter(**{lookup: value}))


class ResourceInstanceLookupTests(LookupTestCase):
    def test_cardinality_1(self):
        for lookup, value in [
            ("resource_instance_alias__id", str(self.resource_42.pk)),
            ("resource_instance_list_alias__contains", str(self.resource_42.pk)),
        ]:
            with self.subTest(lookup=lookup, value=value):
                self.assertTrue(self.resources.filter(**{lookup: value}))

    def test_cardinality_n(self):
        for lookup, value in [
            ("resource_instance_alias_n__ids_contain", str(self.resource_42.pk)),
            ("resource_instance_list_alias_n__ids_contain", str(self.resource_42.pk)),
        ]:
            with self.subTest(lookup=lookup, value=value):
                self.assertTrue(self.resources.filter(**{lookup: value}))
