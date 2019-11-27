from arches.app.search.components.base import BaseSearchFilter
from arches.app.search.elasticsearch_dsl_builder import Bool, Terms

details = {
    "searchcomponentid": "",
    "name": "Provisional Filter",
    "icon": "",
    "modulename": "provisional_filter.py",
    "classname": "ProvisionalFilter",
    "type": "",
    "componentpath": "views/components/search/provisional-filter",
    "componentname": "provisional-filter",
    "sortorder": "0",
    "enabled": True,
}


class ProvisionalFilter(BaseSearchFilter):
    def append_dsl(self, search_results_object, permitted_nodegroups, include_provisional):
        search_query = Bool()

        if include_provisional is not True:
            provisional_resource_filter = Bool()

            if include_provisional is False:
                provisional_resource_filter.filter(Terms(field="provisional_resource", terms=["false", "partial"]))

            elif include_provisional == "only provisional":
                provisional_resource_filter.filter(Terms(field="provisional_resource", terms=["true", "partial"]))

            search_query.must(provisional_resource_filter)
            search_results_object["query"].add_query(search_query)
