"""Lists basemaps, removes local ones, picks the default, and brings back the
online basemaps that an --offline install removed."""

import json
import os
import shutil

from django.conf import settings
from django.core import serializers
from django.db import transaction
from django.db.models import Q

from arches.app.models.models import LocalBasemap, MapLayer, MapSource
from arches.app.utils import local_basemap_styles
from arches.app.utils.local_basemap_files import local_basemap_file_path
from arches.app.utils.local_basemap_installer import (
    OVERVIEW_ARCHIVE_PATH,
    LocalBasemapInstallError,
    basemaps_root,
    make_default_basemap,
    online_basemaps_snapshot_path,
    read_online_basemaps_snapshot,
    read_sprite_entries,
    update_knockout_map_assets,
    write_sprite_entries,
)

RESTART_MESSAGE = (
    "Restart the web server: running processes keep the previous System "
    "Settings (fonts and sprites)."
)


def archive_size(local_basemap):
    archive_file_path = local_basemap_file_path(local_basemap.archive_path)
    if archive_file_path is None:
        return "missing"
    return f"{os.path.getsize(archive_file_path) / 1_000_000:.1f} MB"


def basemap_summaries():
    summaries = []
    for map_layer in (
        MapLayer.objects.filter(isoverlay=False)
        .select_related("local_basemap")
        .order_by("name")
    ):
        local_basemap = getattr(map_layer, "local_basemap", None)
        summary = {
            "name": local_basemap.name if local_basemap else map_layer.name,
            "title": map_layer.name,
            "default": map_layer.addtomap,
            "local": local_basemap is not None,
        }
        if local_basemap:
            summary.update(
                flavor=local_basemap.flavor,
                build=local_basemap.build or "",
                size=archive_size(local_basemap),
                area=",".join(f"{coordinate:g}" for coordinate in local_basemap.bounds),
            )
        summaries.append(summary)
    return summaries


def find_local_basemap(name):
    local_basemap = (
        LocalBasemap.objects.filter(name=name).select_related("map_layer").first()
    )
    if local_basemap is None:
        raise LocalBasemapInstallError(
            f"No local basemap is named '{name}'; see `basemap list`."
        )
    return local_basemap


def promote_default_basemap():
    """Makes another basemap the default when none is, preferring local ones."""
    basemaps = MapLayer.objects.filter(isoverlay=False)
    if basemaps.filter(addtomap=True).exists():
        return None
    replacement = (
        basemaps.filter(local_basemap__isnull=False).order_by("name").first()
        or basemaps.order_by("sortorder", "name").first()
    )
    if replacement is not None:
        make_default_basemap(replacement)
    return replacement


def remove_unused_shared_files():
    """Deletes the overview and a flavor's sprites once no basemap uses them.
    Fonts are kept, since every flavor uses the same ones."""
    unused_paths = []
    if not LocalBasemap.objects.filter(overview_archive_path__isnull=False).exists():
        unused_paths.append(OVERVIEW_ARCHIVE_PATH)
    flavors_in_use = set(LocalBasemap.objects.values_list("flavor", flat=True))
    unused_paths += [
        f"{local_basemap_styles.SPRITES_DIRECTORY}/{flavor}{suffix}"
        for flavor in LocalBasemap.FLAVORS
        if flavor not in flavors_in_use
        for suffix in local_basemap_styles.SPRITE_FILE_SUFFIXES
    ]
    removed_paths = []
    for unused_path in unused_paths:
        unused_file_path = basemaps_root() / unused_path
        if unused_file_path.is_file():
            unused_file_path.unlink()
            removed_paths.append(unused_path)
    return removed_paths


def remove_local_basemap(name, report):
    local_basemap = find_local_basemap(name)
    with transaction.atomic():
        MapSource.objects.filter(
            name__in=local_basemap_styles.knockout_source_names(local_basemap)
        ).delete()
        local_basemap.map_layer.delete()
        replacement = promote_default_basemap()
        update_knockout_map_assets()
    shutil.rmtree(basemaps_root() / local_basemap.name, ignore_errors=True)
    removed_paths = remove_unused_shared_files()

    if removed_paths:
        report(f"Removed files no basemap uses: {', '.join(removed_paths)}")
    if replacement is not None:
        report(f"'{replacement.name}' is the default basemap.")
    if not MapLayer.objects.filter(isoverlay=False).exists():
        report(
            "No basemaps remain. Install one, or run `basemap restore-online` to "
            "bring back the online basemaps an --offline install removed."
        )
    report(RESTART_MESSAGE)


def set_default_basemap(name):
    """name is a local basemap's name or any basemap's title."""
    map_layer = (
        MapLayer.objects.filter(isoverlay=False)
        .filter(Q(local_basemap__name=name) | Q(name=name))
        .first()
    )
    if map_layer is None:
        raise LocalBasemapInstallError(
            f"No basemap is named '{name}'; see `basemap list`."
        )
    make_default_basemap(map_layer)
    return map_layer


def restore_online_basemaps(report):
    """Puts back the basemaps, sources and sprites that --offline removed,
    except basemaps whose titles have since been taken."""
    snapshot_path = online_basemaps_snapshot_path()
    if not snapshot_path.is_file():
        raise LocalBasemapInstallError(
            "Nothing to restore: no --offline install has removed online basemaps."
        )
    snapshot = read_online_basemaps_snapshot()
    has_default_basemap = MapLayer.objects.filter(
        isoverlay=False, addtomap=True
    ).exists()
    restored_names = []
    with transaction.atomic():
        for saved_source in snapshot["map_sources"]:
            MapSource.objects.get_or_create(
                name=saved_source["name"], defaults={"source": saved_source["source"]}
            )
        for saved_layer in serializers.deserialize(
            "json", json.dumps(snapshot["map_layers"])
        ):
            if MapLayer.objects.filter(name=saved_layer.object.name).exists():
                continue
            saved_layer.object.addtomap = (
                saved_layer.object.addtomap and not has_default_basemap
            )
            saved_layer.save()
            restored_names.append(saved_layer.object.name)
        current_sprites = read_sprite_entries()
        current_sprite_ids = {sprite_entry["id"] for sprite_entry in current_sprites}
        write_sprite_entries(
            [
                saved_sprite
                for saved_sprite in snapshot["sprites"]
                if saved_sprite["id"] not in current_sprite_ids
            ]
            + current_sprites
        )
        update_knockout_map_assets()
    snapshot_path.unlink()

    report(f"Restored online basemaps: {', '.join(restored_names) or 'none'}")
    if LocalBasemap.objects.exists() and not settings.LOCAL_BASEMAPS_FONT_FALLBACK:
        report(
            "Set LOCAL_BASEMAPS_FONT_FALLBACK in settings.py, so that online "
            "basemaps' fonts load while the local basemaps provide the glyphs URL."
        )
    report(RESTART_MESSAGE)
    return restored_names
