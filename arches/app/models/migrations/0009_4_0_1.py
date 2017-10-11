# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import json
import uuid

def forwards_func(apps, schema_editor):
    
    FunctionXGraph = apps.get_model("models", "FunctionXGraph")
    Node = apps.get_model("models", "Node")
    required_node_configs = FunctionXGraph.objects.filter(function_id = '60000000-0000-0000-0000-000000000002')
    for config in required_node_configs:
        d = json.loads(json.dumps(config.config))
        rn = json.loads(d['required_nodes'])
        for k, v in rn.iteritems():
            for nodeid in v:
                node = Node.objects.get(pk=uuid.UUID(nodeid))
                node.isrequired = True
                node.save()

def reverse_func(apps, schema_editor):
    print 'reversing'

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
