from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase, override_settings

from arches.app.utils import local_basemap_styles
from arches.app.utils.local_basemap_styles import (
    font_stacks,
    icon_image_with_sprite_id,
    knockout_layer_definitions,
    required_asset_paths,
    vue_style,
)

STYLE_LAYERS = {
    "layers": [
        {"id": "background", "type": "background"},
        {"id": "earth", "type": "fill", "source": "protomaps"},
        {"id": "water", "type": "fill", "source": "protomaps", "maxzoom": 6},
        {"id": "roads", "type": "line", "source": "protomaps", "minzoom": 10},
        {
            "id": "pois",
            "type": "symbol",
            "source": "protomaps",
            "layout": {
                "icon-image": ["get", "kind"],
                "text-font": [
                    "case",
                    ["==", ["get", "kind"], "peak"],
                    ["literal", ["Noto Sans Italic"]],
                    ["literal", ["Noto Sans Regular"]],
                ],
            },
        },
        {
            "id": "places",
            "type": "symbol",
            "source": "protomaps",
            "layout": {"text-font": ["Noto Sans Medium"]},
        },
    ]
}


def local_basemap(overview_archive_path=None):
    return SimpleNamespace(
        name="la",
        flavor="light",
        archive_path="la/la.pmtiles",
        overview_archive_path=overview_archive_path,
        overview_max_zoom=6 if overview_archive_path else None,
        map_layer=SimpleNamespace(name="Los Angeles"),
    )


@override_settings(PUBLIC_SERVER_ADDRESS="https://arches.example.org/")
@mock.patch.object(local_basemap_styles, "load_style_layers", return_value=STYLE_LAYERS)
class LocalBasemapStyleTests(SimpleTestCase):
    def test_font_stacks_and_required_assets(self, _load_style_layers):
        self.assertEqual(
            font_stacks(STYLE_LAYERS),
            ["Noto Sans Italic", "Noto Sans Medium", "Noto Sans Regular"],
        )
        self.assertEqual(
            required_asset_paths("light"),
            [
                "fonts/Noto Sans Italic/0-255.pbf",
                "fonts/Noto Sans Medium/0-255.pbf",
                "fonts/Noto Sans Regular/0-255.pbf",
                "sprites/light.json",
                "sprites/light.png",
                "sprites/light@2x.json",
                "sprites/light@2x.png",
            ],
        )

    def test_vue_style_without_overview(self, _load_style_layers):
        style = vue_style(local_basemap())

        self.assertEqual(style["name"], "Los Angeles")
        self.assertEqual(style["glyphs"], "/basemaps/fonts/{fontstack}/{range}.pbf")
        self.assertEqual(
            style["sprite"], "https://arches.example.org/basemaps/sprites/light"
        )
        self.assertEqual(
            style["sources"]["protomaps"]["url"], "pmtiles:///basemaps/la/la.pmtiles"
        )
        self.assertEqual(
            [layer["id"] for layer in style["layers"]],
            ["background", "earth", "water", "roads", "pois", "places"],
        )

    def test_overview_draws_low_zooms_and_land_and_water_beneath_the_archive(
        self, _load_style_layers
    ):
        style = vue_style(local_basemap("la/overview.pmtiles"), lambda url: url)

        self.assertEqual(
            style["sources"]["protomaps-overview"]["url"],
            "pmtiles:///basemaps/la/overview.pmtiles",
        )
        self.assertEqual(
            [
                (
                    layer["id"],
                    layer.get("source"),
                    layer.get("minzoom"),
                    layer.get("maxzoom"),
                )
                for layer in style["layers"]
            ],
            [
                ("background", None, None, None),
                ("earth-overview-underlay", "protomaps-overview", 7, None),
                ("earth-overview", "protomaps-overview", None, 7),
                ("earth", "protomaps", 7, None),
                ("water-overview", "protomaps-overview", None, 6),
                ("roads", "protomaps", 10, None),
                ("pois-overview", "protomaps-overview", None, 7),
                ("pois", "protomaps", 7, None),
                ("places-overview", "protomaps-overview", None, 7),
                ("places", "protomaps", 7, None),
            ],
        )

    def test_knockout_layers_are_prefixed_and_name_their_sprite(
        self, _load_style_layers
    ):
        layer_definitions = knockout_layer_definitions(local_basemap())

        self.assertEqual(layer_definitions[0]["id"], "local-basemap-la-background")
        self.assertEqual(layer_definitions[1]["source"], "local-basemap-la")
        self.assertEqual(
            layer_definitions[4]["layout"]["icon-image"],
            ["concat", "protomaps-light:", ["get", "kind"]],
        )


class IconImageWithSpriteIdTests(SimpleTestCase):
    def test_outputs_are_prefixed(self):
        for icon_image, expected_icon_image in [
            ("arrow", "sprite:arrow"),
            ("", ""),
            (
                ["step", ["zoom"], "townspot", 8, ""],
                ["step", ["zoom"], "sprite:townspot", 8, ""],
            ),
            (
                ["match", ["get", "kind"], "station", "train", ["get", "kind"]],
                [
                    "match",
                    ["get", "kind"],
                    "station",
                    "sprite:train",
                    ["concat", "sprite:", ["get", "kind"]],
                ],
            ),
            (
                ["case", ["has", "capital"], "capital", "town"],
                ["case", ["has", "capital"], "sprite:capital", "sprite:town"],
            ),
        ]:
            with self.subTest(icon_image=icon_image):
                self.assertEqual(
                    icon_image_with_sprite_id(icon_image, "sprite"),
                    expected_icon_image,
                )
