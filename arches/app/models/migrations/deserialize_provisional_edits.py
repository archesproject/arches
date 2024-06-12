# -*- coding: utf-8 -*-


from django.db import migrations
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    TileModel = apps.get_model("models", "TileModel")
    tiles = TileModel.objects.all()
    for tile in tiles:
        if tile.provisionaledits is not None:
            tile.provisionaledits = JSONDeserializer().deserialize(
                tile.provisionaledits
            )
            tile.save()


def reverse_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    TileModel = apps.get_model("models", "TileModel")
    tiles = TileModel.objects.all()
    for tile in tiles:
        if tile.provisionaledits is not None:
            tile.provisionaledits = JSONSerializer().serialize(tile.provisionaledits)
            tile.save()


class Migration(migrations.Migration):

    dependencies = [
        ("models", "3201_second_removal_of_node_nodetype_branch"),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
