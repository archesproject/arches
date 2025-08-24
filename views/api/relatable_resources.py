from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views import View
from django.utils.translation import get_language
from arches.app.models.models import Node, ResourceInstance, GraphModel
from arches.app.utils.response import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches import VERSION as arches_version
from arches.app.utils.decorators import user_can_read_resource
from django.db.models import Value, Case, When, Q


class RelatableResourcesView(View):
    def get(self, request, graph, node_alias):
        node_filter = Q(
            alias=node_alias,
            graph__slug=graph,
            graph__publication__isnull=False,
        )
        if arches_version >= (8, 0):
            node_filter = node_filter & Q(graph__is_active=True)

        node = Node.objects.get(node_filter)

        page_number = request.GET.get("page", 1)
        filter_term = request.GET.get("filter_term", None)
        items_per_page = request.GET.get("items", 25)
        language = get_language()
        initial_values = request.GET.getlist("initialValue", "")
        config = JSONDeserializer().deserialize(node.config.value)
        graphs = [graph["graphid"] for graph in config.get("graphs", [])]

        graph_models = GraphModel.objects.filter(graphid__in=graphs).values(
            "name", "graphid"
        )

        resources = ResourceInstance.objects.filter(graph_id__in=graphs).exclude(
            resourceinstanceid__in=initial_values
        )

        if filter_term:
            resources = resources.filter(
                Q(**{"descriptors__{}__name__icontains".format(language): filter_term})
            )

        resources = resources.values(
            "resourceinstanceid", "descriptors__{}__name".format(language)
        ).order_by("graph", "pk")
        resources.count = lambda self=None: 1_000_000_000
        paginator = Paginator(resources, items_per_page)

        data = [
            {
                "resourceinstanceid": resource["resourceinstanceid"],
                "display_value": resource[(f"descriptors__{language}__name")],
            }
            for resource in sorted(
                paginator.get_page(page_number).object_list,
                key=lambda r: r.get(f"descriptors__{language}__name", "").lower(),
            )
        ]

        return JSONResponse(
            {
                "graphs": graph_models,
                "current_page": paginator.get_page(page_number).number,
                "total_pages": paginator.num_pages,
                "results_per_page": paginator.per_page,
                "total_results": paginator.count,
                "data": data,
            }
        )
