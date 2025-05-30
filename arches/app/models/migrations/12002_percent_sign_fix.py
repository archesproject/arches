from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "11959_unique_node_source_widget"),
    ]

    forward = r"""
        UPDATE cards_x_nodes_x_widgets
        SET config = jsonb_set(
            config,
            '{width}',
            to_jsonb(
                regexp_replace(config->>'width', '^(\d+)%{2,}$', '\1%', 'g')
            )
        )
        WHERE config ? 'width'
        AND config->>'width' ~ '^\d+%{2,}$';
    """

    operations = [
        migrations.RunSQL(
            forward,
            migrations.RunSQL.noop,  # No reverse operation needed
        ),
    ]
