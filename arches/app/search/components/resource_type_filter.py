from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Bool, Terms
from arches.app.search.components.base import BaseSearchFilter
from arches.app.models.models import Node
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


def get_permitted_graphids(permitted_nodegroups):
    permitted_graphids = set()
    for node in Node.objects.filter(nodegroup__in=permitted_nodegroups):
        permitted_graphids.add(str(node.graph_id))
    return permitted_graphids


class ResourceTypeFilter(BaseSearchFilter):
    def append_dsl(self, search_results_object, permitted_nodegroups, include_provisional):
        search_query = Bool()
        querystring_params = self.request.GET.get(details["componentname"], "")
        graph_ids = []
        permitted_graphids = get_permitted_graphids(permitted_nodegroups)

        for resourceTypeFilter in JSONDeserializer().deserialize(querystring_params):
            graphid = str(resourceTypeFilter["graphid"])
            if resourceTypeFilter["inverted"] is True:
                try:
                    permitted_graphids.remove(graphid)
                except KeyError:
                    pass
            else:
                if graphid in permitted_graphids:
                    graph_ids.append(graphid)

        if resourceTypeFilter["inverted"] is True:
            terms = Terms(field="graph_id", terms=list(permitted_graphids))
        else:
            terms = Terms(field="graph_id", terms=graph_ids)

        search_query.filter(terms)

        search_results_object["query"].add_query(search_query)

    def view_data(self):
        return {"resources": get_resource_types_by_perm(self.request.user, "read_nodegroup")}
