from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("arches_controlled_lists", "0004_reconfigure_listitem_sortorder_constraints"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="listitem",
            name="unique_list_uri",
        ),
    ]
