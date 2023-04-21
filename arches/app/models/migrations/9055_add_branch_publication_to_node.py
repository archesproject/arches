import arches.app.models.fields.i18n
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9436_relational_view_null_geom_support"),
    ]

    operations = [
        migrations.AddField(
            model_name="node",
            name="sourcebranchpublication",
            field=models.ForeignKey(
                blank=True,
                db_column="sourcebranchpublicationid",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="models.graphxpublishedgraph",
            ),
        ),
    ]
