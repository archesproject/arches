import gzip
import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.urls import reverse
from pmtiles.tile import Compression, TileType, zxy_to_tileid
from pmtiles.writer import write

from arches.app.models.models import LocalBasemap, MapLayer, MapSource, TileModel
from arches.app.utils.local_basemap_installer import (
    DEFAULT_BOUNDS_NODE_ID,
    MAPLIBRE_GLYPHS_NODE_ID,
    MAPLIBRE_SPRITES_NODE_ID,
    LocalBasemapInstallError,
    install_local_basemap,
    read_system_setting_text,
    write_system_setting_text,
)
from arches.app.utils.local_basemap_styles import required_asset_paths
from tests.base_test import ArchesTestCase, load_system_settings_fixtures

LOS_ANGELES_BOUNDS = [-118.7, 33.7, -118.1, 34.35]
ONLINE_SPRITE_URL = "https://icons.example.org/sprite"


def write_archive(archive_path, max_zoom, tile_type=TileType.MVT, version="4.15.2"):
    west, south, east, north = LOS_ANGELES_BOUNDS
    with write(str(archive_path)) as writer:
        writer.write_tile(zxy_to_tileid(0, 0, 0), gzip.compress(b"tile"))
        writer.write_tile(zxy_to_tileid(max_zoom, 0, 0), gzip.compress(b"tile"))
        writer.finalize(
            {
                "tile_type": tile_type,
                "tile_compression": Compression.GZIP,
                "min_lon_e7": int(west * 10_000_000),
                "min_lat_e7": int(south * 10_000_000),
                "max_lon_e7": int(east * 10_000_000),
                "max_lat_e7": int(north * 10_000_000),
                "center_zoom": 0,
                "center_lon_e7": 0,
                "center_lat_e7": 0,
            },
            {"version": version},
        )
    return archive_path


