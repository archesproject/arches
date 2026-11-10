"""Installs a PMTiles archive as a local basemap for the Knockout and Vue
maps. Files go under settings.LOCAL_BASEMAPS_ROOT:

    fonts/<font stack>/<range>.pbf      shared by every local basemap
    sprites/<flavor>[@2x].{json,png}    shared by basemaps of a flavor
    <name>/<name>.pmtiles               the basemap's archive
    overview/world.pmtiles              a world overview of low zooms, shared
    .online_basemaps.json               what --offline removed, not served
"""

import json
import os
import shutil
import uuid
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.db import transaction
from pmtiles.reader import MmapSource, Reader
from pmtiles.tile import TileType

from arches.app.models.models import LocalBasemap, MapLayer, MapSource, TileModel
from arches.app.utils import local_basemap_styles
from arches.app.utils.local_basemap_files import local_basemap_file_path

SUPPORTED_TILE_SCHEMA_MAJOR_VERSION = "4"
OVERVIEW_ARCHIVE_PATH = "overview/world.pmtiles"
ONLINE_BASEMAPS_SNAPSHOT_PATH = ".online_basemaps.json"
RESERVED_NAMES = {
    local_basemap_styles.FONTS_DIRECTORY,
    local_basemap_styles.SPRITES_DIRECTORY,
    "styles",
    "overview",
}
MAPLIBRE_SPRITES_NODE_ID = "0e900254-4148-11e7-9902-c4b301baab9f"
MAPLIBRE_GLYPHS_NODE_ID = "0e90031e-4148-11e7-a176-c4b301baab9f"
DEFAULT_BOUNDS_NODE_ID = "0e8ffbcf-4148-11e7-a95a-c4b301baab9f"


class LocalBasemapInstallError(Exception):
    pass


def read_archive_header(archive_path):
    """The bounds, zooms and Protomaps tile schema version of an archive."""
    with open(archive_path, "rb") as archive_file:
        archive_reader = Reader(MmapSource(archive_file))
        header = archive_reader.header()
        metadata = archive_reader.metadata()
    if header["tile_type"] != TileType.MVT:
        raise LocalBasemapInstallError(
            f"{archive_path} holds {header['tile_type'].name} tiles, not vector tiles."
        )
    tile_schema_version = metadata.get("version")
    if (
        tile_schema_version is not None
        and tile_schema_version.split(".")[0] != SUPPORTED_TILE_SCHEMA_MAJOR_VERSION
    ):
        raise LocalBasemapInstallError(
            f"{archive_path} uses Protomaps tile schema {tile_schema_version}; the "
            f"styles need version {SUPPORTED_TILE_SCHEMA_MAJOR_VERSION}.x."
        )
    return {
        "bounds": [
            header["min_lon_e7"] / 10_000_000,
            header["min_lat_e7"] / 10_000_000,
            header["max_lon_e7"] / 10_000_000,
            header["max_lat_e7"] / 10_000_000,
        ],
        "min_zoom": header["min_zoom"],
        "max_zoom": header["max_zoom"],
        "tile_schema_version": tile_schema_version,
    }


def basemaps_root():
    if not settings.LOCAL_BASEMAPS_ROOT:
        raise LocalBasemapInstallError(
            "Set LOCAL_BASEMAPS_ROOT in settings.py to install local basemaps."
        )
    return Path(settings.LOCAL_BASEMAPS_ROOT)


def validate_basemap_name(name):
    try:
        validate_slug(name)
    except ValidationError:
        raise LocalBasemapInstallError(
            f"'{name}' is not a valid name: use letters, numbers, - and _."
        )
    if name in RESERVED_NAMES:
        raise LocalBasemapInstallError(f"'{name}' is reserved; choose another name.")


def basemap_flavor(name, flavor=None):
    """The flavor asked for, or else the one a basemap being reinstalled has."""
    if flavor:
        return flavor
    existing_flavor = (
        LocalBasemap.objects.filter(name=name).values_list("flavor", flat=True).first()
    )
    return existing_flavor or LocalBasemap.FLAVORS[0]


