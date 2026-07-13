from django.db import migrations

from arches_vue_components.utils.widget_synchronizer import WidgetSynchronizer


def add_language_widget_mapping(apps, schema_editor):
    WidgetSynchronizer().add_mapping(
        "language-widget",
        "arches_vue_components/widgets/LanguageSelectWidget/LanguageSelectWidget.vue",
    )


def remove_language_widget_mapping(apps, schema_editor):
    Widget = apps.get_model("models", "Widget")
    WidgetMapping = apps.get_model("arches_vue_components", "WidgetMapping")
    widget = Widget.objects.filter(name="language-widget").first()
    if widget:
        WidgetMapping.objects.filter(widget=widget).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12557_add_language_datatype"),
        ("arches_vue_components", "0004_alter_widgetmapping_component_and_more"),
    ]

    operations = [
        migrations.RunPython(
            add_language_widget_mapping, remove_language_widget_mapping
        ),
    ]
