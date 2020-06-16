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
#     "sortorder": "0",  # order in which to display dynamically added filters to the UI
#     "enabled": True  # True to enable in the system
# }


class BaseSearchFilter:
    def __init__(self, request=None):
        self.request = request

    def append_dsl(self, search_results_object, permitted_nodegroups, include_provisional):
        """
        used to append ES query dsl to the search request

        """

        pass

    def view_data(self):
        """
        data that the view should gather to pass to the front end

        """

        pass

    def post_search_hook(self, search_results_object, results, permitted_nodegroups):
        """
        code to run after the search results have been retrieved

        """

        pass


class SearchFilterFactory(object):
    def __init__(self, request=None):
        self.request = request
        self.search_filters = {search_filter.componentname: search_filter for search_filter in models.SearchComponent.objects.all()}
        self.search_filters_instances = {}

    def get_filter(self, componentname):
        if componentname in self.search_filters:
            search_filter = self.search_filters[componentname]
            try:
                filter_instance = self.search_filters_instances[search_filter.componentname]
            except:
                filter_instance = None
                class_method = get_class_from_modulename(
                    search_filter.modulename, search_filter.classname, settings.SEARCH_COMPONENT_LOCATIONS
                )
                if class_method:
                    filter_instance = class_method(self.request)
                self.search_filters_instances[search_filter.componentname] = filter_instance
            return filter_instance
        else:
            return None
