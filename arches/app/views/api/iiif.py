import json
import uuid

from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils.translation import gettext as _

from arches.app.models import models
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase

# Enough for the largest manifests we have seen, small enough to keep a
# single request cheap: the viewer chunks its requests to stay under this.
MAX_CANVASES_PER_BATCH = 500


def annotation_to_feature(annotation):
    return {
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
                    annotation_to_feature(annotation) for annotation in annotations
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


class IIIFAnnotationsBatch(APIBase):
    """Return the annotations of several canvases in a single request.

    The IIIF viewer needs the annotations of every canvas of a manifest, for
    every annotation node. Fetching them from IIIFAnnotations costs one request
    per canvas and per node, which is slow on manifests holding many canvases.

    The canvases are read from the request body rather than the query string
    because canvas ids are URLs: a few hundred of them do not fit in a URL.
    """

    def post(self, request):
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JSONResponse(
                {"error": _("Request body is not valid JSON")}, status=400
            )

        if not isinstance(body, dict):
            return JSONResponse(
                {"error": _("Request body must be a JSON object")}, status=400
            )

        canvases = body.get("canvases")
        if not isinstance(canvases, list):
            return JSONResponse({"error": _("canvases must be an array")}, status=400)

        canvases = [
            canvas.strip()
            for canvas in canvases
            if isinstance(canvas, str) and canvas.strip()
        ]
        if not canvases:
            return JSONResponse(
                {"error": _("canvases must hold at least one canvas id")}, status=400
            )
        if len(canvases) > MAX_CANVASES_PER_BATCH:
            return JSONResponse(
                {
                    "error": _("canvases must hold at most {} canvas ids").format(
                        MAX_CANVASES_PER_BATCH
                    )
                },
                status=400,
            )

        permitted_nodegroups = get_nodegroups_by_perm(
            request.user, "models.read_nodegroup"
        )
        annotations = models.VwAnnotation.objects.filter(
            nodegroup__in=permitted_nodegroups, canvas__in=canvases
        ).select_related("node")

        canvases_with_annotations = {}
        for annotation in annotations:
            feature_collection = canvases_with_annotations.setdefault(
                annotation.canvas, {"type": "FeatureCollection", "features": []}
            )
            feature_collection["features"].append(annotation_to_feature(annotation))

        return JSONResponse(
            {
                "type": "AnnotationsByCanvas",
                "canvases": canvases_with_annotations,
                "total_annotations": sum(
                    len(feature_collection["features"])
                    for feature_collection in canvases_with_annotations.values()
                ),
                "total_canvases": len(canvases_with_annotations),
            }
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
