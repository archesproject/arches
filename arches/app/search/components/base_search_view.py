from arches.app.search.components.base import BaseSearchFilter
from arches.app.models import models

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
#         "availableComponents": [ # search components available to the frontend and permitted to be executed on the backend
#             {
#                 "componentname":"map-filter","searchcomponentid":"09d97fc6-8c83-4319-9cef-3aaa08c3fbec","sortorder":1
#             },
#             {
#                 "componentname":"advanced-search","searchcomponentid":"f0e56205-acb5-475b-9c98-f5e44f1dbd2c","sortorder":2
#             },
#             {
#                 "componentname":"related-resources-filter","searchcomponentid":"59f28272-d1f1-4805-af51-227771739aed","sortorder":3
#             },
#             {
#                 "componentname":"provisional-filter","searchcomponentid":"073406ed-93e5-4b5b-9418-b61c26b3640f","sortorder":4
#             },
#             {
#                 "componentname":"term-filter","searchcomponentid":"1f42f501-ed70-48c5-bae1-6ff7d0d187da","sortorder":10
#             },
#             {
#                 "componentname":"paging-filter","searchcomponentid":"7aff5819-651c-4390-9b9a-a61221ba52c6","sortorder":12
#             },
#             {
#                 "componentname":"search-results","searchcomponentid":"00673743-8c1c-4cc0-bd85-c073a52e03ec","sortorder":13
#             }
#         ],
#         "requiredComponents": [ # components that must be applied on the backend
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


class BaseSearchView(BaseSearchFilter):
    """
    Special type of component that specifies which other components to be used,
    how to execute a search in the search_results method
    """

    def __init__(self, request=None, user=None, componentname=None):
        super().__init__(request=request, user=user, componentname=componentname)
        self.searchview_component = models.SearchComponent.objects.get(
            componentname=componentname
        )
        required_component_sort_order = {
            item["componentname"]: int(item["sortorder"])
            for item in self.searchview_component.config["requiredComponents"]
        }
        self._required_search_components = list(
            models.SearchComponent.objects.filter(
                searchcomponentid__in=[
                    required_component["searchcomponentid"]
                    for required_component in self.searchview_component.config[
                        "requiredComponents"
                    ]
                ]
            )
        )
        self._required_search_components = sorted(
            self._required_search_components,
            key=lambda item: required_component_sort_order.get(
                item.componentname, float("inf")
            ),
        )
        available_component_sort_order = {
            item["componentname"]: int(item["sortorder"])
            for item in self.searchview_component.config["availableComponents"]
        }
        self._available_search_components = list(
            models.SearchComponent.objects.filter(
                searchcomponentid__in=[
                    available_component["searchcomponentid"]
                    for available_component in self.searchview_component.config[
                        "availableComponents"
                    ]
                ]
            )
        )
        self._available_search_components = sorted(
            self._available_search_components,
            key=lambda item: available_component_sort_order.get(
                item.componentname, float("inf")
            ),
        )

    @property
    def required_search_components(self):
        return self._required_search_components

    @property
    def available_search_components(self):
        return self._available_search_components

    def get_searchview_components(self):
        return self._available_search_components + [self.searchview_component]

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
