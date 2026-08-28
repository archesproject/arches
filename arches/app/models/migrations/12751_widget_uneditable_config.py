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


def remove_uneditable_from_widgets(apps, schema_editor):
    CardXNodeXWidget = apps.get_model("models", "CardXNodeXWidget")
    Widget = apps.get_model("models", "Widget")

    widgets_to_remove = Widget.objects.exclude(
        name__in=[
            "non-localized-text-widget",
            "number-widget",
            "rich-text-widget",
            "text-widget",
        ]
    ).all()
    for widget in widgets_to_remove:
        config = dict(widget.defaultconfig or {})
        config.pop("uneditable", None)
        widget.defaultconfig = config
        widget.save()

    for card_widget in CardXNodeXWidget.objects.filter(
        widget__in=widgets_to_remove
    ).all():
        config = dict(card_widget.config or {})
        config.pop("uneditable", None)
        card_widget.config = config
        card_widget.save()


class Migration(migrations.Migration):
    dependencies = [
        ("models", "12587_move_default_value_to_node_config.py"),
    ]

    operations = [
        migrations.RunPython(add_uneditable_to_widgets, remove_uneditable_from_widgets),
    ]
