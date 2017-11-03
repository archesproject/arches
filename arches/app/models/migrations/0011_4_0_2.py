from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0010_4_0_2'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobileproject',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='mobileproject',
            name='enddate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mobileproject',
            name='startdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mobileproject',
            name='name',
            field=models.TextField(null=True),
        ),
    ]
