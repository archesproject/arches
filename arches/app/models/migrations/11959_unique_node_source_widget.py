from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "11958_check_excess_widgets"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="graphmodel",
            name="unique_slug",
        ),
        migrations.AlterUniqueTogether(
            name="cardxnodexwidget",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="cardxnodexwidget",
            constraint=models.UniqueConstraint(
                models.F("node"),
                condition=models.Q(("source_identifier__isnull", True)),
                name="unique_node_widget_source",
            ),
        ),
        migrations.AddConstraint(
            model_name="cardxnodexwidget",
            constraint=models.UniqueConstraint(
                models.F("node"),
                condition=models.Q(("source_identifier__isnull", False)),
                name="unique_node_widget_draft",
            ),
        ),
        migrations.AddConstraint(
            model_name="graphmodel",
            constraint=models.UniqueConstraint(
                models.F("slug"),
                condition=models.Q(("source_identifier__isnull", True)),
                name="unique_slug_source",
            ),
        ),
        migrations.AddConstraint(
            model_name="graphmodel",
            constraint=models.UniqueConstraint(
                models.F("slug"),
                condition=models.Q(("source_identifier__isnull", False)),
                name="unique_slug_draft",
            ),
        ),
    ]
