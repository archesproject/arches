from django.utils.translation import get_language

from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase


class LanguageViewWithRequestLanguage(APIBase):
    def get(self, request):
        languages = models.Language.objects.all()
        serializedLanguages = JSONSerializer().serializeToPython(languages)
        return JSONResponse(
            {
                "languages": serializedLanguages,
                "request_language": get_language(),
            }
        )
