from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.models.tile import Tile as TileProxyModel
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase
from arches.app.views.tile import TileData as TileView


@method_decorator(csrf_exempt, name="dispatch")
class Tile(APIBase):
    def get(self, request, tileid):
        try:
            tile = models.TileModel.objects.get(tileid=tileid)
        except Exception as e:
            return JSONResponse(str(e), status=404)

        # filter tiles from attribute query based on user permissions
        permitted_nodegroups = get_nodegroups_by_perm(
            request.user, "models.read_nodegroup"
        )
        if tile.nodegroup_id in permitted_nodegroups:
            return JSONResponse(tile, status=200)
        else:
            return JSONResponse(_("Tile not found."), status=404)

    def post(self, request, tileid):
        tileview = TileView()
        tileview.action = "update_tile"
        # check that no data is on POST or FILES before assigning body to POST (otherwise request fails)
        if (
            len(dict(request.POST.items())) == 0
            and len(dict(request.FILES.items())) == 0
        ):
            request.POST = request.POST.copy()
            request.POST["data"] = request.body
        return tileview.post(request)


@method_decorator(csrf_exempt, name="dispatch")
class NodeValue(APIBase):
    def post(self, request):
        datatype_factory = DataTypeFactory()
        tileid = request.POST.get("tileid")
        nodeid = request.POST.get("nodeid")
        data = request.POST.get("data")
        resourceid = request.POST.get("resourceinstanceid", None)
        format = request.POST.get("format")
        operation = request.POST.get("operation")
        transaction_id = request.POST.get("transaction_id")

        # get node model return error if not found
        try:
            node = models.Node.objects.get(nodeid=nodeid)
        except Exception as e:
            return JSONResponse(e, status=404)

        # check if user has permissions to write to node
        user_has_perms = request.user.has_perm("write_nodegroup", node.nodegroup)
        if user_has_perms:
            # get datatype of node
            try:
                datatype = datatype_factory.get_instance(node.datatype)
            except Exception as e:
                return JSONResponse(e, status=404)

            # transform data to format expected by tile
            data = datatype.transform_value_for_tile(data, format=format)

            # get existing data and append new data if operation='append'
            if operation == "append":
                tile = models.TileModel.objects.get(tileid=tileid)
                data = datatype.update(tile, data, nodeid, action=operation)

            # update/create tile
            new_tile = TileProxyModel.update_node_value(
                nodeid,
                data,
                tileid,
                request=request,
                resourceinstanceid=resourceid,
                transaction_id=transaction_id,
            )

            response = JSONResponse(new_tile, status=200)
        else:
            response = JSONResponse(
                _("User does not have permission to edit this node."), status=403
            )

        return response
