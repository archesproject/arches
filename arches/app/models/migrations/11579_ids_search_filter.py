from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "11842_userpreferences"),
    ]

    forward = """
        INSERT INTO search_component
        VALUES (
            'f1856bfb-c3c4-4d67-8f23-0aa3eef3a160', 'ResourceIds Filter', '', 'ids.py', 'ResourceIdsFilter', 'ids-filter-type', NULL, 'ids', '{}'
        );
    """

    reverse = """
        DELETE FROM search_component WHERE searchcomponentid = 'f1856bfb-c3c4-4d67-8f23-0aa3eef3a160';
    """

    operations = [
        migrations.RunSQL(
            forward,
            reverse,
        ),
    ]
