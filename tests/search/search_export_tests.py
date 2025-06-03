import uuid
import csv
import io
import os
import time
from base64 import b64encode
from http import HTTPStatus
from pathlib import Path
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.search.elasticsearch_dsl_builder import Query
from arches.app.search.mappings import TERMS_INDEX, CONCEPTS_INDEX, RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.search_export import SearchResultsExporter
from arches.app.utils.skos import SKOSReader

from django.conf import settings
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.urls import get_script_prefix, reverse, set_script_prefix

from arches.app.views.api import SearchExport
from tests.base_test import ArchesTestCase
from tests.utils.search_test_utils import sync_es

# these tests can be run from the command line via
# python manage.py test tests.search.search_export_tests --settings="tests.test_settings"


class SearchExportTests(ArchesTestCase):
    graph_fixtures = ["Search Test Model"]

    search_model_graphid = "d291a445-fa5f-11e6-afa8-14109fd34195"
    search_model_cultural_period_nodeid = "7a182580-fa60-11e6-96d1-14109fd34195"
    search_model_cultural_period_nodename = "Cultural Period Concept"
    search_model_name_nodeid = "2fe14de3-fa61-11e6-897b-14109fd34195"

    def setUp(self):
        super().setUp()
        se = SearchEngineFactory().create()
        sync_es(se)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        se = SearchEngineFactory().create()
        q = Query(se=se)
        for indexname in [TERMS_INDEX, CONCEPTS_INDEX, RESOURCES_INDEX]:
            q.delete(index=indexname, refresh=True)
        cls.factory = RequestFactory()

        cls.user = User.objects.create_user(
            "unprivileged_user", "unprivileged_user@test.com", "test"
        )

        cls.test_resourceinstanceid = uuid.uuid4()

        models.ResourceInstance.objects.get_or_create(
            graph_id=cls.search_model_graphid,
            resourceinstanceid=cls.test_resourceinstanceid,
        )
        tile_data = {}
        tile_data[cls.search_model_name_nodeid] = {
            "en": {"value": "Etiwanda Avenue Street Trees", "direction": "ltr"}
        }
        new_tile = Tile(
            resourceinstance_id=cls.test_resourceinstanceid,
            data=tile_data,
            nodegroup_id=cls.search_model_name_nodeid,
        )
        new_tile.save()
        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/data/concept_label_test_scheme.xml")
        ret = skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/data/concept_label_test_collection.xml")
        ret = skos.save_concepts_from_skos(rdf)
        cls.valueid = "dadaeee5-57ef-409d-a6cf-98d332fdada8"
        cultural_period_tile = Tile(
            data={cls.search_model_cultural_period_nodeid: cls.valueid},
            nodegroup_id=cls.search_model_cultural_period_nodeid,
            resourceinstance_id=cls.test_resourceinstanceid,
        )
        cultural_period_tile.save(index=False)
        cultural_period_tile.index()
        # TODO: create geospatial test data

        # Without some sleep, the next class's setup might fail when
        # get_resource_model_label() raises Node.DoesNotExist
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        se = SearchEngineFactory().create()
        q = Query(se=se)
        for indexname in [TERMS_INDEX, CONCEPTS_INDEX, RESOURCES_INDEX]:
            q.delete(index=indexname, refresh=True)
        super().tearDownClass()

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

    def test_write_export_to_zip(self):
        request = self.factory.get("/search?tiles=True&export=True&format=tilecsv")
        request.user = self.user
        exporter = SearchResultsExporter(search_request=request)
        result, info = exporter.export(format="tilecsv", report_link="false")
        path = Path(settings.MEDIA_ROOT) / "export_deliverables" / "test.zip"
        self.addCleanup(os.remove, path)
        uuid = exporter.write_export_zipfile(result, info, "test")
        self.assertIsNotNone(uuid)

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

    def test_export_to_csv_with_system_values(self):
        """Test exporting search results to CSV with system values included"""
        request = self.factory.get(
            "/search?tiles=True&export=True&format=tilecsv&exportsystemvalues=true"
        )
        request.user = self.user
        exporter = SearchResultsExporter(search_request=request)
        result, _ = exporter.export(format="tilecsv", report_link="false")
        self.assertIn(".csv", result[0]["name"])
        csv_content = result[0]["outputfile"].getvalue()
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        cultural_period_column_name = self.search_model_cultural_period_nodename
        for row in csv_reader:
            self.assertTrue(len(row) > 1, f"{len(row)} column(s) in csv row: {row}")
            cultural_period_value = row[cultural_period_column_name]
            self.assertTrue(
                is_valid_uuid(cultural_period_value),
                f"Expected UUID, got {cultural_period_value}",
            )
            break

    def test_export_to_csv_without_system_values(self):
        """Test exporting search results to CSV without system values"""
        request = self.factory.get(
            "/search?tiles=True&export=True&format=tilecsv&exportsystemvalues=false"
        )
        request.user = self.user
        exporter = SearchResultsExporter(search_request=request)
        result, _ = exporter.export(format="tilecsv", report_link="false")
        self.assertIn(".csv", result[0]["name"])
        csv_content = result[0]["outputfile"].getvalue()
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        cultural_period_column_name = self.search_model_cultural_period_nodename
        for row in csv_reader:
            self.assertTrue(len(row) > 1, f"{len(row)} columns in csv row: {row}")
            cultural_period_value = row[cultural_period_column_name]
            self.assertFalse(
                is_valid_uuid(cultural_period_value),
                f"Expected non-UUID, got {cultural_period_value}",
            )
            break

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

    def test_script_prefix(self):
        prefix = get_script_prefix()
        set_script_prefix("/nginx")
        self.addCleanup(set_script_prefix, prefix)

        request = self.factory.get("/search?tiles=True&export=True&format=tilecsv")
        request.user = self.user
        exporter = SearchResultsExporter(search_request=request)
        exporter.export(format="tilecsv", report_link="false")


def is_valid_uuid(value, version=4):
    """Check if value is a valid UUID."""
    try:
        uuid_obj = uuid.UUID(value, version=version)
        return str(uuid_obj) == value
    except ValueError:
        return False
