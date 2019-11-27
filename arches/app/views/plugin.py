"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.response import JSONResponse
from arches.app.views.base import MapBaseManagerView


class PluginView(MapBaseManagerView):
    action = None

    def get(self, request, pluginid=None, slug=None):
        if slug is not None:
            plugin = models.Plugin.objects.get(slug=slug)
        else:
            plugin = models.Plugin.objects.get(pk=pluginid)
        if not request.user.has_perm("view_plugin", plugin):
            return redirect("home")
        if request.GET.get("json", False):
            return JSONResponse(plugin)
        resource_graphs = (
            models.GraphModel.objects.exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(isresource=False)
            .exclude(isactive=False)
        )
        widgets = models.Widget.objects.all()
        card_components = models.CardComponent.objects.all()
        datatypes = models.DDataType.objects.all()
        map_layers = models.MapLayer.objects.all()
        map_markers = models.MapMarker.objects.all()
        map_sources = models.MapSource.objects.all()
        geocoding_providers = models.Geocoder.objects.all()
        templates = models.ReportTemplate.objects.all()

        context = self.get_context_data(
            plugin=plugin,
            plugin_json=JSONSerializer().serialize(plugin),
            main_script="views/plugin",
            resource_graphs=resource_graphs,
            widgets=widgets,
            widgets_json=JSONSerializer().serialize(widgets),
            card_components=card_components,
            card_components_json=JSONSerializer().serialize(card_components),
            datatypes_json=JSONSerializer().serialize(datatypes, exclude=["iconclass", "modulename", "classname"]),
            map_layers=map_layers,
            map_markers=map_markers,
            map_sources=map_sources,
            geocoding_providers=geocoding_providers,
            report_templates=templates,
            templates_json=JSONSerializer().serialize(templates, sort_keys=False, exclude=["name", "description"]),
        )

        context["nav"]["title"] = ""
        context["nav"]["menu"] = False
        context["nav"]["icon"] = plugin.icon
        context["nav"]["title"] = plugin.name

        return render(request, "views/plugin.htm", context)
