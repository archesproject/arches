from arches.app.models.system_settings import settings
from arches.app.search.components.base import BaseSearchFilter
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.utils.permission_backend import user_is_resource_reviewer
from datetime import datetime
import json

class CoreSearchFilter(BaseSearchFilter):
    def view_data():
        pass

    def append_dsl(self, search_results_object, permitted_nodegroups, include_provisional, request):
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
        load_tiles = request.GET.get("tiles", False)
        if load_tiles:
            try:
                load_tiles = json.loads(load_tiles)
            except TypeError:
                pass
        if load_tiles:
            search_results_object["query"].include("tiles")

    
    def execute_query(self, search_results_object, response_object, request):
        for_export = request.GET.get("export", None)
        pages = request.GET.get("pages", None)
        total = int(request.GET.get("total", "0"))
        resourceinstanceid = request.GET.get("id", None)
        dsl = search_results_object["query"]
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

        if results is not None:
            if "hits" not in results:
                if "docs" in results:
                    results = {"hits": {"hits": results["docs"]}}
                else:
                    results = {"hits": {"hits": [results]}}
        response_object["results"] = results
    
    def post_search_hook(search_results_object, response_object, permitted_nodegroups, request):
        dsl = search_results_object["query"]
        response_object["reviewer"] = user_is_resource_reviewer(request.user)
        response_object["timestamp"] = datetime.now()
        response_object["total_results"] = dsl.count(index=RESOURCES_INDEX)
        response_object["userid"] = request.user.id
    