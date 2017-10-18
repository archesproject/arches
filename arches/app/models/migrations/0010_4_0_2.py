from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0009_4_0_1'),
    ]

    operations = [
        migrations.CreateModel(
            name='MobileProject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'mobile_projects',
                'managed': True,
            },
        ),
    ]
