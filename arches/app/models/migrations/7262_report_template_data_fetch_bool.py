from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '7224_url_datatype'),
    ]

    operations = [
        migrations.RunSQL(
            """
                ALTER TABLE report_templates 
                ADD COLUMN preload_resource_data BOOLEAN NOT NULL 
                DEFAULT TRUE;
            """
        )
    ]
