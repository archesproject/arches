from arches.app.utils import decorators
from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_names):
    if user.is_authenticated():
        if user.is_superuser or bool(user.groups.filter(name__in=group_names.split(','))):
            return True
    return False