from arches.app.search.elasticsearch_dsl_builder import Bool, Terms
from arches.app.search.components.base import BaseSearchFilter
from arches.app.search.components.resource_type_filter import get_permitted_graphids

details = {}


class PermittedGraphsPolicy(BaseSearchFilter):
    def generate_dsl(self, search_query_object, **kwargs):
        resource_model_filter = None
        permitted_nodegroups = kwargs.get("permitted_nodegroups")
        try:
            search_query_object["query"].dsl["query"]["bool"]["filter"][0]["terms"][
                "graph_id"
            ]  # check if resource_type filter is already applied
        except (KeyError, IndexError):
            resource_model_filter = Bool()
            permitted_graphids = get_permitted_graphids(permitted_nodegroups)
            terms = Terms(field="graph_id", terms=list(permitted_graphids))
            resource_model_filter.filter(terms)
            search_query_object["query"].add_query(resource_model_filter)
        return resource_model_filter

    def append_dsl(self, search_query_object, **kwargs):
        dsl = self.generate_dsl(search_query_object, **kwargs)
        if dsl:
            search_query_object["query"].add_query(dsl)
