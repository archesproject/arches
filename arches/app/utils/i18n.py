from arches.app.models.system_settings import settings
from django.utils.translation import get_language


def get_localized_value(obj, lang=None, return_lang=False):
    """
    This method accepts a localized object or a simple string
    eg: obj => {"en": "tree", "es": "arbol"}
    eg: simple string => "tree"
    and attempts to return the string based on the requested language


    If lang is specified it will return the value of the string with that language key
    or th string

    Arguments:
    obj -- (required) a localized object or a simple string

    Keyword Arguments:
    lang -- (optional) the specific value to return from the obj that has that language
    return_lang -- (optional) False (default) to return just the
        string value of the requested language
        True to return an object keyed by the language

    Returns:
        the value of the string in "obj" that was keyed to the requested language
        or an obj with just a single languag

    Examples:
        if obj = {"en": "tree", "es": "arbol"} and lang is "es" then will reutrn "arbol"
        or {"es": "arbol"} if "return_lang" is True

        if lang isn't specified, then the activated language will be used.

    """
    lang = get_language() if lang is None else lang
    if not isinstance(obj, dict):
        return {lang: obj} if return_lang else obj
    else:
        found_lang = None
        if lang in obj:
            found_lang = lang
        else:
            for langcode in obj.keys():
                if langcode.split("-")[0] == lang.split("-")[0]:
                    found_lang = langcode

            if settings.LANGUAGE_CODE in obj:
                found_lang = settings.LANGUAGE_CODE
            else:
                found_lang = langcode

        return {found_lang: obj[found_lang]} if return_lang else obj[found_lang]
