from arches.app.search.components.base import BaseSearchFilter
from arches.app.search.elasticsearch_dsl_builder import Nested
from django.utils.translation import get_language

details = {
    "searchcomponentid": "6a2fe122-de54-4e44-8e93-b6a0cda7955c",
    "name": "Sort",
    "icon": "",
    "modulename": "sort_results.py",
    "classname": "SortResults",
    "type": "",
    "componentpath": "views/components/search/sort-results",
    "componentname": "sort-results",
    "sortorder": "0",
    "enabled": True,
}


class SortResults(BaseSearchFilter):
    def append_dsl(self, search_results_object, permitted_nodegroups, include_provisional):
        sort_param = self.request.GET.get(details["componentname"], None)

        if sort_param is not None and sort_param is not "":
            search_results_object["query"].sort(
                field="displayname.value",
                dsl={"order": sort_param, "nested": {"path": "displayname", "filter": {"term": {"displayname.language": get_language()}}}},
            )
