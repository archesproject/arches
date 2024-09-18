from typing import Dict, Tuple

from arches.app.models.system_settings import settings
from arches.app.search.components.base_search_view import BaseSearchView
from arches.app.search.components.base import SearchFilterFactory
from arches.app.search.elasticsearch_dsl_builder import Query
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.views.search import (
    append_instance_permission_filter_dsl,
    get_permitted_nodegroups,
    get_provisional_type,
)
from arches.app.utils.permission_backend import (
    user_is_resource_reviewer,
    user_is_resource_exporter,
)
from arches.app.utils.string_utils import get_str_kwarg_as_bool
from django.utils.translation import gettext as _
from datetime import datetime
import logging


details = {
    "searchcomponentid": "69695d63-6f03-4536-8da9-841b07116381",
    "name": "Standard Search View",
    "icon": "",
    "modulename": "standard_search_view.py",
    "classname": "StandardSearchView",
    "type": "search-view",
    "componentpath": "views/components/search/standard-search-view",
    "componentname": "standard-search-view",
    "config": {
        "default": True,
        "linkedSearchFilters": [
            {
                "componentname": "paging-filter",
                "searchcomponentid": "7aff5819-651c-4390-9b9a-a61221ba52c6",
                "layoutSortorder": 1,
                "required": True,
                "executionSortorder": 2,
            },
            {
                "componentname": "search-results",
                "searchcomponentid": "00673743-8c1c-4cc0-bd85-c073a52e03ec",
                "layoutSortorder": 2,
            },
            {
                "componentname": "map-filter",
                "searchcomponentid": "09d97fc6-8c83-4319-9cef-3aaa08c3fbec",
                "layoutSortorder": 1,
            },
            {
                "componentname": "advanced-search",
                "searchcomponentid": "f0e56205-acb5-475b-9c98-f5e44f1dbd2c",
                "layoutSortorder": 2,
            },
            {
                "componentname": "related-resources-filter",
                "searchcomponentid": "59f28272-d1f1-4805-af51-227771739aed",
                "layoutSortorder": 3,
            },
            {
                "componentname": "provisional-filter",
                "searchcomponentid": "073406ed-93e5-4b5b-9418-b61c26b3640f",
                "layoutSortorder": 4,
            },
            {
                "componentname": "resource-type-filter",
                "searchcomponentid": "f1c46b7d-0132-421b-b1f3-95d67f9b3980",
                "layoutSortorder": 5,
            },
            {
                "componentname": "saved-searches",
                "searchcomponentid": "6dc29637-43a1-4fba-adae-8d9956dcd3b9",
                "layoutSortorder": 6,
            },
            {
                "componentname": "search-export",
                "searchcomponentid": "9c6a5a9c-a7ec-48d2-8a25-501b55b8eff6",
                "layoutSortorder": 7,
            },
            {
                "componentname": "search-result-details",
                "searchcomponentid": "f5986dae-8b01-11ea-b65a-77903936669c",
                "layoutSortorder": 8,
            },
            {
                "componentname": "sort-results",
                "searchcomponentid": "6a2fe122-de54-4e44-8e93-b6a0cda7955c",
                "layoutSortorder": 9,
            },
            {
                "componentname": "term-filter",
                "searchcomponentid": "1f42f501-ed70-48c5-bae1-6ff7d0d187da",
                "layoutSortorder": 10,
            },
            {
                "componentname": "time-filter",
                "searchcomponentid": "7497ed4f-2085-40da-bee5-52076a48bcb1",
                "layoutSortorder": 11,
            },
            {
                "componentname": "paging-filter",
                "searchcomponentid": "7aff5819-651c-4390-9b9a-a61221ba52c6",
                "layoutSortorder": 12,
            },
            {
                "componentname": "search-results",
                "searchcomponentid": "00673743-8c1c-4cc0-bd85-c073a52e03ec",
                "layoutSortorder": 13,
                "required": True,
                "executionSortorder": 1,
            },
        ],
    },
}

logger = logging.getLogger(__name__)


