from django.conf import settings
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("models", "5972_migrates_iiif_annotations"),
    ]

    operations = [
        migrations.RunSQL(
            """
            INSERT INTO notification_types (typeid, name, emailtemplate, emailnotify, webnotify)
            VALUES (
                '08013c4c-8456-4677-88a6-94511c5771af',
                'Package Load Complete',
                'email/download_ready_email_notification.htm',
                true,
                true
            );
            """,
            """
            DELETE FROM notification_types
                WHERE typeid in ('08013c4c-8456-4677-88a6-94511c5771af');
            """,
        ),
    ]
