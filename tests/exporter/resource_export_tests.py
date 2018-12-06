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
import json
import unicodecsv
from io import BytesIO
from tests import test_settings
from operator import itemgetter
from django.core import management
from tests.base_test import ArchesTestCase
from arches.app.utils.skos import SKOSReader
from arches.app.models.concept import Concept
from arches.app.models.models import TileModel, ResourceInstance
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from arches.app.utils.data_management.resources.exporter import ResourceExporter as BusinessDataExporter
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.datatypes.datatypes import DataTypeFactory
from rdflib import Namespace, URIRef, Literal, Graph
from rdflib.namespace import RDF, RDFS, XSD
from arches.app.utils.data_management.resources.formats.rdffile import RdfWriter
from mock import Mock

# these tests can be run from the command line via
# python manage.py test tests/exporter/resource_export_tests.py --pattern="*.py" --settings="tests.test_settings"

def Mock_Edge(s_uri_str, p_uri_str, o_uri_str, domain_tile_data, range_tile_data,
              s_type_str=None, o_type_str=None):
    # (S, P, O triple, tiledata for domainnode, td for rangenode, S's type, O's type)
    edge = Mock()
    edge_info = {}

    edge_info['r_uri'] = edge.rangenode_id = edge.rangenode.pk = o_uri_str
    edge_info['d_uri'] = edge.domainnode_id = edge.domainnode.pk = s_uri_str
    edge.ontologyproperty = p_uri_str
    edge.domainnode.ontologyclass = s_type_str
    edge.rangenode.ontologyclass = o_type_str

    edge_info['range_tile_data'] = range_tile_data
    edge_info['domain_tile_data'] = domain_tile_data
    return edge_info, edge

class BusinessDataExportTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        ResourceInstance.objects.all().delete()

        skos = SKOSReader()
        rdf = skos.read_file('tests/fixtures/data/concept_label_test_scheme.xml')
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file('tests/fixtures/data/concept_label_test_collection.xml')
        ret = skos.save_concepts_from_skos(rdf)

        with open(os.path.join('tests/fixtures/resource_graphs/resource_export_test.json'), 'rU') as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile['graph'])

        # loading RDF/JSONLD export fixtures
        skos = SKOSReader()
        rdf = skos.read_file('tests/fixtures/data/rdf_export_thesaurus.xml')
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file('tests/fixtures/data/rdf_export_collections.xml')
        ret = skos.save_concepts_from_skos(rdf)

        # Models
        for model_name in ['object_model', 'document_model']:
            with open(os.path.join('tests/fixtures/resource_graphs/rdf_export_{0}.json'.format(model_name)), 'rU') as f:
                archesfile = JSONDeserializer().deserialize(f)
            ResourceGraphImporter(archesfile['graph'])
        # Fixture Instance Data for tests
        for instance_name in ['document', 'object']:
            BusinessDataImporter('tests/fixtures/data/rdf_export_{0}.json'.format(instance_name)).import_business_data()


        # for RDF/JSON-LD export tests
        self.DT = DataTypeFactory()
        self.archesproject = Namespace(test_settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
        self.cidoc = Namespace("http://www.cidoc-crm.org/cidoc-crm/")

    @classmethod
    def tearDownClass(cls):
        pass

    def test_csv_export(self):
        BusinessDataImporter('tests/fixtures/data/csv/resource_export_test.csv').import_business_data()

        export = BusinessDataExporter('csv',
                                      configs='tests/fixtures/data/csv/resource_export_test.mapping',
                                      single_file=True).export()
        csv_export = filter(lambda export: 'csv' in export['name'],
                            export)[0]['outputfile'].getvalue().split('\r')
        csv_output = list(unicodecsv.DictReader(BytesIO(export[0]['outputfile'].getvalue()), encoding='utf-8-sig'))[0]

        csvinputfile = 'tests/fixtures/data/csv/resource_export_test.csv'
        csv_input = list(unicodecsv.DictReader(open(csvinputfile, 'rU'),
                         encoding='utf-8-sig',
                         restkey='ADDITIONAL',
                         restval='MISSING'))[0]

        self.assertDictEqual(csv_input, csv_output)

    def test_json_export(self):

        def deep_sort(obj):
            """
            Recursively sort list or dict nested lists. Taken from
            https://stackoverflow.com/questions/18464095/how-to-achieve-assertdictequal-with-assertsequenceequal-applied-to-values
            """

            if isinstance(obj, dict):
                _sorted = {}
                for key in sorted(obj):
                    _sorted[key] = deep_sort(obj[key])

            elif isinstance(obj, list):
                new_list = []
                for val in obj:
                    new_list.append(deep_sort(val))
                _sorted = sorted(new_list)

            else:
                _sorted = obj

            return _sorted

        BusinessDataImporter(
            'tests/fixtures/data/json/resource_export_business_data_truth.json').import_business_data()

        export = BusinessDataExporter('json').export('ab74af76-fa0e-11e6-9e3e-026d961c88e6')
        json_export = deep_sort(json.loads(export[0]['outputfile'].getvalue()))

        json_truth = deep_sort(json.loads(
            open('tests/fixtures/data/json/resource_export_business_data_truth.json').read()))

        self.assertDictEqual(json_export, json_truth)

    # test_rdf_* - * = datatype (rdf fragment) or full graph
    # test_jsonld_* -> focus on jsonld correct framing and export

    def test_rdf_string(self):
        str_dt = self.DT.get_instance("string")
        pass
