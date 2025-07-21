from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from django.db.models import Q
from django.views.generic import View

from arches import VERSION as arches_version
from arches.app.models import models
from arches.app.utils.response import JSONResponse

# TODO: Replace with DataTypeFactory from arches_querysets
from arches.app.datatypes.datatypes import DataTypeFactory


def serialize_card_x_node_x_widget(widget, datatype_factory):
    data = JSONDeserializer().deserialize(JSONSerializer().serialize(widget))

    data["card"] = JSONDeserializer().deserialize(
        JSONSerializer().serialize(widget.card)
    )
    del data["card_id"]

    data["node"] = JSONDeserializer().deserialize(
        JSONSerializer().serialize(widget.node)
    )
    del data["node_id"]

    data["widget"] = JSONDeserializer().deserialize(
        JSONSerializer().serialize(widget.widget)
    )
    del data["widget_id"]

    try:
        pass
        # datatype = datatype_factory.get_instance(widget.node.datatype)
        # data["config"]["defaultValue"] = datatype.get_interchange_value(
        #     data["config"].get("defaultValue", None)
        # )
    except AttributeError:
        pass

    return data


class CardXNodeXWidgetView(View):
    def get(self, request, graph_slug, node_alias):
        query = Q(node__graph__slug=graph_slug, node__alias=node_alias)

        if arches_version >= (8, 0):
            query &= Q(node__source_identifier_id__isnull=True)

        card_x_node_x_widget = (
            models.CardXNodeXWidget.objects.filter(query)
            .select_related()  # eagerly load all related objects
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

        serialized = serialize_card_x_node_x_widget(
            card_x_node_x_widget, DataTypeFactory()
        )
        return JSONResponse(serialized)


class CardXNodeXWidgetListFromNodegroupView(View):
    def get(self, request, graph_slug, nodegroup_alias):
        card_x_node_x_widgets_query = Q(
            node__graph__slug=graph_slug,
            node__nodegroup__node__alias=nodegroup_alias,
        )

        if arches_version >= (8, 0):
            card_x_node_x_widgets_query &= Q(node__source_identifier_id__isnull=True)

        saved_widget_queryset = (
            models.CardXNodeXWidget.objects.filter(card_x_node_x_widgets_query)
            .select_related()
            .order_by("sortorder")
        )

        datatype_factory = DataTypeFactory()

        saved_widgets_by_node_id = {
            saved_widget.node_id: saved_widget for saved_widget in saved_widget_queryset
        }

        node_queryset = models.Node.objects.filter(
            graph__slug=graph_slug, nodegroup__node__alias=nodegroup_alias
        )
        if arches_version >= (8, 0):
            node_queryset = node_queryset.filter(source_identifier=None)

        widget_instances = []
        for node in node_queryset:
            if node.pk in saved_widgets_by_node_id:
                widget_instances.append(saved_widgets_by_node_id[node.pk])
            else:
                datatype_for_node = datatype_factory.datatypes[node.datatype]
                default_widget_definition = datatype_for_node.defaultwidget

                if default_widget_definition is not None:  # handle semantic nodes
                    widget_instances.append(
                        models.CardXNodeXWidget(
                            node=node,
                            card=node.nodegroup.cardmodel_set.first(),
                            widget=default_widget_definition,
                            config=default_widget_definition.defaultconfig,
                        )
                    )

        serialized_data = [
            serialize_card_x_node_x_widget(widget_instance, datatype_factory)
            for widget_instance in widget_instances
        ]
        return JSONResponse(serialized_data)
