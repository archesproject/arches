from base64 import b64encode
from http import HTTPStatus

from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.urls import reverse

from arches.app.views.api import SearchExport
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.search.search_export_tests --settings="tests.test_settings"

class SearchExportTests(ArchesTestCase):
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
