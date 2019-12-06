from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("models", "5613_notification_type")]

    operations = [
        migrations.RunSQL(
            """
            INSERT INTO notification_types (typeid, name, emailtemplate, emailnotify, webnotify)
            VALUES (uuid('3789b120-0ct4-21ea-913e-784g4833r92a'),'Search Export Download Ready','email/download_ready_email_notification.htm',true,true);
            """,
            """
            DELETE FROM notification_types
                WHERE typeid in ('3789b120-0ct4-21ea-913e-784g4833r92a');
            """,
        )
    ]
