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


from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.models.resource import Resource
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.views.generic import TemplateView
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.permission_backend import get_createable_resource_types, user_is_resource_reviewer

class BaseManagerView(TemplateView):

    template_name = ""

    def get_context_data(self, **kwargs):
        context = super(BaseManagerView, self).get_context_data(**kwargs)
        context["system_settings_graphid"] = settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID
        context["graph_models"] = []
        context["graphs"] = "[]"
        context["plugins"] = []
        for plugin in models.Plugin.objects.all().order_by("sortorder"):
            if self.request.user.has_perm("view_plugin", plugin):
                context["plugins"].append(plugin)

        createable = get_createable_resource_types(self.request.user)
        createable.sort(key=lambda x: x.name.lower())
        context["createable_resources"] = JSONSerializer().serialize(
            createable,
            exclude=[
                "functions",
                "ontology",
                "isactive",
                "isresource",
                "version",
                "deploymentdate",
                "deploymentfile",
                "author",
            ],
        )

        context["notifications"] = models.UserXNotification.objects.filter(recipient=self.request.user, isread=False)
        context["nav"] = {
            "icon": "fa fa-chevron-circle-right",
            "title": "",
            "help": {
                # title:'',template:'' (leave this commented out)
            },
            "menu": False,
            "search": True,
            "notifs": True,
            "res_edit": False,
            "login": True,
            "print": False,
        }
        context["user_is_reviewer"] = user_is_resource_reviewer(self.request.user)
        context["app_name"] = settings.APP_NAME
        context["show_language_swtich"] = settings.SHOW_LANGUAGE_SWITCH
        return context


class MapBaseManagerView(BaseManagerView):
    def get_context_data(self, **kwargs):
        context = super(MapBaseManagerView, self).get_context_data(**kwargs)
        datatype_factory = DataTypeFactory()
        geom_datatypes = [d.pk for d in models.DDataType.objects.filter(isgeometric=True)]
        geom_nodes = models.Node.objects.filter(graph__isresource=True, graph__isactive=True, datatype__in=geom_datatypes).exclude(
            graph__graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID
        )
        resource_layers = []
        resource_sources = []
        for node in geom_nodes:
            if self.request.user.has_perm("read_nodegroup", node.nodegroup):
                datatype = datatype_factory.get_instance(node.datatype)
                map_source = datatype.get_map_source(node)
                if map_source is not None:
                    resource_sources.append(map_source)
                    map_layer = datatype.get_map_layer(node)
                    if map_layer is not None:
                        resource_layers.append(map_layer)

        context["geom_nodes"] = geom_nodes
        context["resource_map_layers"] = resource_layers
        context["resource_map_sources"] = resource_sources

        return context
