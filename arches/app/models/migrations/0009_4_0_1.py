# -*- coding: utf-8 -*-


from django.db import migrations, models
import json
import uuid
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

def forwards_func(apps, schema_editor):

    FunctionXGraph = apps.get_model("models", "FunctionXGraph")
    Node = apps.get_model("models", "Node")
    required_node_configs = FunctionXGraph.objects.filter(function_id = '60000000-0000-0000-0000-000000000002')
    for config in required_node_configs:
        d = json.loads(json.dumps(config.config))
        rn = json.loads(d['required_nodes'])
        for k, v in rn.items():
            for nodeid in v:
                node = Node.objects.get(pk=uuid.UUID(nodeid))
                node.isrequired = True
                node.save()

def reverse_func(apps, schema_editor):
    Node = apps.get_model("models", "Node")
    Function = apps.get_model("models", "Function")
    FunctionXGraph = apps.get_model("models", "FunctionXGraph")
    required_nodes_function = Function.objects.get(pk='60000000-0000-0000-0000-000000000002')

    graphs = {}
    required_nodes = Node.objects.filter(isrequired = True)
    for node in required_nodes:
        if str(node.graph_id) not in graphs:
            graphs[str(node.graph_id)] = {}
        if str(node.nodegroup_id) not in graphs[str(node.graph_id)]:
            graphs[str(node.graph_id)][str(node.nodegroup_id)] = []
        graphs[str(node.graph_id)][str(node.nodegroup_id)].append(str(node.pk))
        node.isrequired = False
        node.save()

    for graph_id, required_nodes in graphs.items():
        function_config = {
            "required_nodes": JSONSerializer().serialize(required_nodes),
            "triggering_nodegroups": list(required_nodes.keys())
        }
        FunctionXGraph.objects.create(function=required_nodes_function, graph_id=graph_id, config=function_config)

class Migration(migrations.Migration):

    dependencies = [
        ('models', '0008_4_0_1'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
        migrations.RunSQL("""
                DELETE FROM functions_x_graphs where functionid = '60000000-0000-0000-0000-000000000002';
                DELETE FROM functions WHERE functionid = '60000000-0000-0000-0000-000000000002';
            """,
            """
                INSERT INTO functions(functionid, modulename, classname, functiontype, name, description, defaultconfig, component)
                    VALUES ('60000000-0000-0000-0000-000000000002', 'required_nodes.py', 'RequiredNodesFunction', 'validation', 'Define Required Nodes', 'Define which values are required for a user to save card', '{"required_nodes":"{}"}', 'views/components/functions/required-nodes');
            """),
    ]
