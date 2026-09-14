from django.db import migrations
from django.db.models import F, Max


ARCHES_JSON_IMPORT_MODULE_PK = "0a1c9d67-8b4e-4f2a-9d31-6c5b2e7a4f18"


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12800_refresh_transaction_resource_relationships"),
    ]

    def add_module(apps, schema_editor):
        ETLModule = apps.get_model("models", "ETLModule")
        max_helpsortorder = ETLModule.objects.aggregate(
            max_helpsortorder=Max(F("helpsortorder"))
        )["max_helpsortorder"]

        ETLModule.objects.update_or_create(
            pk=ARCHES_JSON_IMPORT_MODULE_PK,
            defaults={
                "name": "Import Arches JSON",
                "icon": "fa fa-upload",
                "etl_type": "import",
                "component": "views/components/etl_modules/arches-json-importer",
                "componentname": "arches-json-importer",
                "modulename": "arches_json_importer.py",
                "classname": "ArchesJsonImporter",
                "config": {
                    "bgColor": "#4a6670",
                    "circleColor": "#6c8a95",
                    "show": True,
                    "celeryByteSizeLimit": 100000,
                    "logTileValues": False,
                },
                "reversible": True,
                "slug": "arches-json-importer",
                "description": "Import Arches JSON business data in bulk",
                "helptemplate": "arches-json-importer-help",
                "helpsortorder": (max_helpsortorder or 0) + 1,
            },
        )

    def remove_module(apps, schema_editor):
        ETLModule = apps.get_model("models", "ETLModule")
        ETLModule.objects.filter(pk=ARCHES_JSON_IMPORT_MODULE_PK).delete()

    operations = [
        migrations.RunPython(add_module, remove_module),
    ]
