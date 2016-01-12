# coding: utf-8

import os
from tests import test_settings
from tests import test_setup
from django.core import management
from django.test import SimpleTestCase, TestCase
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.data_management.resources.importer import ResourceLoader
import arches.app.utils.data_management.resources.remover as resource_remover
from arches.management.commands.package_utils import resource_graphs
from arches.management.commands.package_utils import authority_files
from arches.app.models import models
from arches.app.models.entity import Entity
from arches.app.models.resource import Resource
from arches.app.models.concept import Concept
from arches.app.models.concept import ConceptValue
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"

def setUpModule():
    test_setup.install()

class ConceptModelTests(SimpleTestCase):

    def test_create_concept(self):
        """
        Test of basic CRUD on a Concept model

        """

        concept_in = Concept()
        concept_in.nodetype = 'Concept'
        concept_in.values = [ConceptValue({
            #id: '',
            #conceptid: '',
            'type': 'prefLabel',
            'category': 'label',
            'value': 'test pref label',
            'language': 'en-US'
        })]
        concept_in.save()

        concept_out = Concept().get(id=concept_in.id)

        self.assertEqual(concept_out.id, concept_in.id)
        self.assertEqual(concept_out.values[0].value, 'test pref label')

        label = concept_in.values[0] 
        label.value = 'updated pref label'
        concept_in.values[0] = label
        concept_in.save()
        concept_out = Concept().get(id=concept_in.id)

        self.assertEqual(concept_out.values[0].value, 'updated pref label')

        concept_out.delete(delete_self=True)
        with self.assertRaises(models.Concepts.DoesNotExist):
            deleted_concept = Concept().get(id=concept_out.id)


    def test_prefer_preflabel_over_altlabel(self):
        """
        Test to confirm the proper retrieval of the prefLabel based on different language requirements

        """

        concept = Concept()
        concept.values = [
            ConceptValue({
                'type': 'prefLabel',
                'category': 'label',
                'value': 'test pref label en-US',
                'language': 'en-US'
            }),
            ConceptValue({
                'type': 'prefLabel',
                'category': 'label',
                'value': 'test pref label en',
                'language': 'en'
            }),
            ConceptValue({
                'type': 'prefLabel',
                'category': 'label',
                'value': 'test pref label es-SP',
                'language': 'es-SP'
            }),
            ConceptValue({
                'type': 'altLabel',
                'category': 'label',
                'value': 'test alt label en-US',
                'language': 'en-US'
            })
        ]

        self.assertEqual(concept.get_preflabel(lang='en-US').value, 'test pref label en-US')
        self.assertEqual(concept.get_preflabel(lang='en').value, 'test pref label en')
        self.assertEqual(concept.get_preflabel().value, 'test pref label %s' % (test_settings.LANGUAGE_CODE))

    def test_prefer_preflabel_with_just_lang_code_match_over_exact_match_with_altlabel(self):
        """
        Given a language and region, test should pick the preflabel even if that preflabel specifies a language only 
        and even if an altlabel exists with the exact match
        
        """

        concept = Concept()
        concept.values = [
            ConceptValue({
                'type': 'prefLabel',
                'category': 'label',
                'value': 'test pref label en',
                'language': 'en'
            }),
            ConceptValue({
                'type': 'prefLabel',
                'category': 'label',
                'value': 'test pref label es',
                'language': 'es-SP'
            }),
            ConceptValue({
                'type': 'altLabel',
                'category': 'label',
                'value': 'test alt label en-US',
                'language': 'en-US'
            })
        ]

        self.assertEqual(concept.get_preflabel(lang='en-US').value, 'test pref label en')

    def test_get_altlabel_when_no_preflabel_exists(self):
        """
        Given a language and region, test should pick the altlabel when no preflabel exists
        
        """

        concept = Concept()
        concept.values = [
            ConceptValue({
                'type': 'prefLabel',
                'category': 'label',
                'value': 'test pref label es',
                'language': 'es-SP'
            }),
            ConceptValue({
                'type': 'altLabel',
                'category': 'label',
                'value': 'test alt label en-US',
                'language': 'en-US'
            })
        ]

        self.assertEqual(concept.get_preflabel(lang='en-US').value, 'test alt label en-US')

    def test_get_altlabel_when_no_preflabel_exists_and_altlabel_only_specifies_lang_code(self):
        """
        Given a language and region and the system only has values that specify a language code, the 
        the system should pick the altlabel even if the altlabel doesn't specifiy a region
        
        """

        concept = Concept()
        concept.values = [
            ConceptValue({
                'type': 'prefLabel',
                'category': 'label',
                'value': 'test pref label es',
                'language': 'es'
            }),
            ConceptValue({
                'type': 'altLabel',
                'category': 'label',
                'value': 'test alt label en',
                'language': 'en'
            })
        ]

        self.assertEqual(concept.get_preflabel(lang='en-US').value, 'test alt label en')

    def test_get_region_specific_preflabel_when_language_only_version_does_not_exist(self):
        """
        Given a language only and the system only has values that with regions specified, then 
        the system should pick the first preflabel with the same language code 
        
        """

        concept = Concept()
        concept.values = [
            ConceptValue({
                'type': 'prefLabel',
                'category': 'label',
                'value': 'test pref label en-US',
                'language': 'en-US'
            }),
            ConceptValue({
                'type': 'prefLabel',
                'category': 'label',
                'value': 'test pref label es',
                'language': 'es-SP'
            }),
            ConceptValue({
                'type': 'altLabel',
                'category': 'label',
                'value': 'test alt label en-US',
                'language': 'en-US'
            })
        ]

        self.assertEqual(concept.get_preflabel(lang='en').value, 'test pref label en-US')

    def test_get_label_no_exact_match(self):
        """
        Given no match on language code or region, return the first prefLabel found

        """

        values = [
            {'type': 'prefLabel', 'value': 'bier', 'language': 'nl'},
            {'type': 'prefLabel', 'value': 'beer', 'language': 'en'},
        ]
        c = Concept({'values': values})
        pl = c.get_preflabel('fr-BE')
        self.assertEquals(pl.type,'prefLabel')
        self.assertEquals(pl.value,'bier')
        self.assertEquals(pl.language,'nl')
