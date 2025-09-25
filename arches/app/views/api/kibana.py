import logging

from revproxy.views import ProxyView

from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse

logger = logging.getLogger(__name__)


class KibanaProxy(ProxyView):
    upstream = settings.KIBANA_URL

    def dispatch(self, request, path):
        try:
            path = f"{settings.KIBANA_CONFIG_BASEPATH}/{path}"
            return super(KibanaProxy, self).dispatch(request, path)
        except Exception:
            logger.exception(_("Failed to dispatch Kibana proxy"))

        return JSONResponse(_("KibanaProxy failed"), status=500)
