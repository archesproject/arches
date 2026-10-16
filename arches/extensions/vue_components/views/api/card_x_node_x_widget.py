from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import gettext as _
from django.views.generic import View

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from arches.app.utils.permission_backend import nodegroup_ids_with_inherited_permission
from arches.app.utils.response import JSONResponse, JSONErrorResponse


def serialize_card_x_node_x_widget(widget, datatype_factory):
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

    return data


def first_cards_by_nodegroup_id(nodegroup_ids):
    cards_by_nodegroup_id = {}
    for card in models.CardModel.objects.filter(
        nodegroup_id__in=nodegroup_ids
    ).order_by("pk"):
        cards_by_nodegroup_id.setdefault(card.nodegroup_id, card)
    return cards_by_nodegroup_id


def default_card_x_node_x_widget(node, card, datatype_factory):
    default_widget_definition = datatype_factory.datatypes[node.datatype].defaultwidget
    if default_widget_definition is None:  # handle semantic nodes
        return None
    return models.CardXNodeXWidget(
        node=node,
        card=card,
        widget=default_widget_definition,
        config=default_widget_definition.defaultconfig,
        label=node.name,
    )


def build_card_x_node_x_widgets_by_nodegroup_id(
    nodes, saved_widgets, default_cards_by_nodegroup_id
):
    datatype_factory = DataTypeFactory()
    saved_widgets_by_node_id = {
        saved_widget.node_id: saved_widget for saved_widget in saved_widgets
    }

    widget_instances = []
    for node in nodes:
        if node.pk in saved_widgets_by_node_id:
            widget_instances.append(saved_widgets_by_node_id[node.pk])
            continue
        default_widget = default_card_x_node_x_widget(
            node,
            default_cards_by_nodegroup_id.get(node.nodegroup_id),
            datatype_factory,
        )
        if default_widget is not None:
            widget_instances.append(default_widget)

    serialized_widgets_by_nodegroup_id = {}
    for widget_instance in widget_instances:
        serialized_widget = serialize_card_x_node_x_widget(
            widget_instance, datatype_factory
        )
        serialized_widget["widget"][
            "component"
        ] = widget_instance.widget.widgetmapping.component
        serialized_widgets_by_nodegroup_id.setdefault(
            widget_instance.node.nodegroup_id, []
        ).append(serialized_widget)

    for serialized_widgets in serialized_widgets_by_nodegroup_id.values():
        serialized_widgets.sort(key=lambda item: item["sortorder"] or 0)
    return serialized_widgets_by_nodegroup_id


def user_can_read_nodegroup(user, nodegroup_id):
    return nodegroup_id in nodegroup_ids_with_inherited_permission(
        user, "models.read_nodegroup"
    )


def nodegroup_permission_error_response():
    return JSONErrorResponse(
        message=_("You do not have permission to read this nodegroup."),
        status=403,
    )


def widget_mapping_error_response():
    return JSONErrorResponse(
        message=_("Database error occurred while fetching widget mapping."),
        status=503,
    )


class CardXNodeXWidgetView(View):
    def get(self, request, graph_slug, node_alias):
        query = Q(
            node__graph__slug=graph_slug,
            node__alias=node_alias,
            node__source_identifier_id__isnull=True,
        )

        card_x_node_x_widget = (
            models.CardXNodeXWidget.objects.filter(query)
            .select_related()  # eagerly load all related objects
            .first()
        )

        if card_x_node_x_widget:
            node = card_x_node_x_widget.node
        else:
            node = models.Node.objects.filter(
                graph__slug=graph_slug, alias=node_alias, source_identifier=None
            ).get()

        if not user_can_read_nodegroup(request.user, node.nodegroup_id):
            return nodegroup_permission_error_response()

        if not card_x_node_x_widget:
            card_x_node_x_widget = default_card_x_node_x_widget(
                node, node.nodegroup.cardmodel_set.first(), DataTypeFactory()
            )
            if card_x_node_x_widget is None:
                return JSONErrorResponse(
                    message=_("No widget is configured for this node."),
                    status=404,
                )

        serialized_widget = serialize_card_x_node_x_widget(
            card_x_node_x_widget, DataTypeFactory()
        )

        try:
            serialized_widget["widget"][
                "component"
            ] = card_x_node_x_widget.widget.widgetmapping.component
        except ObjectDoesNotExist:
            return widget_mapping_error_response()

        return JSONResponse(serialized_widget)


