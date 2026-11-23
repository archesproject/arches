"""Extracts an area of OpenStreetMap from a Protomaps daily build with the
go-pmtiles command, downloads the fonts and sprites its style needs, and
installs it as a local basemap (see local_basemap_installer)."""

import os
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote

import requests
from django.conf import settings

from arches.app.models.system_settings import settings as system_settings
from arches.app.utils import local_basemap_styles
from arches.app.utils.local_basemap_installer import (
    OVERVIEW_ARCHIVE_PATH,
    LocalBasemapInstallError,
    basemap_flavor,
    basemaps_root,
    install_local_basemap,
    validate_basemap_name,
)

PROTOMAPS_BUILDS_URL = "https://build-metadata.protomaps.dev/builds.json"
PROTOMAPS_BUILD_URL = "https://build.protomaps.com/{build}.pmtiles"
PROTOMAPS_ASSETS_URL = "https://protomaps.github.io/basemaps-assets"
PROTOMAPS_SPRITES_VERSION = "v4"
BUILD_PATTERN = re.compile(r"\d{8}")
ARCHIVE_SIZE_PATTERN = re.compile(r"archive size of (.+)$", re.MULTILINE)
GLYPH_RANGE_COUNT = 256
OVERVIEW_MAX_ZOOM = 6
DOWNLOAD_THREAD_COUNT = 8
REQUEST_TIMEOUT_SECONDS = 60


def pmtiles_command():
    """The go-pmtiles command, checked for the extract options used here,
    since packaged builds report their version as "dev"."""
    command_path = shutil.which(settings.LOCAL_BASEMAPS_PMTILES_COMMAND)
    if command_path is None:
        raise LocalBasemapInstallError(
            f"The pmtiles command ('{settings.LOCAL_BASEMAPS_PMTILES_COMMAND}') wasn't "
            "found. Install it from https://github.com/protomaps/go-pmtiles/releases "
            "(or `brew install pmtiles`), or set LOCAL_BASEMAPS_PMTILES_COMMAND."
        )
    extract_help = subprocess.run(
        [command_path, "extract", "--help"], capture_output=True, text=True
    )
    if not all(
        option in extract_help.stdout + extract_help.stderr
        for option in ("--bbox", "--region", "--dry-run")
    ):
        raise LocalBasemapInstallError(
            f"{command_path} is too old for `pmtiles extract --dry-run`; upgrade it."
        )
    return command_path


def latest_build():
    builds_response = requests.get(
        PROTOMAPS_BUILDS_URL, timeout=REQUEST_TIMEOUT_SECONDS
    )
    builds_response.raise_for_status()
    build_names = [
        build["key"].removesuffix(".pmtiles") for build in builds_response.json()
    ]
    return max(
        build_name for build_name in build_names if BUILD_PATTERN.fullmatch(build_name)
    )


def bounds_of_coordinates(coordinates):
    if isinstance(coordinates[0], (int, float)):
        return [coordinates[0], coordinates[1], coordinates[0], coordinates[1]]
    child_bounds = [bounds_of_coordinates(child) for child in coordinates]
    return [
        min(bounds[0] for bounds in child_bounds),
        min(bounds[1] for bounds in child_bounds),
        max(bounds[2] for bounds in child_bounds),
        max(bounds[3] for bounds in child_bounds),
    ]


def default_bounds_bbox():
    """The bounding box of the DEFAULT_BOUNDS System Setting, which overrides
    the one in settings.py once read from the database."""
    system_settings.update_from_db()
    return bounds_of_coordinates(
        [
            feature["geometry"]["coordinates"]
            for feature in system_settings.DEFAULT_BOUNDS["features"]
        ]
    )


def parse_bbox(bbox_text):
    try:
        west, south, east, north = (float(value) for value in bbox_text.split(","))
    except ValueError:
        raise LocalBasemapInstallError(
            f"'{bbox_text}' is not a bounding box: use west,south,east,north."
        )
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise LocalBasemapInstallError(
            f"'{bbox_text}' is not a bounding box: use west,south,east,north in degrees."
        )
    return [west, south, east, north]


def area_arguments(bbox=None, region_path=None, use_default_bounds=False):
    """The pmtiles extract option for exactly one way of giving the area."""
    if [bool(bbox), bool(region_path), use_default_bounds].count(True) != 1:
        raise LocalBasemapInstallError(
            "Give the area with exactly one of --bbox, --region or --from-default-bounds."
        )
    if region_path:
        if not Path(region_path).is_file():
            raise LocalBasemapInstallError(f"No GeoJSON file at {region_path}.")
        return [f"--region={region_path}"]
    area_bbox = parse_bbox(bbox) if bbox else default_bounds_bbox()
    return [f"--bbox={','.join(str(coordinate) for coordinate in area_bbox)}"]


def extract_arguments(command_path, build, output_path, extra_arguments):
    return [
        command_path,
        "extract",
        PROTOMAPS_BUILD_URL.format(build=build),
        str(output_path),
        *extra_arguments,
    ]


