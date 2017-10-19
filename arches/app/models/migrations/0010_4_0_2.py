from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
from django.db.models.deletion import CASCADE
import uuid

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
        migrations.AddField(
            model_name='mobileproject',
            name='createdby',
            field=models.ForeignKey(default=1, on_delete=CASCADE, related_name='createdby', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mobileproject',
            name='lasteditedby',
            field=models.ForeignKey(default=1, on_delete=CASCADE, related_name='lasteditedby', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
