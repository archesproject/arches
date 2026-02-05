from django.db import migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12557_add_language_datatype"),
        ("arches_component_lab", "0003_add_pk_default"),
    ]

    def forward(apps, schema_editor):
        ArchesWidget = apps.get_model("models", "Widget")
        WidgetMapping = apps.get_model("arches_component_lab", "WidgetMapping")

        language_widget = ArchesWidget.objects.get(name="language-widget")
        component = (
            "arches_component_lab/widgets/LanguageSelectWidget/LanguageSelectWidget.vue"
        )
        WidgetMapping.objects.update_or_create(
            widget_id=language_widget.widgetid,
            defaults={
                "component": component,
            },
        )

    def reverse(apps, schema_editor):
        ArchesWidget = apps.get_model("models", "Widget")
        WidgetMapping = apps.get_model("arches_component_lab", "WidgetMapping")

        language_widget = ArchesWidget.objects.get(name="language-widget")
        WidgetMapping.objects.filter(widget_id=language_widget.widgetid).delete()

    operations = [
        migrations.RunPython(forward, reverse),
    ]
