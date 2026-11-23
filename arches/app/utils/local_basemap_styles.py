"""MapLibre styles for local basemaps, built from the Protomaps style layers
in arches/db/local_basemap_styles (see generate_style_layers.mjs there)."""

import json
from pathlib import Path
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse

STYLE_LAYERS_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "db" / "local_basemap_styles"
)
ATTRIBUTION = (
    '<a href="https://protomaps.com" target="_blank">Protomaps</a> © '
    '<a href="https://openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'
)
MAXIMUM_ZOOM = 24
FONTS_DIRECTORY = "fonts"
SPRITES_DIRECTORY = "sprites"
SPRITE_FILE_SUFFIXES = [".json", ".png", "@2x.json", "@2x.png"]
FIRST_GLYPH_RANGE = "0-255"
OVERVIEW_UNDERLAY_LAYER_IDS = ("earth", "water")


def load_style_layers(flavor):
    return json.loads((STYLE_LAYERS_DIRECTORY / f"{flavor}.json").read_text())


def font_stacks(style_layers):
    """The font stacks the layers' text-font values name, which the local
    fonts folder has to provide."""
    found_font_stacks = set()

    def collect_literal_font_stacks(expression):
        if not isinstance(expression, list) or not expression:
            return
        if expression[0] == "literal" and isinstance(expression[1], list):
            found_font_stacks.add(",".join(expression[1]))
            return
        for expression_argument in expression[1:]:
            collect_literal_font_stacks(expression_argument)

    for layer in style_layers["layers"]:
        text_font = layer.get("layout", {}).get("text-font")
        if isinstance(text_font, list) and all(
            isinstance(font_name, str) for font_name in text_font
        ):
            found_font_stacks.add(",".join(text_font))
        else:
            collect_literal_font_stacks(text_font)
    return sorted(found_font_stacks)


def required_asset_paths(flavor):
    """Paths, relative to LOCAL_BASEMAPS_ROOT, of the fonts and sprites a
    flavor needs. Only the first glyph range of each font is checked."""
    font_paths = [
        f"{FONTS_DIRECTORY}/{font_stack}/{FIRST_GLYPH_RANGE}.pbf"
        for font_stack in font_stacks(load_style_layers(flavor))
    ]
    sprite_paths = [
        f"{SPRITES_DIRECTORY}/{flavor}{suffix}" for suffix in SPRITE_FILE_SUFFIXES
    ]
    return font_paths + sprite_paths


def local_basemap_file_url(relative_path):
    return reverse("local_basemap_file", kwargs={"path": relative_path})


def glyphs_url():
    fonts_url = local_basemap_file_url(f"{FONTS_DIRECTORY}/")
    return f"{fonts_url}{{fontstack}}/{{range}}.pbf"


def public_server_url(relative_url):
    # urljoin keeps a single script prefix when reverse() already added one.
    return urljoin(settings.PUBLIC_SERVER_ADDRESS, relative_url)


def sprite_url(flavor, absolute_url=public_server_url):
    """MapLibre only accepts absolute sprite URLs."""
    return absolute_url(local_basemap_file_url(f"{SPRITES_DIRECTORY}/{flavor}"))


def sprite_id(flavor):
    return f"protomaps-{flavor}"


def archive_source(archive_path):
    return {
        "type": "vector",
        "url": f"pmtiles://{local_basemap_file_url(archive_path)}",
        "attribution": ATTRIBUTION,
    }


def icon_image_with_sprite_id(icon_image, sprite_identifier):
    """Points an icon-image at one sprite of a sprite array. Each output of a
    step, match or case is prefixed rather than wrapping the expression, since
    MapLibre only allows "zoom" at the top of a step or interpolate."""
    if isinstance(icon_image, str):
        return f"{sprite_identifier}:{icon_image}" if icon_image else icon_image
    operator = icon_image[0]
    if operator == "step":
        output_indexes = list(range(2, len(icon_image), 2))
    elif operator in ("match", "case"):
        first_output_index = 3 if operator == "match" else 2
        output_indexes = [
            *range(first_output_index, len(icon_image) - 1, 2),
            len(icon_image) - 1,
        ]
    else:
        return ["concat", f"{sprite_identifier}:", icon_image]
    prefixed_icon_image = list(icon_image)
    for output_index in output_indexes:
        prefixed_icon_image[output_index] = icon_image_with_sprite_id(
            icon_image[output_index], sprite_identifier
        )
    return prefixed_icon_image


