import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase, override_settings

from arches.app.utils import local_basemap_files
from arches.app.utils.local_basemap_files import (
    UnsatisfiableByteRange,
    font_fallback_url,
    iterate_byte_range,
    local_basemap_content_type,
    local_basemap_file_path,
    parse_byte_range,
)

FONT_FALLBACK = "https://fonts.example.org/{fontstack}/{range}.pbf"


class IterateByteRangeTests(SimpleTestCase):
    def test_range_streams_in_chunks_and_stops_at_the_end_of_the_file(self):
        with tempfile.NamedTemporaryFile() as archive_file:
            archive_file.write(b"0123456789")
            archive_file.flush()
            with mock.patch.object(local_basemap_files, "BYTE_RANGE_CHUNK_SIZE", 3):
                self.assertEqual(
                    list(iterate_byte_range(archive_file.name, 2, 8)),
                    [b"234", b"567", b"8"],
                )
                # The file can shrink between the size check and the read.
                self.assertEqual(
                    list(iterate_byte_range(archive_file.name, 8, 20)), [b"89"]
                )


class ParseByteRangeTests(SimpleTestCase):
    def test_satisfiable_ranges(self):
        for range_header, expected_byte_range in [
            ("bytes=0-126", (0, 126)),
            ("bytes=900-", (900, 999)),
            ("bytes=-100", (900, 999)),
            ("bytes=-5000", (0, 999)),
            ("bytes=990-5000", (990, 999)),
            (" bytes=1-1 ", (1, 1)),
        ]:
            with self.subTest(range_header=range_header):
                self.assertEqual(
                    parse_byte_range(range_header, 1000), expected_byte_range
                )

    def test_ranges_ignored_in_favour_of_the_whole_file(self):
        for range_header in ["bytes=-", "bytes=5-1", "bytes=0-1,5-6", "items=0-1"]:
            with self.subTest(range_header=range_header):
                self.assertIsNone(parse_byte_range(range_header, 1000))

    def test_unsatisfiable_ranges(self):
        for range_header, file_size in [
            ("bytes=1000-", 1000),
            ("bytes=-0", 1000),
            ("bytes=-10", 0),
        ]:
            with self.subTest(range_header=range_header, file_size=file_size):
                with self.assertRaises(UnsatisfiableByteRange):
                    parse_byte_range(range_header, file_size)


class LocalBasemapFileTests(SimpleTestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.basemaps_root = Path(temporary_directory.name)
        local_font_path = self.basemaps_root / "fonts" / "Noto Sans Regular"
        local_font_path.mkdir(parents=True)
        (local_font_path / "0-255.pbf").write_bytes(b"glyphs")
        settings_override = override_settings(
            LOCAL_BASEMAPS_ROOT=str(self.basemaps_root),
            LOCAL_BASEMAPS_FONT_FALLBACK=FONT_FALLBACK,
        )
        settings_override.enable()
        self.addCleanup(settings_override.disable)

    def test_file_path_is_found_only_inside_the_basemaps_folder(self):
        self.assertEqual(
            local_basemap_file_path("fonts/Noto Sans Regular/0-255.pbf"),
            str(self.basemaps_root / "fonts" / "Noto Sans Regular" / "0-255.pbf"),
        )
        for missing_path in ["fonts/missing.pbf", "fonts", "../outside.pmtiles"]:
            with self.subTest(missing_path=missing_path):
                self.assertIsNone(local_basemap_file_path(missing_path))

    def test_no_file_paths_when_local_basemaps_are_off(self):
        with override_settings(LOCAL_BASEMAPS_ROOT=None):
            self.assertIsNone(
                local_basemap_file_path("fonts/Noto Sans Regular/0-255.pbf")
            )

    def test_fonts_missing_locally_fall_back(self):
        self.assertEqual(
            font_fallback_url(
                "la/fonts/Open Sans Regular,Arial Unicode MS Regular/256-511.pbf"
            ),
            "https://fonts.example.org/Open%20Sans%20Regular,Arial%20Unicode%20MS%20Regular/256-511.pbf",
        )

    def test_no_fallback_for_local_fonts_other_files_or_without_a_fallback(self):
        self.assertIsNone(font_fallback_url("fonts/Noto Sans Regular/0-255.pbf"))
        self.assertIsNone(font_fallback_url("la/sprites/light.json"))
        with override_settings(LOCAL_BASEMAPS_FONT_FALLBACK=None):
            self.assertIsNone(font_fallback_url("fonts/Proza Libre/0-255.pbf"))

    def test_content_types(self):
        for file_name, expected_content_type in [
            ("la.PMTILES", "application/vnd.pmtiles"),
            ("0-255.pbf", "application/x-protobuf"),
            ("style.json", "application/json"),
            ("unknown.basemap", "application/octet-stream"),
        ]:
            with self.subTest(file_name=file_name):
                self.assertEqual(
                    local_basemap_content_type(file_name), expected_content_type
                )
