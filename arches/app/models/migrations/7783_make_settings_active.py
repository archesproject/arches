import datetime
import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7810_i18n_url_datatype"),
    ]

    operations = [
        migrations.RunSQL(
            """
            update graphs set isactive = true where graphid = 'ff623370-fa12-11e6-b98b-6c4008b05c4c';
            create table if not exists temp_graph_status as (select graphid, isactive from graphs where isactive = true);
            """,
            """
            update graphs set isactive = false where graphid = 'ff623370-fa12-11e6-b98b-6c4008b05c4c';
            drop table if exists temp_graph_status;
            """,
        ),
    ]
