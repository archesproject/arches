from django.views.generic import View

from arches.app.models import models
from arches.app.utils.response import JSONResponse


class Plugins(View):
    def get(self, request, plugin_id=None):
        if plugin_id:
            plugins = models.Plugin.objects.filter(pk=plugin_id)
        else:
            plugins = models.Plugin.objects.all()

        plugins = [
            plugin
            for plugin in plugins
            if self.request.user.has_perm("view_plugin", plugin)
        ]

        return JSONResponse(plugins)
