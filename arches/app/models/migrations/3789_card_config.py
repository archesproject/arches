from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "3725_cardmodel_cssclass"),
    ]

    operations = [
        migrations.RunSQL(
            """
                update cards set config='{}';
            """,
            "",
        ),
    ]
