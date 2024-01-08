from arches.app.models.system_settings import settings
from django.utils.translation import gettext as _

import logging

def return_message_context(greeting="",closing_text="",email=None,additional_context={}):
    try:
        message_context =  dict(
            greeting = greeting,
            closing= closing_text,
        )

        if email != None:
            message_context["email"] = email

        if additional_context != {}:
            for k,v in additional_context.items():
                message_context[k] = v

        if settings.EXTRA_EMAIL_CONTEXT != {}:
            for k,v in settings.EXTRA_EMAIL_CONTEXT.items():
                # The value for `salutation` is a lazy translation object
                # and must be stringified before going to the database.
                # https://code.djangoproject.com/ticket/35071
                message_context[k] = str(v)

        return message_context

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(_('Setting email context failed'),str(e))

        return {}