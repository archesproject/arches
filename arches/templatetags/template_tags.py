from arches.app.utils.permission_backend import get_editable_resource_types
from arches.app.utils.permission_backend import get_createable_resource_types
from arches.app.utils.permission_backend import get_resource_types_by_perm
from django import template
from django.utils.html import escapejs
from django.templatetags.i18n import do_translate, TranslateNode
import json

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_names):
    if user.is_authenticated:
        if user.is_superuser or bool(
            user.groups.filter(name__in=group_names.split(","))
        ):
            return True
    return False


@register.filter(name="can_edit_resource_instance")
def can_edit_resource_instance(user):
    return len(get_editable_resource_types(user)) > 0


@register.filter(name="can_read_resource_instance")
def can_read_resource_instance(user):
    return (
        len(
            get_resource_types_by_perm(
                user,
                [
                    "models.write_nodegroup",
                    "models.delete_nodegroup",
                    "models.read_nodegroup",
                ],
            )
        )
        > 0
    )


@register.filter(name="can_create_resource_instance")
def can_create_resource_instance(user):
    return len(get_createable_resource_types(user)) > 0


@register.filter(name="can_create_graph")
def can_create_graph(user):
    return (
        len(
            get_resource_types_by_perm(
                user, ["models.write_nodegroup", "models.delete_nodegroup"]
            )
        )
        > 0
    )


@register.filter(name="has_key")
def has_dict_key(the_dict, key):
    """
    If the key has a space then template dot notation can't parse it e.g. resource.["Asset Name"]
    Provides a tag to handle an unparsable key check
    """
    value = False
    try:
        value = key in the_dict.keys()
    except:
        pass
    return value


@register.filter(name="val_from_key")
def dict_value_from_key(the_dict, key):
    """
    If the key has a space then template dot notation can't parse it e.g. resource.["Asset Name"]
    Provide a tag to handle fetching a value for an unparsable key
    """
    value = ""
    try:
        if key in the_dict.keys():
            value = the_dict[key]
    except:
        pass
    return value


@register.filter(name="json_to_obj")
def return_json_as_obj(string):
    """
    Allows a json value found in the template context to be converted into an object.
    """
    value = {}
    try:
        if isinstance(string, str):
            value = json.loads(string)
    except:
        pass
    return value


class QuotedTranslateNode(TranslateNode):
    def render(self, context):
        value = super().render(context)
        return "&quot;{0}&quot;".format(value)


@register.tag("quoted_trans")
def quoted_trans_tag(parser, token):
    """
    Returns a translated string wrapped in HTML &quot; characters
    primarily for use in JSON strings embedded in HTML templates
    where using single quotes breaks when the string itself contains a single quote
    which is often found in other languages
    """
    transnode = do_translate(parser, token)
    return QuotedTranslateNode(
        transnode.filter_expression,
        transnode.noop,
        transnode.asvar,
        transnode.message_context,
    )


class JsTranslatedNode(TranslateNode):
    def render(self, context):
        value = super().render(context)
        return escapejs(value)


@register.tag("jsescaped_trans")
def jsescaped_trans(parser, token):
    """
    Returns a translated string wrapped in HTML &quot; characters
    primarily for use in JSON strings embedded in HTML templates
    where using single quotes breaks when the string itself contains a single quote
    which is often found in other languages
    """
    transnode = do_translate(parser, token)
    return JsTranslatedNode(
        transnode.filter_expression,
        transnode.noop,
        transnode.asvar,
        transnode.message_context,
    )
