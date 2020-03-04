

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '5881_fileviewer'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            INSERT INTO card_components(componentid, name, description, component, componentname, defaultconfig)
                VALUES ('4e40b397-d6bc-4660-a398-4a72c90dba07', 'Photo Gallery Card', 'Photo gallery card UI', 'views/components/cards/photo-gallery-card', 'photo-gallery-card', '{}');
            """,
            reverse_sql="""
            DELETE FROM card_components WHERE componentid = '4e40b397-d6bc-4660-a398-4a72c90dba07';
            """,
        ),
    ]