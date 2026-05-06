from django.db import migrations


def _move_default_value_from_widgets_to_nodes(serialized_graph):
    nodes = serialized_graph.get("nodes", [])
    widgets = serialized_graph.get("cards_x_nodes_x_widgets", [])
    node_by_id = {node["nodeid"]: node for node in nodes}
    changed = False

    for widget in widgets:
        config = widget.get("config") or {}
        if "defaultValue" not in config:
            continue
        default_value = config["defaultValue"]
        node_id = widget.get("node_id")
        if default_value is not None and node_id in node_by_id:
            node = node_by_id[node_id]
            if node.get("config") is None:
                node["config"] = {}
            node["config"]["defaultValue"] = default_value
        del config["defaultValue"]
        changed = True

    return changed


def _move_default_value_from_nodes_to_widgets(serialized_graph):
    nodes = serialized_graph.get("nodes", [])
    widgets = serialized_graph.get("cards_x_nodes_x_widgets", [])

    widget_by_node_id = {
        widget["node_id"]: widget
        for widget in widgets
        if widget.get("source_identifier") is None
    }
    changed = False

    for node in nodes:
        config = node.get("config") or {}
        if "defaultValue" not in config:
            continue
        default_value = config["defaultValue"]
        node_id = node.get("nodeid")
        if default_value is not None and node_id in widget_by_node_id:
            widget = widget_by_node_id[node_id]
            if widget.get("config") is None:
                widget["config"] = {}
            widget["config"]["defaultValue"] = default_value
        del config["defaultValue"]
        changed = True

    return changed


def _update_published_graphs(apps, graph_transformer):
    PublishedGraph = apps.get_model("models", "PublishedGraph")
    batch_size = 25
    graphs_to_update = []

    queryset = PublishedGraph.objects.exclude(serialized_graph__isnull=True)
    for published_graph in queryset.iterator(chunk_size=batch_size):
        serialized_graph = published_graph.serialized_graph
        if graph_transformer(serialized_graph):
            graphs_to_update.append(published_graph)
            if len(graphs_to_update) == batch_size:
                PublishedGraph.objects.bulk_update(
                    graphs_to_update, ["serialized_graph"]
                )
                graphs_to_update = []

    if graphs_to_update:
        PublishedGraph.objects.bulk_update(graphs_to_update, ["serialized_graph"])


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12548_remove_whitespace_from_db_function"),
    ]

    def forward(apps, schema_editor):
        schema_editor.execute(
            """
            UPDATE nodes
                        SET config = COALESCE(nodes.config, '{}'::jsonb)
                         || jsonb_build_object('defaultValue', w.config->'defaultValue')
            FROM cards_x_nodes_x_widgets w
            WHERE w.nodeid = nodes.nodeid
              AND w.source_identifier IS NULL
              AND w.config ? 'defaultValue'
              AND w.config->'defaultValue' != 'null'::jsonb;
        """
        )

        schema_editor.execute(
            """
            UPDATE cards_x_nodes_x_widgets
            SET config = config - 'defaultValue'
            WHERE config ? 'defaultValue';
        """
        )

        _update_published_graphs(apps, _move_default_value_from_widgets_to_nodes)

    def reverse(apps, schema_editor):
        schema_editor.execute(
            """
            UPDATE cards_x_nodes_x_widgets
                        SET config = COALESCE(cards_x_nodes_x_widgets.config, '{}'::jsonb)
                         || jsonb_build_object('defaultValue', n.config->'defaultValue')
            FROM nodes n
            WHERE cards_x_nodes_x_widgets.nodeid = n.nodeid
              AND cards_x_nodes_x_widgets.source_identifier IS NULL
              AND n.config ? 'defaultValue'
              AND n.config->'defaultValue' != 'null'::jsonb;
        """
        )

        schema_editor.execute(
            """
            UPDATE nodes
            SET config = config - 'defaultValue'
            WHERE config ? 'defaultValue';
        """
        )

        _update_published_graphs(apps, _move_default_value_from_nodes_to_widgets)

    operations = [migrations.RunPython(forward, reverse)]
