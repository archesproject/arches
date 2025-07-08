from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from django.views.generic import View

from arches import VERSION as arches_version
from arches.app.models import models
from arches.app.utils.response import JSONResponse


class CardDataView(View):
    def get(self, request, graph_slug, nodegroup_alias):

        if arches_version < (8, 0):
            card = models.CardModel.objects.filter(
                graph__slug=graph_slug,
                nodegroup__node__alias=nodegroup_alias,
            ).get()
        else:
            node = models.Node.objects.get(alias=nodegroup_alias)
            card = models.CardModel.objects.get(
                graph__slug=graph_slug,
                nodegroup_id=node.nodegroup_id,
            )

        return JSONResponse(card)
