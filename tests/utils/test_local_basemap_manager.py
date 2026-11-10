import json
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from arches.app.models.models import LocalBasemap, MapLayer, MapSource
from arches.app.utils.local_basemap_installer import (
    MAPLIBRE_GLYPHS_NODE_ID,
    MAPLIBRE_SPRITES_NODE_ID,
    LocalBasemapInstallError,
    install_local_basemap,
    read_system_setting_text,
)
from arches.app.utils.local_basemap_manager import (
    remove_local_basemap,
    restore_online_basemaps,
    set_default_basemap,
)
from arches.app.utils.local_basemap_styles import SPRITE_FILE_SUFFIXES
from tests.utils.test_local_basemap_installer import (
    ONLINE_SPRITE_URL,
    LocalBasemapTestCase,
    write_archive,
)


class LocalBasemapManagerTests(LocalBasemapTestCase):
    def setUp(self):
        super().setUp()
        for suffix in SPRITE_FILE_SUFFIXES:
            (self.assets_directory / "sprites" / f"dark{suffix}").write_bytes(b"sprite")
        self.overview_path = write_archive(self.working_directory / "world.pmtiles", 6)

    def install_dark_basemap(self):
        return install_local_basemap(
            str(self.archive_path),
            "night",
            self.reports.append,
            title="Night",
            flavor="dark",
            assets_directory=str(self.assets_directory),
        )

    def sprite_ids(self):
        return [
            sprite["id"]
            for sprite in json.loads(read_system_setting_text(MAPLIBRE_SPRITES_NODE_ID))
        ]

    def test_removing_the_default_promotes_a_local_basemap_then_the_online_one(self):
        self.install(make_default=True, overview_archive_path=str(self.overview_path))
        self.install_dark_basemap()

        remove_local_basemap("la", self.reports.append)

        self.assertTrue(MapLayer.objects.get(name="Night").addtomap)
        self.assertFalse(MapSource.objects.filter(name="local-basemap-la").exists())
        self.assertFalse((self.basemaps_root / "la").exists())
        self.assertFalse((self.basemaps_root / "overview" / "world.pmtiles").exists())
        self.assertFalse((self.basemaps_root / "sprites" / "light.json").exists())
        self.assertTrue((self.basemaps_root / "sprites" / "dark.json").exists())
        self.assertEqual(self.sprite_ids(), ["default", "protomaps-dark"])
        self.assertIn("'Night' is the default basemap.", self.reports)

        remove_local_basemap("night", self.reports.append)

        self.assertTrue(MapLayer.objects.get(name="streets").addtomap)
        self.assertEqual(
            read_system_setting_text(MAPLIBRE_SPRITES_NODE_ID), ONLINE_SPRITE_URL
        )
        self.assertEqual(
            read_system_setting_text(MAPLIBRE_GLYPHS_NODE_ID),
            "https://fonts.maptoolkit.org/{fontstack}/{range}.pbf",
        )
        self.assertTrue((self.basemaps_root / "fonts").is_dir())

    @override_settings(LOCAL_BASEMAPS_FONT_FALLBACK=None)
    def test_restoring_the_online_basemaps_an_offline_install_removed(self):
        self.install(offline=True)
        self.assertTrue((self.basemaps_root / ".online_basemaps.json").is_file())
        self.assertEqual(
            self.client.get("/basemaps/.online_basemaps.json").status_code, 404
        )

        restored_names = restore_online_basemaps(self.reports.append)

        self.assertEqual(restored_names, ["streets"])
        restored_basemap = MapLayer.objects.get(name="streets")
        self.assertEqual(restored_basemap.pk, self.online_basemap.pk)
        self.assertFalse(restored_basemap.addtomap)
        self.assertTrue(MapSource.objects.filter(name="online-tiles").exists())
        self.assertEqual(self.sprite_ids(), ["default", "protomaps-light"])
        self.assertFalse((self.basemaps_root / ".online_basemaps.json").exists())
        self.assertIn(
            "Set LOCAL_BASEMAPS_FONT_FALLBACK in settings.py, so that online "
            "basemaps' fonts load while the local basemaps provide the glyphs URL.",
            self.reports,
        )
        with self.assertRaisesMessage(LocalBasemapInstallError, "Nothing to restore"):
            restore_online_basemaps(self.reports.append)

    def test_removing_the_last_basemap_then_restoring_skips_taken_titles(self):
        self.install(offline=True)
        remove_local_basemap("la", self.reports.append)

        self.assertFalse(MapLayer.objects.filter(isoverlay=False).exists())
        self.assertEqual(read_system_setting_text(MAPLIBRE_SPRITES_NODE_ID), "[]")
        self.assertIn(
            "No basemaps remain. Install one, or run `basemap restore-online` to "
            "bring back the online basemaps an --offline install removed.",
            self.reports,
        )

        MapLayer.objects.create(name="streets", icon="fa fa-globe")
        self.assertEqual(restore_online_basemaps(self.reports.append), [])
        self.assertEqual(
            read_system_setting_text(MAPLIBRE_SPRITES_NODE_ID), ONLINE_SPRITE_URL
        )

    def test_set_default_then_remove_a_basemap_that_is_not_the_default(self):
        local_basemap = self.install(title="Los Angeles")

        set_default_basemap("la")
        local_basemap.map_layer.refresh_from_db()
        self.assertTrue(local_basemap.map_layer.addtomap)

        set_default_basemap("streets")
        self.assertTrue(MapLayer.objects.get(name="streets").addtomap)
        self.assertFalse(MapLayer.objects.get(name="Los Angeles").addtomap)

        for missing_name in ["missing", "overlay"]:
            with self.subTest(missing_name=missing_name):
                with self.assertRaisesMessage(
                    LocalBasemapInstallError, "No basemap is named"
                ):
                    set_default_basemap(missing_name)

        remove_local_basemap("la", self.reports.append)
        self.assertTrue(MapLayer.objects.get(name="streets").addtomap)
        self.assertNotIn("'streets' is the default basemap.", self.reports)

    def test_commands(self):
        self.install(title="Los Angeles")
        self.install_dark_basemap()
        LocalBasemap.objects.filter(name="night").update(build="20261109")
        (self.basemaps_root / "night" / "night.pmtiles").unlink()
        list_output = StringIO()
        call_command("basemap", "list", stdout=list_output)
        self.assertEqual(
            list_output.getvalue().splitlines(),
            [
                "default  name     title        flavor  build     size     area",
                "         la       Los Angeles  light             0.0 MB   "
                "-118.7,33.7,-118.1,34.35",
                "         night    Night        dark    20261109  missing  "
                "-118.7,33.7,-118.1,34.35",
                "*        streets  streets      online",
            ],
        )

        output = StringIO()
        call_command("basemap", "set-default", "--name=night", stdout=output)
        call_command("basemap", "remove", "--name=night", stdout=output)
        call_command(
            "basemap",
            "install",
            str(self.archive_path),
            "--name=la",
            "--offline",
            stdout=output,
        )
        call_command("basemap", "restore-online", stdout=output)
        output_lines = output.getvalue().splitlines()
        self.assertIn("'Night' is the default basemap.", output_lines)
        self.assertIn("Removed the local basemap 'night'.", output_lines)
        self.assertIn("Restored online basemaps: streets", output_lines)

        MapLayer.objects.filter(isoverlay=False).delete()
        call_command("basemap", "list", stdout=output)
        self.assertEqual(output.getvalue().splitlines()[-1], "No basemaps.")
        for operation in ["remove", "set-default"]:
            with self.subTest(operation=operation):
                with self.assertRaisesMessage(
                    CommandError, f"{operation} needs --name"
                ):
                    call_command("basemap", operation)
        with self.assertRaisesMessage(CommandError, "No local basemap is named 'la2'"):
            call_command("basemap", "remove", "--name=la2")
