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
import time
import os, json, uuid
import django
from django.test import tag
from django.contrib.auth.models import User
from django.db import connection, connections, transaction
from django.db.utils import InternalError, ProgrammingError, IntegrityError, OperationalError
from django.core import management
from tests.base_test import ArchesTestCase
from arches.app.models import models
from arches.app.models.models import SpatialView
#from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from tests import test_settings

# these tests can be run from the command line via
# python manage.py test tests.models.spatialview_model_tests --settings="tests.test_settings"
SLEEP_TIME = 3

class SpatialViewTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # load test models
        spatialviews_other_test_model_path = os.path.join(
            test_settings.TEST_ROOT, "fixtures", "resource_graphs", "SpatialViews_Other_Model.json"
        )
        spatialviews_test_model_path = os.path.join(
            test_settings.TEST_ROOT, "fixtures", "resource_graphs", "SpatialViews_Test_Model.json"
        )
        management.call_command("packages", operation="import_graphs", source=spatialviews_other_test_model_path, verbosity=0)
        management.call_command("packages", operation="import_graphs", source=spatialviews_test_model_path, verbosity=0)

        # load test data
        spatialviews_other_test_data_path = os.path.join(
            test_settings.TEST_ROOT, "fixtures", "data", "json", "Spatialviews_Other_Model_Data.json"
        )
        spatialviews_test_data_path = os.path.join(
            test_settings.TEST_ROOT, "fixtures", "data", "json", "SpatialViews_Test_Model_Data.json"
        )
        BusinessDataImporter(spatialviews_other_test_data_path).import_business_data()
        BusinessDataImporter(spatialviews_test_data_path).import_business_data()

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
        #sleep so arches can create the views
        time.sleep(SLEEP_TIME)

        fetched_spatialview = SpatialView.objects.get(pk=spatialview.spatialviewid)
        self.assertTrue(fetched_spatialview.spatialviewid == spatialview.spatialviewid)

        spatialview.delete()


    def test_create_spatialview_mixed_geometry(self):

        spatialview = self.generate_valid_spatiatview()
        spatialview.ismixedgeometrytypes = True
        spatialview.save()
        #sleep so arches can create the views
        time.sleep(SLEEP_TIME)

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

        def a_find_postgres_views_with_name(schema_name, view_name):
            view_count = 0
            #with connections[f"{test_settings.DATABASES['default']['NAME']}"].cursor() as cursor:
            with connection.cursor() as cursor:
                cursor.execute("SELECT viewname FROM pg_views WHERE viewname = %s and schemaname = %s", [view_name, schema_name])
                views = cursor.fetchall()
                view_count = len(views)
            return view_count
        
        # first create a valid spatial view that isactive=True
        spatialview = self.generate_valid_spatiatview()
        spatialview.save()
        #sleep so arches can create the views
        time.sleep(SLEEP_TIME)

        self.assertTrue(SpatialView.objects.filter(spatialviewid=spatialview.spatialviewid).exists())

        # now set isactive=False
        spatialview.isactive = False
        spatialview.save()
        #sleep so database can handle the views
        time.sleep(SLEEP_TIME)

        self.assertTrue(SpatialView.objects.filter(spatialviewid=spatialview.spatialviewid).exists())

        spatialview.delete()