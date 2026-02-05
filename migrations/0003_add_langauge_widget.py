from django.db import migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12557_add_language_datatype"),
        ("arches_component_lab", "0002_populate_widget_mappings"),
    ]

    def forward(apps, schema_editor):
        ArchesWidget = apps.get_model("models", "Widget")
        WidgetMapping = apps.get_model("arches_component_lab", "WidgetMapping")

        language_widget = ArchesWidget.objects.get(name="language-widget")
        existing_mapping = WidgetMapping.objects.filter(
            widget_id=language_widget.widgetid
        )
        component = (
            "arches_component_lab/widgets/LanguageSelectWidget/LanguageSelectWidget.vue"
        )
        if existing_mapping.exists():
            existing_mapping.update(component=component)
        else:
            WidgetMapping.objects.create(
                id=uuid.uuid4(),
                widget_id=language_widget.widgetid,
                component=component,
            )

    def reverse(apps, schema_editor):
        ArchesWidget = apps.get_model("models", "Widget")
        WidgetMapping = apps.get_model("arches_component_lab", "WidgetMapping")

        language_widget = ArchesWidget.objects.get(name="language-widget")
        WidgetMapping.objects.filter(widget_id=language_widget.widgetid).delete()

    operations = [
        migrations.RunPython(forward, reverse),
    ]
