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

from django.db import models
from django.test.utils import captured_stdout

from arches.app.models.models import Language, Relation
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.skos import SKOSReader
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.importer.concept_import_tests --settings="tests.test_settings"


class ConceptImportTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        se = SearchEngineFactory().create()
        with captured_stdout():
            se.delete_index(index="terms,concepts")
            se.create_index(index="terms,concepts")
        # management.call_command('packages', operation='import_graphs', source='tests/fixtures/resource_graphs/archesv4_resource.json')

    @classmethod
    def tearDownClass(cls):
        se = SearchEngineFactory().create()
        with captured_stdout():
            se.delete_index(index="terms,concepts")
            se.create_index(index="terms,concepts")

        super().tearDownClass()

    # def test_hierarchical_relationships(self):
    #   result = JSONDeserializer().deserialize(JSONSerializer().serialize(Concept().get(id='09bf4b42-51a8-4ff2-9210-c4e4ae0e6755', include_subconcepts=True, depth_limit=1)))
    #   children = len(result['subconcepts'])
    #   self.assertEqual(children, 3)
    #
    #
    # def test_value_import(self):
    #   result = JSONDeserializer().deserialize(JSONSerializer().serialize(Concept().get(id='f2bb7a67-d3b3-488f-af39-e0773585c23a', include_subconcepts=True, depth_limit=1)))
    #   values = len(result['values'])
    #   self.assertEqual(values, 5)

    def test_case_insensitive_language_codes(self):
        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/data/concept_label_test_collection.xml")
        skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/data/concept_label_mixed_case.xml")
        skos.save_concepts_from_skos(rdf)

        regions_inexact = Language.objects.filter(code__iexact="en-ZA").values("code")
        self.assertQuerySetEqual(regions_inexact, [{"code": "en-ZA"}])

    def test_duplicate_relations_gracefully_skipped(self):
        relations_before = list(Relation.objects.values_list("pk", flat=True))
        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/data/concept_label_test_collection.xml")
        skos.save_concepts_from_skos(rdf, staging_options="stage")

        # Get the created relations into an invalid state by reversing
        # the conceptto & conceptfrom, and try again.
        created_relations = Relation.objects.exclude(pk__in=relations_before)
        created_relations.update(
            conceptfrom=models.F("conceptto"), conceptto=models.F("conceptfrom")
        )

        with self.assertLogs("arches.app.utils.skos", level="WARNING"):
            skos.save_concepts_from_skos(rdf, staging_options="stage")
