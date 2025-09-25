import uuid

from django.db import connection
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from arches.app.models import models
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase


@method_decorator(csrf_exempt, name="dispatch")
class NodeGroup(APIBase):
    def get(self, request, nodegroupid=None):
        params = request.GET.dict()
        user = request.user
        perms = "models." + params.pop("perms", "read_nodegroup")
        params["nodegroupid"] = params.get("nodegroupid", nodegroupid)

        try:
            uuid.UUID(params["nodegroupid"])
        except ValueError as e:
            del params["nodegroupid"]

        try:
            nodegroup = models.NodeGroup.objects.get(pk=params["nodegroupid"])
            permitted_nodegroups = get_nodegroups_by_perm(user, perms)
        except Exception as e:
            return JSONResponse(str(e), status=404)

        if not nodegroup or nodegroup.pk not in permitted_nodegroups:
            return JSONResponse(
                _("No nodegroup matching query parameters found."), status=404
            )

        return JSONResponse(nodegroup, status=200)


class GetNodegroupTree(APIBase):
    """
    Returns the path to a nodegroup from the root node. Transforms node alias to node name.
    """

    def get(self, request):
        graphid = request.GET.get("graphid")
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM __get_nodegroup_tree_by_graph(%s)""", (graphid,)
            )
            result = cursor.fetchall()
            permitted_nodegroups = get_nodegroups_by_perm(
                request.user, "models.read_nodegroup"
            )
            permitted_result = [
                nodegroup
                for nodegroup in result
                if nodegroup[0] in permitted_nodegroups
            ]

        return JSONResponse({"path": permitted_result})
