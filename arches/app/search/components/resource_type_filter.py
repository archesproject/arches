from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Bool, Term
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
    "enabled": True
}


class ResourceTypeFilter(BaseSearchFilter):

    def append_dsl(self, query_dsl, permitted_nodegroups, include_provisional):
        search_query = Bool()
        querysting_params = self.request.GET.get(details['componentname'], '')

        for resouceTypeFilter in JSONDeserializer().deserialize(querysting_params):
            term = Term(field='graph_id', term=str(resouceTypeFilter['graphid']))
            if resouceTypeFilter['inverted'] is True:
                search_query.must_not(term)
            else:
                search_query.must(term)

        query_dsl.add_query(search_query)
