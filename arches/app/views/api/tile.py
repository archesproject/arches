import json
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt


from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.models.tile import Tile as TileProxyModel
from arches.app.utils.permission_backend import (
    get_nodegroups_by_perm,
    user_can_read_resource,
    user_can_edit_resource,
)
from arches.app.utils.decorators import group_required
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
        if not user_can_read_resource(request.user, tile.resourceinstance_id):
            return JSONResponse(_("User not permitted to read resource"), status=403)
        if tile.nodegroup_id in permitted_nodegroups:
            return JSONResponse(tile, status=200)
        else:
            return JSONResponse(_("Tile not found."), status=404)

    def post(self, request, tileid):
        data = request.POST.get("data") or request.body
        resourceid = json.loads(data).get("resourceinstance_id")
        # Important! The resource instance permission decorator on the TileView
        # will not be called by the instance of TileView below.
        # Resource edit perms must be checked here.
        if resourceid and models.ResourceInstance.objects.filter(pk=resourceid):
            if not user_can_edit_resource(request.user, resourceid):
                return JSONResponse(
                    _("User is not permitted to edit this resource"), status=403
                )
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
@method_decorator(
    group_required("Resource Editor", raise_exception=True), name="dispatch"
)
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

        try:
            node = models.Node.objects.get(nodeid=nodeid)
        except Exception as e:
            return JSONResponse(_("Node not found"), status=404)

        if not request.user.has_perm("write_nodegroup", node.nodegroup):
            return JSONResponse(
                _("User does not have permission to edit this node."), status=403
            )

        datatype = datatype_factory.get_instance(node.datatype)
        data = datatype.transform_value_for_tile(data, format=format)

        try:
            tile = models.TileModel.objects.get(tileid=tileid)
            if not user_can_edit_resource(request.user, tile.resourceinstance_id):
                return JSONResponse(
                    _("User is not permitted to edit this resource"), status=403
                )
            if operation == "append":
                data = datatype.update(tile, data, nodeid, action=operation)
        except (ObjectDoesNotExist, ValidationError):
            if (
                resourceid
                and models.ResourceInstance.objects.filter(pk=resourceid).exists()
            ):
                if not user_can_edit_resource(request.user, resourceid):
                    return JSONResponse(
                        _("User is not permitted to edit this resource"), status=403
                    )

        new_tile = TileProxyModel.update_node_value(
            nodeid,
            data,
            tileid,
            request=request,
            resourceinstanceid=resourceid,
            transaction_id=transaction_id,
        )

        return JSONResponse(new_tile, status=200)
