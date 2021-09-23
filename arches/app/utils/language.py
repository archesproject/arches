# from django.conf import settings
import json
from arches.app.models.system_settings import settings
from django.utils.translation import get_language

def default_lang_node_json(value=None, lang=None):
    from arches.app.models.models import L10n_Field
    ret = {}
    ret[settings.LANGUAGE_CODE] = ""
    for lang_setting in settings.LANGUAGES:
        ret[lang_setting[0]] = ""

    if value is not None:
        available_languages = [settings.LANGUAGE_CODE] if len(settings.LANGUAGES) == 0 else [lang[0] for lang in settings.LANGUAGES]
        if lang is None:
            lang = get_language()
        if lang in available_languages:
            ret[lang] = value
        else:
            raise Exception("The language code supplied is not enabled in settings.LANGUAGES or settings.LANGUAGE_CODE")

    return L10n_Field(ret)