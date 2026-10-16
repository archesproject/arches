from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer


def serialize_node_widget_config(node):
    card_x_node_x_widget = (
        models.CardXNodeXWidget.objects.filter(node=node)
        .select_related("card", "node", "widget__widgetmapping")
        .first()
    )
    if card_x_node_x_widget is None:
        card_x_node_x_widget = default_card_x_node_x_widget(
            node, node.nodegroup.cardmodel_set.first(), DataTypeFactory()
        )
    if card_x_node_x_widget is None:
        return None
    return serialize_card_x_node_x_widget(card_x_node_x_widget)


def serialize_nodegroup_widget_configs(nodes):
    serialized_widgets_by_nodegroup_id = serialize_widgets_by_nodegroup_id(
        nodes, first_cards_by_nodegroup_id({node.nodegroup_id for node in nodes})
    )
    return [
        serialized_widget
        for serialized_widgets in serialized_widgets_by_nodegroup_id.values()
        for serialized_widget in serialized_widgets
    ]


def serialize_graph_widget_configs(
    graph_slug, readable_nodegroup_ids, writable_nodegroup_ids
):
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
    cards_by_nodegroup_id = first_cards_by_nodegroup_id(
        {node.nodegroup_id for node in readable_nodes}
    )
    serialized_widgets_by_nodegroup_id = serialize_widgets_by_nodegroup_id(
        readable_nodes, cards_by_nodegroup_id
    )
    return {
        node.alias: {
            "parent_nodegroup_alias": nodegroup_aliases_by_id.get(
                node.nodegroup.parentnodegroup_id
            ),
            "cardinality": node.nodegroup.cardinality,
            "is_writable": node.nodegroup_id in writable_nodegroup_ids,
            "card": as_json_data(cards_by_nodegroup_id.get(node.nodegroup_id)),
            "card_x_node_x_widgets": serialized_widgets_by_nodegroup_id.get(
                node.nodegroup_id, []
            ),
        }
        for node in readable_nodes
        if node.pk == node.nodegroup_id
    }


def serialize_widgets_by_nodegroup_id(nodes, cards_by_nodegroup_id):
    datatype_factory = DataTypeFactory()
    saved_widgets_by_node_id = {
        card_x_node_x_widget.node_id: card_x_node_x_widget
        for card_x_node_x_widget in models.CardXNodeXWidget.objects.filter(
            node__in=nodes
        ).select_related("card", "node", "widget__widgetmapping")
    }
    serialized_widgets_by_nodegroup_id = {}
    for node in nodes:
        card_x_node_x_widget = saved_widgets_by_node_id.get(node.pk)
        if card_x_node_x_widget is None:
            card_x_node_x_widget = default_card_x_node_x_widget(
                node, cards_by_nodegroup_id.get(node.nodegroup_id), datatype_factory
            )
        if card_x_node_x_widget is None:
            continue
        serialized_widgets_by_nodegroup_id.setdefault(node.nodegroup_id, []).append(
            serialize_card_x_node_x_widget(card_x_node_x_widget)
        )
    for serialized_widgets in serialized_widgets_by_nodegroup_id.values():
        serialized_widgets.sort(
            key=lambda serialized_widget: serialized_widget["sortorder"] or 0
        )
    return serialized_widgets_by_nodegroup_id


def serialize_card_x_node_x_widget(card_x_node_x_widget):
    data = as_json_data(card_x_node_x_widget)
    data["card"] = as_json_data(card_x_node_x_widget.card)
    del data["card_id"]
    data["node"] = as_json_data(card_x_node_x_widget.node)
    del data["node_id"]
    data["widget"] = as_json_data(card_x_node_x_widget.widget)
    del data["widget_id"]
    data["widget"]["component"] = card_x_node_x_widget.widget.widgetmapping.component
    return data


def default_card_x_node_x_widget(node, card, datatype_factory):
    default_widget = datatype_factory.datatypes[node.datatype].defaultwidget
    if default_widget is None:
        return None
    return models.CardXNodeXWidget(
        node=node,
        card=card,
        widget=default_widget,
        config=default_widget.defaultconfig,
        label=node.name,
    )


def first_cards_by_nodegroup_id(nodegroup_ids):
    cards_by_nodegroup_id = {}
    for card in models.CardModel.objects.filter(
        nodegroup_id__in=nodegroup_ids
    ).order_by("pk"):
        cards_by_nodegroup_id.setdefault(card.nodegroup_id, card)
    return cards_by_nodegroup_id


def as_json_data(model_instance):
    return JSONDeserializer().deserialize(JSONSerializer().serialize(model_instance))
