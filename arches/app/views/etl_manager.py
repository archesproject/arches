from celery import app, Celery
from datetime import datetime
from http import HTTPStatus
import logging
from django.db import connection
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import View
from arches.app.etl_modules.base_import_module import FileValidationError
from arches.app.models.models import ETLModule, LoadEvent, LoadStaging
from arches.app.utils.pagination import get_paginator
from arches.app.utils.decorators import group_required
from arches.app.utils.response import JSONResponse, JSONErrorResponse
import arches.app.utils.task_management as task_management

logger = logging.getLogger(__name__)


@method_decorator(
    group_required("Resource Editor", raise_exception=True), name="dispatch"
)
class ETLManagerView(View):
    """
    to get the ETL modules from db
    """

    def dictfetchall(self, cursor):
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def validate(self, loadid):
        """
        Creates records in the load_staging table (validated before poulating the load_staging table with error message)
        Collects error messages if any and returns table of error messages
        """

        with connection.cursor() as cursor:
            cursor.execute(
                """
                (SELECT n.name as source, e.error as error, n.datatype as datatype, count(n.name), e.type, e.nodeid
                FROM load_errors e
                JOIN nodes n ON e.nodeid = n.nodeid
                WHERE loadid = %s AND e.type = 'node'
                GROUP BY n.name, e.error, n.datatype, e.type, e.nodeid)
                UNION
                (SELECT n.name as source, e.error as error, e.datatype as datatype, count(n.name), e.type, e.nodegroupid
                FROM load_errors e
                JOIN nodes n ON e.nodegroupid = n.nodeid
                WHERE loadid = %s AND e.type = 'tile'
                GROUP BY n.name, e.error, e.datatype, e.type, e.nodegroupid)
                -- Add any errors that are neither node nor tile, e.g. early json-ld failures
                UNION
                (SELECT e.source, e.error, e.datatype, count(e.source), e.type, e.nodeid
                FROM load_errors e
                WHERE loadid = %s AND e.type NOT IN ('node', 'tile')
                GROUP BY e.source, e.error, e.datatype, e.type, e.nodeid);
            """,
                [loadid, loadid, loadid],
            )
            rows = self.dictfetchall(cursor)
        return {"success": True, "data": rows}

    def error_report(self, loadid):
        """
        Creates records in the load_staging table (validated before poulating the load_staging table with error message)
        Collects error messages if any and returns table of error messages
        """

        with connection.cursor() as cursor:
            cursor.execute(
                """
                -- SELECT n.name as node, e.error, e.message, e.value, e.source
                SELECT n.name as node, e.*
                FROM load_errors e
                JOIN nodes n ON n.nodeid = e.nodeid
                WHERE loadid = %s
                """,
                [loadid],
            )
            rows = self.dictfetchall(cursor)
        return {"success": True, "data": rows}

    def node_error(self, loadid, nodeid, error):
        """
        Creates records in the load_staging table (validated before poulating the load_staging table with error message)
        Collects error messages if any and returns table of error messages
        """

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT n.name as node, e.error, e.message, e.value, e.source, e.nodeid, e.nodegroupid
                FROM load_errors e
                JOIN nodes n ON n.nodeid = e.nodeid
                WHERE loadid = %s AND e.nodeid = %s AND e.error = %s
                """,
                [loadid, nodeid, error],
            )
            rows = self.dictfetchall(cursor)
        return {"success": True, "data": rows}

    def clean_load_event(self, loadid):
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM load_errors WHERE loadid = %s""", [loadid])
            cursor.execute("""DELETE FROM load_staging WHERE loadid = %s""", [loadid])
            cursor.execute("""DELETE FROM load_event WHERE loadid = %s""", [loadid])
        return {"success": True, "data": ""}

    def stop_loading(self, loadid):
        if task_management.check_if_celery_available():
            logger.info(_("Cancel Request sent to Celery"))
            load_event = LoadEvent.objects.get(loadid=loadid)
            taskid = load_event.taskid
            celery_app = Celery()
            remote_control = app.control.Control(app=celery_app)
            remote_control.revoke(task_id=taskid, terminate=True)
            # app.control.Control.revoke(task_id=taskid, terminate=True)
            result = _("Cancel Request sent to Celery")
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("cancelled", datetime.now(), loadid),
                )
            return {"success": True, "data": result}
        else:
            err = _(
                "Unable to perform this operation because Celery does not appear to be running. Please contact your administrator."
            )
            return {"success": False, "data": {"title": _("Error"), "message": err}}

    def get(self, request):
        action = request.GET.get("action", None)
        loadid = request.GET.get("loadid", None)
        nodeid = request.GET.get("nodeid", None)
        error = request.GET.get("error", None)
        page = int(request.GET.get("page", 1))
        if action == "modules" or action is None:
            response = []
            for module in ETLModule.objects.all():
                show = (
                    False
                    if "show" in module.config.keys() and module.config["show"] is False
                    else True
                )
                if self.request.user.has_perm("view_etlmodule", module) and show:
                    response.append(module)
        elif action == "loadEvent":
            item_per_page = 5
            all_events = (
                LoadEvent.objects.all()
                .order_by(("-load_start_time"))
                .select_related("user", "etl_module")
            )
            events = Paginator(all_events, item_per_page).page(page).object_list
            total = len(all_events)
            paginator, pages = get_paginator(
                request, all_events, total, page, item_per_page
            )
            page = paginator.page(page)

            response = {
                "events": [
                    {
                        **model_to_dict(event),
                        "user_displayname": self.format_username(event.user),
                        "etl_module": {**model_to_dict(event.etl_module)},
                    }
                    for event in events
                ]
            }
            response["paginator"] = {}
            response["paginator"]["current_page"] = page.number
            response["paginator"]["has_next"] = page.has_next()
            response["paginator"]["has_previous"] = page.has_previous()
            response["paginator"]["has_other_pages"] = page.has_other_pages()
            response["paginator"]["next_page_number"] = (
                page.next_page_number() if page.has_next() else None
            )
            response["paginator"]["previous_page_number"] = (
                page.previous_page_number() if page.has_previous() else None
            )
            response["paginator"]["start_index"] = page.start_index()
            response["paginator"]["end_index"] = page.end_index()
            response["paginator"]["pages"] = pages

        elif action == "stagedData" and loadid:
            response = LoadStaging.objects.get(loadid=loadid)
        elif action == "validate" and loadid:
            response = self.validate(loadid)
        elif action == "cleanEvent" and loadid:
            response = self.clean_load_event(loadid)
        elif action == "stop" and loadid:
            response = self.stop_loading(loadid)
        elif action == "nodeError" and loadid:
            response = self.node_error(loadid, nodeid, error)
        elif action == "errorReport" and loadid:
            return JSONResponse(self.error_report(loadid)["data"], indent=2)
        return JSONResponse(response)

    @staticmethod
    def format_username(user):
        parts = [part for part in (user.first_name, user.last_name) if part]
        if parts:
            return " ".join(parts)
        else:
            return user.username

    def post(self, request):
        """
        instantiate the proper module with proper action and pass the request
        possible actions are "write", "validate", "read", "start"
        """
        action = request.POST.get("action")
        moduleid = request.POST.get("module")
        import_module = ETLModule.objects.get(pk=moduleid).get_class_module()(
            request=request
        )
        import_function = getattr(import_module, action)
        response = import_function(request)
        if response["success"] and "raw" not in response:
            ret = {"result": response["data"]}
            return JSONResponse(ret)
        elif response["success"] and "raw" in response:
            return response["raw"]
        else:
            if (data := response.get("data")) and isinstance(data, FileValidationError):
                return JSONErrorResponse(content=response, status=data.code)
            return JSONErrorResponse(content=response)
