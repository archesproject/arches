import django.contrib.postgres.constraints
import django.db.models.constraints
from django.db import migrations, models
from django.contrib.postgres.operations import BtreeGistExtension


class Migration(migrations.Migration):

    dependencies = [
        ("arches_controlled_lists", "0003_rename_search_only_list_searchable"),
    ]

    operations = [
        BtreeGistExtension(),
        migrations.RemoveConstraint(
            model_name="listitem",
            name="unique_list_sortorder",
        ),
        migrations.AddConstraint(
            model_name="listitem",
            constraint=django.contrib.postgres.constraints.ExclusionConstraint(
                condition=models.Q(("parent__isnull", True)),
                deferrable=django.db.models.constraints.Deferrable["DEFERRED"],
                expressions=[("list", "="), ("sortorder", "=")],
                name="unique_list_sortorder",
                violation_error_message="All items at the root of this list must have distinct sort orders.",
            ),
        ),
        migrations.AddConstraint(
            model_name="listitem",
            constraint=django.contrib.postgres.constraints.ExclusionConstraint(
                condition=models.Q(("parent__isnull", False)),
                deferrable=django.db.models.constraints.Deferrable["DEFERRED"],
                expressions=[("parent", "="), ("sortorder", "=")],
                name="unique_parent_sortorder",
                violation_error_message="All child items in this parent item must have distinct sort orders.",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="listitem",
            name="unique_list_uri",
        ),
        migrations.AddConstraint(
            model_name="listitem",
            constraint=django.contrib.postgres.constraints.ExclusionConstraint(
                condition=models.Q(("parent__isnull", True)),
                deferrable=django.db.models.constraints.Deferrable["DEFERRED"],
                expressions=[("list", "="), ("uri", "=")],
                name="unique_list_uri",
                violation_error_message="All items at the root of this list must have distinct URIs.",
            ),
        ),
        migrations.AddConstraint(
            model_name="listitem",
            constraint=django.contrib.postgres.constraints.ExclusionConstraint(
                condition=models.Q(("parent__isnull", False)),
                deferrable=django.db.models.constraints.Deferrable["DEFERRED"],
                expressions=[("parent", "="), ("uri", "=")],
                name="unique_parent_uri",
                violation_error_message="All child items in this parent item must have distinct URIs.",
            ),
        ),
    ]
