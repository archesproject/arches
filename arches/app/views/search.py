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

import logging
import os

from django.contrib.gis.geos import GEOSGeometry
from django.core.cache import cache
from django.db import connection
from django.http import Http404
from django.shortcuts import render
from django.utils.translation import gettext as _
from arches.app.models.models import (
    MapMarker,
    GraphModel,
    DDataType,
    Widget,
    ReportTemplate,
    CardComponent,
    Geocoder,
    Node,
    SearchExportHistory,
)
from arches.app.models.concept import Concept, get_preflabel_from_conceptid
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    Match,
    Query,
    Term,
    Terms,
    MaxAgg,
    Aggregation,
)
from arches.app.search.search_export import SearchResultsExporter
from arches.app.search.time_wheel import TimeWheel
from arches.app.search.components.base import SearchFilterFactory
from arches.app.views.base import MapBaseManagerView
from arches.app.utils import permission_backend
from arches.app.utils.permission_backend import (
    get_nodegroups_by_perm,
    user_is_resource_reviewer,
)
from arches.app.utils.decorators import group_required
import arches.app.utils.zip as zip_utils
import arches.app.utils.task_management as task_management
from arches.app.utils.data_management.resources.formats.htmlfile import HtmlWriter
import arches.app.tasks as tasks
from io import StringIO
from tempfile import NamedTemporaryFile
from arches.app.models.system_settings import settings

logger = logging.getLogger(__name__)


class SearchView(MapBaseManagerView):
    def get(self, request):
        map_markers = MapMarker.objects.all()
        resource_graphs = (
            GraphModel.objects.exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(isresource=False)
            .exclude(publication=None)
        )
        geocoding_providers = Geocoder.objects.all()
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
            geocoding_providers=geocoding_providers,
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

        return render(request, "views/search.htm", context)


def home_page(request):
    return render(
        request,
        "views/search.htm",
        {
            "main_script": "views/search",
        },
    )


def search_terms(request):
    lang = request.GET.get("lang", request.LANGUAGE_CODE)
    se = SearchEngineFactory().create()
    searchString = request.GET.get("q", "")
    user_is_reviewer = user_is_resource_reviewer(request.user)

    i = 0
    ret = {}
    for index in ["terms", "concepts"]:
        query = Query(se, start=0, limit=0)
        boolquery = Bool()

        if lang != "*":
            boolquery.must(Term(field="language", term=lang))

        boolquery.should(
            Match(field="value", query=searchString.lower(), type="phrase_prefix")
        )
        boolquery.should(
            Match(
                field="value.folded", query=searchString.lower(), type="phrase_prefix"
            )
        )
        boolquery.should(
            Match(
                field="value.folded",
                query=searchString.lower(),
                fuzziness="AUTO",
                prefix_length=settings.SEARCH_TERM_SENSITIVITY,
            )
        )
        boolquery.should(
            Match(field="displayname.value", query=searchString, fuzziness=2, boost=2)
        )

        if user_is_reviewer is False and index == "terms":
            boolquery.filter(Terms(field="provisional", terms=["false"]))

        query.add_query(boolquery)
        base_agg = Aggregation(
            name="value_agg",
            type="terms",
            field="value.raw",
            size=settings.SEARCH_DROPDOWN_LENGTH,
            order={"max_score": "desc"},
        )
        nodegroupid_agg = Aggregation(
            name="nodegroupid", type="terms", field="nodegroupid"
        )
        top_concept_agg = Aggregation(
            name="top_concept", type="terms", field="top_concept"
        )
        conceptid_agg = Aggregation(name="conceptid", type="terms", field="conceptid")
        max_score_agg = MaxAgg(name="max_score", script="_score")

        top_concept_agg.add_aggregation(conceptid_agg)
        base_agg.add_aggregation(max_score_agg)
        base_agg.add_aggregation(top_concept_agg)
        base_agg.add_aggregation(nodegroupid_agg)
        query.add_aggregation(base_agg)

        ret[index] = []
        results = query.search(index=index)
        if results is not None:
            for result in results["aggregations"]["value_agg"]["buckets"]:
                if len(result["top_concept"]["buckets"]) > 0:
                    for top_concept in result["top_concept"]["buckets"]:
                        top_concept_id = top_concept["key"]
                        top_concept_label = get_preflabel_from_conceptid(
                            top_concept["key"], lang=lang if lang != "*" else None
                        )["value"]
                        for concept in top_concept["conceptid"]["buckets"]:
                            ret[index].append(
                                {
                                    "type": "concept",
                                    "context": top_concept_id,
                                    "context_label": top_concept_label,
                                    "id": i,
                                    "text": result["key"],
                                    "value": concept["key"],
                                }
                            )
                        i = i + 1
                else:
                    ret[index].append(
                        {
                            "type": "term",
                            "context": "",
                            "context_label": get_resource_model_label(result),
                            "id": i,
                            "text": result["key"],
                            "value": result["key"],
                            "nodegroupid": result["nodegroupid"]["buckets"][0]["key"],
                        }
                    )
                    i = i + 1

    return JSONResponse(ret)


def get_resource_model_label(result):
    if len(result["nodegroupid"]["buckets"]) > 0:
        for nodegroup in result["nodegroupid"]["buckets"]:
            nodegroup_id = nodegroup["key"]
            node = Node.objects.get(nodeid=nodegroup_id)
            graph = node.graph
        return "{0} - {1}".format(graph.name, node.name)
    else:
        return ""


@group_required("Resource Exporter")
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


def get_dsl_from_search_string(request):
    dsl = search_results(request, returnDsl=True).dsl
    return JSONResponse(dsl)


def search_results(request, returnDsl=False):
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


def time_wheel_config(request):
    time_wheel = TimeWheel()
    key = "time_wheel_config_{0}".format(request.user.username)
    config = cache.get(key)
    if config is None:
        config = time_wheel.time_wheel_config(request.user)
    return JSONResponse(config, indent=4)


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
