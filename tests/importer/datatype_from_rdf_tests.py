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
# python manage.py test tests/importer/datatype_from_rdf_tests.py --settings="tests.test_settings"

ARCHES_NS = Namespace(test_settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
CIDOC_NS = Namespace("http://www.cidoc-crm.org/cidoc-crm/")


class RDFImportUnitTests(ArchesTestCase):
    """
    Unit tests for the `from_rdf` method on Datatype classes.
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
        # Fixture Instance Data for tests
        # for instance_name in ['document', 'object']:
        #     BusinessDataImporter(
        #             'tests/fixtures/data/rdf_export_{0}.json'.format(instance_name)).import_business_data()

    def setUp(self):
        # for RDF/JSON-LD export tests
        self.DT = DataTypeFactory()

    @classmethod
    def tearDownClass(cls):
        pass

    # test_jsonld_* -> focus on jsonld correct framing and export

    def test_jsonld_string(self):
        dt = self.DT.get_instance("string")
        # expected fragment, based on conversations about the from_rdf method
        jf = [{"@value": "test string"}]
        resp = dt.from_rdf(jf)
        self.assertTrue(isinstance(resp, str))
        self.assertTrue(resp == "test string")

    def test_jsonld_number(self):
        dt = self.DT.get_instance("number")
        # expected fragment, based on conversations about the from_rdf method
        jf = [{"@value": 42.3}]
        resp = dt.from_rdf(jf)
        self.assertTrue(resp == 42.3)

    def test_jsonld_bool(self):
        dt = self.DT.get_instance("boolean")
        # expected fragment, based on conversations about the from_rdf method
        jf = [{"@value": True}]
        resp = dt.from_rdf(jf)
        self.assertTrue(isinstance(resp, bool))
        self.assertTrue(resp)

    def test_jsonld_date(self):
        dt = self.DT.get_instance("date")
        # expected fragment, based on conversations about the from_rdf method
        jf = [{"@value": "2018-12-18", "@type": "http://www.w3.org/2001/XMLSchema#dateTime"}]
        resp = dt.from_rdf(jf)
        self.assertTrue(resp == "2018-12-18")

    def test_jsonld_resource_http_port(self):
        dt = self.DT.get_instance("resource-instance")
        jf = {
            "@id": "http://localhost:8000/resources/037daf4d-054a-44d2-9c0a-108b59e39109",
            "@type": "http://www.cidoc-crm.org/cidoc-crm/E21_Person",
        }
        resp = dt.from_rdf(jf)
        self.assertTrue(resp[0]["resourceId"] == "037daf4d-054a-44d2-9c0a-108b59e39109")

    def test_jsonld_resource_urn_uuid(self):
        dt = self.DT.get_instance("resource-instance")
        jf = {"@id": "urn:uuid:eccaa586-284b-4f98-b4db-bdf8bdc9efcb", "@type": "http://www.cidoc-crm.org/cidoc-crm/E21_Person"}
        resp = dt.from_rdf(jf)
        self.assertTrue(resp[0]["resourceId"] == "eccaa586-284b-4f98-b4db-bdf8bdc9efcb")

    def test_jsonld_resource_not_a_uuid(self):
        dt = self.DT.get_instance("resource-instance")
        jf = {"@id": "https://en.wikipedia.org/wiki/Alan_Smithee", "@type": "http://www.cidoc-crm.org/cidoc-crm/E21_Person"}
        resp = dt.from_rdf(jf)
        self.assertTrue(resp is None)

    def test_jsonld_concept_internal(self):
        dt = self.DT.get_instance("concept")
        # from the thesaurus that should be loaded into Arches,
        # the following concept value should have a key of 4beb7055-8a6e-45a3-9bfb-32984b6f82e0
        jf = [
            {
                "@id": "http://localhost:8000/concepts/037daf4d-054a-44d2-9c0a-108b59e39109",
                "http://www.w3.org/2000/01/rdf-schema#label": [{"@language": "en-us", "@value": "example document type"}],
                "@type": ["http://www.cidoc-crm.org/cidoc-crm/E55_Type"],
            }
        ]
        resp = dt.from_rdf(jf)
        self.assertTrue(resp == "4beb7055-8a6e-45a3-9bfb-32984b6f82e0")

    def test_jsonld_concept_external(self):
        dt = self.DT.get_instance("concept")
        jf = [
            {
                "@id": "http://vocab.getty.edu/aat/300047196",
                "http://www.w3.org/2000/01/rdf-schema#label": [{"@language": "en", "@value": "junk sculpture"}],
                "@type": ["http://www.cidoc-crm.org/cidoc-crm/E55_Type"],
            }
        ]
        resp = dt.from_rdf(jf)
        self.assertTrue(resp == "d75977c1-635b-41d5-b53d-1c82d2237b67")


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
    edge.rangenode_id = edge.rangenode.pk = o_id
    if o_id:
        edge_info["r_uri"] = ARCHES_NS["{0}/{1}".format(o_pref, o_id)]
    edge.ontologyproperty = p_uri_str
    edge.domainnode.ontologyclass = s_type_str
    edge.rangenode.ontologyclass = o_type_str
    edge_info["range_tile_data"] = range_tile_data
    edge_info["domain_tile_data"] = domain_tile_data
    return edge_info, edge
