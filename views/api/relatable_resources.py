import uuid
from django.core.paginator import Paginator
from django.views import View
from django.utils.translation import get_language
from arches.app.models.models import Node, ResourceInstance, GraphModel
from arches.app.utils.response import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches import VERSION as arches_version
from django.db.models import Q, F


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
        filter_term = request.GET.getlist("filter_term", [])
        items_per_page = request.GET.get("items", 25)
        language = get_language()
        initial_values = request.GET.getlist("initialValue", "")
        config = JSONDeserializer().deserialize(node.config.value)
        graphs = [graph["graphid"] for graph in config.get("graphs", [])]

        graph_models = GraphModel.objects.filter(graphid__in=graphs).values(
            "name", "graphid"
        )

        resources = (
            ResourceInstance.objects.filter(graph_id__in=graphs)
            .exclude(resourceinstanceid__in=initial_values)
            .values("resourceinstanceid")
            .annotate(display_value=F("descriptors__{}__name".format(language)))
            .order_by("graph", "pk")
        )

        selected_resources = (
            (
                ResourceInstance.objects.filter(resourceinstanceid__in=initial_values)
                .values("resourceinstanceid")
                .annotate(display_value=F("descriptors__{}__name".format(language)))
                .order_by("graph", "pk")
            )
            if int(page_number) == 1
            else []
        )

        if filter_term:
            query_filter = Q()
            for term in filter_term:
                try:
                    uuid.UUID(str(term))
                    query_filter = query_filter & Q(resourceinstanceid=str(term))
                except ValueError:
                    query_filter = query_filter & Q(
                        **{"display_value__icontains": term}
                    )
            resources = resources.filter(query_filter)

        resources.count = lambda self=None: 1_000_000_000
        paginator = Paginator(resources, items_per_page)

        data = list(selected_resources) + sorted(
            paginator.get_page(page_number).object_list,
            key=lambda r: r.get("display_value", "").lower(),
        )

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
