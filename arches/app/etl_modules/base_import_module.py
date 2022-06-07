from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.db import connection
from arches.app.utils.decorators import user_created_transaction_match
from arches.app.utils.transaction import reverse_edit_log_entries
import logging

logger = logging.getLogger(__name__)


class BaseImportModule(object):
    @method_decorator(user_created_transaction_match, name="dispatch")
    def reverse(self, request, **kwargs):
        success = False
        response = {"success": success, "data": ""}
        loadid = self.loadid if self.loadid else request.POST.get("loadid")
        try:
            with connection.cursor() as cursor:
                print("updating load event status")
                cursor.execute(
                    """UPDATE load_event SET status = %s WHERE loadid = %s""",
                    ("reversing", loadid),
                )
                response["changes"] = reverse_edit_log_entries(loadid)
                success = True
                cursor.execute(
                    """UPDATE load_event SET status = %s WHERE loadid = %s""",
                    ("unloaded", loadid),
                )
            response["success"] = success
        except Exception as e:
            response["data"] = e
            logger.error(e)
        logger.warn(response)
        return response
