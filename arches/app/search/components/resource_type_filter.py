from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Bool, Terms
from arches.app.search.components.base import BaseSearchFilter
from arches.app.models.models import GraphModel
from arches.app.utils.permission_backend import get_resource_types_by_perm

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
        search_query = Bool()
        querystring_params = self.request.GET.get(details["componentname"], "")
        graph_ids = []
        for resourceTypeFilter in JSONDeserializer().deserialize(querystring_params):
            graphid = str(resourceTypeFilter["graphid"])
            graph = GraphModel.objects.get(pk=graphid)
            graph_nodegroups = {str(val[0]) for val in graph.cardmodel_set.values_list('nodegroup_id')}
            if len(set(permitted_nodegroups).intersection(graph_nodegroups)) > 0:
                graph_ids.append(graphid)

        terms = Terms(field="graph_id", terms=graph_ids)
        if resourceTypeFilter["inverted"] is True:
            search_query.must_not(terms)
        else:
            search_query.filter(terms)

        search_results_object["query"].add_query(search_query)


    def view_data(self):
        return  {"resources": get_resource_types_by_perm(self.request.user, 'read_nodegroup')}