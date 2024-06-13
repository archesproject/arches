import logging
from kombu import Connection
from django.utils.translation import gettext as _
from arches.app.models.system_settings import settings
from arches.celery import app
import time

logger = logging.getLogger(__name__)


def check_if_celery_available():
    result = False
    if settings.CELERY_BROKER_URL != "":
        try:
            conn = Connection(settings.CELERY_BROKER_URL)
            conn.ensure_connection(max_retries=2)
            if settings.CELERY_CHECK_ONLY_INSPECT_BROKER:
                result = True
            else:
                inspect = app.control.inspect()
                for i in range(4):
                    try:
                        # ping returns an object or None
                        ping_result = inspect.ping()
                        break
                    except (BrokenPipeError, ConnectionResetError) as e:
                        time.sleep(0.10)
                        logger.error(_("Celery worker connection failed. Reattempting"))
                        if i == 3:
                            logger.error(
                                _(
                                    "Failed to connect to celery due to a BrokenPipeError/ConnectionResetError"
                                )
                            )
                            logger.exception(e)
                if ping_result is None:
                    logger.error(
                        _(
                            "A celery broker is running, but a celery worker is not available"
                        )
                    )
                else:
                    result = True
        except Exception as e:
            logger.error(_("Unable to connect to a celery broker"))
    return result
