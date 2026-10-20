"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import json
import logging
import os

from django.contrib.gis.geos import GEOSGeometry
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import get_language, gettext as _
from arches.app.utils.decorators import deprecated
from arches.app.models.models import (
    Node,
    ResourceInstance,
    MapMarker,
    GraphModel,
    DDataType,
    Widget,
    ReportTemplate,
    CardComponent,
    SearchExportHistory,
)
from arches.app.models.concept import Concept
from arches.app.utils import import_class_from_string
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Query
from arches.app.search.search_export import SearchResultsExporter
from arches.app.search.time_wheel import TimeWheel
from arches.app.search.components.base import SearchFilterFactory
from arches.app.views.base import MapBaseManagerView
from arches.app.utils import permission_backend
from arches.app.utils.permission_backend import (
    get_nodegroups_by_perm,
    user_is_resource_reviewer,
)
from arches.app.utils.decorators import group_required, requires_elasticsearch
import arches.app.utils.zip as zip_utils
import arches.app.utils.task_management as task_management
from arches.app.utils.data_management.resources.formats.htmlfile import HtmlWriter
import arches.app.tasks as tasks
from io import StringIO
from tempfile import NamedTemporaryFile
from arches.app.models.system_settings import settings

logger = logging.getLogger(__name__)


@method_decorator(requires_elasticsearch, name="dispatch")
class SearchView(MapBaseManagerView):
    def get(self, request):
        map_markers = MapMarker.objects.all()
        resource_graphs = GraphModel.objects.get_resource_models()
        search_component_factory = SearchFilterFactory(request)
        searchview_instance = search_component_factory.get_searchview_instance()
        if not searchview_instance:
            raise Http404(_("Search view instance not found"))
        search_components = searchview_instance.get_searchview_filters()

        datatypes = DDataType.objects.all()
        widgets = Widget.objects.all()
        templates = ReportTemplate.objects.all()
        card_components = CardComponent.objects.all()

        context = self.get_context_data(
            map_markers=map_markers,
            search_components=search_components,
            widgets=widgets,
            report_templates=templates,
            card_components=card_components,
            main_script="views/search",
            resource_graphs=resource_graphs,
            datatypes=datatypes,
            user_is_reviewer=user_is_resource_reviewer(request.user),
        )

        graphs = JSONSerializer().serialize(
            context["resource_graphs"],
            exclude=[
                "functions",
                "author",
                "deploymentdate",
                "deploymentfile",
                "version",
                "subtitle",
                "description",
                "disable_instance_creation",
                "ontology_id",
            ],
        )
        context["graphs"] = graphs
        context["nav"]["title"] = _("Search")
        context["nav"]["icon"] = "fa-search"
        context["nav"]["search"] = False
        context["nav"]["help"] = {
            "title": _("Searching the Database"),
            "templates": ["search-help"],
        }
        context["celery_running"] = task_management.check_if_celery_available()
        context["export_html_templates"] = (
            HtmlWriter.get_graphids_with_export_template()
        )
        term_search_types = [
            {
                "type": term_search_type["type"],
                "label": str(term_search_type["label"]),
                "key": term_search_type["key"],
            }
            for term_search_type in settings.TERM_SEARCH_TYPES
        ]
        context["term_search_types"] = JSONSerializer().serialize(term_search_types)

        return render(request, "views/search.htm", context)


@deprecated
def home_page(request):
    return render(
        request,
        "views/search.htm",
        {
            "main_script": "views/search",
        },
    )


@requires_elasticsearch
def search_terms(request):
    lang = request.GET.get("lang", request.LANGUAGE_CODE)
    searchString = request.GET.get("q", "")
    ret = {}

    for term_search_type in settings.TERM_SEARCH_TYPES:
        try:
            module = term_search_type["module"]
            index = import_class_from_string(module)
            ret[term_search_type["key"]] = index.search_terms(
                searchString, lang, request.user, term_search_type
            )
        except (KeyError, ValueError):
            pass
    return JSONResponse(ret)


