from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import gettext as _

from arches.app.datatypes.core.external_domain import BaseExternalDomainDataType

User = get_user_model()


class UserDataType(BaseExternalDomainDataType):
    """Domain datatype backed by the auth_user table.

    Stores the user's primary key (id) in tile data and displays
    the username as the human-readable value.
    """

    def get_options_queryset(self):
        return User.objects.all()

    def get_option_id(self, user):
        return user.pk

    def get_option_display(self, user):
        return user.username

    def get_lookup_filter(self, value):
        try:
            int_value = int(value)
            return Q(pk=int_value) | Q(username=value)
        except (ValueError, TypeError):
            return Q(username=value)

    def get_invalid_message(self, value):
        message = _("The value '{0}' is not a valid user id or username.".format(value))
        title = _("Invalid User Datatype")
        return message, title
