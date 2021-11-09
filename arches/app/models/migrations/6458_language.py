from django.db import migrations, models
from django.utils import translation
from arches.app.models.system_settings import settings


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7794_i18n_string_datatype"),
    ]
    translation.activate(settings.LANGUAGE_CODE)

    language = translation.get_language()
    if language is None:
        language = "en"

    language_info = translation.get_language_info(language)

    operations = [
        migrations.CreateModel(
            name="Language",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("code", models.TextField()),
                ("name", models.TextField()),
                ("default_direction", models.TextField(choices=[("ltr", "Left to Right"), ("rtl", "Right to Left")], default="ltr")),
                ("scope", models.TextField(choices=[("system", "System Scope"), ("data", "Data Scope")], default="system")),
            ],
            options={
                "db_table": "languages",
                "managed": True,
            },
        ),
        migrations.RunSQL(
            sql=[
                (
                    "insert into languages (code, name, default_direction, scope) values (%s, %s, %s, %s);",
                    [language, language_info["name"], "rtl" if language_info["bidi"] else "ltr", "system"],
                )
            ],
            reverse_sql=[("delete from languages")],
        ),
        migrations.RunSQL(
            sql=[
                (
                    """
                do
                $$
                declare
                    l record;
                    updated_count integer default -1;
                begin
                    select * into l from languages limit 1;
                    while updated_count != 0 loop
                        update tiles c
                            set tiledata =
                                jsonb_set(
                                    tiledata,
                                    ('{' || b.nodeid || '}')::text[],
                                    jsonb_build_object(
                                        l.code,
                                        jsonb_build_object(
                                            'value',
                                            tiledata->>b.nodeid,
                                            'direction',
                                            l.default_direction)
                                        ),
                                    false)
                        from
                            nodes a,
                            (select tileid, jsonb_object_keys(tiledata) as nodeid from tiles) b
                        where
                            a.nodeid::text = b.nodeid::text and
                            c.tileid = b.tileid and
                            a.datatype = 'string' and
                            (tiledata->>b.nodeid)::text not like '%"direction":%';
                        get diagnostics updated_count = ROW_COUNT;
                    end loop;
                    return;
                end;
                $$
            """
                )
            ],
            reverse_sql=[
                (
                    """
                do
                $$
                declare
                    l record;
                    updated_count integer default -1;
                begin
                    select * into l from languages limit 1;
                    while updated_count != 0 loop
                        update tiles c
                        set tiledata =
                            jsonb_set(
                                tiledata,
                                ('{' || b.nodeid || '}')::text[],
                                to_jsonb(((((tiledata->>b.nodeid)::jsonb)->>l.code)::jsonb)->>'value'),
                                false
                            )
                        from
                            nodes a,
                            (select tileid, jsonb_object_keys(tiledata) as nodeid from tiles) b
                        where
                            a.nodeid::text = b.nodeid::text and
                            c.tileid = b.tileid and a.datatype = 'string' and
                            (tiledata->>b.nodeid)::text like '%"direction":%';
                        get diagnostics updated_count = ROW_COUNT;
                    end loop;
                    return;
                end;
                $$
            """
                )
            ],
        ),
    ]