@group_required("Resource Exporter")
@requires_elasticsearch
def export_results(request):
    total = int(request.GET.get("total", 0))
    format = request.GET.get("format", "tilecsv")
    report_link = request.GET.get("reportlink", False)
    app_name = settings.APP_NAME
    if format == "html":
        download_limit = settings.SEARCH_EXPORT_IMMEDIATE_DOWNLOAD_THRESHOLD_HTML_FORMAT
    else:
        download_limit = settings.SEARCH_EXPORT_IMMEDIATE_DOWNLOAD_THRESHOLD

    if total > download_limit and format != "geojson":
        if (settings.RESTRICT_CELERY_EXPORT_FOR_ANONYMOUS_USER is True) and (
            request.user.username == "anonymous"
        ):
            message = _(
                "Your search exceeds the {download_limit} instance download limit.  \
                Anonymous users cannot run an export exceeding this limit.  \
                Please sign in with your {app_name} account or refine your search"
            ).format(**locals())
            return JSONResponse({"success": False, "message": message})
        else:
            celery_worker_running = task_management.check_if_celery_available()
            if celery_worker_running is True:
                request_values = dict(request.GET)
                request_values["path"] = request.get_full_path()
                result = tasks.export_search_results.apply_async(
                    (request.user.id, request_values, format, report_link),
                    link=tasks.update_user_task_record.s(),
                    link_error=tasks.log_error.s(),
                )
                message = _(
                    "{total} instances have been submitted for export. \
                    Click the Bell icon to check for a link to download your data"
                ).format(**locals())
                return JSONResponse({"success": True, "message": message})
            else:
                message = _(
                    "Your search exceeds the {download_limit} instance download limit. Please refine your search"
                ).format(**locals())
                return JSONResponse({"success": False, "message": message})

    elif format == "tilexl":
        exporter = SearchResultsExporter(search_request=request)
        export_files, export_info = exporter.export(format, report_link)
        wb = export_files[0]["outputfile"]
        try:
            with NamedTemporaryFile(delete=False) as tmp:
                wb.save(tmp.name)
                tmp.seek(0)
                stream = tmp.read()
                export_files[0]["outputfile"] = tmp
                result = zip_utils.zip_response(
                    export_files, zip_file_name=f"{settings.APP_NAME}_export.zip"
                )
        except OSError:
            logger.error("Temp file could not be created.")
            raise
        os.unlink(tmp.name)
        return result
    else:
        exporter = SearchResultsExporter(search_request=request)
        export_files, export_info = exporter.export(format, report_link)

        if len(export_files) == 0 and format == "shp":
            message = _(
                "Either no instances were identified for export or no resources have exportable geometry nodes\
                Please confirm that the models of instances you would like to export have geometry nodes and that\
                those nodes are set as exportable"
            )
            dest = StringIO()
            dest.write(message)
            export_files.append({"name": "error.txt", "outputfile": dest})
        return zip_utils.zip_response(
            export_files, zip_file_name=f"{settings.APP_NAME}_export.zip"
        )


def append_instance_permission_filter_dsl(request, search_query_object):
    if request.user.is_superuser is False:
        query: Query = search_query_object.get("query", None)
        if query:
            inclusions = permission_backend.get_permission_inclusions()
            for inclusion in inclusions:
                query.include(inclusion)
            query.add_query(
                permission_backend.get_permission_search_filter(request.user)
            )


@requires_elasticsearch
def get_dsl_from_search_string(request):
    dsl = search_results(request, returnDsl=True).dsl
    return JSONResponse(dsl)


def _localized(value, language_codes):
    """Picks the first non-empty entry of an i18n dict for the given languages."""
    value = getattr(value, "raw_value", value)  # unwrap I18n_String
    if not isinstance(value, dict):
        return value
    for code in language_codes:
        if value.get(code):
            return value[code]
    return next((v for v in value.values() if v), "")


