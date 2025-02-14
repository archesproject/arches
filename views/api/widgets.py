import json

from django.views.generic import View

from arches.app.models import models
from arches.app.utils.response import JSONResponse


class WidgetConfigurationView(View):
    def get(self, request, graph_slug, node_alias):
        card_x_node_x_widget = models.CardXNodeXWidget.objects.get(
            node__graph__slug=graph_slug,
            node__alias=node_alias,
            node__source_identifier_id__isnull=True,
        )
        card_x_node_x_widget_config = json.loads(card_x_node_x_widget.config.value)

        return JSONResponse(card_x_node_x_widget_config)
