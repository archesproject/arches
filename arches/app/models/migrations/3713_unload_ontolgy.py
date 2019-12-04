import os
from django.db import migrations, models
from arches.app.models.system_settings import settings
from django.core import management


class Migration(migrations.Migration):

    dependencies = [
        ("models", "5076_adds_map_card_sourcelayer_config"),
    ]

    def forwards_func(apps, schema_editor):
        pass
        # Graph = apps.get_model("models", "graphmodel")
        # graphs_using_ontologies = Graph.objects.exclude(ontology_id__isnull=True).count()
        # if graphs_using_ontologies == 0:
        #     Ontology = apps.get_model("models", "Ontology")
        #     Ontology.objects.filter(version="6.2").delete()

    def reverse_func(apps, schema_editor):
        pass
        # extensions = [os.path.join(settings.ONTOLOGY_PATH, x) for x in settings.ONTOLOGY_EXT]
        # try:
        #     management.call_command('load_ontology',
        #                             source=os.path.join(settings.ONTOLOGY_PATH, settings.ONTOLOGY_BASE),
        #                             version=settings.ONTOLOGY_BASE_VERSION,
        #                             ontology_name=settings.ONTOLOGY_BASE_NAME,
        #                             id='e6e8db47-2ccf-11e6-927e-b8f6b115d7dd',
        #                             extensions=','.join(extensions),
        #                             verbosity=0)
        # except Exception:
        #     print("Failed to Reload the Ontology")

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
