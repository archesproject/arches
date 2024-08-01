from arches import settings
from django.db import migrations
from arches.app.models.fields.i18n import I18n_TextField


class Migration(migrations.Migration):

    dependencies = [
        ("models", "8813_resource_model_view_defaults"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                (
                    """
                do
                $$
                declare
                    l record;
                begin
                    select * into l from languages where code='{0}' limit 1;
                    update resource_instances c
                        set name =
                            jsonb_set(
                                '{{}}',
                                ('{{' || l.code || '}}')::text[],
                                to_jsonb(replace(c.name, '"', '')),
                                true)::text;
                end;
                $$
            """.format(
                        settings.LANGUAGE_CODE
                    )
                ),
            ],
            reverse_sql=[
                ("update resource_instances set name = replace(name, '\"', '')")
            ],
        ),
        migrations.AlterField(
            model_name="resourceinstance",
            name="name",
            field=I18n_TextField(blank=True, null=True),
        ),
        migrations.RunSQL(
            sql=[("select * from resource_instances limit 1")],
            reverse_sql=[
                (
                    """
                do
                $$
                declare
                    l record;
                begin
                    select * into l from languages where code='{}' limit 1;
                    update resource_instances 
                        set name = name->l.code;
                end;
                $$
            """.format(
                        settings.LANGUAGE_CODE
                    )
                )
            ],
        ),
    ]
