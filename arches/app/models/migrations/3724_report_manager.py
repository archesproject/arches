

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('models', '3601_remove_forms'),
    ]

    operations = [
        migrations.AddField(
            model_name='graphmodel',
            name='config',
            field=django.contrib.postgres.fields.jsonb.JSONField(db_column='config', default=dict),
        ),
        migrations.AddField(
            model_name='graphmodel',
            name='template',
            field=models.ForeignKey(
                db_column='templateid',
                default='50000000-0000-0000-0000-000000000001',
                on_delete=django.db.models.deletion.CASCADE,
                to='models.ReportTemplate'
            ),
        ),
    ]
