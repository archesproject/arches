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
    resource_instance_nodes = [str(nodeid) for nodeid in nodes.objects.filter(Q(datatype='resource-instance') | Q(datatype='resource-instance-list')).values_list(str('nodeid'), flat=True)]
    resource_instance_tiles = tiles.objects.filter(Q(nodegroup_id__node__datatype='resource-instance') | Q(nodegroup_id__node__datatype='resource-instance-list'))

    return resource, relations, resource_instance_nodes, resource_instance_tiles


def create_relation(relations, resource, resourceinstanceid_from, resourceinstanceid_to):
    relationid = uuid.uuid4()
    relations.objects.create(
        resourcexid=relationid,
        resourceinstanceidfrom=resource.objects.get(resourceinstanceid=resourceinstanceid_from),
        resourceinstanceidto=resource.objects.get(resourceinstanceid=resourceinstanceid_to),
        modified=datetime.datetime.now(),
        created=datetime.datetime.now()
    )
    return str(relationid)


def create_resource_instance_tiledata(relations, tile, nodeid):
    if isinstance(tile.data[nodeid], list):
        new_tile_data = []
        for relationid in tile.data[nodeid]:
            relation = relations.objects.get(resourcexid=relationid)
            resourceinstanceidfrom = str(relation.resourceinstanceidfrom.resourceinstanceid)
            resourceinstanceidto = str(relation.resourceinstanceidto.resourceinstanceid)

            if str(tile.resourceinstance_id) == resourceinstanceidfrom:
                if isinstance(tile.data[nodeid], list):
                    tile.data[nodeid].pop(tile.data[nodeid].index(relationid))
                    tile.data[nodeid].append(resourceinstanceidto)
                else:
                    tile.data[nodeid] = resourceinstanceidto

                    relation.delete()
                    return tile.data[nodeid]


def forward_migrate(apps, schema_editor, with_create_permissions=True):
    resource, relations, resource_instance_nodes, resource_instance_tiles = setup(apps)
    # iterate over resource-instance tiles and identify resource-instance nodes
    for tile in resource_instance_tiles:
        for nodeid in tile.data.keys():
            if nodeid in resource_instance_nodes and tile.data[nodeid] is not None:
                # check if data is a list or string then replace resourceinstanceids with relationids
                if isinstance(tile.data[nodeid], list):
                    new_tile_resource_data = []
                    for resourceinstanceidto in tile.data[nodeid]:
                        new_tile_resource_data.append(create_relation(relations, resource, tile.resourceinstance_id, resourceinstanceidto))
                else:
                    new_tile_resource_data = create_relation(relations, resource, tile.resourceinstance_id, tile.data[nodeid])

                tile.data[nodeid] = new_tile_resource_data
                tile.save()


def reverse_migrate(apps, schema_editor, with_create_permissions=True):
    resource, relations, resource_instance_nodes, resource_instance_tiles = setup(apps)

    for tile in resource_instance_tiles:
        for nodeid in tile.data.keys():
            if nodeid in resource_instance_nodes and tile.data[nodeid] is not None:
                tile.data[nodeid] = create_resource_instance_tiledata(relations, tile, nodeid)
                tile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('models', '2724_instance_permissions'),
    ]

    operations = [
        migrations.RunPython(forward_migrate, reverse_migrate),
    ]
