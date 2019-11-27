import logging
from kombu import Connection
from django.utils.translation import ugettext as _
from arches.app.models.system_settings import settings
from arches.celery import app

logger = logging.getLogger(__name__)


def check_if_celery_available():
    try:
        conn = Connection(settings.CELERY_BROKER_URL)
        conn.ensure_connection(max_retries=2)
    except Exception as e:
        logger.warning(_("Unable to connect to a celery broker"))
        return False
    inspect = app.control.inspect()
    result = inspect.ping()
    if result is None:
        logger.warning(_("A celery broker is running, but a celery worker is not available"))
        result = False  # ping returns True or None, assigning False here so we return only a boolean value
    else:
        result = True
    return result
