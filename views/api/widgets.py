import json

from django.utils import translation
from django.views.generic import View

from arches.app.models import models
from arches.app.utils.response import JSONResponse

def update_i18n_properties(response):
    user_language = translation.get_language()
    if "i18n_properties" in response and isinstance(
        response["i18n_properties"], list
    ):
        for prop in response["i18n_properties"]:
            if (
                prop in response
                and isinstance(response[prop], dict)
                and user_language in response[prop]
            ):
                response[prop] = response[prop][user_language]
    return response


class WidgetConfigurationView(View):
    def get(self, request, graph_slug, node_alias):
        card_x_node_x_widget = models.CardXNodeXWidget.objects.filter(
            node__graph__slug=graph_slug,
            node__alias=node_alias,
            node__source_identifier_id__isnull=True,
        ).first()

        card_x_node_x_widget_config = json.loads(card_x_node_x_widget.config.value)

        response = update_i18n_properties(card_x_node_x_widget_config)

        return JSONResponse(response)

class NodeConfigurationView(View):
    def get(self, request, graph_slug, node_alias):
        user_language = translation.get_language()

        node = models.Node.objects.get(
            graph__slug=graph_slug, alias=node_alias, source_identifier_id__isnull=True
        )

        node_config = {"isrequired": node.isrequired, **json.loads(node.config.value)}

        response = update_i18n_properties(node_config)

        return JSONResponse(response)
