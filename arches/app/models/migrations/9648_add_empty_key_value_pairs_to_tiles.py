from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("models", "9477_fix_for_spatial_view_dbf_function_edtf_displaying_null"),
    ]

    def forwards_func(apps, schema_editor):
        TileModel = apps.get_model("models", "TileModel")

        for tile in TileModel.objects.all():
            tile.save()  # should trigger new code in `TileModel.save` method that adds empty key/value pairs to tile data

    def reverse_func(apps, schema_editor):
        pass

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
