from arches.app.models.system_settings import settings
from django.utils.translation import get_language

def get_localized_value(obj, lang=None):
    lang = get_language() if lang is None else lang
    try:
        return obj[lang]
    except:
        for langcode in obj.keys():
            if langcode.split("-")[0] == lang.split("-")[0]:
                return obj[langcode]
        try:
            return obj[settings.LANGUAGE_CODE]
        except:
            return obj[langcode]