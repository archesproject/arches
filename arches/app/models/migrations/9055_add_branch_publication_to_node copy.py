import arches.app.models.fields.i18n
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('models', '8974_rr_load_performance_v2'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='publication',
            field=models.ForeignKey(blank=True, db_column='publicationid', null=True, on_delete=django.db.models.deletion.SET_NULL, to='models.graphxpublishedgraph'),
        ),
    ]
