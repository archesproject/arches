from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("models", "9477_fix_for_spatial_view_dbf_function_edtf_displaying_null"),
    ]

    def forwards_func(apps, schema_editor):
        TileModel = apps.get_model("models", "TileModel")
        Node = apps.get_model("models", "Node")

        for tile in TileModel.objects.filter(data={}, provisionaledits__isnull=False):
            for node in Node.objects.filter(nodegroup_id=tile.nodegroup_id):
                if not str(node.pk) in tile.data:
                    tile.data[str(node.pk)] = None
            tile.save()

    def reverse_func(apps, schema_editor):
        TileModel = apps.get_model("models", "TileModel")

        for tile in TileModel.objects.filter(provisionaledits__isnull=False):
            if bool(tile.provisionaledits and not any(tile.data.values())):
                tile.data = {}
                tile.save()

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
