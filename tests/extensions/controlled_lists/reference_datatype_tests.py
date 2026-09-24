import uuid
from types import SimpleNamespace
from unittest.mock import Mock, patch


from django.test import TestCase
from rdflib import URIRef
from rdflib.namespace import RDF, RDFS

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.graph import GraphValidationError
from arches.app.models.tile import Tile
from arches.app.models.models import Node, TileModel
from arches.app.search.elasticsearch_dsl_builder import Bool
from arches.extensions.controlled_lists.datatypes.datatypes import (
    Reference,
    ReferenceDataType,
    ReferenceLabel,
)
from arches.extensions.controlled_lists.models import List, ListItem, ListItemValue

from .test_views import ListTests

# these tests can be run from the command line via
# python manage.py test tests.extensions.controlled_lists.reference_datatype_tests --settings="tests.test_settings"


class ReferenceDataTypeTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        return ListTests.setUpTestData()

    def get_mock_tile(self):
        node = ListTests.node_using_list1
        list1 = ListTests.list1
        item = list1.list_items.get(sortorder=0)
        tile_repr = [
            {
                k: v
                for k, v in item.serialize().items()
                if k in ["uri", "values", "list_id"]
            }
        ]
        tile_repr[0]["labels"] = tile_repr[0].pop("values")

        return TileModel(
            resourceinstance_id=uuid.UUID("40000000-0000-0000-0000-000000000000"),
            nodegroup=node.nodegroup,
            data={str(node.pk): tile_repr},
        )

    def test_validate(self):
        reference = DataTypeFactory().get_instance("reference")
        mock_node = SimpleNamespace(config={"multiValue": False})

        for value, message in [
            ([{}], "Missing required value(s): 'uri', 'labels', and 'list_id'"),
            (
                [
                    {
                        "uri": "",
                        "labels": [],  # notice [] rather than None
                        "list_id": str(uuid.uuid4()),
                    }
                ],
                "Missing required value(s): 'labels'",
            ),
            (
                [
                    {
                        "uri": "https://www.domain.com/123",
                        "labels": [],
                        "garbage_key": "garbage_value",
                    }
                ],
                "Unexpected value: 'garbage_key'",
            ),
        ]:
            with self.subTest(reference_value=value):
                errors = reference.validate(value, node=mock_node)
                self.assertEqual(len(errors), 1, errors)
                self.assertEqual(errors[0]["message"], message)

        mock_list_item_id = uuid.uuid4()
        data = {
            "uri": "https://www.domain.com/label",
            "labels": [
                {
                    "id": "23b4efbd-2e46-4b3f-8d75-2f3b2bb96af2",
                    "value": "label",
                    "language_id": "en",
                    "list_item_id": str(mock_list_item_id),
                    "valuetype_id": "prefLabel",
                },
                {
                    "id": "e8676242-f0c7-4e3d-b031-fded4960cd86",
                    "language_id": "de",
                    "list_item_id": str(mock_list_item_id),
                    "valuetype_id": "prefLabel",
                },
            ],
            "list_id": uuid.uuid4(),
        }

        # Label missing value property
        errors = reference.validate(value=[data], node=mock_node)
        self.assertEqual(len(errors), 1, errors)

        data["labels"][1]["value"] = "a label"
        data["labels"][1]["language_id"] = "en"

        # Too many prefLabels per language
        errors = reference.validate(value=[data], node=mock_node)
        self.assertEqual(len(errors), 1, errors)

        data["labels"][1]["value"] = "ein label"
        data["labels"][1]["language_id"] = "de"
        data["labels"][1]["list_item_id"] = str(uuid.uuid4())

        # Mixed list_item_id values
        errors = reference.validate(value=[data], node=mock_node)
        self.assertEqual(len(errors), 1, errors)

        data["labels"][1]["list_item_id"] = str(mock_list_item_id)

        # Valid
        errors = reference.validate(value=[data], node=mock_node)
        self.assertEqual(errors, [])

        # None is always valid.
        errors = reference.validate(value=None, node=mock_node)
        self.assertEqual(errors, [])

        # Too many references
        errors = reference.validate(value=[data, data], node=mock_node)
        self.assertEqual(len(errors), 1, errors)

        # User error (missing arguments)
        errors = reference.validate(value=data)
        self.assertEqual(len(errors), 1, errors)

    def test_tile_clean(self):
        reference = DataTypeFactory().get_instance("reference")
        nodeid = "72048cb3-adbc-11e6-9ccf-14109fd34195"
        resourceinstanceid = "40000000-0000-0000-0000-000000000000"
        data = [
            {
                "uri": "https://www.domain.com/label",
                "labels": [
                    {
                        "id": "23b4efbd-2e46-4b3f-8d75-2f3b2bb96af2",
                        "value": "label",
                        "language_id": "en",
                        "valuetype_id": "prefLabel",
                        "list_item_id": str(uuid.uuid4()),
                    },
                ],
                "list_id": "fd9508dc-2aab-4c46-85ae-dccce1200035",
            }
        ]

        tile_info = {
            "resourceinstance_id": resourceinstanceid,
            "parenttile_id": "",
            "nodegroup_id": nodeid,
            "tileid": "",
            "data": {nodeid: {"en": data}},
        }

        tile1 = Tile(tile_info)
        reference.clean(tile1, nodeid)
        self.assertIsNotNone(tile1.data[nodeid])

        tile1.data[nodeid] = []
        reference.clean(tile1, nodeid)
        self.assertIsNone(tile1.data[nodeid])

    def test_dataclass_roundtrip(self):
        reference = DataTypeFactory().get_instance("reference")
        list1_pk = str(List.objects.get(name="list1").pk)
        config = {"controlledList": list1_pk}
        tile_val = reference.transform_value_for_tile("label1-pref", **config)
        materialized = reference.to_python(tile_val)
        # This transformation will visit the database.
        tile_val_reparsed = reference.transform_value_for_tile(materialized, **config)
        self.assertEqual(tile_val_reparsed, tile_val)
        # This one will not.
        serialized_reference = reference.serialize(materialized)
        self.assertEqual(serialized_reference, tile_val)
        # Also test None.
        self.assertIsNone(reference.serialize(None))

    def test_transform_value_for_tile(self):
        reference = DataTypeFactory().get_instance("reference")
        list1_pk = str(List.objects.get(name="list1").pk)
        config = {"controlledList": list1_pk}

        tile_value0 = reference.transform_value_for_tile("label1-pref", **config)
        self.assertIsInstance(tile_value0, list)
        self.assertIn("uri", tile_value0[0])
        self.assertIn("labels", tile_value0[0])
        self.assertIn("list_id", tile_value0[0])

        self.assertIsNone(reference.transform_value_for_tile(None, **config))

        # Test multiple incoming values (e.g. from csv import)
        tile_value1 = reference.transform_value_for_tile(
            "label1-pref,label3-pref", **config
        )
        self.assertEqual(len(tile_value1), 2)

        # Test proper parsing of values with commas
        ListItemValue.objects.filter(
            value="label2-pref", list_item_id__list_id=list1_pk
        ).update(value="label2,with-commas")
        ListItemValue.objects.filter(
            value="label3-pref", list_item_id__list_id=list1_pk
        ).update(value="label3,with-commas")
        tile_value2 = reference.transform_value_for_tile(
            '"label2,with-commas","label3,with-commas"', **config
        )
        self.assertEqual(len(tile_value2), 2)

        # Test custom delimiter
        tile_value2b = reference.transform_value_for_tile(
            "label2,with-commas;label3,with-commas",
            **{**config, "delimiter": ";", "quotechar": '"'},
        )
        self.assertEqual(len(tile_value2b), 2)

        # Test deterministic sorting:
        #   Force two items to have the same prefLabel in a list,
        #   expect the list item with lower sortorder to be returned
        expected_list_item_pk = str(
            ListItem.objects.get(
                list_item_values__value="label1-pref", list_id=list1_pk
            ).pk
        )
        ListItemValue.objects.filter(
            value="label2,with-commas", list_item_id__list_id=list1_pk
        ).update(value="label1-pref")
        tile_value3 = reference.transform_value_for_tile("label1-pref", **config)
        self.assertEqual(
            tile_value3[0]["labels"][0]["list_item_id"], expected_list_item_pk
        )

    def test_to_json(self):
        reference = DataTypeFactory().get_instance("reference")
        node = ListTests.node_using_list1
        mock_tile = self.get_mock_tile()
        representation = reference.to_json(mock_tile, node)

        self.assertEqual(
            representation["@display_value"],
            "label0-pref",
        )

        mock_tile = Tile(data={str(node.pk): None})
        self.assertEqual(reference.to_json(mock_tile, node)["@display_value"], "")

    def test_get_display_value(self):
        reference = DataTypeFactory().get_instance("reference")
        node = ListTests.node_using_list1
        mock_tile1 = self.get_mock_tile()
        labels = mock_tile1.data[str(node.pk)][0]["labels"]
        french_label = {
            **labels[0],
            "language_id": "fr",
            "value": labels[0]["value"] + "-french",
        }
        labels.append(french_label)
        self.assertEqual(reference.get_display_value(mock_tile1, node), "label0-pref")
        self.assertEqual(
            reference.get_display_value(mock_tile1, node, language="fr"),
            "label0-pref-french",
        )

        mock_tile2 = Tile(
            {
                "resourceinstance_id": "50000000-0000-0000-0000-000000000000",
                "nodegroup_id": str(node.nodegroup_id),
                "tileid": "",
                "data": {str(node.pk): None},
            }
        )
        self.assertEqual(reference.get_display_value(mock_tile2, node), "")

    def test_get_display_value_context_in_bulk(self):
        reference = DataTypeFactory().get_instance("reference")
        node = ListTests.node_using_list1
        mock_tile = self.get_mock_tile()
        node_value = mock_tile.data[str(node.pk)]
        five_identical_node_values = [node_value] * 5

        qs = reference.get_display_value_context_in_bulk(five_identical_node_values)
        with self.assertNumQueries(3):
            # 1: list items
            # 2: list item labels
            # 3: children
            self.assertEqual(len(qs), 1)
        with self.assertNumQueries(0):
            qs[0].build_select_option()

    def test_get_details(self):
        reference = DataTypeFactory().get_instance("reference")
        node = ListTests.node_using_list1
        mock_tile = self.get_mock_tile()
        details = reference.get_details(mock_tile.data[str(node.pk)])
        self.assertEqual(
            set(details[0]),
            {
                "list_item_id",
                "list_item_values",
                "display_value",
                "children",
                "sortorder",
                "uri",
            },
        )

    def test_transform_export_values(self):
        reference = DataTypeFactory().get_instance("reference")
        node = ListTests.node_using_list1
        mock_tile = self.get_mock_tile()
        node_value = mock_tile.data[str(node.pk)]

        # Export as URI
        self.assertEqual(
            reference.transform_export_values(
                node_value, concept_export_value_type="id"
            ),
            "https://archesproject.org/0",
        )
        # Export as label
        self.assertEqual(
            reference.transform_export_values(
                node_value, concept_export_value_type="label"
            ),
            "label0-pref",
        )

    def test_collects_multiple_values(self):
        reference = DataTypeFactory().get_instance("reference")
        self.assertIs(reference.collects_multiple_values(), True)

    def test_append_to_document(self):
        datatype = DataTypeFactory().get_instance("reference")
        tile = TileModel(nodegroup_id=uuid.uuid4())
        document = {"references": [], "strings": []}
        list_item_id = uuid.uuid4()
        reference = Reference(
            uri="http://example.com",
            labels=[
                ReferenceLabel(
                    id=uuid.uuid4(),
                    value="Test Label",
                    language_id="en",
                    valuetype_id="prefLabel",
                    list_item_id=list_item_id,
                )
            ],
            list_id=uuid.uuid4(),
        )
        nodevalue = datatype.serialize([reference])

        datatype.append_to_document(document, nodevalue, uuid.uuid4(), tile)

        self.assertEqual(len(document["references"]), 1)
        self.assertEqual(document["references"][0]["uri"], reference.uri)
        self.assertEqual(document["references"][0]["list_id"], reference.list_id)
        self.assertEqual(document["references"][0]["nodegroup_id"], tile.nodegroup_id)
        self.assertFalse(document["references"][0]["provisional"])

        self.assertEqual(len(document["strings"]), 1)
        self.assertEqual(document["strings"][0]["string"], reference.labels[0].value)
        self.assertEqual(document["strings"][0]["nodegroup_id"], tile.nodegroup_id)
        self.assertFalse(document["strings"][0]["provisional"])

    def test_append_search_filters(self):
        mock_node = Mock(Node)
        mock_query = Mock(Bool)
        reference = ReferenceDataType()

        # Test matching query
        mock_query.should = Mock()
        mock_filter_value = [
            {
                "uri": "https://archesproject.org/1",
                "labels": [
                    {
                        "value": "label1-pref",
                        "language_id": "en",
                        "valuetype_id": "prefLabel",
                    }
                ],
            }
        ]
        mock_value = {"op": "eq", "val": mock_filter_value}
        reference.append_search_filters(mock_value, mock_node, mock_query, Mock())
        mock_query.should.assert_called()

        # Test not matching query
        mock_query.reset_mock()
        mock_query.must_not = Mock()
        mock_query.filter = Mock()
        mock_value = {"op": "!eq", "val": mock_filter_value}
        reference.append_search_filters(mock_value, mock_node, mock_query, Mock())
        mock_query.must_not.assert_called()
        mock_query.filter.assert_called()

        # Test in_list_any
        mock_query.reset_mock()
        mock_query.should = Mock()
        mock_value = {"op": "in_list_any", "val": mock_filter_value}
        reference.append_search_filters(mock_value, mock_node, mock_query, Mock())
        mock_query.should.assert_called()

        # Test in_list_all
        mock_query.reset_mock()
        mock_query.must = Mock()
        mock_value = {"op": "in_list_all", "val": mock_filter_value}
        reference.append_search_filters(mock_value, mock_node, mock_query, Mock())
        mock_query.must.assert_called()

        # Test in_list_not
        mock_query.reset_mock()
        mock_query.must_not = Mock()
        mock_value = {"op": "in_list_not", "val": mock_filter_value}
        reference.append_search_filters(mock_value, mock_node, mock_query, Mock())
        mock_query.must_not.assert_called()

        # Test null op
        mock_query.reset_mock()
        mock_query.should = Mock()
        mock_value = {"op": "null", "val": None}
        reference.append_search_filters(mock_value, mock_node, mock_query, Mock())
        mock_query.should.assert_called()

    def test_get_rdf_uri(self):
        reference = ReferenceDataType()
        node = ListTests.node_using_list1

        # Returns None for empty/falsy data
        self.assertIsNone(reference.get_rdf_uri(node, None))
        self.assertIsNone(reference.get_rdf_uri(node, []))

        data = [
            {"uri": "https://archesproject.org/0"},
            {"uri": "https://archesproject.org/1"},
        ]
        result = reference.get_rdf_uri(node, data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], URIRef("https://archesproject.org/0"))
        self.assertEqual(result[1], URIRef("https://archesproject.org/1"))
        self.assertIsInstance(result[0], URIRef)

    def test_to_rdf_empty(self):
        reference = ReferenceDataType()
        edge_info = {"range_tile_data": None, "d_uri": URIRef("http://example.com/r1")}
        edge = Mock()
        g = reference.to_rdf(edge_info, edge)
        self.assertEqual(len(g), 0)

    def test_to_rdf(self):
        reference = ReferenceDataType()
        domain_uri = URIRef("http://example.com/resource/1")
        range_class = "http://www.cidoc-crm.org/cidoc-crm/E55_Type"
        property_uri = "http://www.cidoc-crm.org/cidoc-crm/P2_has_type"
        ref_uri_str = "https://archesproject.org/0"

        edge_info = {
            "range_tile_data": [
                {
                    "uri": ref_uri_str,
                    "labels": [
                        {
                            "value": "Test Label",
                            "language_id": "en",
                            "valuetype_id": "prefLabel",
                        },
                        {
                            "value": "Alt Label",
                            "language_id": "en",
                            "valuetype_id": "altLabel",
                        },
                    ],
                }
            ],
            "d_uri": domain_uri,
        }
        edge = SimpleNamespace(
            rangenode=SimpleNamespace(ontologyclass=range_class),
            ontologyproperty=property_uri,
        )

        g = reference.to_rdf(edge_info, edge)
        ref_uri = URIRef(ref_uri_str)

        # Type triple
        self.assertIn((ref_uri, RDF.type, URIRef(range_class)), g)
        # Property triple
        self.assertIn((domain_uri, URIRef(property_uri), ref_uri), g)
        # prefLabel triple
        from rdflib import Literal

        self.assertIn((ref_uri, RDFS.label, Literal("Test Label", lang="en")), g)
        # altLabel should NOT produce an rdfs:label triple
        self.assertEqual(len(list(g.triples((ref_uri, RDFS.label, None)))), 1)

    def test_to_rdf_multiple_refs(self):
        reference = ReferenceDataType()
        domain_uri = URIRef("http://example.com/resource/1")
        edge_info = {
            "range_tile_data": [
                {"uri": "https://archesproject.org/0", "labels": []},
                {"uri": "https://archesproject.org/1", "labels": []},
            ],
            "d_uri": domain_uri,
        }
        edge = SimpleNamespace(
            rangenode=SimpleNamespace(
                ontologyclass="http://www.cidoc-crm.org/cidoc-crm/E55_Type"
            ),
            ontologyproperty="http://www.cidoc-crm.org/cidoc-crm/P2_has_type",
        )

        g = reference.to_rdf(edge_info, edge)
        # 2 type triples + 2 property triples = 4
        self.assertEqual(len(g), 4)

    def test_from_rdf_single_known_uri(self):
        reference = ReferenceDataType()
        item = ListItem.objects.get(uri="https://archesproject.org/0")
        expected = item.build_tile_value()

        result = reference.from_rdf({"@id": "https://archesproject.org/0"})
        self.assertEqual(result["uri"], expected["uri"])
        self.assertEqual(result["list_id"], expected["list_id"])

    def test_from_rdf_single_unknown_uri(self):
        reference = ReferenceDataType()
        result = reference.from_rdf({"@id": "https://unknown.example.com/999"})
        self.assertIsNone(result)

    def test_from_rdf_missing_id(self):
        reference = ReferenceDataType()
        result = reference.from_rdf({"@type": "some_type"})
        self.assertIsNone(result)

    def test_from_rdf_list(self):
        reference = ReferenceDataType()
        json_ld_nodes = [
            {"@id": "https://archesproject.org/0"},
            {"@id": "https://unknown.example.com/999"},
            {"@id": "https://archesproject.org/1"},
        ]
        result = reference.from_rdf(json_ld_nodes)
        # Unknown URI is filtered out
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["uri"], "https://archesproject.org/0")
        self.assertEqual(result[1]["uri"], "https://archesproject.org/1")

    def test_from_rdf_empty_list(self):
        reference = ReferenceDataType()
        result = reference.from_rdf([])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_accepts_rdf_uri(self):
        reference = ReferenceDataType()
        self.assertTrue(reference.accepts_rdf_uri("https://archesproject.org/0"))
        self.assertTrue(
            reference.accepts_rdf_uri(URIRef("https://archesproject.org/0"))
        )
        self.assertFalse(
            reference.accepts_rdf_uri("https://nonexistent.example.com/999")
        )

    def test_ignore_keys(self):
        reference = ReferenceDataType()
        keys = reference.ignore_keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(len(keys), 1)
        self.assertIn(str(RDFS.label), keys[0])
        self.assertIn(str(RDFS.Literal), keys[0])

    def test_to_python_directly(self):
        reference = ReferenceDataType()

        # Falsy inputs → None
        self.assertIsNone(reference.to_python(None))
        self.assertIsNone(reference.to_python([]))

        # Valid reference
        list_item_id = uuid.uuid4()
        result = reference.to_python(
            [
                {
                    "uri": "https://example.com/1",
                    "labels": [
                        {
                            "id": str(uuid.uuid4()),
                            "value": "Test",
                            "language_id": "en",
                            "valuetype_id": "prefLabel",
                            "list_item_id": str(list_item_id),
                        }
                    ],
                    "list_id": str(uuid.uuid4()),
                }
            ]
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Reference)
        self.assertIsInstance(result[0].labels[0], ReferenceLabel)
        # list_item_id is stored as the raw string value passed in
        self.assertEqual(result[0].labels[0].list_item_id, str(list_item_id))

    def test_serialize(self):
        reference = ReferenceDataType()

        # None → None
        self.assertIsNone(reference.serialize(None))

        # Reference dataclass → asdict
        ref = Reference(
            uri="https://example.com/ref",
            labels=[
                ReferenceLabel(
                    id=uuid.uuid4(),
                    value="Test",
                    language_id="en",
                    valuetype_id="prefLabel",
                    list_item_id=uuid.uuid4(),
                )
            ],
            list_id=uuid.uuid4(),
        )
        result = reference.serialize([ref])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uri"], ref.uri)
        self.assertEqual(len(result[0]["labels"]), 1)

        # Plain dict → spread passthrough
        raw = {"uri": "https://example.com/dict", "labels": [], "list_id": "abc"}
        result2 = reference.serialize([raw])
        self.assertEqual(result2[0]["uri"], raw["uri"])

    def test_validate_node(self):
        reference = ReferenceDataType()
        node = Mock()

        # Valid UUID → no exception
        node.config = {"controlledList": str(uuid.uuid4())}
        reference.validate_node(node)

        # Missing key → raises
        node.config = {}
        with self.assertRaises(GraphValidationError):
            reference.validate_node(node)

        # None value → raises
        node.config = {"controlledList": None}
        with self.assertRaises(GraphValidationError):
            reference.validate_node(node)

        # Invalid UUID string → ValueError propagates (only TypeError/KeyError are caught)
        node.config = {"controlledList": "not-a-uuid"}
        with self.assertRaises(ValueError):
            reference.validate_node(node)

    def test_transform_exception(self):
        # TypeError: missing required args
        e = TypeError("__init__() missing 1 required positional argument: 'uri'")
        result = ReferenceDataType.transform_exception(e)
        self.assertEqual(result["type"], "ERROR")
        self.assertIn("Missing required value(s):", result["message"])
        self.assertIn("Invalid Reference Datatype Value", result["title"])

        # TypeError: unexpected keyword argument
        e = TypeError("__init__() got an unexpected keyword argument 'garbage'")
        result = ReferenceDataType.transform_exception(e)
        self.assertIn("Unexpected value:", result["message"])

        # TypeError: no args → falls through to "Unknown error"
        e = TypeError()
        result = ReferenceDataType.transform_exception(e)
        self.assertIn("Unknown error", result["message"])

        # ValueError with message
        e = ValueError("Custom error message")
        result = ReferenceDataType.transform_exception(e)
        self.assertEqual(result["message"], "Custom error message")

        # ValueError: no args → "Unknown error"
        e = ValueError()
        result = ReferenceDataType.transform_exception(e)
        self.assertIn("Unknown error", result["message"])

        # Other exception type → "Unknown error"
        e = RuntimeError("something unexpected")
        result = ReferenceDataType.transform_exception(e)
        self.assertIn("Unknown error", result["message"])

    def test_validate_multivalue_nodeid_lookup(self):
        reference = ReferenceDataType()
        node = ListTests.node_using_list1

        parsed = reference.to_python(
            [
                {
                    "uri": "https://example.com",
                    "labels": [
                        {
                            "id": str(uuid.uuid4()),
                            "value": "Test",
                            "language_id": "en",
                            "valuetype_id": "prefLabel",
                            "list_item_id": str(uuid.uuid4()),
                        }
                    ],
                    "list_id": str(uuid.uuid4()),
                },
            ]
        )

        # Valid nodeid → fetches node, single value is allowed on non-multiValue node
        self.assertIsNone(reference.validate_multivalue(parsed, None, str(node.pk)))

        # Nonexistent nodeid → Node.DoesNotExist caught, returns without raising
        self.assertIsNone(
            reference.validate_multivalue(parsed, None, str(uuid.uuid4()))
        )

        two_refs = parsed + parsed
        # Neither node nor nodeid → raises ValueError
        with self.assertRaises(ValueError):
            reference.validate_multivalue(two_refs, None, None)

        # Two references on a non-multiValue node → raises ValueError
        with self.assertRaises(ValueError):
            reference.validate_multivalue(two_refs, node, None)

        # Two references on a multiValue node passes validation
        self.assertIsNone(
            reference.validate_multivalue(
                two_refs, None, str(ListTests.node_using_list2.pk)
            )
        )

        # Node.DoesNotExist with multiValue True (should not raise, should return None)
        # Patch Node.objects.get to raise DoesNotExist and simulate multiValue True
        with patch("arches.app.models.models.Node.objects.get") as mock_get:
            mock_get.side_effect = Node.DoesNotExist
            # Should return None, not raise
            self.assertIsNone(
                reference.validate_multivalue(two_refs, None, str(uuid.uuid4()))
            )

    def test_lookup_listitem_from_label(self):
        reference = ReferenceDataType()
        list1_pk = str(ListTests.list1.pk)

        # Valid lookup returns the expected item
        result = reference.lookup_listitem_from_label("label1-pref", list1_pk)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ListItem)

        # Empty value → None
        self.assertIsNone(reference.lookup_listitem_from_label("", list1_pk))

        # None list_id → None
        self.assertIsNone(reference.lookup_listitem_from_label("label1-pref", None))

        # Nonexistent label → None
        self.assertIsNone(
            reference.lookup_listitem_from_label("xyz_no_such_label", list1_pk)
        )

    def test_transform_value_for_tile_uuid_string(self):
        reference = DataTypeFactory().get_instance("reference")
        config = {"controlledList": str(ListTests.list1.pk)}

        # UUID string for a known item → resolved to tile value
        item = ListTests.list1.list_items.get(sortorder=0)
        result = reference.transform_value_for_tile([str(item.pk)], **config)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("uri", result[0])
        self.assertIn("labels", result[0])

        # UUID string for unknown item → not found → empty list
        result_not_found = reference.transform_value_for_tile(
            [str(uuid.uuid4())], **config
        )
        self.assertEqual(result_not_found, [])

        # Reference object → passes through as asdict
        ref = Reference(
            uri="https://example.com/passthrough",
            labels=[
                ReferenceLabel(
                    id=uuid.uuid4(),
                    value="Passthrough",
                    language_id="en",
                    valuetype_id="prefLabel",
                    list_item_id=uuid.uuid4(),
                )
            ],
            list_id=uuid.uuid4(),
        )
        result_ref = reference.transform_value_for_tile([ref], **config)
        self.assertEqual(len(result_ref), 1)
        self.assertEqual(result_ref[0]["uri"], ref.uri)

    def test_transform_export_values_extended(self):
        reference = DataTypeFactory().get_instance("reference")
        node = ListTests.node_using_list1
        mock_tile = self.get_mock_tile()
        node_value = mock_tile.data[str(node.pk)]

        # None value → implicit None return
        self.assertIsNone(reference.transform_export_values(None))

        # concept_export_value_type="" → treated as "label"
        self.assertEqual(
            reference.transform_export_values(node_value, concept_export_value_type=""),
            "label0-pref",
        )

        # concept_export_value_type=None → treated as "label"
        self.assertEqual(
            reference.transform_export_values(
                node_value, concept_export_value_type=None
            ),
            "label0-pref",
        )

    def test_get_details_none(self):
        reference = DataTypeFactory().get_instance("reference")

        # None → None
        self.assertIsNone(reference.get_details(None))

        # Empty list → None (hits `else: return None` branch)
        self.assertIsNone(reference.get_details([]))

    def test_get_details_with_datatype_context(self):
        reference = DataTypeFactory().get_instance("reference")
        node = ListTests.node_using_list1
        mock_tile = self.get_mock_tile()
        value = mock_tile.data[str(node.pk)]

        list_item_id = uuid.UUID(value[0]["labels"][0]["list_item_id"])
        item = (
            ListItem.objects.filter(pk=list_item_id)
            .with_list_item_labels()
            .prefetch_related("children")
            .first()
        )

        # Item provided in context → taken from context rather than fetched separately
        details = reference.get_details(value, datatype_context=[item])
        self.assertEqual(len(details), 1)
        self.assertIn("list_item_id", details[0])

    def test_default_es_mapping(self):
        reference = ReferenceDataType()
        mapping = reference.default_es_mapping()
        self.assertIn("properties", mapping)
        self.assertEqual(mapping["properties"]["uri"]["type"], "keyword")
        self.assertEqual(mapping["properties"]["id"]["type"], "keyword")
        self.assertIn("labels", mapping["properties"])

    def test_append_search_filters_text_ops(self):
        reference = ReferenceDataType()
        mock_node = Mock(Node)
        mock_node.config = {"controlledList": str(ListTests.list1.pk)}
        mock_query = Mock()

        # Ops that search by label value or URI and find matches
        for op, term in [
            ("like", "label1"),
            ("startswith", "label1"),
            ("like_uri", "archesproject"),
            ("startswith_uri", "https://archesproject"),
        ]:
            with self.subTest(op=op):
                mock_query.reset_mock()
                mock_query.must = Mock()
                reference.append_search_filters(
                    {"op": op, "val": term}, mock_node, mock_query, Mock()
                )
                mock_query.must.assert_called()

        # No matching items → must called with _no_match_ sentinel
        mock_query.reset_mock()
        mock_query.must = Mock()
        reference.append_search_filters(
            {"op": "like", "val": "xyz_absolutely_no_match_xyz"},
            mock_node,
            mock_query,
            Mock(),
        )
        mock_query.must.assert_called()

    def test_append_search_filters_not_null(self):
        reference = ReferenceDataType()
        mock_node = Mock(Node)
        mock_query = Mock()
        # Should delegate to append_null_search_filters without raising
        reference.append_search_filters(
            {"op": "not_null", "val": None}, mock_node, mock_query, Mock()
        )

    def test_append_search_filters_empty_val(self):
        reference = ReferenceDataType()
        mock_node = Mock(Node)
        mock_query = Mock()
        # Empty val list → falls through without calling should/must
        reference.append_search_filters(
            {"op": "eq", "val": []}, mock_node, mock_query, Mock()
        )
        mock_query.should.assert_not_called()
        mock_query.must.assert_not_called()

    def test_append_search_filters_missing_op(self):
        reference = ReferenceDataType()
        mock_node = Mock(Node)
        mock_query = Mock()
        # KeyError on missing "op" is caught silently
        reference.append_search_filters({"val": []}, mock_node, mock_query, Mock())

    def test_append_to_document_provisional(self):
        datatype = DataTypeFactory().get_instance("reference")
        tile = TileModel(nodegroup_id=uuid.uuid4())
        document = {"references": [], "strings": []}
        ref = Reference(
            uri="http://example.com/provisional",
            labels=[
                ReferenceLabel(
                    id=uuid.uuid4(),
                    value="Provisional Label",
                    language_id="en",
                    valuetype_id="prefLabel",
                    list_item_id=uuid.uuid4(),
                )
            ],
            list_id=uuid.uuid4(),
        )
        nodevalue = datatype.serialize([ref])
        datatype.append_to_document(
            document, nodevalue, uuid.uuid4(), tile, provisional=True
        )
        self.assertTrue(document["references"][0]["provisional"])
        self.assertTrue(document["strings"][0]["provisional"])
