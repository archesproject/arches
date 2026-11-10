import tempfile
from io import StringIO
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

import requests
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from arches.app.models.models import LocalBasemap, MapLayer
from arches.app.utils import local_basemap_extractor
from arches.app.utils.local_basemap_extractor import (
    area_arguments,
    asset_downloads,
    extract_local_basemap,
    latest_build,
    pmtiles_command,
)
from arches.app.utils.local_basemap_installer import (
    DEFAULT_BOUNDS_NODE_ID,
    LocalBasemapInstallError,
    write_system_setting,
)
from tests.base_test import ArchesTestCase, load_system_settings_fixtures
from tests.utils.test_local_basemap_installer import write_archive

PMTILES_PATH = "/usr/local/bin/pmtiles"
EXTRACT_HELP = "Flags: --region=STRING --bbox=STRING --maxzoom=-1 --dry-run"
DRY_RUN_OUTPUT = "extract.go:612: Extract transferred 132 MB (overfetch 0.05) for an archive size of 126 MB\n"


def fake_pmtiles(arguments, **_options):
    """Stands in for the pmtiles command: answers --help and --dry-run, and
    writes a small archive for an extract."""
    if arguments[1:] == ["extract", "--help"]:
        return CompletedProcess(arguments, 0, stdout=EXTRACT_HELP, stderr="")
    if "--dry-run" in arguments:
        return CompletedProcess(arguments, 0, stdout="", stderr=DRY_RUN_OUTPUT)
    max_zoom = int(
        next(
            argument for argument in arguments if argument.startswith("--maxzoom=")
        ).split("=")[1]
    )
    write_archive(Path(arguments[3]), max_zoom)
    return CompletedProcess(arguments, 0)


def asset_response(url, timeout):
    return mock.Mock(content=b"asset", raise_for_status=mock.Mock())


class LocalBasemapExtractorTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        load_system_settings_fixtures()

    def setUp(self):
        working_directory = tempfile.TemporaryDirectory()
        self.addCleanup(working_directory.cleanup)
        self.basemaps_root = Path(working_directory.name)
        settings_override = override_settings(
            LOCAL_BASEMAPS_ROOT=working_directory.name
        )
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        for patcher in [
            mock.patch.object(
                local_basemap_extractor.shutil, "which", return_value=PMTILES_PATH
            ),
            mock.patch.object(
                local_basemap_extractor.subprocess, "run", side_effect=fake_pmtiles
            ),
            mock.patch.object(
                local_basemap_extractor, "latest_build", return_value="20261109"
            ),
            mock.patch.object(
                local_basemap_extractor.requests.Session,
                "get",
                side_effect=asset_response,
            ),
        ]:
            patcher.start()
            self.addCleanup(patcher.stop)
        MapLayer.objects.filter(isoverlay=False).delete()
        self.reports = []

    def extract(self, confirm=lambda estimated_size: True, **options):
        return extract_local_basemap(
            "la",
            self.reports.append,
            confirm,
            bbox="-118.7,33.7,-118.1,34.35",
            **options,
        )

    def test_extract_downloads_and_installs_the_basemap(self):
        local_basemap = self.extract()

        self.assertEqual(local_basemap.build, "20261109")
        self.assertEqual(local_basemap.overview_archive_path, "overview/world.pmtiles")
        self.assertEqual(local_basemap.overview_max_zoom, 6)
        self.assertEqual(local_basemap.max_zoom, 15)
        self.assertTrue((self.basemaps_root / "la" / "la.pmtiles").is_file())
        self.assertFalse((self.basemaps_root / "la" / "la.pmtiles.partial").exists())
        self.assertEqual(
            (
                self.basemaps_root / "fonts" / "Noto Sans Medium" / "65280-65535.pbf"
            ).read_bytes(),
            b"asset",
        )
        self.assertIn(
            "Protomaps build 20261109: the extract will be about 126 MB.",
            self.reports,
        )
        regional_extract = local_basemap_extractor.subprocess.run.call_args_list[-1]
        self.assertEqual(
            regional_extract.args[0][1:],
            [
                "extract",
                "https://build.protomaps.com/20261109.pmtiles",
                str(self.basemaps_root / "la" / "la.pmtiles.partial"),
                "--bbox=-118.7,33.7,-118.1,34.35",
                "--maxzoom=15",
            ],
        )

    def test_extracting_again_reuses_overview_and_assets(self):
        self.extract()
        self.reports.clear()
        local_basemap_extractor.subprocess.run.reset_mock()

        self.extract(with_overview=False)

        self.assertIn("Downloaded 0 font and sprite files.", self.reports)
        self.assertEqual(local_basemap_extractor.subprocess.run.call_count, 3)
        self.assertIsNone(LocalBasemap.objects.get(name="la").overview_archive_path)
        self.assertNotIn(
            "Extracting the world overview (zooms 0-6, about 45 MB)...", self.reports
        )

    def test_refreshing_extracts_the_overview_again_and_keeps_the_flavor(self):
        self.extract(flavor="dark")
        local_basemap_extractor.subprocess.run.reset_mock()

        local_basemap = self.extract(refresh_overview=True)

        self.assertEqual(local_basemap.flavor, "dark")
        self.assertIn(
            "Extracting the world overview (zooms 0-6, about 45 MB)...", self.reports
        )
        self.assertEqual(local_basemap_extractor.subprocess.run.call_count, 4)

    def test_cancelling_downloads_nothing(self):
        with self.assertRaisesMessage(LocalBasemapInstallError, "Cancelled."):
            self.extract(confirm=lambda estimated_size: False)
        self.assertEqual(list(self.basemaps_root.iterdir()), [])

    def test_missing_pmtiles_command_and_failed_dry_run(self):
        with mock.patch.object(
            local_basemap_extractor.shutil, "which", return_value=None
        ):
            with self.assertRaisesMessage(LocalBasemapInstallError, "wasn't found"):
                self.extract()

        def dry_run_fails(arguments, **options):
            if "--dry-run" in arguments:
                return CompletedProcess(arguments, 1, stdout="", stderr="no such build")
            return fake_pmtiles(arguments)

        local_basemap_extractor.subprocess.run.side_effect = dry_run_fails
        with self.assertRaisesMessage(
            LocalBasemapInstallError, "--dry-run failed: no such build"
        ):
            self.extract()

    def test_failed_extract_leaves_no_partial_archive(self):
        def extract_fails(arguments, **options):
            if "--dry-run" in arguments or "--help" in arguments:
                return fake_pmtiles(arguments)
            Path(arguments[3]).write_bytes(b"partial")
            return CompletedProcess(arguments, 2)

        local_basemap_extractor.subprocess.run.side_effect = extract_fails
        with self.assertRaisesMessage(LocalBasemapInstallError, "exit code 2"):
            self.extract(with_overview=False)
        self.assertFalse((self.basemaps_root / "la" / "la.pmtiles.partial").exists())

    def test_old_pmtiles_command_and_failed_downloads(self):
        local_basemap_extractor.subprocess.run.side_effect = (
            lambda arguments, **options: CompletedProcess(
                arguments, 0, stdout="Flags: --bbox", stderr=""
            )
        )
        with self.assertRaisesMessage(LocalBasemapInstallError, "too old"):
            pmtiles_command()

        local_basemap_extractor.subprocess.run.side_effect = fake_pmtiles
        local_basemap_extractor.requests.Session.get.side_effect = (
            requests.ConnectionError("offline")
        )
        with self.assertRaisesMessage(LocalBasemapInstallError, "fonts or sprites"):
            self.extract()

    def test_area_arguments(self):
        region_path = self.basemaps_root / "region.geojson"
        region_path.write_text("{}")
        write_system_setting(
            DEFAULT_BOUNDS_NODE_ID,
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "MultiPolygon",
                            "coordinates": [
                                [[[1, 2], [3, 2], [3, 4], [1, 2]]],
                                [[[-5, 0], [0, 0], [0, 6], [-5, 0]]],
                            ],
                        },
                    }
                ],
            },
        )
        self.assertEqual(
            area_arguments(region_path=str(region_path)), [f"--region={region_path}"]
        )
        self.assertEqual(area_arguments(use_default_bounds=True), ["--bbox=-5,0,3,6"])
        for area_options, expected_message in [
            ({}, "exactly one"),
            ({"bbox": "1,2,3,4", "use_default_bounds": True}, "exactly one"),
            ({"bbox": "1,2,3"}, "not a bounding box"),
            ({"bbox": "3,2,1,4"}, "in degrees"),
            ({"region_path": "missing.geojson"}, "No GeoJSON file"),
        ]:
            with self.subTest(area_options=area_options):
                with self.assertRaisesMessage(
                    LocalBasemapInstallError, expected_message
                ):
                    area_arguments(**area_options)

    def test_build_errors(self):
        with self.assertRaisesMessage(LocalBasemapInstallError, "not a build"):
            self.extract(build="latest")
        local_basemap_extractor.latest_build.side_effect = requests.ConnectionError(
            "offline"
        )
        with self.assertRaisesMessage(LocalBasemapInstallError, "latest Protomaps"):
            self.extract()

    def test_command(self):
        output = StringIO()
        with mock.patch("builtins.input", return_value="y"):
            call_command(
                "basemap",
                "extract",
                "--name=la",
                "--bbox=-118.7,33.7,-118.1,34.35",
                "--no-overview",
                stdout=output,
            )
        self.assertIn("Installed the local basemap 'la'.", output.getvalue())
        with mock.patch("builtins.input", return_value="n"):
            with self.assertRaisesMessage(CommandError, "Cancelled."):
                call_command(
                    "basemap", "extract", "--name=la", "--bbox=1,2,3,4", stdout=output
                )
        call_command(
            "basemap",
            "extract",
            "--name=la",
            "--bbox=1,2,3,4",
            "--noinput",
            stdout=output,
        )
        with self.assertRaisesMessage(CommandError, "needs the path"):
            call_command("basemap", "install", "--name=la")


class LatestBuildTests(ArchesTestCase):
    def test_latest_dated_build(self):
        builds = [
            {"key": "20261108.pmtiles"},
            {"key": "20261109.pmtiles"},
            {"key": "test.pmtiles"},
        ]
        with mock.patch.object(
            local_basemap_extractor.requests,
            "get",
            return_value=mock.Mock(json=mock.Mock(return_value=builds)),
        ):
            self.assertEqual(latest_build(), "20261109")

    def test_asset_downloads_cover_every_glyph_range(self):
        downloads = asset_downloads("dark")
        self.assertEqual(len(downloads), 3 * 256 + 4)
        self.assertEqual(
            downloads[0],
            (
                "https://protomaps.github.io/basemaps-assets/fonts/Noto%20Sans%20Italic/0-255.pbf",
                "fonts/Noto Sans Italic/0-255.pbf",
            ),
        )
        self.assertEqual(
            downloads[-1],
            (
                "https://protomaps.github.io/basemaps-assets/sprites/v4/dark@2x.png",
                "sprites/dark@2x.png",
            ),
        )
