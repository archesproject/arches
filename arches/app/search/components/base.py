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
#         "default": True, # set for CoreSearch components; only 1 can be the default
#         "requiredComponents": [ # other components on which this one depends
#             {
#                 "componentname": "paging-filter",
#                 "searchcomponentid": "7aff5819-651c-4390-9b9a-a61221ba52c6",
#                 "sortorder": 1,
#             },
#             {
#                 "componentname": "provisional-filter",
#                 "searchcomponentid": "073406ed-93e5-4b5b-9418-b61c26b3640f",
#                 "sortorder": 2,
#             },
#             {
#                 "componentname": "search-results",
#                 "searchcomponentid": "00673743-8c1c-4cc0-bd85-c073a52e03ec",
#                 "sortorder": 3,
#             }
#         ]
#     }
# }


class BaseSearchFilter:
    def __init__(self, request=None, user=None):
        self.request = request
        self.user = user

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


class BaseCoreSearch(BaseSearchFilter):
    """
    Special type of component that specifies which other components to be used,
    how to execute a search in the search_results method
    """

    def __init__(self, request=None, user=None, componentname=None):
        super().__init__(request=request, user=user)
        self.core_component = models.SearchComponent.objects.get(
            componentname=componentname
        )
        self._required_search_components = list(
            models.SearchComponent.objects.filter(
                searchcomponentid__in=[
                    required_component["searchcomponentid"]
                    for required_component in self.core_component.config[
                        "requiredComponents"
                    ]
                ]
            )
        )
        self._available_search_components = list(
            models.SearchComponent.objects.filter(
                searchcomponentid__in=[
                    required_component["searchcomponentid"]
                    for required_component in self.core_component.config[
                        "availableComponents"
                    ]
                ]
            )
        )

    @property
    def required_search_components(self):
        return self._required_search_components

    @property
    def available_search_components(self):
        return self._available_search_components

    def get_searchview_components(self):
        return self._available_search_components + [self.core_component]

    def handle_search_results_query(
        self, search_query_object, response_object, search_filter_factory, returnDsl
    ):
        """
        Called in-place to modify both search_query_object and response_object
        See arches.app.search.components.arches_core_search for example implementation
        """

        sorted_query_obj = search_filter_factory.create_search_query_dict(
            list(self.request.GET.items()) + list(self.request.POST.items())
        )

        for filter_type, querystring in list(sorted_query_obj.items()):
            search_filter = search_filter_factory.get_filter(filter_type)
            if search_filter:
                search_filter.append_dsl(search_query_object)

        if returnDsl:
            return search_query_object.pop("query", None)

        for filter_type, querystring in list(sorted_query_obj.items()):
            search_filter = search_filter_factory.get_filter(filter_type)
            if search_filter:
                search_filter.execute_query(search_query_object, response_object)

        if response_object["results"] is not None:
            # allow filters to modify the results
            for filter_type, querystring in list(sorted_query_obj.items()):
                search_filter = search_filter_factory.get_filter(filter_type)
                if search_filter:
                    search_filter.post_search_hook(search_query_object, response_object)


class SearchFilterFactory(object):
    def __init__(self, request=None, user=None):
        self.request = request
        self.user = user
        self.search_filters = {
            search_filter.componentname: search_filter
            for search_filter in models.SearchComponent.objects.all()
        }
        self.search_filters_instances = {}

    def get_filter(self, componentname, core=False):
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
                if class_method and core:
                    filter_instance = class_method(
                        self.request, self.user, componentname
                    )
                elif class_method:
                    filter_instance = class_method(self.request, self.user)
                self.search_filters_instances[search_filter.componentname] = (
                    filter_instance
                )
            return filter_instance
        else:
            return None

    def get_core_component_name(self):
        if not self.request:
            core_search_component_name = None
        elif self.request.method == "POST":
            core_search_component_name = self.request.POST.get("core", None)
        else:
            core_search_component_name = self.request.GET.get("core", None)

        if not core_search_component_name:
            # get default core search component
            core_search_component = list(
                filter(
                    lambda x: x.config.get("default", False) and x.type == "core",
                    list(self.search_filters.values()),
                )
            )[0]
            core_search_component_name = core_search_component.componentname

        return core_search_component_name

    def get_core_component_instance(self):
        core_search_component_name = self.get_core_component_name()
        core_search_component_instance = self.get_filter(
            core_search_component_name, core=True
        )
        return core_search_component_instance

    def get_sorted_query_dict(self, query_dict, core_search_component):
        component_sort_order = {
            item["componentname"]: int(item["sortorder"])
            for item in core_search_component.config["requiredComponents"]
        }
        # Sort the query_dict items based on the requiredComponent's sortorder
        sorted_items = sorted(
            query_dict.items(),
            key=lambda item: component_sort_order.get(item[0], float("inf")),
        )

        return dict(sorted_items)

    def get_query_dict_with_core_component(self, query_dict: Dict[str, Any]):
        """
        Set core=arches-core-search on query_dict to arches-core-search=True
        """
        ret = dict(query_dict)
        core_component_name = self.get_core_component_name()
        ret[core_component_name] = True
        # check that all core-search component requiredComponents are present
        for required_component in self.search_filters[core_component_name].config[
            "requiredComponents"
        ]:
            if required_component["componentname"] not in ret:
                ret[required_component["componentname"]] = {}

        return ret, self.search_filters[core_component_name]

    def create_search_query_dict(self, key_value_pairs: List[Tuple[str, Any]]):
        # handles list of key,value tuples so that dict-like data from POST and GET
        # requests can be concatenated into single method call
        query_dict, core_search_component = self.get_query_dict_with_core_component(
            dict(key_value_pairs)
        )
        return self.get_sorted_query_dict(query_dict, core_search_component)
