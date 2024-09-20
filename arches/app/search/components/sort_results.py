from arches.app.search.components.base import BaseSearchFilter
from django.utils.translation import get_language

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

    def generate_dsl(self, search_query_object, **kwargs):
        sort_param = self.request.GET.get(self.componentname, "")
        field = None
        dsl = None
        if sort_param != "":
            field = "displayname.value"
            dsl = {
                "order": sort_param,
                "nested": {
                    "path": "displayname",
                    "filter": {"term": {"displayname.language": get_language()}},
                },
            }
        return field, dsl

    def append_dsl(self, search_query_object, **kwargs):
        sort_field, sort_dsl = self.generate_dsl(search_query_object, **kwargs)
        if sort_field and sort_dsl:
            search_query_object["query"].sort(
                field=sort_field,
                dsl=sort_dsl,
            )
