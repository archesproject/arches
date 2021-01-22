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

import os
import logging
from datetime import datetime
from django.contrib.gis.geos import GEOSGeometry
from django.core.cache import cache
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils.translation import ugettext as _
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, MaxAgg, Aggregation
from arches.app.search.search_export import SearchResultsExporter
from arches.app.search.time_wheel import TimeWheel
from arches.app.search.components.base import SearchFilterFactory
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.views.base import MapBaseManagerView
from arches.app.models.concept import get_preflabel_from_conceptid
from arches.app.utils.permission_backend import get_nodegroups_by_perm, user_is_resource_reviewer
import arches.app.utils.zip as zip_utils
import arches.app.utils.task_management as task_management
import arches.app.tasks as tasks
from io import StringIO

logger = logging.getLogger(__name__)

class SearchView(MapBaseManagerView):
    def get(self, request):
        map_layers = models.MapLayer.objects.all()
        map_markers = models.MapMarker.objects.all()
        map_sources = models.MapSource.objects.all()
        resource_graphs = (
            models.GraphModel.objects.exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(isresource=False)
            .exclude(isactive=False)
        )
        geocoding_providers = models.Geocoder.objects.all()
        search_components = models.SearchComponent.objects.all()
        datatypes = models.DDataType.objects.all()
        widgets = models.Widget.objects.all()
        templates = models.ReportTemplate.objects.all()
        card_components = models.CardComponent.objects.all()

        context = self.get_context_data(
            map_layers=map_layers,
            map_markers=map_markers,
            map_sources=map_sources,
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
            "template": "search-help",
        }
        context["celery_running"] = task_management.check_if_celery_available()

        return render(request, "views/search.htm", context)


def home_page(request):
    return render(request, "views/search.htm", {"main_script": "views/search",})


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
        boolquery.should(Match(field="value", query=searchString.lower(), type="phrase_prefix"))
        boolquery.should(Match(field="value.folded", query=searchString.lower(), type="phrase_prefix"))
        boolquery.should(
            Match(field="value.folded", query=searchString.lower(), fuzziness="AUTO", prefix_length=settings.SEARCH_TERM_SENSITIVITY)
        )

        if user_is_reviewer is False and index == "terms":
            boolquery.filter(Terms(field="provisional", terms=["false"]))

        query.add_query(boolquery)
        base_agg = Aggregation(
            name="value_agg", type="terms", field="value.raw", size=settings.SEARCH_DROPDOWN_LENGTH, order={"max_score": "desc"}
        )
        nodegroupid_agg = Aggregation(name="nodegroupid", type="terms", field="nodegroupid")
        top_concept_agg = Aggregation(name="top_concept", type="terms", field="top_concept")
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
                        top_concept_label = get_preflabel_from_conceptid(top_concept["key"], lang)["value"]
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
                        }
                    )
                    i = i + 1

    return JSONResponse(ret)


def get_resource_model_label(result):
    if len(result["nodegroupid"]["buckets"]) > 0:
        for nodegroup in result["nodegroupid"]["buckets"]:
            nodegroup_id = nodegroup["key"]
            node = models.Node.objects.get(nodeid=nodegroup_id)
            graph = node.graph
        return "{0} - {1}".format(graph.name, node.name)
    else:
        return ""


def export_results(request):

    total = int(request.GET.get("total", 0))
    format = request.GET.get("format", "tilecsv")
    download_limit = settings.SEARCH_EXPORT_IMMEDIATE_DOWNLOAD_THRESHOLD
    if total > download_limit:
        celery_worker_running = task_management.check_if_celery_available()
        if celery_worker_running is True:
            request_values = dict(request.GET)
            request_values["path"] = request.get_full_path()
            result = tasks.export_search_results.apply_async(
                (request.user.id, request_values, format), link=tasks.update_user_task_record.s(), link_error=tasks.log_error.s()
            )
            message = _(
                "{total} instances have been submitted for export. \
                Click the Bell icon to check for a link to download your data"
            ).format(**locals())
            return JSONResponse({"success": True, "message": message})
        else:
            message = _("Your search exceeds the {download_limit} instance download limit. Please refine your search").format(**locals())
            return JSONResponse({"success": False, "message": message})
    else:
        exporter = SearchResultsExporter(search_request=request)
        export_files, export_info = exporter.export(format)
        if len(export_files) == 0 and format == "shp":
            message = _(
                "Either no instances were identified for export or no resources have exportable geometry nodes\
                Please confirm that the models of instances you would like to export have geometry nodes and that\
                those nodes are set as exportable"
            )
            dest = StringIO()
            dest.write(message)
            export_files.append({"name": "error.txt", "outputfile": dest})
        return zip_utils.zip_response(export_files, zip_file_name=f"{settings.APP_NAME}_export.zip")


