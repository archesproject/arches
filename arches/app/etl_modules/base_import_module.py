from datetime import datetime
import os
from django.core.files.storage import default_storage
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.db import connection
from arches.app.utils.decorators import user_created_transaction_match
from arches.app.utils.transaction import reverse_edit_log_entries
import arches.app.tasks as tasks
import arches.app.utils.task_management as task_management
import logging

logger = logging.getLogger(__name__)


class BaseImportModule(object):
    def reverse_load(self, loadid):
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET status = %s WHERE loadid = %s""",
                ("reversing", loadid),
            )
            resources_changed_count = reverse_edit_log_entries(loadid)
            cursor.execute(
                """UPDATE load_event SET status = %s, load_details = load_details::jsonb || ('{"resources_removed":' || %s || '}')::jsonb WHERE loadid = %s""",
                ("unloaded", resources_changed_count, loadid),
            )

    @method_decorator(user_created_transaction_match, name="dispatch")
    def reverse(self, request, **kwargs):
        success = False
        response = {"success": success, "data": ""}
        loadid = self.loadid if self.loadid else request.POST.get("loadid")
        try:
            if task_management.check_if_celery_available():
                logger.info(_("Delegating load reversal to Celery task"))
                tasks.reverse_etl_load.apply_async([loadid])
            else:
                self.reverse_load(loadid)
            response["success"] = True
        except Exception as e:
            response["data"] = e
            logger.error(e)
        logger.warn(response)
        return response

    def load_data_async(self, request):
        if task_management.check_if_celery_available():
            logger.info(_("Delegating load to Celery task"))
            self.run_load_task_async(request)
            result = _("delegated_to_celery")
            return {"success": True, "data": result}
        else:
            err = _("Unable to perform this operation because Celery does not appear to be running. Please contact your administrator.")
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("failed", datetime.now(), self.loadid),
                )
            return {"success": False, "data": {"title": _("Error"), "message": err}}

    def delete_from_default_storage(self, directory):
        dirs, files = default_storage.listdir(directory)
        for dir in dirs:
            dir_path = os.path.join(directory, dir)
            self.delete_from_default_storage(dir_path)
        for file in files:
            file_path = os.path.join(directory, file)
            default_storage.delete(file_path)
        default_storage.delete(directory)

    def get_validation_result(self, loadid):
        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM __arches_load_staging_report_errors(%s)""", [loadid])
            rows = cursor.fetchall()
        return rows

    def prepare_data_for_loading(self, datatype_instance, source_value, config):
        try:
            value = datatype_instance.transform_value_for_tile(source_value, **config) if source_value else None
        except:
            value = source_value
        try:
            errors =[]
            if value is not None:
                errors = datatype_instance.validate(value, **config)
        except:
            message = "Unexpected Error Occurred"
            title = "Invalid {} Format".format(datatype_instance.datatype_name)
            errors = [datatype_instance.create_error_message(value, "", "", message, title)]

        return value, errors
