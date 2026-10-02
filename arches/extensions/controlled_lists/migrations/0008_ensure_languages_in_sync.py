from django.db import migrations
import uuid
from django.conf import settings
from django.utils.translation import get_language_info


def add_missing_languages(apps, schema_editor):
    Language = apps.get_model("models", "Language")
    if settings.LANGUAGES:
        for lang in settings.LANGUAGES:
            found_language = Language.objects.filter(code=lang[0]).first()
            if found_language:
                continue
            language_info = get_language_info(lang[0])
            Language.objects.create(
                code=lang[0],
                name=language_info["name"],
                default_direction="rtl" if language_info["bidi"] else "ltr",
                scope="system",
                isdefault=False,
            )


class Migration(migrations.Migration):
    dependencies = [
        (
            "arches_controlled_lists",
            "0007_change_listitemvalue_value_from_char_to_text_field",
        ),
    ]

    operations = [
        migrations.RunPython(
            add_missing_languages,
            migrations.RunPython.noop,
        ),
    ]