class LocalBasemapTestCase(ArchesTestCase):
    """Starts each test with an online basemap, an overlay sharing one of its
    sources, and fonts and light sprites to install from."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        load_system_settings_fixtures()

    def setUp(self):
        working_directory = tempfile.TemporaryDirectory()
        self.addCleanup(working_directory.cleanup)
        self.working_directory = Path(working_directory.name)
        self.basemaps_root = self.working_directory / "basemaps"
        self.assets_directory = self.working_directory / "assets"
        for asset_path in required_asset_paths("light"):
            (self.assets_directory / asset_path).parent.mkdir(
                parents=True, exist_ok=True
            )
            (self.assets_directory / asset_path).write_bytes(b"asset")
        self.archive_path = write_archive(self.working_directory / "la.pmtiles", 15)
        settings_override = override_settings(
            LOCAL_BASEMAPS_ROOT=str(self.basemaps_root),
            PUBLIC_SERVER_ADDRESS="https://arches.example.org/",
        )
        settings_override.enable()
        self.addCleanup(settings_override.disable)

        MapLayer.objects.filter(isoverlay=False).delete()
        MapSource.objects.create(name="online-tiles", source={"type": "vector"})
        MapSource.objects.create(name="shared-tiles", source={"type": "vector"})
        self.online_basemap = MapLayer.objects.create(
            name="streets",
            icon="fa fa-globe",
            addtomap=True,
            layerdefinitions=[
                {"id": "roads", "source": "online-tiles"},
                {"id": "labels", "source": "shared-tiles"},
            ],
        )
        MapLayer.objects.create(
            name="overlay",
            icon="fa fa-map",
            isoverlay=True,
            layerdefinitions=[{"id": "points", "source": "shared-tiles"}],
        )
        write_system_setting_text(MAPLIBRE_SPRITES_NODE_ID, ONLINE_SPRITE_URL)
        self.reports = []

    def install(self, **options):
        return install_local_basemap(
            str(self.archive_path),
            "la",
            self.reports.append,
            assets_directory=str(self.assets_directory),
            **options,
        )


class LocalBasemapInstallerTests(LocalBasemapTestCase):
    def test_install_beside_online_basemaps(self):
        local_basemap = self.install(title="Los Angeles")

        self.assertEqual(local_basemap.archive_path, "la/la.pmtiles")
        self.assertTrue((self.basemaps_root / "la" / "la.pmtiles").is_file())
        self.assertTrue((self.basemaps_root / "sprites" / "light.json").is_file())
        self.assertEqual(local_basemap.bounds, LOS_ANGELES_BOUNDS)
        self.assertEqual((local_basemap.min_zoom, local_basemap.max_zoom), (0, 15))
        self.assertEqual(local_basemap.tile_schema_version, "4.15.2")
        self.assertEqual(local_basemap.map_layer.name, "Los Angeles")
        self.assertFalse(local_basemap.map_layer.addtomap)
        self.assertEqual(
            MapSource.objects.get(name="local-basemap-la").source["url"],
            "pmtiles:///basemaps/la/la.pmtiles",
        )
        self.assertEqual(
            json.loads(read_system_setting_text(MAPLIBRE_SPRITES_NODE_ID)),
            [
                {"id": "default", "url": ONLINE_SPRITE_URL},
                {
                    "id": "protomaps-light",
                    "url": "https://arches.example.org/basemaps/sprites/light",
                },
            ],
        )
        self.assertEqual(
            read_system_setting_text(MAPLIBRE_GLYPHS_NODE_ID),
            "/basemaps/fonts/{fontstack}/{range}.pbf",
        )

    def test_install_as_default_with_fitted_bounds(self):
        local_basemap = self.install(make_default=True, fit_bounds=True)

        self.online_basemap.refresh_from_db()
        self.assertFalse(self.online_basemap.addtomap)
        self.assertTrue(local_basemap.map_layer.addtomap)
        default_bounds = TileModel.objects.get(
            data__has_key=DEFAULT_BOUNDS_NODE_ID
        ).data[DEFAULT_BOUNDS_NODE_ID]
        self.assertEqual(
            default_bounds["features"][0]["geometry"]["coordinates"][0][:3],
            [[-118.7, 33.7], [-118.1, 33.7], [-118.1, 34.35]],
        )
        self.assertIn("Maps now open on the basemap's bounds.", self.reports)

    def test_offline_install_with_overview_then_reinstall_without_it(self):
        overview_path = write_archive(self.working_directory / "world.pmtiles", 6)

        local_basemap = self.install(
            title="Los Angeles", overview_archive_path=str(overview_path), offline=True
        )

        self.assertEqual(local_basemap.overview_max_zoom, 6)
        self.assertTrue(local_basemap.map_layer.addtomap)
        self.assertFalse(MapLayer.objects.filter(name="streets").exists())
        self.assertEqual(
            set(MapSource.objects.values_list("name", flat=True))
            & {"online-tiles", "shared-tiles", "local-basemap-la-overview"},
            {"shared-tiles", "local-basemap-la-overview"},
        )
        self.assertEqual(
            [
                sprite["id"]
                for sprite in json.loads(
                    read_system_setting_text(MAPLIBRE_SPRITES_NODE_ID)
                )
            ],
            ["protomaps-light"],
        )
        self.assertIn("Removed online basemaps: streets", self.reports)

        LocalBasemap.objects.filter(name="la").update(build="20261109")
        install_local_basemap(
            str(self.basemaps_root / "la" / "la.pmtiles"), "la", self.reports.append
        )

        reinstalled_basemap = LocalBasemap.objects.get(name="la")
        self.assertIsNone(reinstalled_basemap.overview_archive_path)
        self.assertEqual(reinstalled_basemap.map_layer.name, "Los Angeles")
        self.assertEqual(reinstalled_basemap.build, "20261109")
        self.assertFalse(
            MapSource.objects.filter(name="local-basemap-la-overview").exists()
        )

    def test_install_errors(self):
        raster_archive = write_archive(
            self.working_directory / "raster.pmtiles", 2, tile_type=TileType.PNG
        )
        old_schema_archive = write_archive(
            self.working_directory / "old.pmtiles", 2, version="3.0.0"
        )
        for install_arguments, expected_message in [
            ({"name": "Los Angeles"}, "not a valid name"),
            ({"name": "fonts"}, "reserved"),
            ({"flavor": "sepia"}, "not a flavor"),
            ({"archive_path": raster_archive}, "not vector tiles"),
            ({"archive_path": old_schema_archive}, "tile schema 3.0.0"),
            ({"assets_directory": None}, "missing fonts or sprites"),
            ({"title": "streets"}, "already exists"),
        ]:
            with self.subTest(install_arguments=install_arguments):
                arguments = {
                    "archive_path": str(self.archive_path),
                    "name": "la",
                    "report": self.reports.append,
                    "assets_directory": str(self.assets_directory),
                    **install_arguments,
                }
                if arguments["assets_directory"] is None:
                    self.basemaps_root.mkdir(exist_ok=True)
                with self.assertRaisesMessage(
                    LocalBasemapInstallError, expected_message
                ):
                    install_local_basemap(**arguments)

    def test_install_needs_basemaps_root_and_system_settings(self):
        with override_settings(LOCAL_BASEMAPS_ROOT=None):
            with self.assertRaisesMessage(
                LocalBasemapInstallError, "Set LOCAL_BASEMAPS_ROOT"
            ):
                self.install()
        TileModel.objects.filter(data__has_key=MAPLIBRE_SPRITES_NODE_ID).delete()
        with self.assertRaisesMessage(
            LocalBasemapInstallError, "System Settings resource is missing"
        ):
            self.install()

    def test_command_and_style_view(self):
        output = StringIO()
        call_command(
            "basemap",
            "install",
            str(self.archive_path),
            "--name=la",
            f"--assets={self.assets_directory}",
            stdout=output,
        )
        self.assertIn("Installed the local basemap 'la'.", output.getvalue())
        with self.assertRaisesMessage(CommandError, "not a valid name"):
            call_command("basemap", "install", str(self.archive_path), "--name=L A")

        style = self.client.get(
            reverse("local_basemap_style", kwargs={"name": "la"})
        ).json()
        self.assertEqual(style["sprite"], "http://testserver/basemaps/sprites/light")
        self.assertEqual(
            self.client.get(
                reverse("local_basemap_style", kwargs={"name": "missing"})
            ).status_code,
            404,
        )
