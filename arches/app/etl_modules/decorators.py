from datetime import datetime
import functools
import logging

from django.utils.translation import gettext as _

from arches.app.models.models import LoadEvent
import arches.app.utils.task_management as task_management

logger = logging.getLogger(__name__)


def load_data_async(func):
    @functools.wraps(func)
    def wrapper(self, request, loadid):
        if task_management.check_if_celery_available():
            logger.info(_("Delegating load to Celery task"))
            func(self, request)
            result = _("delegated_to_celery")
            return {"success": True, "data": result}
        else:
            err = _(
                "Unable to perform this operation because Celery does not appear to be running. Please contact your administrator."
            )
            LoadEvent.objects.filter(loadid=loadid).update(
                status="failed", load_end_time=datetime.now()
            )
            return {"success": False, "data": {"title": _("Error"), "message": err}}

    return wrapper
