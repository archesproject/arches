from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Bool, Terms
from arches.app.search.components.base import BaseSearchFilter

details = {
    "searchcomponentid": "",
    "name": "Resource Type Filter",
    "icon": "",
    "modulename": "resource_type_filter.py",
    "classname": "ResourceTypeFilter",
    "type": "resource-type-filter",
    "componentpath": "views/components/search/resource-type-filter",
    "componentname": "resource-type-filter",
    "sortorder": "0",
    "enabled": True,
}


class ResourceTypeFilter(BaseSearchFilter):
    def append_dsl(self, search_results_object, permitted_nodegroups, include_provisional):
        parcel_graphid = '7d24462d-d32b-11eb-b1b2-ed35bfac87bc'
        parcel_included = False
        search_query = Bool()
        querystring_params = self.request.GET.get(details["componentname"], "")

        graph_ids = []
        for resourceTypeFilter in JSONDeserializer().deserialize(querystring_params):
            if str(resourceTypeFilter["graphid"]) == parcel_graphid:
                parcel_included = True
            graph_ids.append(str(resourceTypeFilter["graphid"]))

        terms = Terms(field="graph_id", terms=graph_ids)
        if resourceTypeFilter["inverted"] is True:
            search_query.must_not(terms)
        else:
            search_query.filter(terms)


        if not parcel_included:
            terms = Terms(field="graph_id", terms=[parcel_graphid])
            search_query.must_not(terms)

        search_results_object["query"].add_query(search_query)
