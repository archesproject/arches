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

from tests import test_settings
from tests.base_test import ArchesTestCase
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.models.concept import ConceptValue

# these tests can be run from the command line via
# python manage.py test tests/models/concept_model_tests.py --pattern="*.py" --settings="tests.test_settings"


class ConceptModelTests(ArchesTestCase):
    def test_create_concept(self):
        """
        Test of basic CRUD on a Concept model

        """

        concept_in = Concept()
        concept_in.nodetype = "Concept"
        concept_in.values = [
            ConceptValue(
                {
                    # id: '',
                    # conceptid: '',
                    "type": "prefLabel",
                    "category": "label",
                    "value": "test pref label",
                    "language": "en-US",
                }
            )
        ]
        concept_in.save()

        concept_out = Concept().get(id=concept_in.id)

        self.assertEqual(concept_out.id, concept_in.id)
        self.assertEqual(concept_out.values[0].value, "test pref label")

        label = concept_in.values[0]
        label.value = "updated pref label"
        concept_in.values[0] = label
        concept_in.save()
        concept_out = Concept().get(id=concept_in.id)

        self.assertEqual(concept_out.values[0].value, "updated pref label")

        concept_out.delete(delete_self=True)
        with self.assertRaises(models.Concept.DoesNotExist):
            deleted_concept = Concept().get(id=concept_out.id)

    def test_prefer_preflabel_over_altlabel(self):
        """
        Test to confirm the proper retrieval of the prefLabel based on different language requirements

        """

        concept = Concept()
        concept.values = [
            ConceptValue({"type": "prefLabel", "category": "label", "value": "test pref label en-US", "language": "en-US"}),
            ConceptValue({"type": "prefLabel", "category": "label", "value": "test pref label en", "language": "en"}),
            ConceptValue({"type": "prefLabel", "category": "label", "value": "test pref label es-SP", "language": "es-SP"}),
            ConceptValue({"type": "altLabel", "category": "label", "value": "test alt label en-US", "language": "en-US"}),
        ]

        self.assertEqual(concept.get_preflabel(lang="en-US").value, "test pref label en-US")
        self.assertEqual(concept.get_preflabel(lang="en").value, "test pref label en")
        self.assertEqual(concept.get_preflabel().value, "test pref label %s" % (test_settings.LANGUAGE_CODE))

    def test_prefer_preflabel_with_just_lang_code_match_over_exact_match_with_altlabel(self):
        """
        Given a language and region, test should pick the preflabel even if that preflabel specifies a language only 
        and even if an altlabel exists with the exact match
        
        """

        concept = Concept()
        concept.values = [
            ConceptValue({"type": "prefLabel", "category": "label", "value": "test pref label en", "language": "en"}),
            ConceptValue({"type": "prefLabel", "category": "label", "value": "test pref label es", "language": "es-SP"}),
            ConceptValue({"type": "altLabel", "category": "label", "value": "test alt label en-US", "language": "en-US"}),
        ]

        self.assertEqual(concept.get_preflabel(lang="en-US").value, "test pref label en")

    def test_get_altlabel_when_no_preflabel_exists(self):
        """
        Given a language and region, test should pick the altlabel when no preflabel exists
        
        """

        concept = Concept()
        concept.values = [
            ConceptValue({"type": "prefLabel", "category": "label", "value": "test pref label es", "language": "es-SP"}),
            ConceptValue({"type": "altLabel", "category": "label", "value": "test alt label en-US", "language": "en-US"}),
        ]

        self.assertEqual(concept.get_preflabel(lang="en-US").value, "test alt label en-US")

    def test_get_altlabel_when_no_preflabel_exists_and_altlabel_only_specifies_lang_code(self):
        """
        Given a language and region and the system only has values that specify a language code, the 
        the system should pick the altlabel even if the altlabel doesn't specifiy a region
        
        """

        concept = Concept()
        concept.values = [
            ConceptValue({"type": "prefLabel", "category": "label", "value": "test pref label es", "language": "es"}),
            ConceptValue({"type": "altLabel", "category": "label", "value": "test alt label en", "language": "en"}),
        ]

        self.assertEqual(concept.get_preflabel(lang="en-US").value, "test alt label en")

    def test_get_region_specific_preflabel_when_language_only_version_does_not_exist(self):
        """
        Given a language only and the system only has values that with regions specified, then 
        the system should pick the first preflabel with the same language code 
        
        """

        concept = Concept()
        concept.values = [
            ConceptValue({"type": "prefLabel", "category": "label", "value": "test pref label en-US", "language": "en-US"}),
            ConceptValue({"type": "prefLabel", "category": "label", "value": "test pref label es", "language": "es-SP"}),
            ConceptValue({"type": "altLabel", "category": "label", "value": "test alt label en-US", "language": "en-US"}),
        ]

        self.assertEqual(concept.get_preflabel(lang="en").value, "test pref label en-US")

    def test_get_label_no_exact_match(self):
        """
        Given no match on language code or region, return the first prefLabel found

        """

        concept = Concept()
        concept.values = [
            ConceptValue({"type": "prefLabel", "value": "bier", "language": "nl"}),
            ConceptValue({"type": "prefLabel", "category": "label", "value": "beer", "language": "es-SP"}),
            ConceptValue({"type": "altLabel", "category": "label", "value": "test alt label en-US", "language": "en-US"}),
        ]

        pl = concept.get_preflabel("fr-BE")

        self.assertEqual(pl.type, "prefLabel")
        self.assertEqual(pl.value, "bier" or "beer")
        self.assertEqual(pl.language, "nl" or "es-SP")
