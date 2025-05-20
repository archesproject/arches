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

class CardDataView(View):
    def get(self, request, graph_slug, nodegroup_grouping_node_alias):

        import pdb; pdb.set_trace()
        if arches_version < "8":
            card = (
                models.Card.objects.filter(
                    node__graph__slug=graph_slug,
                    node__alias=nodegroup_grouping_node_alias,
                )
                .select_related("node")
                .get()
            )

        # TODO: Add support for v8

        response = update_i18n_properties(
            JSONDeserializer().deserialize(
                JSONSerializer().serialize(card)
            )
        )

        return JSONResponse(response)
