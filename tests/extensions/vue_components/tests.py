from types import SimpleNamespace
from unittest import mock
from uuid import uuid4
from django.test import SimpleTestCase, TestCase
from django.core import management
from django.test.utils import captured_stdout

from arches.app.models.models import Widget
from arches.extensions.vue_components.models import WidgetMapping
from arches.extensions.vue_components.utils.widget_synchronizer import (
    WidgetSynchronizer,
)
from arches.extensions.vue_components.views.api import map as map_api


class WidgetSynchronizerTestCase(TestCase):
    def setUp(self):
        self.dummy_widget_0 = Widget.objects.create(
            widgetid=uuid4(),
            name="dummy-widget",
            component="views/components/widgets/dummy",
            helptext=None,
            datatype="string",
            defaultconfig={"defaultValue": None},
        )

        self.dummy_widget_1 = Widget.objects.create(
            widgetid=uuid4(),
            name="another-widget",
            component="views/components/widgets/another",
            helptext=None,
            datatype="string",
            defaultconfig={"defaultValue": None},
        )

    def tearDown(self):
        WidgetMapping.objects.filter(
            widget__in=[self.dummy_widget_0, self.dummy_widget_1]
        ).delete()
        self.dummy_widget_0.delete()
        self.dummy_widget_1.delete()
        super().tearDown()

    def test_check_for_missing_mappings(self):
        self.assertFalse(
            WidgetMapping.objects.filter(
                widget_id__in=[
                    self.dummy_widget_0.widgetid,
                    self.dummy_widget_1.widgetid,
                ]
            ).exists()
        )
        widgets_without_mappings = WidgetSynchronizer().check_for_missing_mappings()
        self.assertIn(self.dummy_widget_0.widgetid, widgets_without_mappings)
        self.assertIn(self.dummy_widget_1.widgetid, widgets_without_mappings)

    def test_add_mapping(self):
        self.assertFalse(
            WidgetMapping.objects.filter(
                widget_id__in=[
                    self.dummy_widget_0.widgetid,
                    self.dummy_widget_1.widgetid,
                ]
            ).exists()
        )
        synchronizer = WidgetSynchronizer()
        expected_component_path_0 = (
            "arches_vue_components/widgets/DummyWidget/DummyWidget.vue"
        )

        mapping_0 = synchronizer.add_mapping(
            self.dummy_widget_0.name,
            expected_component_path_0,
        )

        self.assertIsNotNone(mapping_0)
        self.assertEqual(mapping_0.widget, self.dummy_widget_0)
        self.assertEqual(mapping_0.component, expected_component_path_0)

    def test_validate(self):
        with captured_stdout() as stdout:
            management.call_command("validate", "--codes", "2001", "--verbosity", "2")
            output = stdout.getvalue()
            self.assertIn(
                "Widgets without a mapping to an Arches Vue Components Vue component",
                output,
            )


class EnsureAbsoluteTileURLsTests(SimpleTestCase):
    """Tile paths reach this code from reverse(), so they always begin with a
    slash, while PUBLIC_SERVER_ADDRESS conventionally ends with one. The two
    have to be reconciled rather than concatenated: "//en/mvt/..." matches no
    URLconf, so the map silently serves no tiles."""

    TILE_PATH = "/en/mvt/{}/{{z}}/{{x}}/{{y}}.pbf".format(uuid4())

    @staticmethod
    def stub_settings(public_server_address):
        """Stand-in for the whole settings object rather than patching an
        attribute on it"""
        return mock.patch.object(
            map_api,
            "settings",
            SimpleNamespace(PUBLIC_SERVER_ADDRESS=public_server_address),
        )

    def make_absolute(self, public_server_address, tiles):
        source = {"type": "vector", "tiles": tiles}
        with self.stub_settings(public_server_address):
            map_api.MapDataAPI._ensure_absolute_tile_urls(source)
        return source["tiles"]

    def test_slash_on_both_sides_yields_one_slash(self):
        self.assertEqual(
            self.make_absolute("http://localhost:8000/", [self.TILE_PATH]),
            ["http://localhost:8000" + self.TILE_PATH],
        )

    def test_address_without_trailing_slash(self):
        self.assertEqual(
            self.make_absolute("http://localhost:8000", [self.TILE_PATH]),
            ["http://localhost:8000" + self.TILE_PATH],
        )

    def test_z_x_y_placeholders_are_preserved(self):
        (tile_url,) = self.make_absolute("http://localhost:8000/", [self.TILE_PATH])
        self.assertTrue(tile_url.endswith("/{z}/{x}/{y}.pbf"))

    def test_script_prefix_is_not_duplicated(self):
        # Under FORCE_SCRIPT_NAME, reverse() already includes the prefix, so
        # the address's copy of it must not be prepended a second time.
        self.assertEqual(
            self.make_absolute(
                "https://example.org/arches/", ["/arches/en/mvt/0/0/0.pbf"]
            ),
            ["https://example.org/arches/en/mvt/0/0/0.pbf"],
        )

    def test_already_absolute_urls_are_left_alone(self):
        absolute = "https://tiles.example.org/en/mvt/0/0/0.pbf"
        self.assertEqual(
            self.make_absolute("http://localhost:8000/", [absolute]), [absolute]
        )

    def test_empty_tiles_list_is_left_alone(self):
        self.assertEqual(self.make_absolute("http://localhost:8000/", []), [])

    def test_source_without_tiles_is_left_alone(self):
        source = {"type": "raster"}
        with self.stub_settings("http://localhost:8000/"):
            map_api.MapDataAPI._ensure_absolute_tile_urls(source)
        self.assertEqual(source, {"type": "raster"})
