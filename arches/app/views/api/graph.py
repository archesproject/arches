from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from arches.app.models import models
from arches.app.models.card import Card as CardProxyModel
from arches.app.models.graph import Graph
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase


@method_decorator(csrf_exempt, name="dispatch")
class Graphs(APIBase):
    action = None

    def get(self, request, graph_id=None):
        cards_querystring = request.GET.get("cards", None)
        exclusions_querystring = request.GET.get("exclude", None)
        if cards_querystring == "false":
            get_cards = False
        else:
            get_cards = True

        if exclusions_querystring is not None:
            exclusions = list(map(str.strip, exclusions_querystring.split(",")))
        else:
            exclusions = []

        perm = "read_nodegroup"
        user = request.user
        if graph_id and not self.action:
            graph = Graph.objects.get(graphid=graph_id)
            graph = JSONSerializer().serializeToPython(
                graph, sort_keys=False, exclude=["functions"] + exclusions
            )

            if get_cards:
                datatypes = models.DDataType.objects.all()
                cards = CardProxyModel.objects.filter(graph_id=graph_id)
                permitted_cards = []
                for card in cards:
                    if user.has_perm(perm, card.nodegroup):
                        card.filter_by_perm(user, perm)
                        permitted_cards.append(card)
                cardwidgets = [
                    widget
                    for widgets in [
                        card.cardxnodexwidget_set.all() for card in permitted_cards
                    ]
                    for widget in widgets
                ]

                permitted_cards = JSONSerializer().serializeToPython(
                    permitted_cards, sort_keys=False
                )

                return JSONResponse(
                    {
                        "datatypes": datatypes,
                        "cards": permitted_cards,
                        "graph": graph,
                        "cardwidgets": cardwidgets,
                    }
                )
            else:
                return JSONResponse({"graph": graph})
        elif self.action == "get_graph_models":
            graphs = models.GraphModel.objects.all()
            return JSONResponse(JSONSerializer().serializeToPython(graphs))


class GraphHasUnpublishedChanges(APIBase):
    def get(self, request, graph_id=None):
        graph = models.GraphModel.objects.get(pk=graph_id)
        return JSONResponse(graph.has_unpublished_changes)

    def post(self, request, graph_id=None):
        has_unpublished_changes = bool(
            request.POST.get("has_unpublished_changes") == "true"
        )
        graph = models.GraphModel.objects.filter(
            pk=graph_id
        )  # need filter here for `update` to work
        graph.update(has_unpublished_changes=has_unpublished_changes)

        return JSONResponse({"has_unpublished_changes": has_unpublished_changes})


class GraphIsActive(APIBase):
    def get(self, request, graph_id=None):
        graph = Graph.objects.get(pk=graph_id)

        if graph.source_identifier:
            raise ValueError(_("Cannot get the active status of a draft."))

        return JSONResponse(graph.is_active)

    def post(self, request, graph_id=None):
        try:
            is_active = bool(request.POST.get("is_active") == "true")

            with transaction.atomic():
                graph = Graph.objects.get(pk=graph_id)

                if graph.source_identifier:
                    raise ValueError(_("Cannot change the active status of a draft."))

                if graph.is_active != is_active:
                    models.GraphModel.objects.filter(pk=graph.pk).update(
                        is_active=is_active
                    )

            return JSONResponse({"is_graph_active": graph.is_active})
        except:
            return JSONResponse(status=500)


class DraftGraph(APIBase):
    def get(self, request, graph_id):
        """
        Get a draft graph.
        """
        existing_draft_graph = Graph.objects.filter(
            source_identifier_id=graph_id
        ).first()

        if not existing_draft_graph:
            raise ValueError(_("No draft graph exists for this model."))

        return JSONResponse(
            {
                "draft_graph_id": existing_draft_graph.pk,
                "draft_graph": JSONSerializer().serialize(existing_draft_graph),
            }
        )

    def post(self, request, graph_id):
        """
        Create a draft graph.
        """
        existing_draft_graph = Graph.objects.filter(
            source_identifier_id=graph_id
        ).first()

        if existing_draft_graph:
            raise ValueError(_("A draft already exists for this model."))

        graph = Graph.objects.get(pk=graph_id)
        draft_graph = graph.create_draft_graph()

        return JSONResponse(
            {
                "draft_graph_id": draft_graph.pk,
                "draft_graph": JSONSerializer().serialize(draft_graph),
            }
        )

    def delete(self, request, graph_id):
        """
        Delete a draft graph.
        """
        existing_draft_graph = Graph.objects.filter(
            source_identifier_id=graph_id
        ).first()

        if not existing_draft_graph:
            raise ValueError(_("No draft graph exists for this model."))

        existing_draft_graph.delete()

        return JSONResponse({"message": _("Draft graph deleted successfully.")})
