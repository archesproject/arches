import json
import logging
# from django.core.exceptions import ObjectDoesNotExist
# from django.db import transaction
# from django.utils.translation import ugettext as _
from django.views.generic import View
from arches.app.models.models import ETLModule
# from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.response import JSONResponse

logger = logging.getLogger(__name__)

class ETLManagerView(View):
    """
    to get the ETL modules from db
    """
    def get(self, request):
        etlmodules = ETLModule.objects.all()
        print(etlmodules)
        return JSONResponse(etlmodules)

    def post(self, request):
        """
        instantiate the proper module and pass the request 
        """
        pass
