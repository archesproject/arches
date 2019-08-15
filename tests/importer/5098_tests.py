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
from arches.app.models.concept import Concept
from arches.app.datatypes.datatypes import DataTypeFactory
from rdflib import Namespace, URIRef, Literal, Graph
from rdflib.namespace import RDF, RDFS, XSD, SKOS, DCTERMS
from arches.app.utils.data_management.resources.formats.rdffile import RdfWriter
from pyld.jsonld import compact, frame, from_rdf
from arches.app.utils.data_management.resources.formats.rdffile import JsonLdReader
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.models.graph import Graph

# these tests can be run from the command line via
# python manage.py test tests/importer/datatype_from_rdf_tests.py --settings="tests.test_settings"

ARCHES_NS = Namespace(test_settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
CIDOC_NS = Namespace("http://www.cidoc-crm.org/cidoc-crm/")


class ConceptListJSONLDUnitTests(ArchesTestCase):
    """
    Unit tests for the `from_rdf` method on Datatype classes.
    """
    @classmethod
    def setUpClass(cls):
        ResourceInstance.objects.all().delete()

        for skospath in ['tests/fixtures/data/5098-thesaurus.xml',
                         'tests/fixtures/data/5098-collections.xml']:
            skos = SKOSReader()
            rdf = skos.read_file(skospath)
            ret = skos.save_concepts_from_skos(rdf)

        with open('tests/fixtures/data/5098-model.json', 'rU') as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile['graph'])

    def setUp(self):
        # for RDF/JSON-LD export tests
        self.DT = DataTypeFactory()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_jsonld_concept_list_expanded(self):
        dt = self.DT.get_instance("concept-list")
        # This is the expanded version of a concept-list fragment:
        jf = [
                {
                  "@id": "http://localhost:8000/concepts/c3c4b8a8-39bb-41e7-af45-3a0c60fa4ddf",
                  "@type": [
                    "http://www.cidoc-crm.org/cidoc-crm/E55_Type"
                  ],
                  "http://www.w3.org/2000/01/rdf-schema#label": [
                    {
                      "@value": "Concept 2"
                    }
                  ]
                },
                {
                  "@id": "http://localhost:8000/concepts/0bb450bc-8fe3-46cb-968e-2b56849e6e96",
                  "@type": [
                    "http://www.cidoc-crm.org/cidoc-crm/E55_Type"
                  ],
                  "http://www.w3.org/2000/01/rdf-schema#label": [
                    {
                      "@value": "Concept 1"
                    }
                  ]
                }
              ]
        resp = dt.from_rdf(jf)
        self.assertTrue(len(resp) == 2)

    def test_jsonld_concept_list_full_import(self):
        reader = JsonLdReader()
        slug = "92ccf5aa-bec9-11e9-bd39-0242ac160002"
        resourceid = "0b4439a8-beca-11e9-b4dc-0242ac160002"
        graphid = models.GraphModel.objects.get(slug=slug).pk

        raw_data = """
{"@id": "http://localhost:8001/resources/0b4439a8-beca-11e9-b4dc-0242ac160002",
"@type": "http://www.cidoc-crm.org/cidoc-crm/E21_Person",
"http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by":
  {"@id": "http://localhost:8000/tile/cad329aa-1802-416e-bbce-5f71e21b1a47/node/accb030c-bec9-11e9-b4dc-0242ac160002",
    "@type": "http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object",
    "http://www.cidoc-crm.org/cidoc-crm/P2_has_type": [
      {"@id": "http://localhost:8000/concepts/c3c4b8a8-39bb-41e7-af45-3a0c60fa4ddf",
      "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
      "http://www.w3.org/2000/01/rdf-schema#label": "Concept 2"},
      {"@id": "http://localhost:8000/concepts/0bb450bc-8fe3-46cb-968e-2b56849e6e96",
      "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
      "http://www.w3.org/2000/01/rdf-schema#label": "Concept 1"}]
  }
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

        # Get the tile with the concept-list in (should be the only tile)
        clist_tile = reader.tiles[reader.tiles.keys()[0]]
        self.assertTrue(len(clist_tile.data.keys()) == 1)  # single datatype node from input
        clist_data = clist_tile.data[clist_tile.data.keys()[0]]
        self.assertTrue('ac1d498c-9c61-4573-bfe8-1653641c028a' in clist_data)  # Concept 1 in list?
        self.assertTrue('9a94ce98-4d76-4405-89df-b9ddeaddfae1' in clist_data)  # Concept 2 in list?
