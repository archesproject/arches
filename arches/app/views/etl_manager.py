import logging
from django.http import HttpResponse
from django.views.generic import View
from arches.app.models.models import ETLModule
from arches.app.utils.response import JSONResponse, JSONErrorResponse

logger = logging.getLogger(__name__)


class ETLManagerView(View):
    """
    to get the ETL modules from db
    """

    def get(self, request):
        etl_modules = ETLModule.objects.all()
        return JSONResponse(etl_modules)

    def post(self, request):
        """
        instantiate the proper module with proper action and pass the request
        possible actions are "import", "validate", "return first line", ""
        """
        action = request.POST.get("action")
        module = request.POST.get("module")
        import_module = ETLModule.objects.get(pk=module).get_class_module()(request)
        import_function = getattr(import_module, action)
        response = import_function(request=request)
        if response["success"] and "raw" not in response:
            ret = {"result": response["data"]}
            return JSONResponse(ret)
        elif response["success"] and "raw" in response:
            return response["raw"]
        else:
            return JSONErrorResponse(content=response)
