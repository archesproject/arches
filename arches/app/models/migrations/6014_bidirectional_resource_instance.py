import os
import uuid
import datetime
from django.db.models import Q
from django.db import migrations, models


def setup(apps):
    nodes = apps.get_model("models", "Node")
    tiles = apps.get_model("models", "Tile")
    relations = apps.get_model("models", "ResourceXResource")
    resource = apps.get_model("models", "Resource")
    resource_instance_nodes = {str(node["nodeid"]):node["datatype"] for node in nodes.objects.filter(Q(datatype='resource-instance') | Q(datatype='resource-instance-list')).values('nodeid', 'datatype')}
    resource_instance_tiles = tiles.objects.filter(Q(nodegroup_id__node__datatype='resource-instance') | Q(nodegroup_id__node__datatype='resource-instance-list')).distinct()

    return resource, relations, resource_instance_nodes, resource_instance_tiles


def create_relation(relations, resource, resourceinstanceid_from, resourceinstanceid_to):
    relationid = uuid.uuid4()
    relations.objects.create(
        resourcexid=relationid,
        resourceinstanceidfrom_id=resourceinstanceid_from,
        resourceinstanceidto_id=resourceinstanceid_to,
        modified=datetime.datetime.now(),
        created=datetime.datetime.now()
    )
    resourceName = ""
    ontologyClass = ""
    try:
        resTo = resource.objects.get(resourceinstanceid=resourceinstanceid_to)
        resourceName = resTo.displayname
        ontologyClass = resTo.get_root_ontology()
    except:
        pass

    ret = {
        "resourceId": resourceinstanceid_to,
        "ontologyProperty": "",
        "inverseOntologyProperty": "",
        "resourceName": resourceName,
        "ontologyClass": ontologyClass,
        "resourceXresourceId": str(relationid)
    }
    return ret


def create_resource_instance_tiledata(relations, tile, nodeid, datatype):
    if tile.data[nodeid] is None:
        return None
    else:
        new_tile_data = []
        for resourceRelationItem in tile.data[nodeid]:
            relation = relations.objects.get(resourcexid=resourceRelationItem["resourceXresourceId"])
            relation.delete()
            new_tile_data.append(str(resourceRelationItem["resourceXresourceId"]))

        if datatype == "resource-instance-list":
            return new_tile_data
        else:
            return new_tile_data[0]


def forward_migrate(apps, schema_editor, with_create_permissions=True):
    resource, relations, resource_instance_nodes, resource_instance_tiles = setup(apps)
    # iterate over resource-instance tiles and identify resource-instance nodes
    for tile in resource_instance_tiles:
        for nodeid in tile.data.keys():
            if nodeid in resource_instance_nodes and tile.data[nodeid] is not None:
                # check if data is a list or string then replace resourceinstanceids with relationids
                new_tile_resource_data = []
                if isinstance(tile.data[nodeid], list):
                    for resourceinstanceidto in tile.data[nodeid]:
                        new_tile_resource_data.append(create_relation(relations, resource, tile.resourceinstance_id, resourceinstanceidto))
                else:
                    new_tile_resource_data.append(create_relation(relations, resource, tile.resourceinstance_id, tile.data[nodeid]))

                tile.data[nodeid] = new_tile_resource_data
                tile.save()


def reverse_migrate(apps, schema_editor, with_create_permissions=True):
    resource, relations, resource_instance_nodes, resource_instance_tiles = setup(apps)
    for tile in resource_instance_tiles:
        for nodeid in tile.data.keys():
            if nodeid in resource_instance_nodes.keys() and tile.data[nodeid] is not None:
                tile.data[nodeid] = create_resource_instance_tiledata(relations, tile, nodeid, resource_instance_nodes[nodeid])
                tile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('models', '6125_details_search_component'),
    ]

    operations = [
        migrations.RunPython(forward_migrate, reverse_migrate),
    ]
