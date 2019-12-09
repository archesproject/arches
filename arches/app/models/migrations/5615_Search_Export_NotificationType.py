from django.db import migrations
import django.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):

    dependencies = [("models", "5613_notification_type")]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="context",
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True),
        ),
        migrations.RunSQL(
            """
            INSERT INTO notification_types (typeid, name, emailtemplate, emailnotify, webnotify)
            VALUES (
                '441e6ed4-188d-11ea-a35b-784f435179ea',
                'Search Export Download Ready',
                'email/download_ready_email_notification.htm',
                true,
                true
            );
            """,
            """
            DELETE FROM notification_types
                WHERE typeid in ('441e6ed4-188d-11ea-a35b-784f435179ea');
            """,
        ),
    ]
