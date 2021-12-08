import logging
from django.views.generic import View

logger = logging.getLogger(__name__)

class ImportSingleCsvView(View):
    def validate(self, request):
        pass
    