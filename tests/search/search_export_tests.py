import time
import uuid
import os
from base64 import b64encode
from http import HTTPStatus
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.search.search_export import SearchResultsExporter
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import (
    import_graph as ResourceGraphImporter,
)
from arches.app.utils.i18n import LanguageSynchronizer

from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.urls import reverse

from arches.app.views.api import SearchExport
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.search.search_export_tests --settings="tests.test_settings"


class SearchExportTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

        LanguageSynchronizer.synchronize_settings_with_db()
        with open(
            os.path.join("tests/fixtures/resource_graphs/Search Test Model.json"), "r"
        ) as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        cls.search_model_graphid = "d291a445-fa5f-11e6-afa8-14109fd34195"
        # cls.search_model_cultural_period_nodeid = "7a182580-fa60-11e6-96d1-14109fd34195"
        # cls.search_model_creation_date_nodeid = "1c1d05f5-fa60-11e6-887f-14109fd34195"
        # cls.search_model_destruction_date_nodeid = "e771b8a1-65fe-11e7-9163-14109fd34195"
        cls.search_model_name_nodeid = "2fe14de3-fa61-11e6-897b-14109fd34195"
        # cls.search_model_sensitive_info_nodeid = "57446fae-65ff-11e7-b63a-14109fd34195"
        # cls.search_model_geom_nodeid = "3ebc6785-fa61-11e6-8c85-14109fd34195"

        cls.user = User.objects.create_user(
            "unprivileged_user", "unprivileged_user@test.com", "test"
        )

        test_resourceinstanceid = uuid.uuid4()

        cls.loadOntology()
        cls.ensure_resource_test_model_loaded()
        models.ResourceInstance.objects.get_or_create(
            graph_id=cls.search_model_graphid,
            resourceinstanceid=test_resourceinstanceid,
        )
        tile_data = {}
        tile_data[cls.search_model_name_nodeid] = {
            "en": {"value": "Etiwanda Avenue Street Trees", "direction": "ltr"}
        }
        new_tile = Tile(
            resourceinstance_id=test_resourceinstanceid,
            data=tile_data,
            nodegroup_id=cls.search_model_name_nodeid,
        )
        new_tile.save()
        time.sleep(1)  # delay to allow for async indexing

        # TODO: create geospatial test data

    def test_search_export_no_request(self):
        """Test SearchResultsExporter without search request"""
        with self.assertRaisesMessage(Exception, "Need to pass in a search request"):
            SearchResultsExporter()

    def test_invalid_format(self):
        """Test SearchResultsExporter with invalid format for shapefile export"""
        request = self.factory.get(
            "/search?tiles=true&export=true&format=shp&compact=false"
        )
        request.user = self.user
        with self.assertRaisesMessage(
            Exception, "Results must be compact to export to shapefile"
        ):
            SearchResultsExporter(search_request=request)

    def test_export_to_csv(self):
        request = self.factory.get("/search?tiles=True&export=True&format=tilecsv")
        request.user = self.user
        exporter = SearchResultsExporter(search_request=request)
        result, _ = exporter.export(format="tilecsv", report_link="false")
        self.assertIn(".csv", result[0]["name"])

    # def test_export_to_shp(self):
    #     """Test exporting search results to SHP format"""
    #     request = self.factory.get('/search?tiles=True&export=True&format=shp&compact=True')
    #     request.user = self.user
    #     exporter = SearchResultsExporter(search_request=request)
    #     result = exporter.export(format='shp', report_link='false')
    #     self.assertTrue(any('.shp' in file['name'] for file in result))

    # def test_export_to_geojson(self):
    #     """Test exporting search results to GeoJSON format"""
    #     request = self.factory.get('/search?tiles=True&export=True&format=geojson')
    #     request.user = self.user
    #     exporter = SearchResultsExporter(search_request=request)
    #     result, _ = exporter.export(format='geojson', report_link='false')
    #     self.assertEqual(result['type'], 'FeatureCollection')

    # def test_link_append(self):
    #     """Test appending report link to export"""
    #     request = self.factory.get('/search?tiles=True&export=True&format=tilecsv&reportlink=true')
    #     request.user = self.user
    #     exporter = SearchResultsExporter(search_request=request)
    #     result, _ = exporter.export(format='tilecsv', report_link='true')
    #     self.assertIn('Link', result[0]['outputfile'].getvalue())

    def test_login_via_basic_auth_good(self):
        auth_string = "Basic " + b64encode(b"admin:admin").decode("utf-8")
        request = RequestFactory().get(
            reverse("api_export_results"),
            HTTP_AUTHORIZATION=auth_string,
        )
        request.user = User.objects.get(username="anonymous")
        response = SearchExport().get(request)
        self.assertEqual(request.user.username, "admin")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_login_via_basic_auth_rate_limited(self):
        auth_string = "Basic " + b64encode(b"admin:admin").decode("utf-8")
        request = RequestFactory().get(
            reverse("api_export_results"),
            HTTP_AUTHORIZATION=auth_string,
            # In reality this would be added by django_ratelimit.
            QUERY_STRING="limited=True",
        )
        request.user = User.objects.get(username="anonymous")
        response = SearchExport().get(request)
        self.assertEqual(request.user.username, "anonymous")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_login_via_basic_auth_invalid(self):
        bad_auth_string = "Basic " + b64encode(b"admin:garbage").decode("utf-8")
        request = RequestFactory().get(
            reverse("api_export_results"),
            HTTP_AUTHORIZATION=bad_auth_string,
        )
        request.user = User.objects.get(username="anonymous")
        response = SearchExport().get(request)
        self.assertEqual(request.user.username, "anonymous")
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
