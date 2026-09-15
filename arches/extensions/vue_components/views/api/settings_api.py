from django.views.generic import View

from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse


class SettingsAPI(View):
    def get(self, request):
        return JSONResponse(
            {
                "force_script_name": settings.FORCE_SCRIPT_NAME or "",
            }
        )
