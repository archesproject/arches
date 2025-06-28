from django.db.models import Q
from django.views.generic import View

from arches import VERSION as arches_version
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from arches.app.utils.response import JSONResponse
from arches.app.datatypes.datatypes import DataTypeFactory


# TODO: Remove this in favor of card_x_node_x_widget.py View
class WidgetDataView(View):
    def get(self, request, graph_slug, node_alias):
        query_filter = Q(
            node__graph__slug=graph_slug,
            node__alias=node_alias,
        )
        if arches_version >= (8, 0):
            query_filter = query_filter & Q(
                node__source_identifier_id__isnull=True,
            )

        card_x_node_x_widget = (
            models.CardXNodeXWidget.objects.select_related("node")
            .filter(query_filter)
            .first()
        )

        if not card_x_node_x_widget:
            # Supply default widget configuration.
            nodes = models.Node.objects.filter(graph__slug=graph_slug, alias=node_alias)
            if arches_version >= (8, 0):
                nodes = nodes.filter(source_identifier=None)
            node = nodes.get()
            datatype_factory = DataTypeFactory()
            d_data_type = datatype_factory.datatypes[node.datatype]
            default_widget = d_data_type.defaultwidget
            card_x_node_x_widget = models.CardXNodeXWidget(
                node=node,
                card=node.nodegroup.cardmodel_set.first(),
                widget=default_widget,
                config=default_widget.defaultconfig,
            )

        card_x_node_x_widget_dict = JSONDeserializer().deserialize(
            JSONSerializer().serialize(card_x_node_x_widget)
        )

        datatype = DataTypeFactory().get_instance(card_x_node_x_widget.node.datatype)
        # When dropping support for v7.6, try/except can be removed
        try:
            card_x_node_x_widget_dict["config"]["defaultValue"] = (
                datatype.get_interchange_value(
                    card_x_node_x_widget_dict["config"].get("defaultValue", None)
                )
            )
        except AttributeError:
            # Handle the case where the datatype does not have a get_interchange_value method
            pass

        return JSONResponse(card_x_node_x_widget_dict)


# TODO: Replace this with nodes.py view
class NodeDataView(View):
    def get(self, request, graph_slug, node_alias):
        node_filter = Q(
            graph__slug=graph_slug,
            alias=node_alias,
        )
        if arches_version >= (8, 0):
            node_filter = node_filter & Q(
                source_identifier_id__isnull=True,
            )
        node = models.Node.objects.get(node_filter)

        return JSONResponse(node)
