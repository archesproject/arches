import logging
from django.db import connection
from django.views.generic import View
from arches.app.models.models import ETLModule, LoadEvent, LoadStaging
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
        if action == "modules" or action is None:
            response = ETLModule.objects.all()
        elif action == "loadEvent":
            response = LoadEvent.objects.all()
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
        if response["success"]:
            ret = {"result": response["data"]}
            return JSONResponse(ret)
        else:
            return JSONErrorResponse(content=response)
