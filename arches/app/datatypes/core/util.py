from django.utils.translation import get_language, gettext as _


def get_value_from_jsonld(json_ld_node):
    try:
        language = json_ld_node[0].get("@language")
        if language is None:
            language = get_language()
        return (json_ld_node[0].get("@value"), language)
    except KeyError as e:
        try:
            language = json_ld_node.get("@language")
            if language is None:
                language = get_language()
            return (json_ld_node.get("@value"), language)
        except AttributeError as e:
            return
    except IndexError as e:
        return
