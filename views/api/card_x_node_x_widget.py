from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from django.utils import translation
from django.views.generic import View

from arches import __version__ as arches_version
from arches.app.models import models
from arches.app.utils.response import JSONResponse
from arches.app.datatypes.datatypes import DataTypeFactory


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
        elif arches_version >= "8":
            card_x_node_x_widget = (
                models.CardXNodeXWidget.objects.filter(
                    node__graph__slug=graph_slug,
                    node__alias=node_alias,
                    node__source_identifier_id__isnull=True,
                )
                .select_related()  # eagerly load all related objects
                .get()
            )

        serialized_card_x_node_x_widget = JSONDeserializer().deserialize(
            JSONSerializer().serialize(card_x_node_x_widget)
        )

        serialized_card_x_node_x_widget["card"] = JSONDeserializer().deserialize(
            JSONSerializer().serialize(card_x_node_x_widget.card)
        )
        del serialized_card_x_node_x_widget["card_id"]

        serialized_card_x_node_x_widget["node"] = JSONDeserializer().deserialize(
            JSONSerializer().serialize(card_x_node_x_widget.node)
        )
        del serialized_card_x_node_x_widget["node_id"]

        serialized_card_x_node_x_widget["widget"] = JSONDeserializer().deserialize(
            JSONSerializer().serialize(card_x_node_x_widget.widget)
        )
        del serialized_card_x_node_x_widget["widget_id"]

        # TODO: update this method to be more generic
        update_i18n_properties(serialized_card_x_node_x_widget)

        # When dropping support for v7.6, try/except can be removed
        try:
            datatype_factory = DataTypeFactory()
            datatype = datatype_factory.get_instance(card_x_node_x_widget.node.datatype)

            serialized_card_x_node_x_widget.config["defaultValue"] = (
                datatype.get_interchange_value(
                    serialized_card_x_node_x_widget.config.get("defaultValue", None)
                )
            )

        except AttributeError:
            # Handle the case where the datatype does not have a get_interchange_value method
            pass

        return JSONResponse(serialized_card_x_node_x_widget)


class CardXNodeXWidgetListFromNodegroupView(View):
    def get(self, request, graph_slug, nodegroup_grouping_node_alias):
        if arches_version < "8":
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

        # TODO: Add support for v8

        datatype_factory = DataTypeFactory()
        card_x_node_x_widget_data = []

        for card_x_node_x_widget in card_x_node_x_widgets:
            datatype = datatype_factory.get_instance(card_x_node_x_widget.node.datatype)

            card_x_node_x_widget_datum = update_i18n_properties(
                JSONDeserializer().deserialize(
                    JSONSerializer().serialize(card_x_node_x_widget)
                )
            )

            card_x_node_x_widget_datum["card"] = JSONDeserializer().deserialize(
                JSONSerializer().serialize(card_x_node_x_widget.card)
            )
            del card_x_node_x_widget_datum["card_id"]
            card_x_node_x_widget_datum["node"] = JSONDeserializer().deserialize(
                JSONSerializer().serialize(card_x_node_x_widget.node)
            )
            del card_x_node_x_widget_datum["node_id"]
            card_x_node_x_widget_datum["widget"] = JSONDeserializer().deserialize(
                JSONSerializer().serialize(card_x_node_x_widget.widget)
            )
            del card_x_node_x_widget_datum["widget_id"]

            # TODO: update this method to be more generic
            update_i18n_properties(card_x_node_x_widget_datum)

            # When dropping support for v7.6, try/except can be removed
            try:
                card_x_node_x_widget_datum.config["defaultValue"] = (
                    datatype.get_interchange_value(
                        card_x_node_x_widget_datum.config.get("defaultValue", None)
                    )
                )

            except AttributeError:
                # Handle the case where the datatype does not have a get_interchange_value method
                pass

            card_x_node_x_widget_data.append(card_x_node_x_widget_datum)

        return JSONResponse(card_x_node_x_widget_data)
