from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from django.utils import translation
from django.views.generic import View

from arches import __version__ as arches_version
from arches.app.models import models
from arches.app.utils.response import JSONResponse
from arches.app.datatypes.datatypes import DataTypeFactory


_datatype_factory = DataTypeFactory()


def update_i18n_properties(response):
    user_language = translation.get_language()
    config = response["config"]

    if "i18n_properties" in config and isinstance(config["i18n_properties"], list):
        for prop in config["i18n_properties"]:
            if (
                prop in config
                and isinstance(config[prop], dict)
                and user_language in config[prop]
            ):
                config[prop] = config[prop][user_language]
    response["config"] = config
    return response


def serialize_card_x_node_x_widget(widget):
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

    update_i18n_properties(data)

    try:
        datatype = _datatype_factory.get_instance(widget.node.datatype)
        data["config"]["defaultValue"] = datatype.get_interchange_value(
            data["config"].get("defaultValue", None)
        )
    except AttributeError:
        pass

    return data


class CardXNodeXWidgetView(View):
    def get(self, request, graph_slug, node_alias):
        if arches_version < "8":
            card_x_node_x_widget = (
                models.CardXNodeXWidget.objects.filter(
                    node__graph__slug=graph_slug,
                    node__alias=node_alias,
                )
                .select_related()  # eagerly load all related objects
                .get()
            )
        else:
            card_x_node_x_widget = (
                models.CardXNodeXWidget.objects.filter(
                    node__graph__slug=graph_slug,
                    node__alias=node_alias,
                    node__source_identifier_id__isnull=True,
                )
                .select_related()  # eagerly load all related objects
                .get()
            )

        serialized = serialize_card_x_node_x_widget(card_x_node_x_widget)
        return JSONResponse(serialized)


class CardXNodeXWidgetListFromNodegroupView(View):
    def get(self, request, graph_slug, nodegroup_grouping_node_alias):
        grouping_node = models.Node.objects.get(
            graph__slug=graph_slug, alias=nodegroup_grouping_node_alias
        )

        card_x_node_x_widgets = (
            models.CardXNodeXWidget.objects.filter(
                node__nodegroup=grouping_node.nodegroup
            )
            .select_related()  # Eagerly load _all_ related objects
            .order_by("sortorder")
        )

        data = [
            serialize_card_x_node_x_widget(widget) for widget in card_x_node_x_widgets
        ]

        return JSONResponse(data)