def place_archive(source_path, relative_destination_path):
    """Copies an archive into LOCAL_BASEMAPS_ROOT, replacing any previous copy
    only once the new one is complete. Returns whether it was copied, which it
    isn't when the source is already in place."""
    destination_path = basemaps_root() / relative_destination_path
    if Path(source_path).resolve() == destination_path.resolve():
        return False
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path = destination_path.with_name(f"{destination_path.name}.partial")
    shutil.copyfile(source_path, partial_path)
    os.replace(partial_path, destination_path)
    return True


def copy_assets(assets_directory):
    for asset_folder_name in (
        local_basemap_styles.FONTS_DIRECTORY,
        local_basemap_styles.SPRITES_DIRECTORY,
    ):
        source_folder = Path(assets_directory) / asset_folder_name
        if source_folder.is_dir():
            shutil.copytree(
                source_folder, basemaps_root() / asset_folder_name, dirs_exist_ok=True
            )


def require_assets(flavor):
    missing_asset_paths = [
        asset_path
        for asset_path in local_basemap_styles.required_asset_paths(flavor)
        if local_basemap_file_path(asset_path) is None
    ]
    if missing_asset_paths:
        raise LocalBasemapInstallError(
            f"LOCAL_BASEMAPS_ROOT is missing fonts or sprites: {', '.join(missing_asset_paths)}. "
            "Pass --assets with a folder that has fonts/ and sprites/ in it."
        )


def system_settings_tile(node_id):
    return TileModel.objects.filter(data__has_key=node_id).first()


def read_system_setting_text(node_id):
    tile = system_settings_tile(node_id)
    values_by_language = (tile.data.get(node_id) or {}) if tile else {}
    return next(
        (
            language_value["value"]
            for language_value in values_by_language.values()
            if language_value.get("value")
        ),
        "",
    )


def write_system_setting(node_id, value):
    tile = system_settings_tile(node_id)
    if tile is None:
        raise LocalBasemapInstallError(
            "The System Settings resource is missing; run setup_db first."
        )
    tile.data[node_id] = value
    tile.save()


def write_system_setting_text(node_id, text):
    tile = system_settings_tile(node_id)
    language_codes = list((tile.data.get(node_id) or {}) if tile else {}) or [
        settings.LANGUAGE_CODE
    ]
    write_system_setting(
        node_id,
        {
            language_code: {"value": text, "direction": "ltr"}
            for language_code in language_codes
        },
    )


def sprite_entries(sprites_setting):
    """MAPLIBRE_SPRITES as a MapLibre sprite array; a single URL becomes the
    array's unprefixed "default" sprite."""
    if sprites_setting.strip().startswith("["):
        return json.loads(sprites_setting)
    if sprites_setting:
        return [{"id": "default", "url": sprites_setting}]
    return []


def is_local_sprite(sprite_entry):
    return urlparse(sprite_entry["url"]).path.startswith(
        local_basemap_styles.local_basemap_file_url(
            f"{local_basemap_styles.SPRITES_DIRECTORY}/"
        )
    )


def read_sprite_entries():
    return sprite_entries(read_system_setting_text(MAPLIBRE_SPRITES_NODE_ID))


def write_sprite_entries(sprites):
    """Writes a lone unprefixed sprite back as the plain URL it started as."""
    if len(sprites) == 1 and sprites[0]["id"] == "default":
        sprites_setting = sprites[0]["url"]
    else:
        sprites_setting = json.dumps(sprites)
    write_system_setting_text(MAPLIBRE_SPRITES_NODE_ID, sprites_setting)


def update_knockout_map_assets():
    """The Knockout maps draw every basemap in one style, which has a single
    glyphs URL and a sprite array: glyphs come from the local fonts while any
    local basemap remains, and each local flavor in use has a sprite."""
    local_flavors = sorted(set(LocalBasemap.objects.values_list("flavor", flat=True)))
    sprites = [
        sprite_entry
        for sprite_entry in read_sprite_entries()
        if not is_local_sprite(sprite_entry)
    ]
    sprites += [
        {
            "id": local_basemap_styles.sprite_id(flavor),
            "url": local_basemap_styles.sprite_url(flavor),
        }
        for flavor in local_flavors
    ]
    write_sprite_entries(sprites)
    write_system_setting_text(
        MAPLIBRE_GLYPHS_NODE_ID,
        (
            local_basemap_styles.glyphs_url()
            if local_flavors
            else settings.MAPLIBRE_GLYPHS
        ),
    )