def estimated_archive_size(command_path, build, extra_arguments):
    dry_run = subprocess.run(
        extract_arguments(
            command_path, build, "dry-run.pmtiles", [*extra_arguments, "--dry-run"]
        ),
        capture_output=True,
        text=True,
    )
    size_match = ARCHIVE_SIZE_PATTERN.search(dry_run.stdout + dry_run.stderr)
    if dry_run.returncode != 0 or size_match is None:
        raise LocalBasemapInstallError(
            f"pmtiles extract --dry-run failed: {(dry_run.stderr or dry_run.stdout).strip()[-500:]}"
        )
    return size_match.group(1).strip()


def extract_archive(command_path, build, relative_output_path, extra_arguments):
    """Runs pmtiles extract with its progress shown, replacing any previous
    archive only once the new one is complete."""
    output_path = basemaps_root() / relative_output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path = output_path.with_name(f"{output_path.name}.partial")
    extract_process = subprocess.run(
        extract_arguments(command_path, build, partial_path, extra_arguments)
    )
    if extract_process.returncode != 0:
        partial_path.unlink(missing_ok=True)
        raise LocalBasemapInstallError(
            f"pmtiles extract failed with exit code {extract_process.returncode}."
        )
    os.replace(partial_path, output_path)
    return output_path


def asset_downloads(flavor):
    """The fonts and sprites a flavor's style needs, as (URL, relative path)
    pairs. Every glyph range is downloaded, about 11 MB for the Noto Sans
    stacks, so labels in any script work offline."""
    downloads = []
    for font_stack in local_basemap_styles.font_stacks(
        local_basemap_styles.load_style_layers(flavor)
    ):
        for range_index in range(GLYPH_RANGE_COUNT):
            glyph_range = f"{range_index * 256}-{range_index * 256 + 255}"
            downloads.append(
                (
                    f"{PROTOMAPS_ASSETS_URL}/fonts/{quote(font_stack)}/{glyph_range}.pbf",
                    f"{local_basemap_styles.FONTS_DIRECTORY}/{font_stack}/{glyph_range}.pbf",
                )
            )
    for suffix in local_basemap_styles.SPRITE_FILE_SUFFIXES:
        downloads.append(
            (
                f"{PROTOMAPS_ASSETS_URL}/sprites/{PROTOMAPS_SPRITES_VERSION}/{flavor}{suffix}",
                f"{local_basemap_styles.SPRITES_DIRECTORY}/{flavor}{suffix}",
            )
        )
    return downloads


def download_file(session, url, relative_path):
    destination_path = basemaps_root() / relative_path
    if destination_path.is_file():
        return False
    download_response = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    download_response.raise_for_status()
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path = destination_path.with_name(f"{destination_path.name}.partial")
    partial_path.write_bytes(download_response.content)
    os.replace(partial_path, destination_path)
    return True


def download_assets(flavor):
    """Downloads the fonts and sprites missing under LOCAL_BASEMAPS_ROOT and
    returns how many were downloaded."""
    downloads = asset_downloads(flavor)
    with (
        requests.Session() as session,
        ThreadPoolExecutor(DOWNLOAD_THREAD_COUNT) as executor,
    ):
        try:
            downloaded = list(
                executor.map(
                    lambda download: download_file(session, *download), downloads
                )
            )
        except requests.RequestException as error:
            raise LocalBasemapInstallError(
                f"Downloading fonts or sprites failed: {error}"
            )
    return downloaded.count(True)


def extract_local_basemap(
    name,
    report,
    confirm,
    bbox=None,
    region_path=None,
    use_default_bounds=False,
    max_zoom=15,
    build=None,
    flavor=None,
    with_overview=True,
    refresh_overview=False,
    **install_options,
):
    """Extracts and installs a local basemap, or refreshes one extracted
    before. confirm is called with the estimated size and returns whether to
    go ahead."""
    validate_basemap_name(name)
    flavor = basemap_flavor(name, flavor)
    basemaps_root()
    command_path = pmtiles_command()
    area_extract_arguments = [
        *area_arguments(bbox, region_path, use_default_bounds),
        f"--maxzoom={max_zoom}",
    ]
    try:
        build = build or latest_build()
    except requests.RequestException as error:
        raise LocalBasemapInstallError(
            f"Finding the latest Protomaps build failed: {error}"
        )
    if not BUILD_PATTERN.fullmatch(build):
        raise LocalBasemapInstallError(f"'{build}' is not a build: use YYYYMMDD.")

    estimated_size = estimated_archive_size(command_path, build, area_extract_arguments)
    report(f"Protomaps build {build}: the extract will be about {estimated_size}.")
    if not confirm(estimated_size):
        raise LocalBasemapInstallError("Cancelled.")

    report(f"Downloaded {download_assets(flavor)} font and sprite files.")
    overview_path = basemaps_root() / OVERVIEW_ARCHIVE_PATH
    if with_overview and (refresh_overview or not overview_path.is_file()):
        report("Extracting the world overview (zooms 0-6, about 45 MB)...")
        extract_archive(
            command_path,
            build,
            OVERVIEW_ARCHIVE_PATH,
            [f"--maxzoom={OVERVIEW_MAX_ZOOM}"],
        )
    report(f"Extracting '{name}'...")
    archive_path = extract_archive(
        command_path, build, f"{name}/{name}.pmtiles", area_extract_arguments
    )
    return install_local_basemap(
        str(archive_path),
        name,
        report,
        flavor=flavor,
        overview_archive_path=str(overview_path) if with_overview else None,
        build=build,
        **install_options,
    )
