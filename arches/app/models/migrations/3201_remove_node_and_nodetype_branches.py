# -*- coding: utf-8 -*-


from django.db import migrations


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    GraphModel = apps.get_model("models", "GraphModel")
    NodeGroup = apps.get_model("models", "NodeGroup")

    try:
        GraphModel.objects.get(graphid="22000000-0000-0000-0000-000000000000").delete()
    except GraphModel.DoesNotExist:
        pass

    try:
        GraphModel.objects.get(graphid="22000000-0000-0000-0000-000000000001").delete()
        NodeGroup.objects.get(
            nodegroupid="20000000-0000-0000-0000-100000000001"
        ).delete()
    except (GraphModel.DoesNotExist, NodeGroup.DoesNotExist):
        pass


def reverse_func(apps, schema_editor):
    GraphModel = apps.get_model("models", "GraphModel")
    Node = apps.get_model("models", "Node")
    NodeGroup = apps.get_model("models", "NodeGroup")
    Edge = apps.get_model("models", "Edge")
    CardModel = apps.get_model("models", "CardModel")

    # Node Branch
    graph_dict = {
        "author": "Arches",
        "color": None,
        "deploymentdate": None,
        "deploymentfile": None,
        "description": "Represents a single node in a graph",
        "graphid": "22000000-0000-0000-0000-000000000000",
        "iconclass": "fa fa-circle",
        "isactive": True,
        "isresource": False,
        "name": "Node",
        "ontology_id": None,
        "subtitle": "Represents a single node in a graph.",
        "version": "v1",
    }
    GraphModel.objects.create(**graph_dict).save()

    node_dict = {
        "config": None,
        "datatype": "semantic",
        "description": "Represents a single node in a graph",
        "graph_id": "22000000-0000-0000-0000-000000000000",
        "isrequired": False,
        "issearchable": True,
        "istopnode": True,
        "name": "Node",
        "nodegroup_id": None,
        "nodeid": "20000000-0000-0000-0000-100000000000",
        "ontologyclass": "http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity",
    }
    Node.objects.create(**node_dict).save()

    # Node/Node Type Branch
    graph_dict = {
        "author": "Arches",
        "color": None,
        "deploymentdate": None,
        "deploymentfile": None,
        "description": "Represents a node and node type pairing",
        "graphid": "22000000-0000-0000-0000-000000000001",
        "iconclass": "fa fa-angle-double-down",
        "isactive": True,
        "isresource": False,
        "name": "Node/Node Type",
        "ontology_id": None,
        "subtitle": "Represents a node and node type pairing",
        "version": "v1",
    }
    GraphModel.objects.create(**graph_dict).save()

    nodegroup_dict = {
        "cardinality": "n",
        "legacygroupid": "",
        "nodegroupid": "20000000-0000-0000-0000-100000000001",
        "parentnodegroup_id": None,
    }
    NodeGroup.objects.create(**nodegroup_dict).save()

    card_dict = {
        "active": True,
        "cardid": "bf9ea150-3eaa-11e8-8b2b-c3a348661f61",
        "description": "Represents a node and node type pairing",
        "graph_id": "22000000-0000-0000-0000-000000000001",
        "helpenabled": False,
        "helptext": None,
        "helptitle": None,
        "instructions": "",
        "name": "Node/Node Type",
        "nodegroup_id": "20000000-0000-0000-0000-100000000001",
        "sortorder": None,
        "visible": True,
    }
    CardModel.objects.create(**card_dict).save()

    nodes = [
        {
            "config": None,
            "datatype": "string",
            "description": "",
            "graph_id": "22000000-0000-0000-0000-000000000001",
            "isrequired": False,
            "issearchable": True,
            "istopnode": True,
            "name": "Node",
            "nodegroup_id": "20000000-0000-0000-0000-100000000001",
            "nodeid": "20000000-0000-0000-0000-100000000001",
            "ontologyclass": "http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity",
        },
        {
            "config": {"rdmCollection": None},
            "datatype": "concept",
            "description": "",
            "graph_id": "22000000-0000-0000-0000-000000000001",
            "isrequired": False,
            "issearchable": True,
            "istopnode": False,
            "name": "Node Type",
            "nodegroup_id": "20000000-0000-0000-0000-100000000001",
            "nodeid": "20000000-0000-0000-0000-100000000002",
            "ontologyclass": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
        },
    ]

    for node in nodes:
        Node.objects.create(**node).save()

    edges_dict = {
        "description": None,
        "domainnode_id": "20000000-0000-0000-0000-100000000001",
        "edgeid": "22200000-0000-0000-0000-000000000001",
        "graph_id": "22000000-0000-0000-0000-000000000001",
        "name": None,
        "ontologyproperty": "http://www.cidoc-crm.org/cidoc-crm/P2_has_type",
        "rangenode_id": "20000000-0000-0000-0000-100000000002",
    }
    Edge.objects.create(**edges_dict).save()


class Migration(migrations.Migration):

    dependencies = [
        ("models", "3199_graphmodel_color"),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