def layer_source_names(map_layer):
    return {
        layer_definition["source"]
        for layer_definition in map_layer.layerdefinitions or []
        if "source" in layer_definition
    }


def online_basemaps_snapshot_path():
    return basemaps_root() / ONLINE_BASEMAPS_SNAPSHOT_PATH


def read_online_basemaps_snapshot():
    snapshot_path = online_basemaps_snapshot_path()
    if not snapshot_path.is_file():
        return {"map_layers": [], "map_sources": [], "sprites": []}
    return json.loads(snapshot_path.read_text())


def save_online_basemaps_snapshot(map_layers, map_sources, sprites):
    """Adds what --offline removes to the snapshot, so that removing online
    basemaps more than once keeps the first copy of each."""
    snapshot = read_online_basemaps_snapshot()
    saved_layer_names = {
        saved_layer["fields"]["name"] for saved_layer in snapshot["map_layers"]
    }
    snapshot["map_layers"] += [
        serialized_layer
        for serialized_layer in json.loads(serializers.serialize("json", map_layers))
        if serialized_layer["fields"]["name"] not in saved_layer_names
    ]
    saved_source_names = {
        saved_source["name"] for saved_source in snapshot["map_sources"]
    }
    snapshot["map_sources"] += [
        {"name": map_source.name, "source": map_source.source}
        for map_source in map_sources
        if map_source.name not in saved_source_names
    ]
    saved_sprite_ids = {saved_sprite["id"] for saved_sprite in snapshot["sprites"]}
    snapshot["sprites"] += [
        sprite_entry
        for sprite_entry in sprites
        if sprite_entry["id"] not in saved_sprite_ids
    ]
    snapshot_path = online_basemaps_snapshot_path()
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path = snapshot_path.with_name(f"{snapshot_path.name}.partial")
    partial_path.write_text(json.dumps(snapshot, indent=2))
    os.replace(partial_path, snapshot_path)


def remove_online_basemaps():
    """Removes basemaps, sources and sprites that aren't local, since core's
    maps load every source whether its layer shows or not, and saves them for
    `basemap restore-online`."""
    online_basemaps = list(
        MapLayer.objects.filter(isoverlay=False, local_basemap__isnull=True)
    )
    source_names_in_use = set()
    for remaining_layer in MapLayer.objects.exclude(
        pk__in=[online_basemap.pk for online_basemap in online_basemaps]
    ):
        source_names_in_use |= layer_source_names(remaining_layer)
    removed_source_names = set()
    for online_basemap in online_basemaps:
        removed_source_names |= layer_source_names(online_basemap)
    removed_sources = MapSource.objects.filter(
        name__in=removed_source_names - source_names_in_use
    )
    sprites = read_sprite_entries()
    save_online_basemaps_snapshot(
        online_basemaps,
        list(removed_sources),
        [sprite_entry for sprite_entry in sprites if not is_local_sprite(sprite_entry)],
    )
    removed_sources.delete()
    for online_basemap in online_basemaps:
        online_basemap.delete()
    write_sprite_entries(
        [sprite_entry for sprite_entry in sprites if is_local_sprite(sprite_entry)]
    )
    return [online_basemap.name for online_basemap in online_basemaps]


def fit_default_bounds(bounds):
    west, south, east, north = bounds
    write_system_setting(
        DEFAULT_BOUNDS_NODE_ID,
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": uuid.uuid4().hex,
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [west, south],
                                [east, south],
                                [east, north],
                                [west, north],
                                [west, south],
                            ]
                        ],
                    },
                }
            ],
        },
    )


