from django.views.generic import View
from arches.app.utils.response import JSONResponse
from arches_component_lab.views.node_config_mixin import CardNodeWidgetConfigMixin
from arches.app.models.concept import Concept


class ConceptsTreeView(View, CardNodeWidgetConfigMixin):
    def get(self, request, graph_slug, node_alias):
        cnw_config = self.get_card_x_node_x_widget(graph_slug, node_alias)

        concept_id = cnw_config.node.config["rdmCollection"]
        results_tree = Concept().get_e55_domain(concept_id)

        def set_results_keys(results):
            results = [
                result | {"key": result["id"], "label": result["text"]}
                for result in results
            ]
            for result in results:
                if len(result["children"]) > 0:
                    result["children"] = set_results_keys(result["children"])
            return results

        results_tree = set_results_keys(results_tree)

        def count_results(results):
            return len(results) + sum(
                list(map(lambda result: count_results(result["children"]), results))
            )

        total_count = count_results(results_tree)
        data = results_tree

        return JSONResponse({"results": data, "total_results": total_count})
