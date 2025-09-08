from django.db import migrations
import uuid


def create_reference_select_widget_mapping(apps, schema_editor):
    WidgetMapping = apps.get_model("arches_component_lab", "WidgetMapping")

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
    WidgetMapping = apps.get_model("arches_component_lab", "WidgetMapping")
    WidgetMapping.objects.filter(
        widget_id="19e56148-82b8-47eb-b66e-f6243639a1a8",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("arches_controlled_lists", "0004_reconfigure_listitem_sortorder_constraints"),
        ("arches_component_lab", "0002_populate_widget_mappings"),
    ]

    operations = [
        migrations.RunPython(
            create_reference_select_widget_mapping,
            revert_reference_select_widget_mapping,
        ),
    ]