def resource_lookup_from_db(request):
    """
    Minimal database-backed equivalent of search_results, used when
    settings.ELASTICSEARCH_ENABLED is False. It serves the resource-instance widgets,
    which look resources up through the search_results url, and supports only the
    parameters they send: id, paging-filter, resource-type-filter, term-filter
    (matched against the resource name) and sort-results.
    """
    language_codes = [get_language(), settings.LANGUAGE_CODE]

    queryset = ResourceInstance.objects.exclude(
        pk=settings.SYSTEM_SETTINGS_RESOURCE_ID
    ).select_related("graph")

    readable_graphids = permission_backend.get_resource_types_by_perm(
        request.user, ["models.read_nodegroup"]
    )
    queryset = queryset.filter(graph_id__in=readable_graphids)
    queryset = permission_backend.filter_resource_queryset(request.user, queryset)

    ids = request.GET.get("id")
    if ids:
        queryset = queryset.filter(pk__in=ids.split(","))

    graphids = [
        f["graphid"]
        for f in json.loads(request.GET.get("resource-type-filter") or "[]")
        if not f.get("inverted")
    ]
    if graphids:
        queryset = queryset.filter(graph_id__in=graphids)

    for term in json.loads(request.GET.get("term-filter") or "[]"):
        value = term.get("value")
        if not value or term.get("inverted"):
            continue
        name_query = Q()
        for code in language_codes:
            name_query |= Q(**{"name__%s__icontains" % code: value})
        queryset = queryset.filter(name_query)

    ordering = "name__%s" % language_codes[0]
    if request.GET.get("sort-results") == "desc":
        ordering = "-" + ordering
    queryset = queryset.order_by(ordering, "pk")

    page_number = int(request.GET.get("paging-filter") or 1)
    paginator = Paginator(queryset, settings.SEARCH_ITEMS_PER_PAGE)
    page = paginator.get_page(page_number)

    ontology_classes = dict(
        Node.objects.filter(
            graph_id__in={r.graph_id for r in page.object_list}, istopnode=True
        ).values_list("graph_id", "ontologyclass")
    )

    hits = []
    for resource in page.object_list:
        descriptors = resource.descriptors or {}
        source = {
            "graph_id": str(resource.graph_id),
            "displayname": _localized(resource.name, language_codes) or _("Undefined"),
            "displaydescription": _localized(
                {k: v.get("description") for k, v in descriptors.items()},
                language_codes,
            ),
            "root_ontology_class": ontology_classes.get(resource.graph_id),
        }
        hits.append({"_id": str(resource.pk), "_source": source})

    return JSONResponse(
        {
            "results": {
                "hits": {"hits": hits, "total": {"value": paginator.count}},
            },
            "paging-filter": {
                "paginator": {
                    "current_page": page.number,
                    "has_next": page.has_next(),
                    "has_previous": page.has_previous(),
                    "has_other_pages": page.has_other_pages(),
                    "next_page_number": (
                        page.next_page_number() if page.has_next() else None
                    ),
                    "previous_page_number": (
                        page.previous_page_number() if page.has_previous() else None
                    ),
                    "start_index": page.start_index(),
                    "end_index": page.end_index(),
                }
            },
        }
    )


def search_results(request, returnDsl=False):
    if not settings.ELASTICSEARCH_ENABLED:
        if returnDsl:
            raise Http404("This view requires Elasticsearch, which is disabled.")
        return resource_lookup_from_db(request)

    search_filter_factory = SearchFilterFactory(request)
    searchview_component_instance = search_filter_factory.get_searchview_instance()
    if not searchview_component_instance:
        unavailable_searchview_name = search_filter_factory.get_searchview_name()
        message = _("No search-view named {0}").format(unavailable_searchview_name)
        return JSONErrorResponse(
            _("Search Failed"),
            message,
            status=400,
        )

    try:
        response_object, search_query_object = (
            searchview_component_instance.handle_search_results_query(
                search_filter_factory, returnDsl
            )
        )
        if returnDsl:
            return search_query_object.pop("query")
        else:
            return JSONResponse(content=response_object)
    except Exception as e:
        message = _("There was an error retrieving the search results")
        try:
            message = e.args[0].get("message", message)
        except:
            logger.exception("Error retrieving search results:")
            logger.exception(e)

        return JSONErrorResponse(
            _("Search Failed"),
            message,
            status=500,
        )


