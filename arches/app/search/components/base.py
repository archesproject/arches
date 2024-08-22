from typing import List, Tuple, Any
from arches.app.const import ExtensionType
from arches.app.models.models import SearchComponent
from arches.app.utils.module_importer import get_class_from_modulename

details = {}
# see docs for more info on developing search components:
# https://arches.readthedocs.io/en/latest/developing/reference/search-components/


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
            for search_filter in SearchComponent.objects.all()
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

    def get_searchview_name(self):
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

    def get_searchview_instance(self):
        searchview_component_name = self.get_searchview_name()
        return self.get_filter(searchview_component_name)

    def create_search_query_dict(self, key_value_pairs: List[Tuple[str, Any]]):
        # handles list of key,value tuples so that dict-like data from POST and GET
        # requests can be concatenated into single method call
        searchview_component_name = self.get_searchview_name()
        searchview_instance = self.get_filter(searchview_component_name)
        return searchview_instance.create_query_dict(dict(key_value_pairs))
