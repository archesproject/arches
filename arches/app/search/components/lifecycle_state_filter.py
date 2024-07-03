from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Bool, Terms
from arches.app.search.components.base import BaseSearchFilter
from arches.app.models.models import ResourceInstanceLifecycle
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


def get_resource_instance_lifecycle_states():
    all_keys = set()
    for instance in ResourceInstanceLifecycle.objects.all():
        all_keys.update(instance.states.keys())

    return all_keys


class LifecycleStateFilter(BaseSearchFilter):
    def append_dsl(
        self, search_results_object, permitted_nodegroups, include_provisional
    ):
        search_query = Bool()
        lifecycle_state_filter = Bool()

        querystring_params = self.request.GET.get(details["componentname"], "")
        lifecycle_state_filter_term = JSONDeserializer().deserialize(
            querystring_params
        )[0]

        if lifecycle_state_filter_term["inverted"] is True:
            resource_instance_lifecycle_states = (
                get_resource_instance_lifecycle_states()
            )
            resource_instance_lifecycle_states.remove(
                lifecycle_state_filter_term["name"]
            )

            lifecycle_state_filter.filter(
                Terms(
                    field="lifecycle_state",
                    terms=list(resource_instance_lifecycle_states),
                )
            )
        else:
            lifecycle_state_filter.filter(
                Terms(
                    field="lifecycle_state", terms=[lifecycle_state_filter_term["name"]]
                )
            )

        search_query.must(lifecycle_state_filter)
        search_results_object["query"].add_query(search_query)
