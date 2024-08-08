from typing import List, Tuple, Any, Dict
from arches.app.const import ExtensionType
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.module_importer import get_class_from_modulename

details = {}
# details = {
#     "searchcomponentid": "",  # leave blank for the system to generate a uuid
#     "name": "",  # the name that shows up in the UI
#     "icon": "",  # the icon class to use
#     "modulename": "base.py",  # the name of this file
#     "classname": "BaseSearchFilter",  # the classname below",
#     "type": "filter",  # 'filter' if you want the component to show up dynamically
#     "componentpath": "views/components/search/...",  # path to ko component
#     "componentname": "advanced-search",  # lowercase unique name
#     "config": {
#         "requiredComponents": [ # other components on which this one depends
#             {
#                 "componentname": "search-results",
#                 "searchcomponentid": "00673743-8c1c-4cc0-bd85-c073a52e03ec",
#                 "sortorder": 3,
#             }
#         ]
#     }
# }


class BaseSearchFilter:
    def __init__(self, request=None, user=None, componentname=None):
        self.request = request
        self.user = user
        self.componentname = componentname

    def append_dsl(self, search_query_object, **kwargs):
        """
        used to append ES query dsl to the search request

        """

        pass

    def view_data(self):
        """
        data that the view should gather to pass to the front end

        """

        pass

    def execute_query(self, search_query_object, response_object, **kwargs):
        """
        code responsible for execution of the search query logic and mutation of the response object
        """
        pass

    def post_search_hook(self, search_query_object, response_object, **kwargs):
        """
        code to run after the search results have been retrieved

        """

        pass


class SearchFilterFactory(object):
    def __init__(self, request=None, user=None):
        self.request = request
        self.user = user
        self.search_filters = {
            search_filter.componentname: search_filter
            for search_filter in models.SearchComponent.objects.all()
        }
        self.search_filters_instances = {}

    def get_filter(self, componentname):
        if componentname in self.search_filters:
            search_filter = self.search_filters[componentname]
            try:
                filter_instance = self.search_filters_instances[
                    search_filter.componentname
                ]
            except:
                filter_instance = None
                class_method = get_class_from_modulename(
                    search_filter.modulename,
                    search_filter.classname,
                    ExtensionType.SEARCH_COMPONENTS,
                )
                if class_method:
                    filter_instance = class_method(
                        self.request, self.user, componentname
                    )
                self.search_filters_instances[search_filter.componentname] = (
                    filter_instance
                )
            return filter_instance
        else:
            return None

    def get_searchview_component_name(self):
        if not self.request:
            searchview_component_name = None
        elif self.request.method == "POST":
            searchview_component_name = self.request.POST.get("search-view", None)
        else:
            searchview_component_name = self.request.GET.get("search-view", None)

        if not searchview_component_name:
            # get default search_view component
            searchview_component = list(
                filter(
                    lambda x: x.config.get("default", False)
                    and x.type == "search-view",
                    list(self.search_filters.values()),
                )
            )[0]
            searchview_component_name = searchview_component.componentname

        return searchview_component_name

    def get_searchview_component_instance(self):
        searchview_component_name = self.get_searchview_component_name()
        return self.get_filter(searchview_component_name)

    def get_sorted_query_dict(self, query_dict, searchview_component):
        component_sort_order = {
            item["componentname"]: int(item["sortorder"])
            for item in searchview_component.config["requiredComponents"]
        }
        # Sort the query_dict items based on the requiredComponent's sortorder
        sorted_items = sorted(
            query_dict.items(),
            key=lambda item: component_sort_order.get(item[0], float("inf")),
        )

        return dict(sorted_items)

    def get_query_dict_with_searchview_component(self, query_dict: Dict[str, Any]):
        """
        Set search-view=arches-search-view on query_dict to arches-search-view=True
        """
        ret = dict(query_dict)
        searchview_component_name = self.get_searchview_component_name()
        ret[searchview_component_name] = True
        # check that all core-search component requiredComponents are present
        for required_component in self.search_filters[searchview_component_name].config[
            "requiredComponents"
        ]:
            if required_component["componentname"] not in ret:
                ret[required_component["componentname"]] = {}

        return ret, self.search_filters[searchview_component_name]

    def create_search_query_dict(self, key_value_pairs: List[Tuple[str, Any]]):
        # handles list of key,value tuples so that dict-like data from POST and GET
        # requests can be concatenated into single method call
        query_dict, searchview_component = (
            self.get_query_dict_with_searchview_component(dict(key_value_pairs))
        )
        return self.get_sorted_query_dict(query_dict, searchview_component)
