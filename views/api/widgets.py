from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from django.utils import translation
from django.views.generic import View

from arches import VERSION as arches_version
from django.db.models import Q
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

        card_x_node_x_widget = models.CardXNodeXWidget.objects.select_related(
            "node"
        ).get(query_filter)

        response = update_i18n_properties(
            JSONDeserializer().deserialize(
                JSONSerializer().serialize(card_x_node_x_widget)
            )
        )

        datatype = DataTypeFactory().get_instance(card_x_node_x_widget.node.datatype)
        # When dropping support for v7.6, try/except can be removed
        try:
            response["config"]["defaultValue"] = datatype.get_interchange_value(
                response["config"].get("defaultValue", None)
            )
        except AttributeError:
            # Handle the case where the datatype does not have a get_interchange_value method
            pass

        return JSONResponse(response)


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

        response = update_i18n_properties(
            JSONDeserializer().deserialize(JSONSerializer().serialize(node))
        )

        return JSONResponse(response)
