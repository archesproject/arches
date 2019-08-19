'''
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
'''

import os
from tests import test_settings
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.models.models import ResourceInstance
from tests.base_test import ArchesTestCase
from arches.app.utils.skos import SKOSReader
from arches.app.datatypes.datatypes import DataTypeFactory
from rdflib import Namespace
from rdflib.namespace import RDF, RDFS, XSD, SKOS, DCTERMS
from pyld.jsonld import compact, frame, from_rdf
from arches.app.utils.data_management.resources.formats.rdffile import JsonLdReader
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.models.graph import Graph

# these tests can be run from the command line via
# python manage.py test tests/importer/datatype_from_rdf_tests.py --settings="tests.test_settings"

ARCHES_NS = Namespace(test_settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
CIDOC_NS = Namespace("http://www.cidoc-crm.org/cidoc-crm/")


class FalseAmbiguityJSONLDUnitTests(ArchesTestCase):
    """
    Unit tests for the `from_rdf` method on Datatype classes.
    """
    @classmethod
    def setUpClass(cls):
        ResourceInstance.objects.all().delete()

        for skospath in ['tests/fixtures/data/5121-thesaurus.xml',
                         'tests/fixtures/data/5121-collections.xml']:
            skos = SKOSReader()
            rdf = skos.read_file(skospath)
            ret = skos.save_concepts_from_skos(rdf)

        with open('tests/fixtures/data/5121-model.json', 'rU') as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile['graph'])

        with open('tests/fixtures/data/5121-falseambiguity.json', 'rU') as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile['graph'])

    def setUp(self):
        # for RDF/JSON-LD export tests
        self.DT = DataTypeFactory()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_jsonld_concept_list_full_import(self):
        reader = JsonLdReader()
        slug = "9f716aa2-bf96-11e9-bd39-0242ac160002"
        resourceid = "72e6a574-bfa5-11e9-b4dc-0242ac160002"
        graphid = models.GraphModel.objects.get(slug=slug).pk

        raw_data = """
{"@id": "http://localhost:8000/resources/72e6a574-bfa5-11e9-b4dc-0242ac160002",
 "@type": "http://www.cidoc-crm.org/cidoc-crm/E21_Person",
 "http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by":
  {"@id": "http://localhost:8000/tile/17fa1306-d48f-434e-ad37-fc4c9b09d979/node/d1af9e9e-bf96-11e9-b4dc-0242ac160002",
    "@type": "http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object",
    "http://www.cidoc-crm.org/cidoc-crm/P2_has_type":
      { "@id": "http://localhost:8000/concepts/0bb450bc-8fe3-46cb-968e-2b56849e6e96",
         "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
         "http://www.w3.org/2000/01/rdf-schema#label": "Concept 1"},
   "http://www.cidoc-crm.org/cidoc-crm/P3_has_note": "Test Content"}
}
"""

        # The above concepts map onto the following ConceptValue UUIDs with the default lang
        # Concept 2 -> '9a94ce98-4d76-4405-89df-b9ddeaddfae1'
        # Concept 1 -> 'ac1d498c-9c61-4573-bfe8-1653641c028a'

        data = JSONDeserializer().deserialize(raw_data)
        reader.read_resource(data, resourceid=resourceid, graphid=graphid)
        if reader.errors:
            response = []
            for value in reader.errors.itervalues():
                response.append(value.message)
            print(response)
        self.assertTrue(len(reader.errors) == 0)
