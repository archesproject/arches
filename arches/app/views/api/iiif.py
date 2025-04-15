import uuid

from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils.translation import gettext as _

from arches.app.models import models
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase


class IIIFManifest(APIBase):
    def get(self, request):
        query = request.GET.get("query", None)
        start = int(request.GET.get("start", 0))
        limit = request.GET.get("limit", None)
        more = False

        manifests = models.IIIFManifest.objects.all()
        if query is not None:
            manifests = manifests.filter(
                Q(label__icontains=query) | Q(description__icontains=query)
            )
        count = manifests.count()
        if limit is not None:
            manifests = manifests[start : start + int(limit)]
            more = start + int(limit) < count

        response = JSONResponse({"results": manifests, "count": count, "more": more})
        return response


class IIIFAnnotations(APIBase):
    def get(self, request):
        canvas = request.GET.get("canvas", None)
        resourceid = request.GET.get("resourceid", None)
        nodeid = request.GET.get("nodeid", None)
        permitted_nodegroups = get_nodegroups_by_perm(
            request.user, "models.read_nodegroup"
        )
        annotations = models.VwAnnotation.objects.filter(
            nodegroup__in=permitted_nodegroups
        )
        if canvas is not None:
            annotations = annotations.filter(canvas=canvas)
        if resourceid is not None:
            annotations = annotations.filter(resourceinstance_id=resourceid)
        if nodeid is not None:
            annotations = annotations.filter(node_id=nodeid)
        return JSONResponse(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": annotation.feature["id"],
                        "geometry": annotation.feature["geometry"],
                        "properties": {
                            **annotation.feature["properties"],
                            **{
                                "nodeId": annotation.node_id,
                                "nodegroupId": annotation.nodegroup_id,
                                "resourceId": annotation.resourceinstance_id,
                                "graphId": annotation.node.graph_id,
                                "tileId": annotation.tile_id,
                            },
                        },
                    }
                    for annotation in annotations
                ],
            }
        )


class IIIFAnnotationNodes(APIBase):
    def get(self, request, indent=None):
        permitted_nodegroups = get_nodegroups_by_perm(
            request.user, "models.read_nodegroup"
        )
        annotation_nodes = models.Node.objects.filter(
            nodegroup__in=permitted_nodegroups, datatype="annotation"
        )
        return JSONResponse(
            [
                {
                    **model_to_dict(node),
                    "graph_name": node.graph.name,
                    "icon": node.graph.iconclass,
                }
                for node in annotation_nodes
            ]
        )


class Manifest(APIBase):
    def get(self, request, id):
        try:
            uuid.UUID(id)
            manifest = models.IIIFManifest.objects.get(globalid=id).manifest
            return JSONResponse(manifest)
        except:
            manifest = models.IIIFManifest.objects.get(id=id).manifest
            return JSONResponse(manifest)
