import json
from django.test import Client
from django.urls import reverse
from arches.app.models import models
from django.contrib.auth.models import User
from arches.app.search.search_export import SearchResultsExporter
from django.test.client import RequestFactory
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.search.search_export_tests --settings="tests.test_settings"

class SearchExportTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.client = Client()
        
        cls.user = User.objects.create_user(username='testuser', email='test@test.com', password='test')
        cls.search_request = cls.factory.get('/search?tiles=True&export=True&format=tilecsv', HTTP_HOST='testserver')
        cls.search_request.user = cls.user

        # create test data

    def test_search_export_no_request(self):
        """Test SearchResultsExporter without search request"""
        with self.assertRaises(Exception) as context:
            SearchResultsExporter()
        self.assertTrue('Need to pass in a search request' in str(context.exception))

    def test_invalid_format(self):
        """Test SearchResultsExporter with invalid format for shapefile export"""
        request = self.factory.get('/search?tiles=True&export=True&format=shp&compact=False', HTTP_HOST='testserver')
        request.user = self.user
        with self.assertRaises(Exception) as context:
            SearchResultsExporter(search_request=request)
        self.assertTrue('Results must be compact to export to shapefile' in str(context.exception))

    # def test_export_to_csv(self):
    #     request = self.factory.get('/search?tiles=True&export=True&format=tilecsv', HTTP_HOST='testserver')
    #     request.user = self.user
    #     exporter = SearchResultsExporter(search_request=request)
    #     result, _ = exporter.export(format='tilecsv', report_link='false')
    #     self.assertIn('.csv', result[0]['name'])

    # def test_export_to_shp(self):
    #     """Test exporting search results to SHP format"""
    #     request = self.factory.get('/search?tiles=True&export=True&format=shp&compact=True', HTTP_HOST='testserver')
    #     request.user = self.user
    #     exporter = SearchResultsExporter(search_request=request)
    #     result = exporter.export(format='shp', report_link='false')
    #     self.assertTrue(any('.shp' in file['name'] for file in result))

    # def test_export_to_geojson(self):
    #     """Test exporting search results to GeoJSON format"""
    #     request = self.factory.get('/search?tiles=True&export=True&format=geojson', HTTP_HOST='testserver')
    #     request.user = self.user
    #     exporter = SearchResultsExporter(search_request=request)
    #     result, _ = exporter.export(format='geojson', report_link='false')
    #     self.assertEqual(result['type'], 'FeatureCollection')

    # def test_link_append(self):
    #     """Test appending report link to export"""
    #     request = self.factory.get('/search?tiles=True&export=True&format=tilecsv&reportlink=true', HTTP_HOST='testserver')
    #     request.user = self.user
    #     exporter = SearchResultsExporter(search_request=request)
    #     result, _ = exporter.export(format='tilecsv', report_link='true')
    #     self.assertIn('Link', result[0]['outputfile'].getvalue())

