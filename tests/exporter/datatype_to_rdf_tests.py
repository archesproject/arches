"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import os
from tests import test_settings
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.models.models import ResourceInstance
from tests.base_test import ArchesTestCase
from arches.app.utils.skos import SKOSReader
from arches.app.models.concept import Concept
from arches.app.datatypes.datatypes import DataTypeFactory
from rdflib import Namespace, URIRef, Literal, Graph
from rdflib.namespace import RDF, RDFS, XSD
from arches.app.utils.data_management.resources.formats.rdffile import RdfWriter
from mock import Mock

# these tests can be run from the command line via
# python manage.py test tests/exporter/datatype_to_rdf_tests.py --settings="tests.test_settings"

ARCHES_NS = Namespace(test_settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
CIDOC_NS = Namespace("http://www.cidoc-crm.org/cidoc-crm/")


class RDFExportUnitTests(ArchesTestCase):
    """
    Unit tests for the `to_rdf` method on Datatype classes.
    """

    @classmethod
    def setUpClass(cls):
        ResourceInstance.objects.all().delete()

        for skospath in ["tests/fixtures/data/rdf_export_thesaurus.xml", "tests/fixtures/data/rdf_export_collections.xml"]:
            skos = SKOSReader()
            rdf = skos.read_file(skospath)
            ret = skos.save_concepts_from_skos(rdf)

        # Models
        for model_name in ["object_model", "document_model"]:
            with open(os.path.join("tests/fixtures/resource_graphs/rdf_export_{0}.json".format(model_name)), "rU") as f:
                archesfile = JSONDeserializer().deserialize(f)
            ResourceGraphImporter(archesfile["graph"])

    def setUp(self):
        # for RDF/JSON-LD export tests
        self.DT = DataTypeFactory()

    @classmethod
    def tearDownClass(cls):
        pass

    # test_rdf_* - * = datatype (rdf fragment) or full graph

    def test_rdf_string(self):
        dt = self.DT.get_instance("string")
        edge_info, edge = mock_edge(1, CIDOC_NS["name"], None, "", "test string")
        graph = dt.to_rdf(edge_info, edge)
        obj = Literal(edge_info["range_tile_data"])
        self.assertTrue((edge_info["d_uri"], edge.ontologyproperty, obj) in graph)

    def test_rdf_None_string(self):
        dt = self.DT.get_instance("string")
        edge_info, edge = mock_edge(1, CIDOC_NS["name"], None, "", None)
        graph = dt.to_rdf(edge_info, edge)
        self.assertTrue(len(graph) == 0)  # the graph should be empty

    def test_rdf_number(self):
        dt = self.DT.get_instance("number")
        edge_info, edge = mock_edge(1, CIDOC_NS["some_value"], None, "", 42)
        graph = dt.to_rdf(edge_info, edge)
        obj = Literal(edge_info["range_tile_data"])
        self.assertTrue((edge_info["d_uri"], edge.ontologyproperty, obj) in graph)

    def test_rdf_None_number(self):
        dt = self.DT.get_instance("number")
        edge_info, edge = mock_edge(1, CIDOC_NS["some_value"], None, "", None)
        graph = dt.to_rdf(edge_info, edge)
        self.assertTrue(len(graph) == 0)  # the graph should be empty

    def test_rdf_bool(self):
        dt = self.DT.get_instance("boolean")
        edge_info, edge = mock_edge(1, CIDOC_NS["some_value"], None, "", True)
        graph = dt.to_rdf(edge_info, edge)
        obj = Literal(edge_info["range_tile_data"])
        self.assertTrue((edge_info["d_uri"], edge.ontologyproperty, obj) in graph)

    def test_rdf_None_bool(self):
        dt = self.DT.get_instance("boolean")
        edge_info, edge = mock_edge(1, CIDOC_NS["some_value"], None, "", None)
        graph = dt.to_rdf(edge_info, edge)
        self.assertTrue(len(graph) == 0)  # the graph should be empty

    def test_rdf_date(self):
        dt = self.DT.get_instance("date")
        edge_info, edge = mock_edge(1, CIDOC_NS["some_value"], None, "", "2018-12-11")
        graph = dt.to_rdf(edge_info, edge)
        obj = Literal(edge_info["range_tile_data"], datatype=XSD.dateTime)
        self.assertTrue((edge_info["d_uri"], edge.ontologyproperty, obj) in graph)

    def test_rdf_resource(self):
        dt = self.DT.get_instance("resource-instance")
        edge_info, edge = mock_edge(1, CIDOC_NS["some_value"], None, "", {"resourceId": 2})
        graph = dt.to_rdf(edge_info, edge)
        self.assertTrue((edge_info["d_uri"], edge.ontologyproperty, edge_info["r_uri"]) in graph)

    def test_rdf_resource_list(self):
        dt = self.DT.get_instance("resource-instance-list")
        res_inst_list = [{"resourceId": 2}, {"resourceId": 3}, {"resourceId": 4}, {"resourceId": 5}]
        edge_info, edge = mock_edge(1, CIDOC_NS["some_value"], None, "", res_inst_list)
        graph = dt.to_rdf(edge_info, edge)
        for res_inst in res_inst_list:
            self.assertTrue((edge_info["d_uri"], edge.ontologyproperty, ARCHES_NS["resources/{0}".format(res_inst["resourceId"])]) in graph)

    def test_rdf_domain(self):
        dt = self.DT.get_instance("domain-value")
        edge_info, edge = mock_edge(1, CIDOC_NS["some_value"], None, "", "3f0aaf74-f7d9-44ae-82cf-196c76d8cbc3")
        # will have to further mock the range node for domain
        append_domain_config_to_node(edge.rangenode)
        graph = dt.to_rdf(edge_info, edge)
        self.assertTrue((edge_info["d_uri"], edge.ontologyproperty, Literal("one")) in graph)

    def test_rdf_domain_list(self):
        dt = self.DT.get_instance("domain-value-list")
        dom_list = ["3f0aaf74-f7d9-44ae-82cf-196c76d8cbc3", "11755d2b-36ee-4de7-8639-6914925a1f86", "ebd99837-c7d9-4be0-b5f5-87f387ae0661"]
        dom_text = ["one", "four", "six"]

        edge_info, edge = mock_edge(1, CIDOC_NS["some_value"], None, "", dom_list)
        # will have to further mock the range node for domain
        append_domain_config_to_node(edge.rangenode)
        graph = dt.to_rdf(edge_info, edge)
        for item in dom_text:
            self.assertTrue((edge_info["d_uri"], edge.ontologyproperty, Literal(item)) in graph)
        self.assertFalse((edge_info["d_uri"], edge.ontologyproperty, Literal("Not Domain Text")) in graph)

    def test_rdf_concept(self):
        dt = self.DT.get_instance("concept")
        # d75977c1-635b-41d5-b53d-1c82d2237b67 should be the ConceptValue for "junk sculpture"
        # Main concept should be 0ad97528-0fb0-43bf-afee-0fb9dde78b99
        # should also have an identifier of http://vocab.getty.edu/aat/300047196

        edge_info = {}
        edge_info["range_tile_data"] = "d75977c1-635b-41d5-b53d-1c82d2237b67"
        edge_info["r_uri"] = URIRef("http://vocab.getty.edu/aat/300047196")
        edge_info["d_uri"] = URIRef("test")
        edge = Mock()
        edge.ontologyproperty = CIDOC_NS["P2_has_type"]
        edge.rangenode.ontologyclass = CIDOC_NS["E55_Type"]

        graph = dt.to_rdf(edge_info, edge)
        print(graph.serialize(format="ttl"))
        self.assertTrue((edge_info["d_uri"], edge.ontologyproperty, URIRef("http://vocab.getty.edu/aat/300047196")) in graph)
        self.assertTrue((URIRef("http://vocab.getty.edu/aat/300047196"), RDFS.label, Literal("junk sculpture")) in graph)

    def test_rdf_concept_list(self):
        dt = self.DT.get_instance("concept-list")
        concept_list = [
            "d75977c1-635b-41d5-b53d-1c82d2237b67",  # junk sculpture@en, has aat identifier
            "4beb7055-8a6e-45a3-9bfb-32984b6f82e0",  # "example document type"@en-us, no ext id}
        ]

        edge_info = {}
        edge_info["range_tile_data"] = concept_list
        edge_info["r_uri"] = URIRef("http://vocab.getty.edu/aat/300047196")
        edge_info["d_uri"] = URIRef("test")
        edge = Mock()
        edge.ontologyproperty = CIDOC_NS["P2_has_type"]
        edge.rangenode.ontologyclass = CIDOC_NS["E55_Type"]
        graph = dt.to_rdf(edge_info, edge)

        edge_info["r_uri"] = ARCHES_NS["concepts/037daf4d-054a-44d2-9c0a-108b59e39109"]
        graph += dt.to_rdf(edge_info, edge)

        self.assertTrue((edge_info["d_uri"], edge.ontologyproperty, URIRef("http://vocab.getty.edu/aat/300047196")) in graph)
        self.assertTrue((URIRef("http://vocab.getty.edu/aat/300047196"), RDFS.label, Literal("junk sculpture")) in graph)
        self.assertTrue((edge_info["d_uri"], edge.ontologyproperty, ARCHES_NS["concepts/037daf4d-054a-44d2-9c0a-108b59e39109"]) in graph)
        self.assertTrue((ARCHES_NS["concepts/037daf4d-054a-44d2-9c0a-108b59e39109"], RDFS.label, Literal("example document type")) in graph)


def append_domain_config_to_node(node):
    node.config = {
        "options": [
            {"id": "3f0aaf74-f7d9-44ae-82cf-196c76d8cbc3", "selected": False, "text": "one"},
            {"id": "eccaa586-284b-4f98-b4db-bdf8bdc9efcb", "selected": False, "text": "two"},
            {"id": "ac843999-864a-4d43-9bb9-aa3197958c7a", "selected": False, "text": "three"},
            {"id": "11755d2b-36ee-4de7-8639-6914925a1f86", "selected": False, "text": "four"},
            {"id": "848a65b7-51f6-47f2-8ced-4c5398e956d4", "selected": False, "text": "five"},
            {"id": "ebd99837-c7d9-4be0-b5f5-87f387ae0661", "selected": False, "text": "six"},
        ]
    }


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
