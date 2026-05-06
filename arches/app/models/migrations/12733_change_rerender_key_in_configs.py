from django.db import migrations
from arches.app.models import models


def add_geojson_config_entry(apps, schema_editor):
    cnws = models.CardXNodeXWidget.objects.filter(
        node__datatype__contains="geojson"
    ).all()

    for cnw in cnws:
        cnw.config["rerender"] = True
        cnw.save()

    widgets = models.Widget.objects.filter(datatype__contains="geojson")
    for widget in widgets:
        widget.defaultconfig["rerender"] = True
        widget.save()


def remove_geojson_config_key(apps, schema_editor):
    cnws = models.CardXNodeXWidget.objects.filter(
        node__datatype__contains="geojson"
    ).all()

    for cnw in cnws:
        cnw.config.pop("rerender")
        cnw.save()

    widgets = models.Widget.objects.filter(datatype__contains="geojson")
    for widget in widgets:
        if "rerender" in widget.defaultconfig:
            widget.defaultconfig.pop("rerender")
            widget.save()


def add_concept_config_entry(apps, schema_editor):
    widgets = models.Widget.objects.filter(datatype__contains="concept")
    for widget in widgets:
        print(widget.name, widget.defaultconfig)
        widget.defaultconfig["rerender"] = True
        widget.save()


def remove_concept_config_key(apps, schema_editor):
    widgets = models.Widget.objects.filter(datatype__contains="concept")
    for widget in widgets:
        print(widget.name, widget.defaultconfig)
        if "rerender" in widget.defaultconfig:
            del widget.defaultconfig["rerender"]
        widget.save()


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12587_move_default_value_to_node_config"),
    ]

    operations = [
        migrations.RunPython(remove_geojson_config_key, add_geojson_config_entry),
        migrations.RunPython(add_concept_config_entry, remove_concept_config_key),
    ]
