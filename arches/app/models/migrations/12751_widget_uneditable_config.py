from django.db import migrations


def add_uneditable_to_widgets(apps, schema_editor):
    CardXNodeXWidget = apps.get_model("models", "CardXNodeXWidget")
    Widget = apps.get_model("models", "Widget")

    for widget in Widget.objects.all():
        config = dict(widget.defaultconfig or {})
        if "uneditable" not in config:
            config["uneditable"] = False
            widget.defaultconfig = config
            widget.save()

    for card_widget in CardXNodeXWidget.objects.all():
        config = dict(card_widget.config or {})
        if "uneditable" not in config:
            config["uneditable"] = False
            card_widget.config = config
            card_widget.save()


class Migration(migrations.Migration):
    dependencies = [
        ("models", "12779_add_multicard_resource_descriptor"),
    ]

    operations = [
        # no reverse: a leftover "uneditable": false is the default value and is
        # ignored by widgets that don't read it.
        migrations.RunPython(add_uneditable_to_widgets, migrations.RunPython.noop),
    ]
