from unittest import TestCase
from unittest.mock import Mock

from rdflib import ConjunctiveGraph

from arches.app.datatypes.core.non_localized_string import NonLocalizedStringDataType
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import Node
from arches.app.models.tile import Tile
from arches.app.search.elasticsearch_dsl_builder import Bool
from tests.exporter.datatype_to_rdf_tests import ARCHES_NS, CIDOC_NS


class NonLocalizedStringDataTypeTests(TestCase):
    def test_string_validate(self):
        string = NonLocalizedStringDataType()
        some_errors = string.validate(float(1.2))
        self.assertGreater(len(some_errors), 0)
        no_errors = string.validate("Hello World")
        self.assertEqual(len(no_errors), 0)

    def test_string_clean(self):
        string = NonLocalizedStringDataType()
        nodeid1 = "72048cb3-adbc-11e6-9ccf-14109fd34195"
        nodeid2 = "72048cb3-adbc-11e6-9ccf-14109fd34196"

        tile_mock = Mock()
        tile_mock.data = {}
        tile_mock.data[nodeid1] = "''"
        tile_mock.data[nodeid2] = ""
        string.clean(tile_mock, nodeid1)
        self.assertIsNone(tile_mock.data[nodeid1])
        string.clean(tile_mock, nodeid2)
        self.assertIsNone(tile_mock.data[nodeid2])

    def test_append_null_search_filters(self):
        mock_node = Mock(Node)
        mock_query = Mock(Bool)
        mock_query.filter = Mock()
        mock_value = {"op": "null"}
        nonlocalized_string_dt = NonLocalizedStringDataType()
        nonlocalized_string_dt.append_null_search_filters(
            mock_value, mock_node, mock_query, Mock()
        )

        mock_query.filter.assert_called()

    def test_to_rdf(self):
        nonlocalized_string_dt = NonLocalizedStringDataType()
        edge_info, edge = mock_edge(1, CIDOC_NS["name"], None, "", "bob")
        result = nonlocalized_string_dt.to_rdf(edge_info, edge)
        self.assertIsInstance(result, ConjunctiveGraph)

    def test_string_clean_json(self):
        string = DataTypeFactory().get_instance("non-localized-string")
        nodeid1 = "72048cb3-adbc-11e6-9ccf-14109fd34195"
        nodeid2 = "72048cb3-adbc-11e6-9ccf-14109fd34196"
        resourceinstanceid = "40000000-0000-0000-0000-000000000000"

        json_empty_strings = {
            "resourceinstance_id": resourceinstanceid,
            "parenttile_id": "",
            "nodegroup_id": nodeid1,
            "tileid": "",
            "data": {nodeid1: "''", nodeid2: ""},
        }
        tile1 = Tile(json_empty_strings)
        string.clean(tile1, nodeid1)
        self.assertIsNone(tile1.data[nodeid1])
        string.clean(tile1, nodeid2)
        self.assertIsNone(tile1.data[nodeid2])


def mock_edge(
    s_id,
    p_uri_str,
    o_id,
    domain_tile_data,
    range_tile_data,
    s_type_str=CIDOC_NS["E22_Man-Made_Object"],
    o_type_str=None,
    s_pref="resources",
    o_pref="resources",
):
    # (S, P, O triple, tiledata for domainnode, td for rangenode, S's type, O's type)
    edge = Mock()
    edge_info = {}
    edge.domainnode_id = edge.domainnode.pk = s_id
    edge_info["d_uri"] = ARCHES_NS["{0}/{1}".format(s_pref, s_id)]
    edge_info["r_uri"] = None
    edge_info["d_datatype"] = None
    edge_info["r_datatype"] = None
    edge.rangenode_id = edge.rangenode.pk = o_id
    if o_id:
        edge_info["r_uri"] = ARCHES_NS["{0}/{1}".format(o_pref, o_id)]
    edge.ontologyproperty = p_uri_str
    edge.domainnode.ontologyclass = s_type_str
    edge.rangenode.ontologyclass = o_type_str
    edge_info["range_tile_data"] = range_tile_data
    edge_info["domain_tile_data"] = domain_tile_data
    return edge_info, edge
