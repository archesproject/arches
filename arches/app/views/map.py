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

from django.db import transaction
from django.shortcuts import render
from django.http import Http404
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from revproxy.views import ProxyView
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.models.card import Card
from arches.app.views.base import BaseManagerView, MapBaseManagerView
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.decorators import group_required
from arches.app.utils.response import JSONResponse
from arches.app.utils.permission_backend import (
    get_users_with_permission_for_object,
    get_groups_with_permission_for_object,
)
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Bool, GeoBoundsAgg, Term
from arches.app.search.mappings import RESOURCES_INDEX


@method_decorator(group_required("Application Administrator"), name="dispatch")
class MapLayerManagerView(MapBaseManagerView):
    def get(self, request):
        se = SearchEngineFactory().create()
        datatype_factory = DataTypeFactory()
        datatypes = models.DDataType.objects.all()
        widgets = models.Widget.objects.all()
        map_markers = models.MapMarker.objects.all()
        icons = models.Icon.objects.order_by("name")
        context = self.get_context_data(
            icons=JSONSerializer().serialize(icons),
            datatypes=datatypes,
            widgets=widgets,
            map_markers=map_markers,
            datatypes_json=JSONSerializer().serialize(datatypes),
            main_script="views/map-layer-manager",
        )

        def get_resource_bounds(node):
            query = Query(se, start=0, limit=0)
            search_query = Bool()
            query.add_query(search_query)
            query.add_aggregation(GeoBoundsAgg(field="points.point", name="bounds"))
            query.add_query(Term(field="graph_id", term=str(node.graph.graphid)))
            results = query.search(index=RESOURCES_INDEX)
            bounds = (
                results["aggregations"]["bounds"]["bounds"]
                if "bounds" in results["aggregations"]["bounds"]
                else None
            )
            return bounds

        context["geom_nodes_json"] = JSONSerializer().serialize(context["geom_nodes"])
        resource_layers = []
        resource_sources = []
        permissions = {}
        for node in context["geom_nodes"]:
            datatype = datatype_factory.get_instance(node.datatype)
            map_layer = datatype.get_map_layer(node=node, preview=True)
            if map_layer is not None:
                count = models.TileModel.objects.filter(
                    nodegroup_id=node.nodegroup_id, data__has_key=str(node.nodeid)
                ).count()
                if count > 0:
                    map_layer["bounds"] = get_resource_bounds(node)
                else:
                    map_layer["bounds"] = None
                resource_layers.append(map_layer)
            map_source = datatype.get_map_source(node=node, preview=True)
            if map_source is not None:
                resource_sources.append(map_source)
            permissions[str(node.pk)] = {
                "users": sorted(
                    [
                        user.email or user.username
                        for user in get_users_with_permission_for_object(
                            "read_nodegroup", node.nodegroup
                        )
                    ]
                ),
                "groups": sorted(
                    [
                        group.name
                        for group in get_groups_with_permission_for_object(
                            "read_nodegroup", node.nodegroup
                        )
                    ]
                ),
            }
        context["resource_map_layers_json"] = JSONSerializer().serialize(
            resource_layers
        )
        context["resource_map_sources_json"] = JSONSerializer().serialize(
            resource_sources
        )
        context["node_permissions"] = JSONSerializer().serialize(permissions)

        context["nav"]["title"] = _("Map Layer Manager")
        context["nav"]["icon"] = "fa-server"
        context["nav"]["help"] = {
            "title": _("Map Layer Manager"),
            "templates": ["map-manager-help"],
        }

        return render(request, "views/map-layer-manager.htm", context)

    def post(self, request, maplayerid):
        map_layer = models.MapLayer.objects.get(pk=maplayerid)
        data = JSONDeserializer().deserialize(request.body)
        map_layer.name = data["name"]
        map_layer.icon = data["icon"]
        map_layer.activated = data["activated"]
        map_layer.addtomap = data["addtomap"]
        map_layer.layerdefinitions = data["layer_definitions"]
        map_layer.centerx = data["centerx"]
        map_layer.centery = data["centery"]
        map_layer.zoom = data["zoom"]
        map_layer.legend = data["legend"]
        map_layer.searchonly = data["searchonly"]
        map_layer.sortorder = data["sortorder"]
        map_layer.ispublic = data["ispublic"]
        with transaction.atomic():
            map_layer.save()
            if not map_layer.isoverlay and map_layer.addtomap:
                models.MapLayer.objects.filter(isoverlay=False).exclude(
                    pk=map_layer.pk
                ).update(addtomap=False)
        return JSONResponse({"success": True, "map_layer": map_layer})

    def delete(self, request, maplayerid):
        map_layer = models.MapLayer.objects.get(pk=maplayerid)
        with transaction.atomic():
            map_layer.delete()
        return JSONResponse({"succces": True})


class TileserverProxyView(ProxyView):
    upstream = settings.TILESERVER_URL

    def get_request_headers(self):
        headers = super(TileserverProxyView, self).get_request_headers()
        if settings.TILESERVER_URL is None:
            raise Http404(_("Tileserver proxy not configured"))
        return headers
