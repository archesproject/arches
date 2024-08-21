from arches.app.search.components.base import BaseSearchFilter
from arches.app.models.models import SearchComponent

details = {}
# details = {
#     "searchcomponentid": "",  # leave blank for the system to generate a uuid
#     "name": "",  # the name that shows up in the UI
#     "icon": "",  # the icon class to use
#     "modulename": "custom_search_view.py",  # the name of this file
#     "classname": "BaseSearchView",  # the classname below",
#     "type": "search-view",  # 'search-view' if you want this to govern the search
#     "componentpath": "views/components/search/...",  # path to ko component
#     "componentname": "custom-search-view",  # lowercase unique name
#     "config": {
#         "default": True, # set for search-view components; only 1 can be the default
#         "linkedSearchFilters": [
#             {
#                 "componentname":"map-filter","searchcomponentid":"09d97fc6-8c83-4319-9cef-3aaa08c3fbec","layoutSortorder":1
#             },
#             {
#                 "componentname":"advanced-search","searchcomponentid":"f0e56205-acb5-475b-9c98-f5e44f1dbd2c","layoutSortorder":2
#             },
#             {
#                 "componentname":"related-resources-filter","searchcomponentid":"59f28272-d1f1-4805-af51-227771739aed","layoutSortorder":3
#             },
#             {
#                 "componentname":"provisional-filter","searchcomponentid":"073406ed-93e5-4b5b-9418-b61c26b3640f","layoutSortorder":4
#             },
#             {
#                 "componentname":"term-filter","searchcomponentid":"1f42f501-ed70-48c5-bae1-6ff7d0d187da","layoutSortorder":10
#             },
#             {
#                 "required": True, "componentname":"paging-filter","searchcomponentid":"7aff5819-651c-4390-9b9a-a61221ba52c6","layoutSortorder":12, "executionSortorder":2
#             },
#             {
#                 "required": True, "componentname":"search-results","searchcomponentid":"00673743-8c1c-4cc0-bd85-c073a52e03ec","layoutSortorder":13, "executionSortorder":1
#             }
#         ]
#     }
# }


class BaseSearchView(BaseSearchFilter):
    """
    Special type of component that specifies which other components to be used,
    how to execute a search in the search_results method
    """

    def __init__(self, request=None, user=None, componentname=None):
        super().__init__(request=request, user=user, componentname=componentname)
        self.searchview_component = SearchComponent.objects.get(
            componentname=componentname
        )
        required_filter_sort_order = {
            item["componentname"]: int(item.get("executionSortorder", 99))
            for item in self.searchview_component.config["linkedSearchFilters"]
        }
        self._required_search_filters = list(
            SearchComponent.objects.filter(
                searchcomponentid__in=[
                    linked_filter["searchcomponentid"]
                    for linked_filter in self.searchview_component.config[
                        "linkedSearchFilters"
                    ]
                    if linked_filter.get("required", False)
                ]
            )
        )
        self._required_search_filters = sorted(
            self._required_search_filters,
            key=lambda item: required_filter_sort_order.get(
                item.componentname, float("inf")
            ),
        )
        available_filter_sort_order = {
            item["componentname"]: int(item.get("layoutSortorder", 99))
            for item in self.searchview_component.config["linkedSearchFilters"]
        }
        self._available_search_filters = list(
            SearchComponent.objects.filter(
                searchcomponentid__in=[
                    available_filter["searchcomponentid"]
                    for available_filter in self.searchview_component.config[
                        "linkedSearchFilters"
                    ]
                ],
                componentpath__isnull=False,
            )
        )
        self._available_search_filters = sorted(
            self._available_search_filters,
            key=lambda item: available_filter_sort_order.get(
                item.componentname, float("inf")
            ),
        )

    @property
    def required_search_filters(self):
        return self._required_search_filters

    @property
    def available_search_filters(self):
        return self._available_search_filters

    def get_searchview_filters(self):
        return self.available_search_filters + [self.searchview_component]

    def sort_query_dict(self, query_dict):
        filter_sort_order = {
            item["componentname"]: int(item.get("executionSortorder", 99))
            for item in self.searchview_component.config["linkedSearchFilters"]
        }
        sorted_items = sorted(
            query_dict.items(),
            key=lambda item: filter_sort_order.get(item[0], float("inf")),
        )

        return dict(sorted_items)

    def create_query_dict(self, query_dict):
        # check that all searchview required linkedSearchFilters are present
        query_dict[self.searchview_component.componentname] = True
        for linked_filter in self.searchview_component.config["linkedSearchFilters"]:
            if (
                linked_filter.get("required", False)
                and linked_filter["componentname"] not in query_dict
            ):
                query_dict[linked_filter["componentname"]] = {}
        return self.sort_query_dict(query_dict)

    def handle_search_results_query(
        self, search_query_object, response_object, search_filter_factory, returnDsl
    ):
        """
        returns response_object, search_query_object
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
            dsl = search_query_object.pop("query", None)
            return dsl, search_query_object

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

            search_query_object.pop("query")
            # ensure that if a search filter modified the query in some way
            # that the modification is set on the response_object
            for key, value in list(search_query_object.items()):
                if key not in response_object:
                    response_object[key] = value

        return response_object, search_query_object
