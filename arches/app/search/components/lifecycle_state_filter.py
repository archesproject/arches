from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Bool, Terms
from arches.app.search.components.base import BaseSearchFilter
from arches.app.models.models import ResourceInstanceLifecycleState

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


class LifecycleStateFilter(BaseSearchFilter):
    def append_dsl(
        self, search_results_object, permitted_nodegroups, include_provisional
    ):
        search_query = Bool()
        resource_instance_lifecycle_state_filter = Bool()

        querystring_params = self.request.GET.get(details["componentname"], "")
        resource_instance_lifecycle_state_filter_term = JSONDeserializer().deserialize(
            querystring_params
        )[0]

        if resource_instance_lifecycle_state_filter_term["inverted"] is True:
            resource_instance_lifecycle_state_ids = (
                ResourceInstanceLifecycleState.objects.exclude(
                    pk=resource_instance_lifecycle_state_filter_term["id"]
                ).values_list("pk", flat=True)
            )

            resource_instance_lifecycle_state_filter.filter(
                Terms(
                    field="resource_instance_lifecycle_state_id",
                    terms=[
                        str(resource_instance_lifecycle_state_id)
                        for resource_instance_lifecycle_state_id in resource_instance_lifecycle_state_ids
                    ],
                )
            )
        else:
            resource_instance_lifecycle_state_filter.filter(
                Terms(
                    field="resource_instance_lifecycle_state_id",
                    terms=[resource_instance_lifecycle_state_filter_term["id"]],
                )
            )

        search_query.must(resource_instance_lifecycle_state_filter)
        search_results_object["query"].add_query(search_query)
