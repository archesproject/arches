from django.utils.translation import gettext as _

from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase


class Card(APIBase):
    def get(self, request, resourceid):
        resource_query = Resource.objects.filter(pk=resourceid).select_related("graph")
        try:
            resource_instance = resource_query.get()
            graph = resource_instance.graph
        except Resource.DoesNotExist:
            graph = models.GraphModel.objects.get(pk=resourceid)
            resourceid = None
            resource_instance = None

        permitted_nodegroups = []
        editable_nodegroup_ids: set[str] = set()
        nodes = graph.node_set.all().select_related("nodegroup")
        for node in nodes:
            if node.is_collector:
                added = False
                if request.user.has_perm("write_nodegroup", node.nodegroup):
                    editable_nodegroup_ids.add(str(node.nodegroup.pk))
                    permitted_nodegroups.append(node.nodegroup)
                    added = True
                if not added and request.user.has_perm(
                    "read_nodegroup", node.nodegroup
                ):
                    permitted_nodegroups.append(node.nodegroup)

        user_is_reviewer = user_is_resource_reviewer(request.user)

        if resource_instance is None:
            tiles = []
            displayname = _("New Resource")
        else:
            displayname = resource_instance.displayname()
            if displayname == "undefined":
                displayname = _("Unnamed Resource")
            if (
                str(resource_instance.graph_id)
                == settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID
            ):
                displayname = _("System Settings")

            tiles = resource_instance.tilemodel_set.filter(
                nodegroup_id__in=[ng.pk for ng in permitted_nodegroups]
            ).order_by("sortorder")
            provisionaltiles = []
            for tile in tiles:
                append_tile = True
                isfullyprovisional = False
                if tile.provisionaledits is not None:
                    if len(list(tile.provisionaledits.keys())) > 0:
                        if len(tile.data) == 0:
                            isfullyprovisional = True
                        if user_is_reviewer is False:
                            if str(request.user.id) in tile.provisionaledits:
                                tile.provisionaledits = {
                                    str(request.user.id): tile.provisionaledits[
                                        str(request.user.id)
                                    ]
                                }
                                tile.data = tile.provisionaledits[str(request.user.id)][
                                    "value"
                                ]
                            else:
                                if isfullyprovisional is True:
                                    # if the tile IS fully provisional and the current user is not the owner,
                                    # we don't send that tile back to the client.
                                    append_tile = False
                                else:
                                    # if the tile has authoritative data and the current user is not the owner,
                                    # we don't send the provisional data of other users back to the client.
                                    tile.provisionaledits = None
                if append_tile is True:
                    provisionaltiles.append(tile)
            tiles = provisionaltiles

        serialized_graph = None
        if graph.publication:
            published_graph = graph.get_published_graph()
            serialized_graph = published_graph.serialized_graph

        if serialized_graph:
            serialized_cards = serialized_graph["cards"]
            cardwidgets = [
                widget
                for widget in models.CardXNodeXWidget.objects.filter(
                    pk__in=[
                        widget_dict["id"]
                        for widget_dict in serialized_graph["cards_x_nodes_x_widgets"]
                    ]
                )
            ]
        else:
            cards = graph.cardmodel_set.filter(
                nodegroup__in=permitted_nodegroups
            ).prefetch_related("cardxnodexwidget_set")
            serialized_cards = JSONSerializer().serializeToPython(cards)
            cardwidgets = []
            for card in cards:
                cardwidgets += card.cardxnodexwidget_set.all()

        for card in serialized_cards:
            card["is_writable"] = False
            if card["nodegroup_id"] in editable_nodegroup_ids:
                card["is_writable"] = True

        permitted_nodes = [
            node
            for node in nodes._result_cache
            if node.nodegroup in permitted_nodegroups
        ]
        context = {
            "resourceid": resourceid,
            "displayname": displayname,
            "tiles": tiles,
            "cards": serialized_cards,
            "nodegroups": permitted_nodegroups,
            "nodes": permitted_nodes,
            "cardwidgets": cardwidgets,
            "datatypes": models.DDataType.objects.all(),
            "userisreviewer": user_is_reviewer,
            "widgets": models.Widget.objects.all(),
            "card_components": models.CardComponent.objects.all(),
        }

        return JSONResponse(context, indent=4)
