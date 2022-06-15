import logging
from django.db import connection
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.views.generic import View
from arches.app.models.models import ETLModule, LoadEvent, LoadStaging
from arches.app.utils.pagination import get_paginator
from arches.app.utils.response import JSONResponse, JSONErrorResponse

logger = logging.getLogger(__name__)


class ETLManagerView(View):
    """
    to get the ETL modules from db
    """

    def validate(self, loadid):
        """
        Creates records in the load_staging table (validated before poulating the load_staging table with error message)
        Collects error messages if any and returns table of error messages
        """

        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM __arches_load_staging_report_errors(%s)""", [loadid])
            rows = cursor.fetchall()
        return {"success": True, "data": rows}

    def clean_load_event(self, loadid):
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM load_staging WHERE loadid = %s""", [loadid])
            cursor.execute("""DELETE FROM load_event WHERE loadid = %s""", [loadid])
        return {"success": True, "data": ""}

    def get(self, request):
        action = request.GET.get("action", None)
        loadid = request.GET.get("loadid", None)
        page = int(request.GET.get("page", 1))
        if action == "modules" or action is None:
            response = []
            for module in ETLModule.objects.all():
                show = False if "show" in module.config.keys() and module.config["show"] is False else True
                if self.request.user.has_perm("view_etlmodule", module) and show:
                    response.append(module)
        elif action == "loadEvent":
            item_per_page = 5
            all_events = LoadEvent.objects.all().order_by(("-load_start_time")).prefetch_related("user", "etl_module")
            events = Paginator(all_events, item_per_page).page(page).object_list
            total = len(all_events)
            paginator, pages = get_paginator(request, all_events, total, page, item_per_page)
            page = paginator.page(page)

            response = {
                "events": [
                    {**model_to_dict(event), "user": {**model_to_dict(event.user)}, "etl_module": {**model_to_dict(event.etl_module)}}
                    for event in events
                ]
            }
            response["paginator"] = {}
            response["paginator"]["current_page"] = page.number
            response["paginator"]["has_next"] = page.has_next()
            response["paginator"]["has_previous"] = page.has_previous()
            response["paginator"]["has_other_pages"] = page.has_other_pages()
            response["paginator"]["next_page_number"] = page.next_page_number() if page.has_next() else None
            response["paginator"]["previous_page_number"] = page.previous_page_number() if page.has_previous() else None
            response["paginator"]["start_index"] = page.start_index()
            response["paginator"]["end_index"] = page.end_index()
            response["paginator"]["pages"] = pages

        elif action == "stagedData" and loadid:
            response = LoadStaging.objects.get(loadid=loadid)
        elif action == "validate" and loadid:
            response = self.validate(loadid)
        elif action == "cleanEvent" and loadid:
            response = self.clean_load_event(loadid)
        return JSONResponse(response)

    def post(self, request):
        """
        instantiate the proper module with proper action and pass the request
        possible actions are "import", "validate", "return first line", ""
        """
        action = request.POST.get("action")
        moduleid = request.POST.get("module")
        import_module = ETLModule.objects.get(pk=moduleid).get_class_module()(request)
        import_function = getattr(import_module, action)
        response = import_function(request=request)
        if response["success"] and "raw" not in response:
            ret = {"result": response["data"]}
            return JSONResponse(ret)
        elif response["success"] and "raw" in response:
            return response["raw"]
        else:
            return JSONErrorResponse(content=response)
