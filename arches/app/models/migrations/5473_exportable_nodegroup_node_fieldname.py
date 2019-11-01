from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '5477_fix_makemigrations'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE nodes
            ADD fieldname TEXT;

            ALTER TABLE node_groups
            ADD exportable BOOLEAN;
            """,
            reverse_sql="""
            ALTER TABLE nodes
            DROP COLUMN fieldname;

            ALTER TABLE node_groups
            DROP COLUMN exportable;
            """,
        ),
    ]
