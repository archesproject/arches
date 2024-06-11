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

import random
import os, uuid
from django.test import TransactionTestCase
from django.test.utils import captured_stdout
from django.db import connection, connections
from django.core import management
from tests.base_test import ArchesTestCase
from arches.app.models import models
from arches.app.models.models import SpatialView
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from arches.app.utils.data_management.resource_graphs.importer import import_graph as resource_graph_importer
from arches.app.utils.i18n import LanguageSynchronizer
from tests import test_settings
from django.conf import settings

# these tests can be run from the command line via
# python manage.py test tests.models.spatialview_model_tests --settings="tests.test_settings"
SLEEP_TIME = 1

class SpatialViewTests(ArchesTestCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        spatialviews_other_test_model_path = os.path.join(
            test_settings.TEST_ROOT, "fixtures", "resource_graphs", "SpatialViews_Other_Model.json"
        )
        spatialviews_test_model_path = os.path.join(
            test_settings.TEST_ROOT, "fixtures", "resource_graphs", "SpatialViews_Test_Model.json"
        )

        spatialviews_other_test_data_path = os.path.join(
            test_settings.TEST_ROOT, "fixtures", "data", "json", "Spatialviews_Other_Model_Data.json"
        )
        spatialviews_test_data_path = os.path.join(
            test_settings.TEST_ROOT, "fixtures", "data", "json", "SpatialViews_Test_Model_Data.json"
        )
        with captured_stdout():
            management.call_command("packages", operation="import_graphs", source=spatialviews_other_test_model_path, verbosity=0)
            management.call_command("packages", operation="import_graphs", source=spatialviews_test_model_path, verbosity=0)
            BusinessDataImporter(spatialviews_other_test_data_path).import_business_data()
            BusinessDataImporter(spatialviews_test_data_path).import_business_data()

        # load en concepts value
        self.extra_concept_value_id = "ac41d9be-79db-4256-b368-2f4559cfbe66"
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO values(valueid, conceptid, valuetype, value, languageid) VALUES (%s, '00000000-0000-0000-0000-000000000007', 'prefLabel', '(en) is related to', 'en');", [self.extra_concept_value_id])
        self.extra_concept_value_id = "ac41d9be-79db-4256-b368-2f4559cfbe66"
    
    @classmethod
    def tearDownClass(self):
        # delete extra concept value
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM values WHERE valueid = %s;", [self.extra_concept_value_id])

        super().tearDownClass()


    def setUp(self):
        # test ids
        self.spatialviews_test_model_id = "5db49c51-2c70-47b3-b7be-66afced863c8"
        self.spatialviews_other_test_model_id = "114dd3fb-404d-4fb3-a639-1333b89cf60c"
        self.spatialview_id = "47ddb63e-9d04-4953-910a-b780759c22e9"
        self.spatialview_geometrynode_id = "95b2c8de-1cf8-11ef-971a-0242ac130005"
        self.spatialview_invalid_geometrynode_id = "7584e966-1cf8-11ef-971a-0242ac130005"
        self.generated_spatialview_ids = []
    
    def find_postgres_views_with_name(self, schema_name, view_name):
        view_count = 0
        with connections[f"{test_settings.DATABASES['default']['NAME']}"].cursor() as cursor:
            cursor.execute("SELECT viewname FROM pg_views WHERE viewname = %s and schemaname = %s", [view_name, schema_name])
            views = cursor.fetchall()
            view_count = len(views)
        return view_count
    
    def get_language_instance(self, language):
        return models.Language.objects.get(code=language)

    def generate_valid_spatiatview(self):
        spatialview = SpatialView()
        spatialview.spatialviewid = uuid.uuid4()
        spatialview.schema = "public"
        spatialview.slug = "spatialviews_test_" + str(random.randint(1, 1000))
        spatialview.description = "test_description"
        spatialview.geometrynode = models.Node.objects.get(nodeid=self.spatialview_geometrynode_id)
        spatialview.ismixedgeometrytypes = False # Discreet geometry
        spatialview.language = self.get_language_instance("en")
        spatialview.isactive = True
        spatialview.attributenodes = [
            {"nodeid": "a379b7ac-1cf8-11ef-ab82-0242ac130005", "description": "gridref"},
            {"nodeid": "bee90060-1cf8-11ef-971a-0242ac130005", "description": "name"},
            {"nodeid": "ccfe0a6a-1cf8-11ef-971a-0242ac130005", "description": "date"},
            {"nodeid": "d1a59230-1cf9-11ef-a1fe-0242ac130005", "description": "concept_list"},
            {"nodeid": "d2a55a44-1cf9-11ef-a1fe-0242ac130005", "description": "bool"},
            {"nodeid": "d2f5d474-1cf9-11ef-a1fe-0242ac130005", "description": "non_local_string"},
            {"nodeid": "e514005a-1cf8-11ef-971a-0242ac130005", "description": "edtf_date"},
            {"nodeid": "e674837a-1cf8-11ef-971a-0242ac130005", "description": "count"},
            {"nodeid": "e70850dc-1cf8-11ef-971a-0242ac130005", "description": "url"},
            {"nodeid": "fe3a586c-1cf9-11ef-a1fe-0242ac130005", "description": "domain"},
            {"nodeid": "298ef7ac-1cfa-11ef-a1fe-0242ac130005", "description": "file"},
            {"nodeid": "0e65f1d4-1cf9-11ef-971a-0242ac130005", "description": "concept"},
            {"nodeid": "0e8d1560-1cfa-11ef-a1fe-0242ac130005", "description": "domain_list"},
            {"nodeid": "348eb80a-1cf9-11ef-ab82-0242ac130005", "description": "other_spatialviews"},
            {"nodeid": "54fc2d0c-1cf9-11ef-ab82-0242ac130005", "description": "other_models_list"}
        ]
        return spatialview

    def test_create_spatialview_discreet_geometry(self):
        spatialview = self.generate_valid_spatiatview()

        spatialview.save()

        fetched_spatialview = SpatialView.objects.get(pk=spatialview.spatialviewid)
        self.assertTrue(fetched_spatialview.spatialviewid == spatialview.spatialviewid)

        spatialview.delete()


    def test_create_spatialview_mixed_geometry(self):

        spatialview = self.generate_valid_spatiatview()
        spatialview.ismixedgeometrytypes = True
        spatialview.save()

        fetched_spatialview = SpatialView.objects.get(pk=spatialview.spatialviewid)
        self.assertTrue(fetched_spatialview.spatialviewid == spatialview.spatialviewid and fetched_spatialview.ismixedgeometrytypes == True)

        spatialview.delete()


    def test_create_spatialview_invalid_geometrynode(self):
        spatialview = self.generate_valid_spatiatview()
        spatialview.geometrynode = models.Node.objects.get(nodeid="7584e966-1cf8-11ef-971a-0242ac130005")
        node_type = spatialview.geometrynode.datatype

        with self.assertRaises(Exception):
           spatialview.save()

        with self.assertRaises(SpatialView.DoesNotExist):
            fetched_spatialview = SpatialView.objects.get(pk=spatialview.spatialviewid)
    
    
    def test_create_spatialview_invalid_attributenode(self):
        spatialview = self.generate_valid_spatiatview()
        spatialview.attributenodes.append({"nodeid": "7584e966-1cf8-9999-9999-0242ac130005", "description": "invalid"})

        with self.assertRaises(Exception):
           spatialview.save()

        with self.assertRaises(SpatialView.DoesNotExist):
            fetched_spatialview = SpatialView.objects.get(pk=spatialview.spatialviewid)


    def test_create_spatialview_invalid_language(self):
        spatialview = self.generate_valid_spatiatview()
        spatialview.language = self.get_language_instance("fr")

        with self.assertRaises(Exception):
           spatialview.save()

        with self.assertRaises(SpatialView.DoesNotExist):
            fetched_spatialview = SpatialView.objects.get(pk=spatialview.spatialviewid)
        


    def test_create_spatialview_invalid_schema(self):
        spatialview = self.generate_valid_spatiatview()
        spatialview.schema = "invalid"
        
        with self.assertRaises(Exception):
           spatialview.save()

        with self.assertRaises(SpatialView.DoesNotExist):
            fetched_spatialview = SpatialView.objects.get(pk=spatialview.spatialviewid)
        


    def test_create_spatialview_invalid_slug(self):
        spatialview = self.generate_valid_spatiatview()
        spatialview.slug = "1_invalid"
        
        with self.assertRaises(Exception):
           spatialview.save()

        with self.assertRaises(SpatialView.DoesNotExist):
            fetched_spatialview = SpatialView.objects.get(pk=spatialview.spatialviewid)

            

    def test_spatial_view_isactive_set_to_false_removes_views(self):
        
        # first create a valid spatial view that isactive=True
        spatialview = self.generate_valid_spatiatview()
        spatialview.save()

        self.assertTrue(SpatialView.objects.filter(spatialviewid=spatialview.spatialviewid).exists())

        # now set isactive=False
        spatialview.isactive = False
        spatialview.save()

        self.assertTrue(SpatialView.objects.filter(spatialviewid=spatialview.spatialviewid).exists())

        spatialview.delete()

class SpatialViewTriggerTests(TransactionTestCase):

    serialized_rollback = True

    def setUp(self):
        LanguageSynchronizer.synchronize_settings_with_db()

        spatialviews_other_test_model_path = os.path.join(
            test_settings.TEST_ROOT, "fixtures", "resource_graphs", "SpatialViews_Other_Model.json"
        )
        spatialviews_test_model_path = os.path.join(
            test_settings.TEST_ROOT, "fixtures", "resource_graphs", "SpatialViews_Test_Model.json"
        )

        spatialviews_other_test_data_path = os.path.join(
            test_settings.TEST_ROOT, "fixtures", "data", "json", "Spatialviews_Other_Model_Data.json"
        )
        spatialviews_test_data_path = os.path.join(
            test_settings.TEST_ROOT, "fixtures", "data", "json", "SpatialViews_Test_Model_Data.json"
        )
        
        with captured_stdout():
            management.call_command("packages", operation="import_graphs", source=spatialviews_other_test_model_path, verbosity=0)
            management.call_command("packages", operation="import_graphs", source=spatialviews_test_model_path, verbosity=0)
            BusinessDataImporter(spatialviews_other_test_data_path).import_business_data()
            BusinessDataImporter(spatialviews_test_data_path).import_business_data()

        self.spatialviews_test_model_id = "5db49c51-2c70-47b3-b7be-66afced863c8"
        self.spatialviews_other_test_model_id = "114dd3fb-404d-4fb3-a639-1333b89cf60c"
        self.spatialview_geometrynode_id = "95b2c8de-1cf8-11ef-971a-0242ac130005"

        # load en concepts value
        self.extra_concept_value_id = "ac41d9be-79db-4256-b368-2f4559cfbe66"
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO values(valueid, conceptid, valuetype, value, languageid) VALUES (%s, '00000000-0000-0000-0000-000000000007', 'prefLabel', '(en) is related to', 'en');", [self.extra_concept_value_id])
        self.extra_concept_value_id = "ac41d9be-79db-4256-b368-2f4559cfbe66"
        
        # create a spatialview with objects to test triggers
        self.spatialview_slug = "spatialviews_test"
        self.test_spatial_view = self.generate_valid_spatiatview()
        self.test_spatial_view.save()
        self.spatialview_id = self.test_spatial_view.spatialviewid


    
    def get_language_instance(self, language):
        return models.Language.objects.get(code=language)
    
    
    def generate_valid_spatiatview(self):
        spatialview = SpatialView()
        spatialview.spatialviewid = uuid.uuid4()
        spatialview.schema = "public"
        spatialview.slug = self.spatialview_slug
        spatialview.description = "test description"
        spatialview.geometrynode = models.Node.objects.get(nodeid="95b2c8de-1cf8-11ef-971a-0242ac130005") #self.spatialview_geometrynode_id)
        spatialview.ismixedgeometrytypes = False # Discreet geometry
        spatialview.language = self.get_language_instance("en")
        spatialview.isactive = True
        spatialview.attributenodes = [
            {"nodeid": "a379b7ac-1cf8-11ef-ab82-0242ac130005", "description": "gridref"},
            {"nodeid": "bee90060-1cf8-11ef-971a-0242ac130005", "description": "name"},
            {"nodeid": "ccfe0a6a-1cf8-11ef-971a-0242ac130005", "description": "date"},
            {"nodeid": "d1a59230-1cf9-11ef-a1fe-0242ac130005", "description": "concept_list"},
            {"nodeid": "d2a55a44-1cf9-11ef-a1fe-0242ac130005", "description": "bool"},
            {"nodeid": "d2f5d474-1cf9-11ef-a1fe-0242ac130005", "description": "non_local_string"},
            {"nodeid": "e514005a-1cf8-11ef-971a-0242ac130005", "description": "edtf_date"},
            {"nodeid": "e674837a-1cf8-11ef-971a-0242ac130005", "description": "count"},
            {"nodeid": "e70850dc-1cf8-11ef-971a-0242ac130005", "description": "url"},
            {"nodeid": "fe3a586c-1cf9-11ef-a1fe-0242ac130005", "description": "domain"},
            {"nodeid": "298ef7ac-1cfa-11ef-a1fe-0242ac130005", "description": "file"},
            {"nodeid": "0e65f1d4-1cf9-11ef-971a-0242ac130005", "description": "concept"},
            {"nodeid": "0e8d1560-1cfa-11ef-a1fe-0242ac130005", "description": "domain_list"},
            {"nodeid": "348eb80a-1cf9-11ef-ab82-0242ac130005", "description": "other_spatialviews"},
            {"nodeid": "54fc2d0c-1cf9-11ef-ab82-0242ac130005", "description": "other_models_list"}
        ]
        return spatialview

    def test_check_spatialview_row_values(self):
        """
        Test views for the spatial view are created and have the correct values
        """
        # check spatial view got created
        self.assertTrue(SpatialView.objects.filter(spatialviewid=self.spatialview_id).exists())
        
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    gid, 
                    tileid, 
                    nodeid, 
                    geom, 
                    resourceinstanceid, 
                    gridref, 
                    name, 
                    date, 
                    concept_list, 
                    bool, 
                    non_local_string, 
                    edtf_date, 
                    count, 
                    url, 
                    domain, 
                    file, 
                    concept, 
                    domain_list, 
                    other_spatialviews, 
                    other_models_list 
                FROM public.{self.test_spatial_view.slug}_polygon""")
            rows = cursor.fetchall()
            self.assertTrue(len(rows) == 1)
            row = rows[0]
            self.assertTrue(row[5] == "ABC123") # gridref
            self.assertTrue(row[6] == "Bat Willow") # name
            self.assertTrue(row[7] == "2024-05-10") # date
            self.assertTrue(row[8] == "(en) is related to") # concept_list
            self.assertTrue(row[9] == "true") # bool (disabled as boolean node)
            self.assertTrue(row[10] == "non-local") # non_local_string
            self.assertTrue(row[11] == "2010") # edtf_date
            self.assertTrue(row[12] == "11111") # count
            self.assertTrue(row[13] == "https://www.cnbc.com")  # url
            self.assertTrue(row[14] == "1") # domain
            self.assertTrue(row[15] == "Arches Project, elastic.png") # file
            self.assertTrue(row[16] == "(en) is related to") # concept
            self.assertTrue(row[17] == "george, john, ringo, Paul") # domain_list
            self.assertTrue(row[18] == "Bat Willow") # other_spatialviews
            self.assertTrue(row[19] == "Other Model 2") # other_models_list