def save_map_layer(local_basemap, title):
    existing_map_layer = (
        MapLayer.objects.filter(name=title)
        .exclude(local_basemap__name=local_basemap.name)
        .first()
    )
    if existing_map_layer is not None:
        raise LocalBasemapInstallError(
            f"A map layer named '{title}' already exists; pass another --title."
        )
    map_layer = getattr(local_basemap, "map_layer", None) or MapLayer(
        isoverlay=False, icon="fa fa-globe"
    )
    map_layer.name = title
    map_layer.layerdefinitions = local_basemap_styles.knockout_layer_definitions(
        local_basemap
    )
    map_layer.save()
    knockout_sources = local_basemap_styles.knockout_sources(local_basemap)
    MapSource.objects.filter(
        name__in=local_basemap_styles.knockout_source_names(local_basemap)
    ).exclude(name__in=knockout_sources).delete()
    for source_name, source in knockout_sources.items():
        MapSource.objects.update_or_create(
            name=source_name, defaults={"source": source}
        )
    return map_layer


def make_default_basemap(map_layer):
    MapLayer.objects.filter(isoverlay=False).exclude(pk=map_layer.pk).update(
        addtomap=False
    )
    map_layer.addtomap = True
    map_layer.save()


def install_local_basemap(
    archive_path,
    name,
    report,
    title=None,
    flavor=None,
    overview_archive_path=None,
    assets_directory=None,
    make_default=False,
    offline=False,
    fit_bounds=False,
    build=None,
):
    validate_basemap_name(name)
    flavor = basemap_flavor(name, flavor)
    if flavor not in LocalBasemap.FLAVORS:
        raise LocalBasemapInstallError(
            f"'{flavor}' is not a flavor; use one of {', '.join(LocalBasemap.FLAVORS)}."
        )
    basemaps_root()
    archive_header = read_archive_header(archive_path)
    overview_header = (
        read_archive_header(overview_archive_path) if overview_archive_path else None
    )
    if assets_directory:
        copy_assets(assets_directory)
    require_assets(flavor)

    relative_archive_path = f"{name}/{name}.pmtiles"
    relative_overview_path = OVERVIEW_ARCHIVE_PATH if overview_header else None
    archive_replaced = place_archive(archive_path, relative_archive_path)
    if overview_header:
        place_archive(overview_archive_path, relative_overview_path)

    with transaction.atomic():
        existing_local_basemap = (
            LocalBasemap.objects.filter(name=name).select_related("map_layer").first()
        )
        local_basemap = existing_local_basemap or LocalBasemap(name=name)
        title = title or (
            existing_local_basemap.map_layer.name if existing_local_basemap else name
        )
        local_basemap.flavor = flavor
        local_basemap.archive_path = relative_archive_path
        local_basemap.overview_archive_path = relative_overview_path
        local_basemap.bounds = archive_header["bounds"]
        local_basemap.min_zoom = archive_header["min_zoom"]
        local_basemap.max_zoom = archive_header["max_zoom"]
        local_basemap.overview_max_zoom = (
            overview_header["max_zoom"] if overview_header else None
        )
        local_basemap.tile_schema_version = archive_header["tile_schema_version"]
        if build or archive_replaced:
            local_basemap.build = build
        local_basemap.map_layer = save_map_layer(local_basemap, title)
        local_basemap.save()

        if offline:
            removed_basemap_names = remove_online_basemaps()
            if removed_basemap_names:
                report(f"Removed online basemaps: {', '.join(removed_basemap_names)}")
        has_default_basemap = (
            MapLayer.objects.filter(isoverlay=False, addtomap=True)
            .exclude(pk=local_basemap.map_layer.pk)
            .exists()
        )
        if make_default or not has_default_basemap:
            make_default_basemap(local_basemap.map_layer)
            report(f"'{local_basemap.map_layer.name}' is the default basemap.")
        update_knockout_map_assets()
        if fit_bounds:
            fit_default_bounds(local_basemap.bounds)
            report("Maps now open on the basemap's bounds.")

    if offline and settings.LOCAL_BASEMAPS_FONT_FALLBACK:
        report(
            "Set LOCAL_BASEMAPS_FONT_FALLBACK = None in settings.py, so that fonts "
            "missing locally aren't fetched from the internet."
        )
    report(
        "Restart the web server: running processes keep the previous System "
        "Settings (fonts, sprites and bounds)."
    )
    return local_basemap
