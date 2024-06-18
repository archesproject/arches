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

    def forward_migration(apps, schema_editor=None):
        dlanguage_model = apps.get_model("models", "DLanguage")
        language_model = apps.get_model("models", "Language")
        d_languages = dlanguage_model.objects.all()
        for lang in d_languages:
            language_row = language_model.objects.filter(
                code__iexact=str.lower(lang.languageid)
            ).first()
            if language_row:
                language_row.isdefault = lang.isdefault
                language_row.save()
            else:
                try:
                    language_info = translation.get_language_info(lang.languageid)
                except KeyError:
                    language_info = None

                if language_info:
                    language_model.objects.create(
                        code=lang.languageid,
                        name=language_info["name"],
                        default_direction="rtl" if language_info["bidi"] else "ltr",
                        isdefault=lang.isdefault,
                    )
                else:
                    language_model.objects.create(
                        code=lang.languageid,
                        name=lang.languagename.title(),
                        default_direction="ltr",
                        isdefault=lang.isdefault,
                    )

    def reverse_migration(apps, schema_editor):
        # data migration is one way because the dlanguages model gets deleted
        dlanguage_model = apps.get_model("models", "DLanguage")
        language_model = apps.get_model("models", "Language")
        languages = language_model.objects.all()
        for lang in languages:
            dlanguage_model.objects.create(
                languageid=lang.code,
                languagename=lang.name.upper(),
                isdefault=lang.isdefault,
            )

    # these blanks are necessary because the data needs to exist _before_ the FK is changed over
    def blank_reverse_migration(apps, schema_editor):
        pass

    def blank_forward_migration(apps, schema_editor):
        pass

    operations = [
        migrations.CreateModel(
            name="Language",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("code", models.TextField()),
                ("name", models.TextField()),
                (
                    "default_direction",
                    models.TextField(
                        choices=[("ltr", "Left to Right"), ("rtl", "Right to Left")],
                        default="ltr",
                    ),
                ),
                (
                    "scope",
                    models.TextField(
                        choices=[("system", "System Scope"), ("data", "Data Scope")],
                        default="system",
                    ),
                ),
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
                    [
                        language,
                        language_info["name"],
                        "rtl" if language_info["bidi"] else "ltr",
                        "system",
                    ],
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
                    select * into l from languages where code='{}' limit 1;
                    while updated_count != 0 loop
                        update tiles c
                            set tiledata =
                                jsonb_set(
                                    tiledata,
                                    ('{{' || b.nodeid || '}}')::text[],
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
            """.format(
                        settings.LANGUAGE_CODE
                    )
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
                    select * into l from languages where code='{}' limit 1;
                    while updated_count != 0 loop
                        update tiles c
                        set tiledata =
                            jsonb_set(
                                tiledata,
                                ('{{' || b.nodeid || '}}')::text[],
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
            """.format(
                        settings.LANGUAGE_CODE
                    )
                )
            ],
        ),
        migrations.AddField(
            "language", "isdefault", models.BooleanField(default=False, blank=True)
        ),
        migrations.AlterField("language", "code", models.TextField(unique=True)),
        migrations.RunPython(
            code=forward_migration, reverse_code=blank_reverse_migration
        ),
        migrations.AlterField(
            model_name="value",
            name="language",
            field=models.ForeignKey(
                db_column="languageid",
                blank=True,
                to_field="code",
                null=True,
                on_delete=models.CASCADE,
                to="models.Language",
            ),
        ),
        migrations.AlterField(
            model_name="filevalue",
            name="language",
            field=models.ForeignKey(
                db_column="languageid",
                blank=True,
                to_field="code",
                null=True,
                on_delete=models.CASCADE,
                to="models.Language",
            ),
        ),
        migrations.RunPython(
            code=blank_forward_migration, reverse_code=reverse_migration
        ),
        migrations.DeleteModel("dlanguage"),
    ]