def get_provisional_type(request):
    """
    Parses the provisional filter data to determine if a search results will
    include provisional (True) exclude provisional (False) or inlude only
    provisional 'only provisional'
    """

    result = False
    provisional_filter = JSONDeserializer().deserialize(
        request.GET.get("provisional-filter", "[]")
    )
    user_is_reviewer = user_is_resource_reviewer(request.user)
    if user_is_reviewer is not False:
        if len(provisional_filter) == 0:
            result = True
        else:
            inverted = provisional_filter[0]["inverted"]
            if provisional_filter[0]["provisionaltype"] == "Provisional":
                if inverted is False:
                    result = "only provisional"
                else:
                    result = False
            if provisional_filter[0]["provisionaltype"] == "Authoritative":
                if inverted is False:
                    result = False
                else:
                    result = "only provisional"

    return result


def get_permitted_nodegroups(user):
    return get_nodegroups_by_perm(user, "models.read_nodegroup")


@requires_elasticsearch
def buffer(request):
    spatial_filter = JSONDeserializer().deserialize(
        request.GET.get(
            "filter",
            {
                "geometry": {"type": "", "coordinates": []},
                "buffer": {"width": "0", "unit": "ft"},
            },
        )
    )

    if (
        spatial_filter["geometry"]["coordinates"] != ""
        and spatial_filter["geometry"]["type"] != ""
    ):
        return JSONResponse(
            _buffer(
                spatial_filter["geometry"],
                spatial_filter["buffer"]["width"],
                spatial_filter["buffer"]["unit"],
            ),
            geom_format="json",
        )

    return JSONResponse()


def _buffer(geojson, width=0, unit="ft"):
    geojson = JSONSerializer().serialize(geojson)
    geom = GEOSGeometry(geojson, srid=4326)

    try:
        width = float(width)
    except Exception:
        width = 0

    if width > 0:
        if unit == "ft":
            width = width / 3.28084
        with connection.cursor() as cursor:
            # Transform geom to the analysis SRID, buffer it, and transform it back to wgs84
            cursor.execute(
                """SELECT ST_TRANSFORM(
                    ST_BUFFER(ST_TRANSFORM(ST_SETSRID(%s::geometry, 4326), %s), %s),
                4326)""",
                (
                    geom.hex.decode("utf-8"),
                    settings.ANALYSIS_COORDINATE_SYSTEM_SRID,
                    width,
                ),
            )
            res = cursor.fetchone()
            geom = GEOSGeometry(res[0], srid=4326)
    return geom


def _get_child_concepts(conceptid):
    ret = {conceptid}
    for row in Concept().get_child_concepts(conceptid, ["prefLabel"]):
        ret.add(row[0])
    return list(ret)


@requires_elasticsearch
def time_wheel_config(request):
    time_wheel = TimeWheel()
    key = "time_wheel_config_{0}".format(request.user.username)
    config = cache.get(key)
    if config is None:
        config = time_wheel.time_wheel_config(request.user)
    return JSONResponse(config, indent=4)


@requires_elasticsearch
def get_export_file(request):
    exportid = request.GET.get("exportid", None)
    user = request.user
    url = None
    if exportid is not None:
        export = SearchExportHistory.objects.get(pk=exportid)
        try:
            url = export.downloadfile.url
            return JSONResponse({"message": _("Downloading"), "url": url}, indent=4)
        except ValueError:
            return JSONResponse(
                {"message": _("The requested file is no longer available")}, indent=4
            )