class StandardSearchView(BaseSearchView):

    def append_dsl(self, search_query_object, **kwargs):
        search_query_object["query"].include("graph_id")
        search_query_object["query"].include("root_ontology_class")
        search_query_object["query"].include("resourceinstanceid")
        search_query_object["query"].include("points")
        search_query_object["query"].include("geometries")
        search_query_object["query"].include("displayname")
        search_query_object["query"].include("displaydescription")
        search_query_object["query"].include("map_popup")
        search_query_object["query"].include("provisional_resource")
        search_query_object["query"].include("permissions")
        load_tiles = get_str_kwarg_as_bool("tiles", self.request.GET)
        if load_tiles:
            search_query_object["query"].include("tiles")

    def execute_query(self, search_query_object, response_object, **kwargs):
        for_export = get_str_kwarg_as_bool("export", self.request.GET)
        pages = self.request.GET.get("pages", None)
        total = int(self.request.GET.get("total", "0"))
        resourceinstanceid = self.request.GET.get("id", None)
        dsl = search_query_object["query"]
        if for_export or pages:
            results = dsl.search(index=RESOURCES_INDEX, scroll="1m")
            scroll_id = results["_scroll_id"]
            if not pages:
                if total <= settings.SEARCH_EXPORT_LIMIT:
                    pages = (total // settings.SEARCH_RESULT_LIMIT) + 1
                else:
                    pages = (
                        int(
                            settings.SEARCH_EXPORT_LIMIT // settings.SEARCH_RESULT_LIMIT
                        )
                        - 1
                    )
            for page in range(int(pages)):
                results_scrolled = dsl.se.es.scroll(scroll_id=scroll_id, scroll="1m")
                results["hits"]["hits"] += results_scrolled["hits"]["hits"]
        else:
            results = dsl.search(index=RESOURCES_INDEX, id=resourceinstanceid)

        if results is not None:
            if "hits" not in results:
                if "docs" in results:
                    results = {"hits": {"hits": results["docs"]}}
                else:
                    results = {"hits": {"hits": [results]}}

                results["hits"]["total"] = {"value": len(results["hits"]["hits"])}

        response_object["results"] = results

    def post_search_hook(self, search_query_object, response_object, **kwargs):
        dsl = search_query_object["query"]
        response_object["reviewer"] = user_is_resource_reviewer(self.request.user)
        response_object["timestamp"] = datetime.now()
        response_object["total_results"] = dsl.count(index=RESOURCES_INDEX)
        response_object["userid"] = self.request.user.id

    def get_searchview_filters(self):
        search_filters = [
            available_filter
            for available_filter in self.available_search_filters
            if available_filter.componentname != "search-export"
        ]
        if user_is_resource_exporter(self.request.user):
            search_filters.extend(
                [
                    available_filter
                    for available_filter in self.available_search_filters
                    if available_filter.componentname == "search-export"
                ]
            )

        search_filters.append(self.searchview_component)

        return search_filters

    def handle_search_results_query(
        self,
        search_filter_factory: SearchFilterFactory,
        returnDsl: bool,
    ) -> Tuple[Dict, Dict]:
        se = SearchEngineFactory().create()
        search_query_object = {"query": Query(se)}
        response_object = {"results": None}
        sorted_query_obj = search_filter_factory.create_search_query_dict(
            list(self.request.GET.items()) + list(self.request.POST.items())
        )
        permitted_nodegroups = get_permitted_nodegroups(self.request.user)
        include_provisional = get_provisional_type(self.request)
        try:
            for filter_type, querystring in list(sorted_query_obj.items()):
                search_filter = search_filter_factory.get_filter(filter_type)
                if search_filter:
                    search_filter.append_dsl(
                        search_query_object,
                        permitted_nodegroups=permitted_nodegroups,
                        include_provisional=include_provisional,
                        querystring=querystring,
                    )
            append_instance_permission_filter_dsl(self.request, search_query_object)
        except Exception as err:
            logger.exception(err)
            message = {
                "message": _("Error: {0}. Search failed.").format(str(err)),
            }
            raise Exception(message)

        if returnDsl:
            return response_object, search_query_object

        for filter_type, querystring in list(sorted_query_obj.items()):
            search_filter = search_filter_factory.get_filter(filter_type)
            if search_filter:
                search_filter.execute_query(search_query_object, response_object)

        if response_object["results"] is not None:
            # allow filters to modify the results
            for filter_type, querystring in list(sorted_query_obj.items()):
                search_filter = search_filter_factory.get_filter(filter_type)
                if search_filter:
                    search_filter.post_search_hook(
                        search_query_object,
                        response_object,
                        permitted_nodegroups=permitted_nodegroups,
                    )

            search_query_object.pop("query")
            # ensure that if a search filter modified the query in some way
            # that the modification is set on the response_object
            for key, value in list(search_query_object.items()):
                if key not in response_object:
                    response_object[key] = value

        return response_object, search_query_object
