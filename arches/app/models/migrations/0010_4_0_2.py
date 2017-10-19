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
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=16)),
                ('user', models.OneToOneField(on_delete=CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_profile',
            },
        ),
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
        migrations.AlterModelOptions(
            name='userprofile',
            options={'managed': True},
        ),
        migrations.CreateModel(
            name='MobileProjectXGroup',
            fields=[
                ('mobile_project_x_group_id', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('group', models.ForeignKey(on_delete=CASCADE, to='auth.Group')),
                ('mobile_project', models.ForeignKey(on_delete=CASCADE, to='models.MobileProject')),
            ],
            options={
                'db_table': 'mobile_projects_x_groups',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MobileProjectXUser',
            fields=[
                ('mobile_project_x_user_id', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('mobile_project', models.ForeignKey(on_delete=CASCADE, to='models.MobileProject')),
                ('user', models.ForeignKey(on_delete=CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'mobile_projects_x_users',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='mobileproject',
            name='groups',
            field=models.ManyToManyField(through='models.MobileProjectXGroup', to='auth.Group'),
        ),
        migrations.AddField(
            model_name='mobileproject',
            name='users',
            field=models.ManyToManyField(through='models.MobileProjectXUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='mobileprojectxuser',
            unique_together=set([('mobile_project', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='mobileprojectxgroup',
            unique_together=set([('mobile_project', 'group')]),
        ),
    ]
