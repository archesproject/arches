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
from operator import itemgetter, attrgetter
from tests import test_settings
from tests.base_test import ArchesTestCase
from django.core import management
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONSerializer

# these tests can be run from the command line via
# python manage.py test tests/importer/ontology_import_tests.py --pattern="*.py" --settings="tests.test_settings"


class OntologyModelTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        management.call_command("load_ontology", source=test_settings.ONTOLOGY_FIXTURES)

    @classmethod
    def tearDownClass(cls):
        ontology = models.Ontology.objects.get(pk="11111111-0000-0000-0000-000000000000")
        ontology.delete()

    def test_load_ontology(self):
        ontology_class = models.OntologyClass.objects.get(
            ontology__pk="11111111-0000-0000-0000-000000000000", source="http://www.cidoc-crm.org/cidoc-crm/E53_Place"
        )

        predicted_property_list = {
            "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            "http://www.cidoc-crm.org/cidoc-crm/P2_has_type",
            "http://www.cidoc-crm.org/cidoc-crm/P3_has_note",
            "http://www.cidoc-crm.org/cidoc-crm/P48_has_preferred_identifier",
            "http://www.cidoc-crm.org/cidoc-crm/P137_exemplifies",
            "http://www.cidoc-crm.org/cidoc-crm/P15i_influenced",
            "http://www.cidoc-crm.org/cidoc-crm/P17i_motivated",
            "http://www.cidoc-crm.org/cidoc-crm/P136i_supported_type_creation",
            "http://www.cidoc-crm.org/cidoc-crm/P62i_is_depicted_by",
            "http://www.cidoc-crm.org/cidoc-crm/P67i_is_referred_to_by",
            "http://www.cidoc-crm.org/cidoc-crm/P70i_is_documented_in",
            "http://www.cidoc-crm.org/cidoc-crm/P71i_is_listed_in",
            "http://www.cidoc-crm.org/cidoc-crm/P129i_is_subject_of",
            "http://www.cidoc-crm.org/cidoc-crm/P138i_has_representation",
            "http://www.cidoc-crm.org/cidoc-crm/P140i_was_attributed_by",
            "http://www.cidoc-crm.org/cidoc-crm/P39i_was_measured_by",
            "http://www.cidoc-crm.org/cidoc-crm/P41i_was_classified_by",
            "http://www.cidoc-crm.org/cidoc-crm/P141i_was_assigned_by",
            "http://www.cidoc-crm.org/cidoc-crm/P87_is_identified_by",
            "http://www.cidoc-crm.org/cidoc-crm/P89_falls_within",
            "http://www.cidoc-crm.org/cidoc-crm/P121_overlaps_with",
            "http://www.cidoc-crm.org/cidoc-crm/P122_borders_with",
            "http://www.cidoc-crm.org/cidoc-crm/P157_is_at_rest_relative_to",
            "http://www.cidoc-crm.org/cidoc-crm/P168_place_is_defined_by",
            "http://www.cidoc-crm.org/cidoc-crm/P7i_witnessed",
            "http://www.cidoc-crm.org/cidoc-crm/P26i_was_destination_of",
            "http://www.cidoc-crm.org/cidoc-crm/P27i_was_origin_of",
            "http://www.cidoc-crm.org/cidoc-crm/P53i_is_former_or_current_location_of",
            "http://www.cidoc-crm.org/cidoc-crm/P54i_is_current_permanent_location_of",
            "http://www.cidoc-crm.org/cidoc-crm/P55i_currently_holds",
            "http://www.cidoc-crm.org/cidoc-crm/P59i_is_located_on_or_within",
            "http://www.cidoc-crm.org/cidoc-crm/P74i_is_current_or_former_residence_of",
            "http://www.cidoc-crm.org/cidoc-crm/P89i_contains",
            "http://www.cidoc-crm.org/cidoc-crm/P161i_is_spatial_projection_of",
            "http://www.cidoc-crm.org/cidoc-crm/P156i_is_occupied_by",
            "http://www.cidoc-crm.org/cidoc-crm/P167i_was_place_at",
        }
        self.assertEqual(len(ontology_class.target["down"]), len(predicted_property_list))

        result_property_list = set()
        for item in ontology_class.target["down"]:
            result_property_list.add(item["ontology_property"])
        self.assertEqual(result_property_list, predicted_property_list)

        predicted_subclass_list = {
            "http://www.cidoc-crm.org/cidoc-crm/E41_Appellation",
            "http://www.cidoc-crm.org/cidoc-crm/E42_Identifier",
            "http://www.cidoc-crm.org/cidoc-crm/E44_Place_Appellation",
            "http://www.cidoc-crm.org/cidoc-crm/E45_Address",
            "http://www.cidoc-crm.org/cidoc-crm/E46_Section_Definition" "http://www.cidoc-crm.org/cidoc-crm/E47_Spatial_Coordinates",
            "http://www.cidoc-crm.org/cidoc-crm/E48_Place_Name",
            "http://www.cidoc-crm.org/cidoc-crm/E49_Time_Appellation",
            "http://www.cidoc-crm.org/cidoc-crm/E50_Date",
            "http://www.cidoc-crm.org/cidoc-crm/E75_Conceptual_Object_Appellation",
            "http://www.cidoc-crm.org/cidoc-crm/E82_Actor_Appellation",
            "http://www.cidoc-crm.org/cidoc-crm/E51_Contact_Point",
            "http://www.cidoc-crm.org/cidoc-crm/E35_Title",
        }

        for item in ontology_class.target["down"]:
            if item["ontology_classes"] == "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by":
                self.assertEqual(set(item["ontology_classes"]), predicted_subclass_list)

        # {u'ontology_property': u'P89_falls_within', u'ontology_classes': [u'E53_Place']}
        # {u'ontology_property': u'P89i_contains', u'ontology_classes': [u'E53_Place']}
        # {u'ontology_property': u'P121_overlaps_with', u'ontology_classes': [u'E53_Place']}
        # {u'ontology_property': u'P122_borders_with', u'ontology_classes': [u'E53_Place']}
        # {u'ontology_property': u'P161i_is_spatial_projection_of', u'ontology_classes': [u'E15_Identifier_Assignment', u'E22_Man-Made_Object', u'E86_Leaving', u'E67_Birth', u'E69_Death', u'E8_Acquisition', u'E19_Physical_Object', u'E7_Activity', u'E4_Period', u'E80_Part_Removal', u'E65_Creation', u'E27_Site', u'E87_Curation_Activity', u'E83_Type_Creation', u'E21_Person', u'E78_Collection', u'E81_Transformation', u'E68_Dissolution', u'E5_Event', u'E20_Biological_Object', u'E6_Destruction', u'E63_Beginning_of_Existence', u'E9_Move', u'E12_Production', u'E92_Spacetime_Volume', u'E79_Part_Addition', u'E18_Physical_Thing', u'E16_Measurement', u'E26_Physical_Feature', u'E94_Space', u'E10_Transfer_of_Custody', u'E84_Information_Carrier', u'E17_Type_Assignment', u'E85_Joining', u'E13_Attribute_Assignment', u'E93_Presence', u'E66_Formation', u'E64_End_of_Existence', u'E11_Modification', u'E24_Physical_Man-Made_Thing', u'E14_Condition_Assessment', u'E25_Man-Made_Feature']}
        # {u'ontology_property': u'P87_is_identified_by', u'ontology_classes': [u'E44_Place_Appellation', u'E48_Place_Name', u'E47_Spatial_Coordinates', u'E45_Address', u'E46_Section_Definition']}
        # {u'ontology_property': u'P53i_is_former_or_current_location_of', u'ontology_classes': [u'E22_Man-Made_Object', u'E21_Person', u'E18_Physical_Thing', u'E25_Man-Made_Feature', u'E78_Collection', u'E19_Physical_Object', u'E26_Physical_Feature', u'E84_Information_Carrier', u'E20_Biological_Object', u'E24_Physical_Man-Made_Thing', u'E27_Site']}
        # {u'ontology_property': u'P59i_is_located_on_or_within', u'ontology_classes': [u'E22_Man-Made_Object', u'E21_Person', u'E18_Physical_Thing', u'E25_Man-Made_Feature', u'E78_Collection', u'E19_Physical_Object', u'E26_Physical_Feature', u'E84_Information_Carrier', u'E20_Biological_Object', u'E24_Physical_Man-Made_Thing', u'E27_Site']}
        # {u'ontology_property': u'P156i_is_occupied_by', u'ontology_classes': [u'E22_Man-Made_Object', u'E21_Person', u'E18_Physical_Thing', u'E25_Man-Made_Feature', u'E78_Collection', u'E19_Physical_Object', u'E26_Physical_Feature', u'E84_Information_Carrier', u'E20_Biological_Object', u'E24_Physical_Man-Made_Thing', u'E27_Site']}
        # {u'ontology_property': u'P157_is_at_rest_relative_to', u'ontology_classes': [u'E22_Man-Made_Object', u'E21_Person', u'E18_Physical_Thing', u'E25_Man-Made_Feature', u'E78_Collection', u'E19_Physical_Object', u'E26_Physical_Feature', u'E84_Information_Carrier', u'E20_Biological_Object', u'E24_Physical_Man-Made_Thing', u'E27_Site']}
        # {u'ontology_property': u'P74i_is_current_or_former_residence_of', u'ontology_classes': [u'E40_Legal_Body', u'E74_Group', u'E39_Actor', u'E21_Person']}
        # {u'ontology_property': u'P54i_is_current_permanent_location_of', u'ontology_classes': [u'E84_Information_Carrier', u'E21_Person', u'E22_Man-Made_Object', u'E20_Biological_Object', u'E19_Physical_Object']}
        # {u'ontology_property': u'P55i_currently_holds', u'ontology_classes': [u'E84_Information_Carrier', u'E21_Person', u'E22_Man-Made_Object', u'E20_Biological_Object', u'E19_Physical_Object']}
        # {u'ontology_property': u'P7i_witnessed', u'ontology_classes': [u'E15_Identifier_Assignment', u'E87_Curation_Activity', u'E67_Birth', u'E69_Death', u'E8_Acquisition', u'E7_Activity', u'E4_Period', u'E80_Part_Removal', u'E65_Creation', u'E86_Leaving', u'E16_Measurement', u'E81_Transformation', u'E68_Dissolution', u'E5_Event', u'E6_Destruction', u'E63_Beginning_of_Existence', u'E9_Move', u'E12_Production', u'E79_Part_Addition', u'E83_Type_Creation', u'E10_Transfer_of_Custody', u'E17_Type_Assignment', u'E85_Joining', u'E13_Attribute_Assignment', u'E66_Formation', u'E64_End_of_Existence', u'E11_Modification', u'E14_Condition_Assessment']}
        # {u'ontology_property': u'P168_place_is_defined_by', u'ontology_classes': [u'E94_Space']}
        # {u'ontology_property': u'P26i_was_destination_of', u'ontology_classes': [u'E9_Move']}
        # {u'ontology_property': u'P27i_was_origin_of', u'ontology_classes': [u'E9_Move']}
        # {u'ontology_property': u'P39i_was_measured_by', u'ontology_classes': [u'E16_Measurement']}
        # {u'ontology_property': u'P140i_was_attributed_by', u'ontology_classes': [u'E15_Identifier_Assignment', u'E16_Measurement', u'E17_Type_Assignment', u'E13_Attribute_Assignment', u'E14_Condition_Assessment']}
        # {u'ontology_property': u'P141i_was_assigned_by', u'ontology_classes': [u'E15_Identifier_Assignment', u'E16_Measurement', u'E17_Type_Assignment', u'E13_Attribute_Assignment', u'E14_Condition_Assessment']}
        # {u'ontology_property': u'P48_has_preferred_identifier', u'ontology_classes': [u'E42_Identifier']}
        # {u'ontology_property': u'P2_has_type', u'ontology_classes': [u'E57_Material', u'E58_Measurement_Unit', u'E56_Language', u'E55_Type']}
        # {u'ontology_property': u'P137_exemplifies', u'ontology_classes': [u'E57_Material', u'E58_Measurement_Unit', u'E56_Language', u'E55_Type']}
        # {u'ontology_property': u'P1_is_identified_by', u'ontology_classes': [u'E51_Contact_Point', u'E75_Conceptual_Object_Appellation', u'E42_Identifier', u'E45_Address', u'E41_Appellation', u'E44_Place_Appellation', u'E35_Title', u'E50_Date', u'E82_Actor_Appellation', u'E48_Place_Name', u'E49_Time_Appellation', u'E47_Spatial_Coordinates', u'E46_Section_Definition']}
        # {u'ontology_property': u'P67i_is_referred_to_by', u'ontology_classes': [u'E37_Mark', u'E30_Right', u'E89_Propositional_Object', u'E38_Image', u'E29_Design_or_Procedure', u'E36_Visual_Item', u'E32_Authority_Document', u'E31_Document', u'E34_Inscription', u'E73_Information_Object', u'E33_Linguistic_Object', u'E35_Title']}
        # {u'ontology_property': u'P129i_is_subject_of', u'ontology_classes': [u'E37_Mark', u'E30_Right', u'E89_Propositional_Object', u'E38_Image', u'E29_Design_or_Procedure', u'E36_Visual_Item', u'E32_Authority_Document', u'E31_Document', u'E34_Inscription', u'E73_Information_Object', u'E33_Linguistic_Object', u'E35_Title']}
        # {u'ontology_property': u'P136i_supported_type_creation', u'ontology_classes': [u'E83_Type_Creation']}
        # {u'ontology_property': u'P71i_is_listed_in', u'ontology_classes': [u'E32_Authority_Document']}
        # {u'ontology_property': u'P15i_influenced', u'ontology_classes': [u'E15_Identifier_Assignment', u'E12_Production', u'E16_Measurement', u'E13_Attribute_Assignment', u'E87_Curation_Activity', u'E79_Part_Addition', u'E66_Formation', u'E11_Modification', u'E8_Acquisition', u'E14_Condition_Assessment', u'E80_Part_Removal', u'E65_Creation', u'E10_Transfer_of_Custody', u'E7_Activity', u'E17_Type_Assignment', u'E83_Type_Creation', u'E9_Move', u'E85_Joining', u'E86_Leaving']}
        # {u'ontology_property': u'P17i_motivated', u'ontology_classes': [u'E15_Identifier_Assignment', u'E12_Production', u'E16_Measurement', u'E13_Attribute_Assignment', u'E87_Curation_Activity', u'E79_Part_Addition', u'E66_Formation', u'E11_Modification', u'E8_Acquisition', u'E14_Condition_Assessment', u'E80_Part_Removal', u'E65_Creation', u'E10_Transfer_of_Custody', u'E7_Activity', u'E17_Type_Assignment', u'E83_Type_Creation', u'E9_Move', u'E85_Joining', u'E86_Leaving']}
        # {u'ontology_property': u'P70i_is_documented_in', u'ontology_classes': [u'E32_Authority_Document', u'E31_Document']}
        # {u'ontology_property': u'P3_has_note', u'ontology_classes': [u'E62_String']}
        # {u'ontology_property': u'P138i_has_representation', u'ontology_classes': [u'E34_Inscription', u'E37_Mark', u'E36_Visual_Item', u'E38_Image']}
        # {u'ontology_property': u'P62i_is_depicted_by', u'ontology_classes': [u'E84_Information_Carrier', u'E24_Physical_Man-Made_Thing', u'E22_Man-Made_Object', u'E25_Man-Made_Feature', u'E78_Collection']}
        # {u'ontology_property': u'P41i_was_classified_by', u'ontology_classes': [u'E17_Type_Assignment']}
