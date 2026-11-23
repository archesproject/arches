from datetime import datetime, timezone
import os

from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseRedirect,
    StreamingHttpResponse,
)
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition
from django.views.generic import View

from arches.app.models.models import LocalBasemap
from arches.app.utils.local_basemap_files import (
    UnsatisfiableByteRange,
    font_fallback_url,
    iterate_byte_range,
    local_basemap_content_type,
    local_basemap_file_entity_tag,
    local_basemap_file_path,
    parse_byte_range,
)
from arches.app.utils.local_basemap_styles import vue_style
from arches.app.utils.response import JSONResponse


def local_basemap_file_entity_tag_for_request(request, path):
    file_path = local_basemap_file_path(path)
    return local_basemap_file_entity_tag(file_path) if file_path else None


def local_basemap_file_last_modified_for_request(request, path):
    file_path = local_basemap_file_path(path)
    if file_path is None:
        return None
    return datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)


@method_decorator(
    condition(
        etag_func=local_basemap_file_entity_tag_for_request,
        last_modified_func=local_basemap_file_last_modified_for_request,
    ),
    name="get",
)
class LocalBasemapFileView(View):
    """Serves local basemap files, with the HTTP range requests that PMTiles
    archives need and Django's static file view does not support. Production
    web servers can serve LOCAL_BASEMAPS_ROOT at /basemaps/ directly."""

    def get(self, request, path):
        fallback_url = font_fallback_url(path)
        if fallback_url:
            return HttpResponseRedirect(fallback_url)

        file_path = local_basemap_file_path(path)
        if file_path is None:
            raise Http404
        file_size = os.path.getsize(file_path)
        content_type = local_basemap_content_type(file_path)

        range_header = request.headers.get("Range")
        try:
            byte_range = (
                parse_byte_range(range_header, file_size) if range_header else None
            )
        except UnsatisfiableByteRange:
            response = HttpResponse(status=416)
            response["Content-Range"] = f"bytes */{file_size}"
            return response

        if byte_range is None:
            response = FileResponse(open(file_path, "rb"), content_type=content_type)
        else:
            first_byte, last_byte = byte_range
            response = StreamingHttpResponse(
                iterate_byte_range(file_path, first_byte, last_byte),
                status=206,
                content_type=content_type,
            )
            response["Content-Length"] = last_byte - first_byte + 1
            response["Content-Range"] = f"bytes {first_byte}-{last_byte}/{file_size}"
        response["Accept-Ranges"] = "bytes"
        return response


class LocalBasemapStyleView(View):
    """The MapLibre style of an installed local basemap, which the Vue maps
    load by URL (see MapDataAPI)."""

    def get(self, request, name):
        local_basemap = (
            LocalBasemap.objects.select_related("map_layer").filter(name=name).first()
        )
        if local_basemap is None:
            raise Http404
        return JSONResponse(vue_style(local_basemap, request.build_absolute_uri))
