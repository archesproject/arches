import uuid

from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase


@method_decorator(csrf_exempt, name="dispatch")
class Node(APIBase):
    def get(self, request, nodeid=None):
        graph_cache = {}
        params = request.GET.dict()
        user = request.user
        perms = "models." + params.pop("perms", "read_nodegroup")
        params["nodeid"] = params.get("nodeid", nodeid)
        try:
            uuid.UUID(params["nodeid"])
        except ValueError as e:
            del params["nodeid"]
        # parse node attributes from params
        # datatype = params.get("datatype")
        # description=params.get('description')
        # exportable=params.get('exportable')
        # fieldname=params.get('fieldname')
        # graph_id=params.get('graph_id')
        # is_collector=params.get('is_collector')
        # isrequired=params.get('isrequired')
        # issearchable=params.get('issearchable')
        # istopnode=params.get('istopnode')
        # name=params.get('name')
        # nodegroup_id=params.get('nodegroup_id')
        # nodeid=params.get('nodeid')
        # ontologyclass=params.get('ontologyclass')
        # sortorder=params.get('sortorder')

        def graphLookup(graphid):
            try:
                return graph_cache[graphid]
            except:
                graph_cache[graphid] = Graph.objects.get(pk=node["graph_id"]).name
                return graph_cache[graphid]

        # try to get nodes by attribute filter and then get nodes by passed in user perms
        try:
            nodes = models.Node.objects.filter(**dict(params)).values()
            permitted_nodegroups = get_nodegroups_by_perm(user, perms)
        except Exception as e:
            return JSONResponse(str(e), status=404)

        # check if any nodes were returned from attribute filter and throw error if none were returned
        if len(nodes) == 0:
            return JSONResponse(
                _("No nodes matching query parameters found."), status=404
            )

        # filter nodes from attribute query based on user permissions
        permitted_nodes = [
            node for node in nodes if node["nodegroup_id"] in permitted_nodegroups
        ]
        for node in permitted_nodes:
            try:
                node["resourcemodelname"] = graphLookup(node["graph_id"])
            except:
                return JSONResponse(
                    _("No graph found for graphid %s" % (node["graph_id"])), status=404
                )

        return JSONResponse(permitted_nodes, status=200)
