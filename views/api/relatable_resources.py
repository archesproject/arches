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

        resources = ResourceInstance.objects.filter(graph_id__in=graphs).annotate(
            order_field=Case(
                When(resourceinstanceid__in=initial_values, then=Value(0)),
                default=Value(1),
            )
        )

        query_string = "descriptors__{}__name__icontains".format(language)

        if filter_term:
            resources = resources.filter(
                Q(**{query_string: filter_term})
                | Q(resourceinstanceid__in=initial_values)
            )

        paginator = Paginator(
            resources.order_by(
                "order_field", "descriptors__{}__name".format(get_language())
            ),
            items_per_page,
        )
        page_object = paginator.get_page(page_number)
        data = [
            {
                "resourceinstanceid": resource.resourceinstanceid,
                "display_value": resource.descriptors[language]["name"],
                "order_field": resource.order_field,
            }
            for resource in page_object
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
