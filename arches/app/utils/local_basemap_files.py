"""Files of locally served basemaps (PMTiles archives, fonts, sprites and
styles) under settings.LOCAL_BASEMAPS_ROOT."""

import mimetypes
import os
import re
from urllib.parse import quote

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.utils._os import safe_join

BYTE_RANGE_PATTERN = re.compile(r"bytes=(\d*)-(\d*)")
FONT_PATH_PATTERN = re.compile(r"(?:[^/]+/)*fonts/([^/]+)/(\d+-\d+)\.pbf")
BYTE_RANGE_CHUNK_SIZE = 64 * 1024
CONTENT_TYPES_BY_EXTENSION = {
    ".pbf": "application/x-protobuf",
    ".pmtiles": "application/vnd.pmtiles",
}


class UnsatisfiableByteRange(Exception):
    pass


def local_basemap_file_path(relative_path):
    """Returns None when no local basemap file is at relative_path, including
    when local basemaps are turned off, the path leaves the folder or it names
    a hidden file, such as the snapshot of removed online basemaps."""
    if not settings.LOCAL_BASEMAPS_ROOT or any(
        path_part.startswith(".") for path_part in relative_path.split("/")
    ):
        return None
    try:
        file_path = safe_join(settings.LOCAL_BASEMAPS_ROOT, relative_path)
    except SuspiciousFileOperation:
        return None
    return file_path if os.path.isfile(file_path) else None


def local_basemap_content_type(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    if extension in CONTENT_TYPES_BY_EXTENSION:
        return CONTENT_TYPES_BY_EXTENSION[extension]
    guessed_content_type, _encoding = mimetypes.guess_type(file_path)
    return guessed_content_type or "application/octet-stream"


def font_fallback_url(relative_path):
    """A map style has a single glyphs URL, so fonts that no local basemap
    provides, such as those of an online basemap, are fetched from
    settings.LOCAL_BASEMAPS_FONT_FALLBACK. Returns None when the font is
    local, the path is not a font, or there is no fallback."""
    font_path_match = FONT_PATH_PATTERN.fullmatch(relative_path)
    if (
        font_path_match is None
        or not settings.LOCAL_BASEMAPS_FONT_FALLBACK
        or local_basemap_file_path(relative_path) is not None
    ):
        return None
    font_stack, glyph_range = font_path_match.groups()
    return settings.LOCAL_BASEMAPS_FONT_FALLBACK.replace(
        "{fontstack}", quote(font_stack, safe=",")
    ).replace("{range}", glyph_range)


def parse_byte_range(range_header, file_size):
    """Returns the first and last byte positions a Range header asks for, or
    None when the header should be ignored and the whole file sent, which RFC
    9110 allows for malformed and multi-part ranges."""
    byte_range_match = BYTE_RANGE_PATTERN.fullmatch(range_header.strip())
    if byte_range_match is None:
        return None
    first_byte_text, last_byte_text = byte_range_match.groups()
    if not first_byte_text and not last_byte_text:
        return None

    if not first_byte_text:
        suffix_length = int(last_byte_text)
        if suffix_length == 0 or file_size == 0:
            raise UnsatisfiableByteRange
        return max(file_size - suffix_length, 0), file_size - 1

    first_byte = int(first_byte_text)
    if last_byte_text and int(last_byte_text) < first_byte:
        return None
    if first_byte >= file_size:
        raise UnsatisfiableByteRange
    last_byte = int(last_byte_text) if last_byte_text else file_size - 1
    return first_byte, min(last_byte, file_size - 1)


def iterate_byte_range(file_path, first_byte, last_byte):
    """Streams the range in chunks, since an open range such as "bytes=0-"
    can ask for a whole multi-gigabyte archive."""
    remaining_byte_count = last_byte - first_byte + 1
    with open(file_path, "rb") as basemap_file:
        basemap_file.seek(first_byte)
        while remaining_byte_count > 0:
            chunk = basemap_file.read(min(BYTE_RANGE_CHUNK_SIZE, remaining_byte_count))
            if not chunk:
                return
            remaining_byte_count -= len(chunk)
            yield chunk


def local_basemap_file_entity_tag(file_path):
    file_status = os.stat(file_path)
    return f'"{file_status.st_mtime_ns:x}-{file_status.st_size:x}"'
