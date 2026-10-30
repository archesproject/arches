from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("arches_vue_components", "0004_alter_widgetmapping_component_and_more"),
    ]

    # This migration originally depended on a core Arches migration
    # (12557_add_language_datatype) that was never released, which broke
    # installs on Arches core versions that don't have it (e.g. 7.6.x).
    operations = [
        migrations.RunPython(migrations.RunPython.noop, migrations.RunPython.noop),
    ]
