import logging

from django.utils.translation import gettext as _
from django.views.generic import View

logger = logging.getLogger(__name__)


class APIBase(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            get_params = request.GET.copy()
            accept = request.META.get("HTTP_ACCEPT")
            format = request.GET.get("format", False)
            format_values = {
                "application/ld+json": "json-ld",
                "application/json": "json",
                "application/xml": "xml",
            }
            if not format and accept in format_values:
                get_params["format"] = format_values[accept]
            for key, value in request.META.items():
                if key.startswith("HTTP_X_ARCHES_"):
                    if key.replace("HTTP_X_ARCHES_", "").lower() not in request.GET:
                        get_params[key.replace("HTTP_X_ARCHES_", "").lower()] = value
            get_params._mutable = False
            request.GET = get_params

        except Exception:
            logger.exception(_("Failed to create API request"))

        return super().dispatch(request, *args, **kwargs)
