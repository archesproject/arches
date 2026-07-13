from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("arches_controlled_lists", "0004_reconfigure_listitem_sortorder_constraints"),
    ]

    # ReferenceSelectWidget's mapping is registered by
    # 0011_add_reference_select_widget_mapping instead, against
    # arches_vue_components.WidgetMapping. This migration's slot can't be
    # removed since it's already applied on real projects, so it's kept
    # as a no-op.
    operations = [
        migrations.RunPython(migrations.RunPython.noop, migrations.RunPython.noop),
    ]
