import json
import random
import os, uuid
from django.test import TestCase, RequestFactory, TransactionTestCase
from django.urls import reverse
from tests.base_test import ArchesTestCase
from django.test.utils import captured_stdout
from django.contrib.auth.models import User
from django.core import management
from django.db import connection, connections
from arches.app.models.models import SpatialView as SpatialViewModel
from arches.app.views.api import SpatialView
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from arches.app.utils.i18n import LanguageSynchronizer
from arches.app.models import models
from uuid import uuid4
from tests import test_settings


# these tests can be run from the command line via
# python manage.py test tests.views.spatialview_api_tests --settings="tests.test_settings"


class SpatialViewApiTest(TransactionTestCase):

    serialized_rollback = True

    def setUp(self):
        LanguageSynchronizer.synchronize_settings_with_db()

        spatialviews_other_test_model_path = os.path.join(
            test_settings.TEST_ROOT,
            "fixtures",
            "resource_graphs",
            "SpatialViews_Other_Model.json",
        )
        spatialviews_test_model_path = os.path.join(
            test_settings.TEST_ROOT,
            "fixtures",
            "resource_graphs",
            "SpatialViews_Test_Model.json",
        )

        spatialviews_other_test_data_path = os.path.join(
            test_settings.TEST_ROOT,
            "fixtures",
            "data",
            "json",
            "Spatialviews_Other_Model_Data.json",
        )
        spatialviews_test_data_path = os.path.join(
            test_settings.TEST_ROOT,
            "fixtures",
            "data",
            "json",
            "SpatialViews_Test_Model_Data.json",
        )

        with captured_stdout():
            management.call_command("es", operation="index_concepts")
            management.call_command(
                "packages",
                operation="import_graphs",
                source=spatialviews_other_test_model_path,
                verbosity=0,
            )
            management.call_command(
                "packages",
                operation="import_graphs",
                source=spatialviews_test_model_path,
                verbosity=0,
            )
            BusinessDataImporter(
                spatialviews_other_test_data_path
            ).import_business_data()
            BusinessDataImporter(spatialviews_test_data_path).import_business_data()

        self.spatialviews_test_model_id = "5db49c51-2c70-47b3-b7be-66afced863c8"
        self.spatialviews_other_test_model_id = "114dd3fb-404d-4fb3-a639-1333b89cf60c"
        self.spatialview_geometrynode_id = "95b2c8de-1cf8-11ef-971a-0242ac130005"

        # create a spatialview with objects to test triggers
        self.spatialview_slug = "spatialviews_test"
        self.test_spatial_view = self.generate_valid_spatiatview()
        self.test_spatial_view.full_clean()
        self.test_spatial_view.save()
        self.spatialview_id = self.test_spatial_view.spatialviewid

    def get_language_instance(self, language):
        return models.Language.objects.get(code=language)

    def generate_valid_spatiatview(self):
        spatialview = SpatialViewModel()
        spatialview.spatialviewid = uuid.uuid4()
        spatialview.schema = "public"
        spatialview.slug = "spatialviews_test_" + str(random.randint(1, 1000))
        spatialview.description = "test_description"
        spatialview.geometrynode = models.Node.objects.get(
            nodeid=self.spatialview_geometrynode_id
        )
        spatialview.ismixedgeometrytypes = False  # Discreet geometry
        spatialview.language = self.get_language_instance("en")
        spatialview.isactive = True
        spatialview.attributenodes = [
            {
                "nodeid": "a379b7ac-1cf8-11ef-ab82-0242ac130005",
                "description": "gridref",
            },
            {"nodeid": "bee90060-1cf8-11ef-971a-0242ac130005", "description": "name"},
            {"nodeid": "ccfe0a6a-1cf8-11ef-971a-0242ac130005", "description": "date"},
            {
                "nodeid": "d1a59230-1cf9-11ef-a1fe-0242ac130005",
                "description": "concept_list",
            },
            {"nodeid": "d2a55a44-1cf9-11ef-a1fe-0242ac130005", "description": "bool"},
            {
                "nodeid": "d2f5d474-1cf9-11ef-a1fe-0242ac130005",
                "description": "non_local_string",
            },
            {
                "nodeid": "e514005a-1cf8-11ef-971a-0242ac130005",
                "description": "edtf_date",
            },
            {"nodeid": "e674837a-1cf8-11ef-971a-0242ac130005", "description": "count"},
            {"nodeid": "e70850dc-1cf8-11ef-971a-0242ac130005", "description": "url"},
            {"nodeid": "fe3a586c-1cf9-11ef-a1fe-0242ac130005", "description": "domain"},
            {"nodeid": "298ef7ac-1cfa-11ef-a1fe-0242ac130005", "description": "file"},
            {
                "nodeid": "0e65f1d4-1cf9-11ef-971a-0242ac130005",
                "description": "concept",
            },
            {
                "nodeid": "0e8d1560-1cfa-11ef-a1fe-0242ac130005",
                "description": "domain_list",
            },
            {
                "nodeid": "348eb80a-1cf9-11ef-ab82-0242ac130005",
                "description": "other_spatialviews",
            },
            {
                "nodeid": "54fc2d0c-1cf9-11ef-ab82-0242ac130005",
                "description": "other_models_list",
            },
        ]
        return spatialview

    def test_spatialview_api_crud(self):
        """
        Test the CRUD operations of the spatialview api. Putting these in a single test avoids issues with the order of tests
        and the database errors I get with ContentTypes disappearing
        """

        # test post
        new_spatialview = self.generate_valid_spatiatview()
        new_spatialview_json = new_spatialview.to_json()
        del new_spatialview_json["spatialviewid"]

        # elevated
        self.client.login(username="admin", password="admin")

        # create a new spatialview
        response = self.client.post(
            reverse("spatialview_api", kwargs={"identifier": ""}),
            data=new_spatialview_json,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        response_json = json.loads(response.content)

        self.assertTrue("spatialviewid" in response_json.keys())

        new_spatialview.spatialviewid = response_json["spatialviewid"]

        self.assertEqual(response_json["schema"], new_spatialview.schema)
        self.assertEqual(response_json["slug"], new_spatialview.slug)
        self.assertEqual(response_json["description"], new_spatialview.description)
        self.assertEqual(
            response_json["geometrynodeid"], str(new_spatialview.geometrynode.pk)
        )
        self.assertEqual(
            response_json["ismixedgeometrytypes"], new_spatialview.ismixedgeometrytypes
        )
        self.assertEqual(response_json["language"], new_spatialview.language.code)
        self.assertEqual(response_json["isactive"], new_spatialview.isactive)
        self.assertEqual(
            response_json["attributenodes"], new_spatialview.attributenodes
        )

        # test get all
        response = self.client.get(
            reverse("spatialview_api", kwargs={"identifier": ""})
        )
        self.assertEqual(response.status_code, 200)

        # check content is a list
        response_json = json.loads(response.content)
        self.assertTrue(isinstance(response_json, list))

        # test get one
        response = self.client.get(
            reverse(
                "spatialview_api", kwargs={"identifier": new_spatialview.spatialviewid}
            )
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)

        self.assertEqual(
            response_json["spatialviewid"], str(new_spatialview.spatialviewid)
        )
        self.assertEqual(response_json["schema"], new_spatialview.schema)
        self.assertEqual(response_json["slug"], new_spatialview.slug)
        self.assertEqual(response_json["description"], new_spatialview.description)
        self.assertEqual(
            response_json["geometrynodeid"], str(new_spatialview.geometrynode.pk)
        )
        self.assertEqual(
            response_json["ismixedgeometrytypes"], new_spatialview.ismixedgeometrytypes
        )
        self.assertEqual(response_json["language"], new_spatialview.language.code)
        self.assertEqual(response_json["isactive"], new_spatialview.isactive)
        self.assertEqual(
            response_json["attributenodes"], new_spatialview.attributenodes
        )

        # test put by changing the description
        updated_spatialview = new_spatialview
        updated_spatialview.description = "updated_description"
        updated_spatialview_json = updated_spatialview.to_json()
        response = self.client.put(
            reverse(
                "spatialview_api", kwargs={"identifier": new_spatialview.spatialviewid}
            ),
            data=updated_spatialview_json,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.content)
        self.assertEqual(response_json["description"], updated_spatialview.description)

        # test delete
        response = self.client.delete(
            reverse(
                "spatialview_api",
                kwargs={"identifier": updated_spatialview.spatialviewid},
            )
        )
        self.assertEqual(response.status_code, 204)

        # test create with spatialviewid - should error
        bad_id_create_spatialview = self.generate_valid_spatiatview()
        bad_id_create_spatialview_json = bad_id_create_spatialview.to_json()
        with self.assertLogs(
            "django.request", level="WARNING"
        ):  # suppress expected warning log
            response = self.client.post(
                reverse("spatialview_api", kwargs={"identifier": ""}),
                data=bad_id_create_spatialview_json,
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 400)
