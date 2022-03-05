from django.db import IntegrityError, ProgrammingError, migrations, models
from django.utils import translation


def forward_migration(apps, schema_editor):
    dlanguage_model = apps.get_model("models", "DLanguage")
    language_model = apps.get_model("models", "Language")
    d_languages = dlanguage_model.objects.all()
    for lang in d_languages:
        language_row = language_model.objects.filter(code__iexact=str.lower(lang.languageid)).first()
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
                    code=lang.languageid, name=lang.languagename.title(), default_direction="ltr", isdefault=lang.isdefault
                )


def reverse_migration(apps, schema_editor):
    # data migration is one way because the dlanguages model gets deleted
    dlanguage_model = apps.get_model("models", "DLanguage")
    language_model = apps.get_model("models", "Language")
    languages = language_model.objects.all()
    for lang in languages:
        dlanguage_model.objects.create(languageid=lang.code, languagename=lang.name.upper(), isdefault=lang.isdefault)


# these blanks are necessary because the data needs to exist _before_ the FK is changed over
def blank_reverse_migration(apps, schema_editor):
    pass


def blank_forward_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("models", "8085_relational_data_model_handle_dates"),
    ]

    operations = [
        migrations.AddField("language", "isdefault", models.BooleanField(default=False, blank=True)),
        migrations.AlterField("language", "code", models.TextField(unique=True)),
        migrations.RunPython(code=forward_migration, reverse_code=blank_reverse_migration),
        migrations.AlterField(
            model_name="value",
            name="language",
            field=models.ForeignKey(
                db_column="languageid", blank=True, to_field="code", null=True, on_delete=models.CASCADE, to="models.Language"
            ),
        ),
        migrations.AlterField(
            model_name="filevalue",
            name="language",
            field=models.ForeignKey(
                db_column="languageid", blank=True, to_field="code", null=True, on_delete=models.CASCADE, to="models.Language"
            ),
        ),
        migrations.RunPython(code=blank_forward_migration, reverse_code=reverse_migration),
        migrations.DeleteModel("dlanguage"),
    ]