class CardXNodeXWidgetListFromNodegroupView(View):
    def get(self, request, graph_slug, nodegroup_alias):
        nodes = list(
            models.Node.objects.filter(
                graph__slug=graph_slug,
                nodegroup__node__alias=nodegroup_alias,
                source_identifier=None,
            )
        )
        if nodes and not user_can_read_nodegroup(request.user, nodes[0].nodegroup_id):
            return nodegroup_permission_error_response()

        saved_widgets = models.CardXNodeXWidget.objects.filter(
            node__graph__slug=graph_slug,
            node__nodegroup__node__alias=nodegroup_alias,
            node__source_identifier_id__isnull=True,
        ).select_related()

        try:
            serialized_widgets_by_nodegroup_id = (
                build_card_x_node_x_widgets_by_nodegroup_id(
                    nodes,
                    saved_widgets,
                    first_cards_by_nodegroup_id({node.nodegroup_id for node in nodes}),
                )
            )
        except ObjectDoesNotExist:
            return widget_mapping_error_response()

        return JSONResponse(
            [
                serialized_widget
                for serialized_widgets in serialized_widgets_by_nodegroup_id.values()
                for serialized_widget in serialized_widgets
            ]
        )


class CardXNodeXWidgetListFromGraphView(View):
    def get(self, request, graph_slug):
        readable_nodegroup_ids = nodegroup_ids_with_inherited_permission(
            request.user, "models.read_nodegroup"
        )
        writable_nodegroup_ids = nodegroup_ids_with_inherited_permission(
            request.user, "models.write_nodegroup"
        )

        graph_nodes = list(
            models.Node.objects.filter(
                graph__slug=graph_slug,
                source_identifier=None,
                nodegroup__isnull=False,
            ).select_related("nodegroup")
        )
        nodegroup_aliases_by_id = {
            node.nodegroup_id: node.alias
            for node in graph_nodes
            if node.pk == node.nodegroup_id
        }
        readable_nodes = [
            node for node in graph_nodes if node.nodegroup_id in readable_nodegroup_ids
        ]
        saved_widgets = models.CardXNodeXWidget.objects.filter(
            node__in=readable_nodes
        ).select_related("card", "node", "widget__widgetmapping")
        cards_by_nodegroup_id = first_cards_by_nodegroup_id(
            {node.nodegroup_id for node in readable_nodes}
        )

        try:
            serialized_widgets_by_nodegroup_id = (
                build_card_x_node_x_widgets_by_nodegroup_id(
                    readable_nodes, saved_widgets, cards_by_nodegroup_id
                )
            )
        except ObjectDoesNotExist:
            return widget_mapping_error_response()

        nodegroups_by_alias = {}
        for node in readable_nodes:
            if node.pk != node.nodegroup_id:
                continue
            nodegroups_by_alias[node.alias] = {
                "parent_nodegroup_alias": nodegroup_aliases_by_id.get(
                    node.nodegroup.parentnodegroup_id
                ),
                "cardinality": node.nodegroup.cardinality,
                "is_writable": node.nodegroup_id in writable_nodegroup_ids,
                "card": JSONDeserializer().deserialize(
                    JSONSerializer().serialize(
                        cards_by_nodegroup_id.get(node.nodegroup_id)
                    )
                ),
                "card_x_node_x_widgets": serialized_widgets_by_nodegroup_id.get(
                    node.nodegroup_id, []
                ),
            }
        return JSONResponse(nodegroups_by_alias)
