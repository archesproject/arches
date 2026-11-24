import uuid
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse

from arches.app.models.models import SearchExportHistory
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.views.file_tests --settings="tests.test_settings"

EXPORT_PATH = "export_deliverables/my_export.zip"


class SearchExportFileTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = User.objects.create_user(username="export_owner", password="pw")
        cls.other_user = User.objects.create_user(
            username="export_other", password="pw"
        )
        cls.export = SearchExportHistory.objects.create(
            searchexportid=uuid.uuid4(),
            user=cls.owner,
            numberofinstances=1,
            url="",
            downloadfile=EXPORT_PATH,
        )

    def get_export(self):
        return self.client.get(reverse("file_access", args=[self.export.pk]))

    def test_owner_downloads_their_export(self):
        self.client.force_login(self.owner)

        self.assertRedirects(
            self.get_export(),
            settings.MEDIA_URL + EXPORT_PATH,
            fetch_redirect_response=False,
        )

    def test_another_user_cannot_download_the_export(self):
        self.client.force_login(self.other_user)

        self.assertEqual(self.get_export().status_code, HTTPStatus.FORBIDDEN)

    def test_anonymous_visitor_cannot_download_the_export(self):
        self.assertEqual(self.get_export().status_code, HTTPStatus.FORBIDDEN)


@override_settings(ELASTICSEARCH_ENABLED=True)
class GetExportFileTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = User.objects.create_user(username="export_owner", password="pw")
        cls.other_user = User.objects.create_user(
            username="export_other", password="pw"
        )
        cls.superuser = User.objects.create_superuser(
            username="export_admin", password="pw"
        )
        cls.export = SearchExportHistory.objects.create(
            searchexportid=uuid.uuid4(),
            user=cls.owner,
            numberofinstances=1,
            url="",
            downloadfile=EXPORT_PATH,
        )

    def get_export_file(self):
        return self.client.get(
            reverse("get_export_file"), {"exportid": str(self.export.pk)}
        )

    def test_owner_gets_the_export_url(self):
        self.client.force_login(self.owner)

        response = self.get_export_file()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()["url"], settings.MEDIA_URL + EXPORT_PATH)

    def test_superuser_gets_the_export_url(self):
        self.client.force_login(self.superuser)

        self.assertEqual(self.get_export_file().status_code, HTTPStatus.OK)

    def test_another_user_cannot_get_the_export_url(self):
        self.client.force_login(self.other_user)

        self.assertEqual(self.get_export_file().status_code, HTTPStatus.FORBIDDEN)

    def test_anonymous_visitor_cannot_get_the_export_url(self):
        self.assertEqual(self.get_export_file().status_code, HTTPStatus.FORBIDDEN)
