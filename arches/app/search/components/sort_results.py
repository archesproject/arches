from arches.app.search.components.base import BaseSearchFilter
from django.utils.translation import get_language
from arches.app.models.models import SearchComponent

details = {
    "searchcomponentid": "6a2fe122-de54-4e44-8e93-b6a0cda7955c",
    "name": "Sort",
    "icon": "",
    "modulename": "sort_results.py",
    "classname": "SortResults",
    "type": "sort-results-type",
    "componentpath": "views/components/search/sort-results",
    "componentname": "sort-results",
    "config": {},
}


class SortResults(BaseSearchFilter):
    def append_dsl(self, search_query_object, **kwargs):

        query_string = kwargs["querystring"]
        try:
            sort_order = query_string["sort_order"]
            sort_by = query_string["sort_by"]
        except TypeError:  # sort order is a string e.g. 'asc'
            sort_order = query_string
            sort_by = "resource_name"

        if sort_by == "resource_name":
            sort_field = "displayname.value"
            sort_dsl = {
                "nested": {
                    "path": "displayname",
                    "filter": {"term": {"displayname.language": get_language()}},
                },
                "order": sort_order,
            }

        else:
            sort_field = sort_by
            sort_dsl = {"order": sort_order}

        search_query_object["query"].sort(
            field=sort_field,
            dsl=sort_dsl,
        )