def append_instance_permission_filter_dsl(request, search_results_object):
    if request.user.is_superuser is False:
        has_access = Bool()
        terms = Terms(field="permissions.users_with_no_access", terms=[str(request.user.id)])
        nested_term_filter = Nested(path="permissions", query=terms)
        has_access.must_not(nested_term_filter)
        search_results_object["query"].add_query(has_access)


def search_results(request):
    for_export = request.GET.get("export")
    pages = request.GET.get("pages", None)
    total = int(request.GET.get("total", "0"))
    resourceinstanceid = request.GET.get("id", None)
    se = SearchEngineFactory().create()
    search_results_object = {"query": Query(se)}

    include_provisional = get_provisional_type(request)
    permitted_nodegroups = get_permitted_nodegroups(request.user)

    search_filter_factory = SearchFilterFactory(request)
    try:
        for filter_type, querystring in list(request.GET.items()) + [("search-results", "")]:
            search_filter = search_filter_factory.get_filter(filter_type)
            if search_filter:
                search_filter.append_dsl(search_results_object, permitted_nodegroups, include_provisional)
        append_instance_permission_filter_dsl(request, search_results_object)
    except Exception as err:
        logger.exception(err)
        return JSONErrorResponse(message=err)

    dsl = search_results_object.pop("query", None)
    dsl.include("graph_id")
    dsl.include("root_ontology_class")
    dsl.include("resourceinstanceid")
    dsl.include("points")
    dsl.include("permissions.users_without_read_perm")
    dsl.include("permissions.users_without_edit_perm")
    dsl.include("permissions.users_without_delete_perm")
    dsl.include("permissions.users_with_no_access")
    dsl.include("geometries")
    dsl.include("displayname")
    dsl.include("displaydescription")
    dsl.include("map_popup")
    dsl.include("provisional_resource")
    if request.GET.get("tiles", None) is not None:
        dsl.include("tiles")
    if for_export or pages:
        results = dsl.search(index=RESOURCES_INDEX, scroll="1m")
        scroll_id = results["_scroll_id"]
        if not pages:
            if total <= settings.SEARCH_EXPORT_LIMIT:
                pages = (total // settings.SEARCH_RESULT_LIMIT) + 1
            if total > settings.SEARCH_EXPORT_LIMIT:
                pages = int(settings.SEARCH_EXPORT_LIMIT // settings.SEARCH_RESULT_LIMIT) - 1
        for page in range(int(pages)):
            results_scrolled = dsl.se.es.scroll(scroll_id=scroll_id, scroll="1m")
            results["hits"]["hits"] += results_scrolled["hits"]["hits"]
    else:
        results = dsl.search(index=RESOURCES_INDEX, id=resourceinstanceid)

    ret = {}
    if results is not None:
        if "hits" not in results:
            if "docs" in results:
                results = {"hits": {"hits": results["docs"]}}
            else:
                results = {"hits": {"hits": [results]}}

        # allow filters to modify the results
        for filter_type, querystring in list(request.GET.items()) + [("search-results", "")]:
            search_filter = search_filter_factory.get_filter(filter_type)
            if search_filter:
                search_filter.post_search_hook(search_results_object, results, permitted_nodegroups)

        ret["results"] = results

        for key, value in list(search_results_object.items()):
            ret[key] = value

        ret["reviewer"] = user_is_resource_reviewer(request.user)
        ret["timestamp"] = datetime.now()
        ret["total_results"] = dsl.count(index=RESOURCES_INDEX)
        ret["userid"] = request.user.id
        return JSONResponse(ret)

    else:
        ret = {"message": _("There was an error retrieving the search results")}
        return JSONResponse(ret, status=500)


def get_provisional_type(request):
    """
    Parses the provisional filter data to determine if a search results will
    include provisional (True) exclude provisional (False) or inlude only
    provisional 'only provisional'
    """

    result = False
    provisional_filter = JSONDeserializer().deserialize(request.GET.get("provisional-filter", "[]"))
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
    return [str(nodegroup.pk) for nodegroup in get_nodegroups_by_perm(user, "models.read_nodegroup")]


def buffer(request):
    spatial_filter = JSONDeserializer().deserialize(
        request.GET.get("filter", {"geometry": {"type": "", "coordinates": []}, "buffer": {"width": "0", "unit": "ft"}})
    )

    if spatial_filter["geometry"]["coordinates"] != "" and spatial_filter["geometry"]["type"] != "":
        return JSONResponse(
            _buffer(spatial_filter["geometry"], spatial_filter["buffer"]["width"], spatial_filter["buffer"]["unit"]), geom_format="json"
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

        geom.transform(settings.ANALYSIS_COORDINATE_SYSTEM_SRID)
        geom = geom.buffer(width)
        geom.transform(4326)

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
        export = models.SearchExportHistory.objects.get(pk=exportid)
        try:
            url = export.downloadfile.url
            return JSONResponse({"message": _("Downloading"), "url": url}, indent=4)
        except ValueError:
            return JSONResponse({"message": _("The requested file is no longer available")}, indent=4)
