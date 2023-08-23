# Generated by Django 3.2.20 on 2023-08-18 02:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('models', '9748_alter_graphmodel_functions_alter_icon_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkflowHistory',
            fields=[
                ('workflowid', models.UUIDField(primary_key=True, serialize=False)),
                ('workflowstepids', models.JSONField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('completed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(db_column='userid', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'workflow_history',
                'managed': True,
            },
        ),
    ]
