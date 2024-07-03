from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Bool, Terms
from arches.app.search.components.base import BaseSearchFilter
from arches.app.models.models import Node
from arches.app.utils.permission_backend import get_resource_types_by_perm

details = {
    "searchcomponentid": "",
    "name": "Lifecycle State Filter",
    "icon": "",
    "modulename": "lifecycle_state_filter.py",
    "classname": "LifecycleStateFilter",
    "type": "lifecycle-state-filter",
    "componentpath": "views/components/search/lifecycle-state-filter",
    "componentname": "lifecycle-state-filter",
    "sortorder": "0",
    "enabled": True,
}


# def get_permitted_graphids(permitted_nodegroups):
#     permitted_graphids = set()
#     for node in Node.objects.filter(nodegroup__in=permitted_nodegroups):
#         permitted_graphids.add(str(node.graph_id))
#     return permitted_graphids


class LifecycleStateFilter(BaseSearchFilter):
    def append_dsl(
        self, search_results_object, permitted_nodegroups, include_provisional
    ):
        search_query = Bool()
        querystring_params = self.request.GET.get(details["componentname"], "")

        for resourceTypeFilter in JSONDeserializer().deserialize(querystring_params):
            pass

        if resourceTypeFilter["inverted"] is True:
            terms = Terms(field="lifecycle_state", terms=["retired"])
        else:
            terms = Terms(field="lifecycle_state", terms=["active"])

        search_query.filter(terms)

        search_results_object["query"].add_query(search_query)

    def view_data(self):
        return {
            "resources": get_resource_types_by_perm(self.request.user, "read_nodegroup")
        }
