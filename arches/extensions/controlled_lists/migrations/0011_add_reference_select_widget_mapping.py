import uuid

from django.db import migrations


def create_reference_select_widget_mapping(apps, schema_editor):
    WidgetMapping = apps.get_model("arches_vue_components", "WidgetMapping")

    # first delete old mapping if it exists
    WidgetMapping.objects.filter(
        widget_id="19e56148-82b8-47eb-b66e-f6243639a1a8",
    ).delete()

    WidgetMapping.objects.create(
        id=uuid.uuid4(),
        widget_id="19e56148-82b8-47eb-b66e-f6243639a1a8",
        component="arches_controlled_lists/widgets/ReferenceSelectWidget/ReferenceSelectWidget.vue",
    )


def revert_reference_select_widget_mapping(apps, schema_editor):
    WidgetMapping = apps.get_model("arches_vue_components", "WidgetMapping")
    WidgetMapping.objects.filter(
        widget_id="19e56148-82b8-47eb-b66e-f6243639a1a8",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("arches_controlled_lists", "0010_fix_whitespace_in_previous_migration"),
        ("arches_vue_components", "0002_populate_widget_mappings"),
    ]

    operations = [
        migrations.RunPython(
            create_reference_select_widget_mapping,
            revert_reference_select_widget_mapping,
        ),
    ]
