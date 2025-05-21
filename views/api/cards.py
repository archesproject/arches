from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from django.views.generic import View

from arches import __version__ as arches_version
from arches.app.models import models
from arches.app.utils.response import JSONResponse


class CardDataView(View):
    def get(self, request, graph_slug, nodegroup_grouping_node_alias):

        if arches_version < "8":
            card = models.CardModel.objects.filter(
                graph__slug=graph_slug,
                nodegroup__node__alias=nodegroup_grouping_node_alias,
            ).get()
        # TODO: Add support for v8

        return JSONResponse(
            JSONDeserializer().deserialize(JSONSerializer().serialize(card))
        )
