from base64 import b64decode
from http import HTTPStatus

from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.debug import sensitive_variables
from django.views.generic import View
from django_ratelimit.decorators import ratelimit

from arches.app.models.system_settings import settings
from arches.app.search.components.base import SearchFilterFactory
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.views.api import APIBase


class SearchExport(View):
    @sensitive_variables("user_cred")
    @method_decorator(
        ratelimit(
            key="header:http-authorization", rate=settings.RATE_LIMIT, block=False
        )
    )
    def get(self, request):
        from arches.app.search.search_export import SearchResultsExporter

        total = int(request.GET.get("total", 0))
        download_limit = settings.SEARCH_EXPORT_IMMEDIATE_DOWNLOAD_THRESHOLD
        format = request.GET.get("format", "tilecsv")
        report_link = request.GET.get("reportlink", False)
        if "HTTP_AUTHORIZATION" in request.META and not request.GET.get(
            "limited", False
        ):
            request_auth = request.META.get("HTTP_AUTHORIZATION").split()
            if request_auth[0].lower() == "basic":
                user_cred = b64decode(request_auth[1]).decode().split(":")
                user = authenticate(username=user_cred[0], password=user_cred[1])
                if user is not None:
                    request.user = user
                else:
                    return JSONErrorResponse(status=HTTPStatus.UNAUTHORIZED)
        exporter = SearchResultsExporter(search_request=request)
        export_files, export_info = exporter.export(format, report_link)
        if format == "geojson" and total <= download_limit:
            if settings.EXPORT_DATA_FIELDS_IN_CARD_ORDER:
                response = JSONResponse(export_files, sort_keys=False)
            else:
                response = JSONResponse(export_files)
            return response
        return JSONErrorResponse(status=404)


class SearchComponentData(APIBase):
    def get(self, request, componentname):
        search_filter_factory = SearchFilterFactory(request)
        search_filter = search_filter_factory.get_filter(componentname)
        if search_filter:
            return JSONResponse(search_filter.view_data())
        return JSONErrorResponse(status=404)
