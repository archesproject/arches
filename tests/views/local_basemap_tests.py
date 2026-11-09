import tempfile
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse

ARCHIVE_BYTES = bytes(range(256)) * 4


class LocalBasemapFileViewTests(TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        (Path(temporary_directory.name) / "la.pmtiles").write_bytes(ARCHIVE_BYTES)
        settings_override = override_settings(
            LOCAL_BASEMAPS_ROOT=temporary_directory.name,
            LOCAL_BASEMAPS_FONT_FALLBACK="https://fonts.example.org/{fontstack}/{range}.pbf",
        )
        settings_override.enable()
        self.addCleanup(settings_override.disable)

    def get_basemap_file(self, path, **headers):
        return self.client.get(
            reverse("local_basemap_file", kwargs={"path": path}), headers=headers
        )

    def test_byte_range(self):
        response = self.get_basemap_file("la.pmtiles", Range="bytes=0-126")

        self.assertEqual(response.status_code, 206)
        self.assertEqual(b"".join(response.streaming_content), ARCHIVE_BYTES[:127])
        self.assertEqual(response["Content-Length"], "127")
        self.assertEqual(response["Content-Range"], "bytes 0-126/1024")
        self.assertEqual(response["Content-Type"], "application/vnd.pmtiles")
        self.assertEqual(response["Accept-Ranges"], "bytes")

    def test_whole_file_and_unchanged_file(self):
        response = self.get_basemap_file("la.pmtiles")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), ARCHIVE_BYTES)
        self.assertEqual(response["Accept-Ranges"], "bytes")
        self.assertIn("Last-Modified", response)
        self.assertEqual(
            self.get_basemap_file(
                "la.pmtiles", If_None_Match=response["ETag"]
            ).status_code,
            304,
        )

    def test_unsatisfiable_range(self):
        response = self.get_basemap_file("la.pmtiles", Range="bytes=5000-")

        self.assertEqual(response.status_code, 416)
        self.assertEqual(response["Content-Range"], "bytes */1024")

    def test_missing_file(self):
        self.assertEqual(self.get_basemap_file("missing.pmtiles").status_code, 404)

    def test_font_missing_locally_redirects_to_the_fallback(self):
        response = self.get_basemap_file("fonts/Proza Libre Medium/0-255.pbf")

        self.assertRedirects(
            response,
            "https://fonts.example.org/Proza%20Libre%20Medium/0-255.pbf",
            fetch_redirect_response=False,
        )
