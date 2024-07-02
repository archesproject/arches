from arches.app.models.system_settings import settings
from arches.app.search.components.base import CoreSearchComponent
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.utils.permission_backend import (
    user_is_resource_reviewer,
    user_is_resource_exporter,
)
from datetime import datetime
import json


details = {
    "searchcomponentid": "69695d63-6f03-4536-8da9-841b07116381",
    "name": "Arches Core Search",
    "icon": "",
    "modulename": "arches_core_search.py",
    "classname": "ArchesCoreSearch",
    "type": "core",
    "componentpath": "views/components/search/arches-core-search",
    "componentname": "arches-core-search",
    "config": {
        "default": True,
        "requiredComponents": [
            {
                "componentname": "map-filter",
                "searchcomponentid": "09d97fc6-8c83-4319-9cef-3aaa08c3fbec",
                "sortorder": 1,
            },
            {
                "componentname": "advanced-search",
                "searchcomponentid": "f0e56205-acb5-475b-9c98-f5e44f1dbd2c",
                "sortorder": 2,
            },
            {
                "componentname": "related-resources-filter",
                "searchcomponentid": "59f28272-d1f1-4805-af51-227771739aed",
                "sortorder": 3,
            },
            {
                "componentname": "provisional-filter",
                "searchcomponentid": "073406ed-93e5-4b5b-9418-b61c26b3640f",
                "sortorder": 4,
            },
            {
                "componentname": "resource-type-filter",
                "searchcomponentid": "f1c46b7d-0132-421b-b1f3-95d67f9b3980",
                "sortorder": 5,
            },
            {
                "componentname": "saved-searches",
                "searchcomponentid": "6dc29637-43a1-4fba-adae-8d9956dcd3b9",
                "sortorder": 6,
            },
            {
                "componentname": "search-export",
                "searchcomponentid": "9c6a5a9c-a7ec-48d2-8a25-501b55b8eff6",
                "sortorder": 7,
            },
            {
                "componentname": "search-result-details",
                "searchcomponentid": "f5986dae-8b01-11ea-b65a-77903936669c",
                "sortorder": 8,
            },
            {
                "componentname": "sort-results",
                "searchcomponentid": "6a2fe122-de54-4e44-8e93-b6a0cda7955c",
                "sortorder": 9,
            },
            {
                "componentname": "term-filter",
                "searchcomponentid": "1f42f501-ed70-48c5-bae1-6ff7d0d187da",
                "sortorder": 10,
            },
            {
                "componentname": "time-filter",
                "searchcomponentid": "7497ed4f-2085-40da-bee5-52076a48bcb1",
                "sortorder": 11,
            },
            {
                "componentname": "paging-filter",
                "searchcomponentid": "7aff5819-651c-4390-9b9a-a61221ba52c6",
                "sortorder": 12,
            },
            {
                "componentname": "search-results",
                "searchcomponentid": "00673743-8c1c-4cc0-bd85-c073a52e03ec",
                "sortorder": 13,
            },
        ],
    },
}

SEARCH_RESULT_PAGES = (
    int(settings.SEARCH_EXPORT_LIMIT // settings.SEARCH_RESULT_LIMIT) - 1
)


class ArchesCoreSearch(CoreSearchComponent):

    def append_dsl(
        self, search_results_object, permitted_nodegroups, include_provisional
    ):
        search_results_object["query"].include("graph_id")
        search_results_object["query"].include("root_ontology_class")
        search_results_object["query"].include("resourceinstanceid")
        search_results_object["query"].include("points")
        search_results_object["query"].include("permissions.users_without_read_perm")
        search_results_object["query"].include("permissions.users_without_edit_perm")
        search_results_object["query"].include("permissions.users_without_delete_perm")
        search_results_object["query"].include("permissions.users_with_no_access")
        search_results_object["query"].include("geometries")
        search_results_object["query"].include("displayname")
        search_results_object["query"].include("displaydescription")
        search_results_object["query"].include("map_popup")
        search_results_object["query"].include("provisional_resource")
        load_tiles = self.request.GET.get("tiles", False)
        if load_tiles:
            try:
                load_tiles = json.loads(load_tiles)
            except TypeError:
                pass
        if load_tiles:
            search_results_object["query"].include("tiles")

    def execute_query(self, search_results_object, response_object):
        for_export = self.request.GET.get("export", None)
        pages = self.request.GET.get("pages", None)
        total = int(self.request.GET.get("total", "0"))
        resourceinstanceid = self.request.GET.get("id", None)
        dsl = search_results_object["query"]
        if for_export or pages:
            results = dsl.search(index=RESOURCES_INDEX, scroll="1m")
            scroll_id = results["_scroll_id"]
            if not pages:
                if total <= settings.SEARCH_EXPORT_LIMIT:
                    pages = (total // settings.SEARCH_RESULT_LIMIT) + 1
                else:
                    pages = SEARCH_RESULT_PAGES
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
        response_object["results"] = results

    def post_search_hook(
        self, search_results_object, response_object, permitted_nodegroups
    ):
        dsl = search_results_object["query"]
        response_object["reviewer"] = user_is_resource_reviewer(self.request.user)
        response_object["timestamp"] = datetime.now()
        response_object["total_results"] = dsl.count(index=RESOURCES_INDEX)
        response_object["userid"] = self.request.user.id

    def get_search_components(self):
        search_components = [
            required_component
            for required_component in self._required_search_components
            if required_component.componentname != "search-export"
        ]
        # TODO: Apply new permission logic after #11005 is merged
        if user_is_resource_exporter(self.request.user):
            search_components.extend(
                [
                    required_component
                    for required_component in self._required_search_components
                    if required_component.componentname == "search-export"
                ]
            )

        search_components.append(self.core_component)

        return search_components
