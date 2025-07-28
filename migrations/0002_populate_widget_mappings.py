from django.db import migrations
import uuid


def populate_widget_mappings(apps, schema_editor):
    ArchesWidget = apps.get_model("models", "Widget")
    WidgetMapping = apps.get_model("arches_component_lab", "WidgetMapping")

    widget_id_to_updated_component_path = {
        "10000000-0000-0000-0000-000000000001": "arches_component_lab/widgets/TextWidget/TextWidget.vue",
        "10000000-0000-0000-0000-000000000002": "arches_component_lab/widgets/ConceptSelectWidget/ConceptSelectWidget.vue",
        "10000000-0000-0000-0000-000000000003": "arches_component_lab/widgets/SwitchWidget/SwitchWidget.vue",
        "10000000-0000-0000-0000-000000000004": "arches_component_lab/widgets/DatePickerWidget/DatePickerWidget.vue",
        "10000000-0000-0000-0000-000000000005": "arches_component_lab/widgets/RichTextWidget/RichTextWidget.vue",
        "10000000-0000-0000-0000-000000000006": "arches_component_lab/widgets/RadioBooleanWidget/RadioBooleanWidget.vue",
        "10000000-0000-0000-0000-000000000007": "arches_component_lab/widgets/MapWidget/MapWidget.vue",
        "10000000-0000-0000-0000-000000000008": "arches_component_lab/widgets/NumberWidget/NumberWidget.vue",
        "10000000-0000-0000-0000-000000000009": "arches_component_lab/widgets/ConceptRadioWidget/ConceptRadioWidget.vue",
        "10000000-0000-0000-0000-000000000012": "arches_component_lab/widgets/ConceptMultiselectWidget/ConceptMultiselectWidget.vue",
        "10000000-0000-0000-0000-000000000013": "arches_component_lab/widgets/ConceptCheckboxWidget/ConceptCheckboxWidget.vue",
        "10000000-0000-0000-0000-000000000015": "arches_component_lab/widgets/DomainSelectWidget/DomainSelectWidget.vue",
        "10000000-0000-0000-0000-000000000016": "arches_component_lab/widgets/DomainMultiselectWidget/DomainMultiselectWidget.vue",
        "10000000-0000-0000-0000-000000000017": "arches_component_lab/widgets/DomainRadioWidget/DomainRadioWidget.vue",
        "10000000-0000-0000-0000-000000000018": "arches_component_lab/widgets/DomainCheckboxWidget/DomainCheckboxWidget.vue",
        "10000000-0000-0000-0000-000000000019": "arches_component_lab/widgets/FileListWidget/FileListWidget.vue",
        "31f3728c-7613-11e7-a139-784f435179ea": "arches_component_lab/widgets/ResourceInstanceSelectWidget/ResourceInstanceSelectWidget.vue",
        "46ef064b-2611-4708-9f52-60136bd8a65b": "arches_component_lab/widgets/NonLocalizedTextWidget/NonLocalizedTextWidget.vue",
        "aae743b8-4c48-11ea-988b-2bc775672c81": "arches_component_lab/widgets/IIIFWidget/IIIFWidget.vue",
        "adfd15ce-dbab-11e7-86d1-0fcf08612b27": "arches_component_lab/widgets/EDTFWidget/EDTFWidget.vue",
        "ca0c43ff-af73-4349-bafd-53ff9f22eebd": "arches_component_lab/widgets/URLWidget/URLWidget.vue",
        "f5d6b190-bbf0-4dc9-b991-1debab8cb4a9": "arches_component_lab/widgets/NodeValueSelectWidget/NodeValueSelectWidget.vue",
        "ff3c400a-76ec-11e7-a793-784f435179ea": "arches_component_lab/widgets/ResourceInstanceMultiselectWidget/ResourceInstanceMultiselectWidget.vue",
    }

    for widget in ArchesWidget.objects.all():
        WidgetMapping.objects.create(
            id=uuid.uuid4(),
            widget_id=widget.widgetid,
            component=widget_id_to_updated_component_path.get(
                str(widget.widgetid), widget.component
            ),
        )


def revert_widget_mappings(apps, schema_editor):
    WidgetMapping = apps.get_model("arches_component_lab", "WidgetMapping")
    WidgetMapping.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("arches_component_lab", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(populate_widget_mappings, revert_widget_mappings),
    ]