def layer_for_zooms(layer, source_name, min_zoom, max_zoom, layer_id_suffix=""):
    """A copy of a style layer drawn from source_name between min_zoom and
    max_zoom, or None when that leaves no zooms for the layer."""
    layer_min_zoom = max(layer.get("minzoom", 0), min_zoom)
    layer_max_zoom = min(layer.get("maxzoom", MAXIMUM_ZOOM), max_zoom)
    if layer_min_zoom >= layer_max_zoom:
        return None
    zoomed_layer = {**layer, "id": f"{layer['id']}{layer_id_suffix}"}
    zoomed_layer["source"] = source_name
    if layer_min_zoom > 0:
        zoomed_layer["minzoom"] = layer_min_zoom
    if layer_max_zoom < MAXIMUM_ZOOM:
        zoomed_layer["maxzoom"] = layer_max_zoom
    return zoomed_layer


def basemap_layers(local_basemap, source_name, overview_source_name):
    """The style layers drawn from the basemap's archive and, below the zoom
    where the regional archive takes over, from its world overview."""
    style_layers = load_style_layers(local_basemap.flavor)["layers"]
    if not local_basemap.overview_archive_path:
        return [
            {**layer, "source": source_name} if "source" in layer else layer
            for layer in style_layers
        ]

    regional_min_zoom = local_basemap.overview_max_zoom + 1
    layers = []
    for layer in style_layers:
        if "source" not in layer:
            layers.append(layer)
            continue
        overview_layer = layer_for_zooms(
            layer, overview_source_name, 0, regional_min_zoom, "-overview"
        )
        regional_layer = layer_for_zooms(
            layer, source_name, regional_min_zoom, MAXIMUM_ZOOM
        )
        layers.extend(
            zoomed_layer
            for zoomed_layer in (overview_layer, regional_layer)
            if zoomed_layer is not None
        )
    first_sourced_layer_index = next(
        (index for index, layer in enumerate(layers) if "source" in layer),
        len(layers),
    )
    layers[first_sourced_layer_index:first_sourced_layer_index] = overview_underlays(
        style_layers, overview_source_name, regional_min_zoom
    )
    return layers


def overview_underlays(style_layers, overview_source_name, regional_min_zoom):
    """The overview's land and water, drawn beneath everything else at the
    zooms the regional archive covers, so the world outside a small extract
    isn't left blank there."""
    underlays = [
        layer_for_zooms(
            layer,
            overview_source_name,
            regional_min_zoom,
            MAXIMUM_ZOOM,
            "-overview-underlay",
        )
        for layer in style_layers
        if layer["id"] in OVERVIEW_UNDERLAY_LAYER_IDS
    ]
    return [underlay for underlay in underlays if underlay is not None]


def vue_style(local_basemap, absolute_url=public_server_url):
    """A complete MapLibre style for the Vue maps, which load each basemap's
    style by URL."""
    source_name = "protomaps"
    overview_source_name = "protomaps-overview"
    sources = {source_name: archive_source(local_basemap.archive_path)}
    if local_basemap.overview_archive_path:
        sources[overview_source_name] = archive_source(
            local_basemap.overview_archive_path
        )
    return {
        "version": 8,
        "name": local_basemap.map_layer.name,
        "glyphs": glyphs_url(),
        "sprite": sprite_url(local_basemap.flavor, absolute_url),
        "sources": sources,
        "layers": basemap_layers(local_basemap, source_name, overview_source_name),
    }


def knockout_source_names(local_basemap):
    return (
        f"local-basemap-{local_basemap.name}",
        f"local-basemap-{local_basemap.name}-overview",
    )


def knockout_sources(local_basemap):
    source_name, overview_source_name = knockout_source_names(local_basemap)
    sources = {source_name: archive_source(local_basemap.archive_path)}
    if local_basemap.overview_archive_path:
        sources[overview_source_name] = archive_source(
            local_basemap.overview_archive_path
        )
    return sources


def knockout_layer_definitions(local_basemap):
    """The Knockout maps put every basemap's sources and layers in one style
    with a sprite array, so layer ids are prefixed with the basemap's name and
    icons name this flavor's sprite."""
    source_name, overview_source_name = knockout_source_names(local_basemap)
    layer_definitions = []
    for layer in basemap_layers(local_basemap, source_name, overview_source_name):
        layer_definition = {
            **layer,
            "id": f"local-basemap-{local_basemap.name}-{layer['id']}",
        }
        layout = layer.get("layout", {})
        if "icon-image" in layout:
            layer_definition["layout"] = {
                **layout,
                "icon-image": icon_image_with_sprite_id(
                    layout["icon-image"], sprite_id(local_basemap.flavor)
                ),
            }
        layer_definitions.append(layer_definition)
    return layer_definitions
