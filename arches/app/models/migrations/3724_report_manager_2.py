

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('models', '3724_report_manager'),
    ]

    operations = [
        migrations.RunSQL(
            """
                update reports
                set config = '{}'::json
                where config is NULL;

                update graphs
                set templateid = r.templateid, config = r.config
                from reports r where r.graphid = graphs.graphid and r.active = true;
            """,
            ""
        ),
        migrations.DeleteModel(
            name='Report',
        ),
    ]
