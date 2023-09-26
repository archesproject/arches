from arches.app.models.fields.i18n import I18n_JSONField
from django.db import migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7803_i18n_ri_list_datatype"),
    ]

    sql = """
        UPDATE public.cards_x_nodes_x_widgets
        SET config = config ||
        jsonb_set(
            jsonb_set(
                config, '{{url_placeholder}}', json_build_object('{0}', config->>'url_placeholder')::jsonb, true),
        '{{url_label_placeholder}}', json_build_object('{0}', config->>'url_label_placeholder')::jsonb, true) ||
        '{{"i18n_properties": ["url_label_placeholder", "url_placeholder"]}}'
        WHERE nodeid in (SELECT nodeid FROM nodes WHERE datatype = 'url');

        UPDATE public.widgets
        SET defaultconfig = defaultconfig ||
        '{{"i18n_properties": ["url_label_placeholder", "url_placeholder"]}}'
        WHERE datatype = 'url';

    """.format(
        settings.LANGUAGE_CODE
    )

    reverse_sql = """
        UPDATE public.cards_x_nodes_x_widgets
        set config = config - 'i18n_properties' ||
        json_build_object('url_placeholder', jsonb_extract_path(config, 'url_placeholder', '{0}'))::jsonb ||
        json_build_object('url_label_placeholder', jsonb_extract_path(config, 'url_label_placeholder', '{0}'))::jsonb
        WHERE nodeid in (SELECT nodeid FROM nodes WHERE datatype = 'url');

        UPDATE public.widgets
        SET defaultconfig = defaultconfig - 'i18n_properties'
        WHERE datatype = 'url';


    """.format(
        settings.LANGUAGE_CODE
    )

    operations = [
        migrations.RunSQL(sql, reverse_sql),
        migrations.AlterField(
            model_name="cardxnodexwidget",
            name="config",
            field=I18n_JSONField(blank=True, null=True),
        ),
    ]
