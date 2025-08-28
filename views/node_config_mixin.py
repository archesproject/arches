from django.db.models import Q
from arches import VERSION as arches_version
from arches.app.models import models
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer


class CardNodeWidgetConfigMixin:
    # Mixin for standard handling of card_x_node_x_widget data. Centralizes logic required to handle
    # Arches Core 7 & 8 version model differences.
    @staticmethod
    def get_card_x_node_x_widget(graph_slug, node_alias):
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
        return card_x_node_x_widget

    @staticmethod
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
            datatype = datatype_factory.get_instance(widget.node.datatype)
            data["config"]["defaultValue"] = datatype.get_interchange_value(
                data["config"].get("defaultValue", None)
            )
        except AttributeError:
            pass

        return data
