from django.db import migrations


USER_WIDGET_ID = "d3a09f3e-5b1c-4a2d-8e6f-7c9b0a1d2e3f"


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12586_tile_cardinality_check"),
    ]

    def forward(apps, schema_editor):
        DDataType = apps.get_model("models", "DDataType")
        Widget = apps.get_model("models", "Widget")

        widget = Widget(
            widgetid=USER_WIDGET_ID,
            name="external-domain",
            component="views/components/widgets/external-domain",
            helptext=None,
            datatype="auth-user",
            defaultconfig={
                "defaultValue": None,
                "i18n_properties": ["placeholder"],
                "placeholder": "Select a user",
                "width": "100%",
                "uneditable": False,
            },
        )
        datatype = DDataType(
            datatype="auth-user",
            iconclass="fa fa-user",
            # UserDataType lives in arches/app/datatypes/core/user.py.
            # The module importer resolves "core.user.py" →
            # arches.app.datatypes.core.user when searching the datatypes dir.
            modulename="core.user.py",
            classname="UserDataType",
            defaultconfig=None,
            configcomponent="views/components/datatypes/external-domain",
            configname="external-domain-datatype-config",
            isgeometric=False,
            defaultwidget=widget,
            issearchable=True,
        )
        widget.save()
        datatype.save()

    def reverse(apps, schema_editor):
        DDataType = apps.get_model("models", "DDataType")
        Widget = apps.get_model("models", "Widget")
        DDataType.objects.filter(datatype="auth-user").delete()
        Widget.objects.filter(widgetid=USER_WIDGET_ID).delete()

    operations = [
        migrations.RunPython(forward, reverse),
    ]
