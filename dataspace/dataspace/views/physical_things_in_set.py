from django.views.generic import View
from arches.app.utils.response import JSONResponse
from arches.app.models import models
from arches.app.views.search import search_results
from django.http import HttpRequest
import json

class PhysicalThingSetView(View):
    def get(self, request):
        # via an id for a set, returns list of phys things and stuff necessary
        set_resourceid = (
            None if request.GET.get("resourceid") == "" or request.GET.get("resourceid") is None else (request.GET.get("resourceid"))
        )
        nodegroupid = request.GET.get("nodegroupid")
        nodeid = request.GET.get("nodeid")
        related = []
        results = []
        tiles = models.TileModel.objects.filter(resourceinstance_id=set_resourceid).filter(nodegroup_id=nodegroupid)
        if len(tiles) > 0:
            tile = tiles[0]
            related = tile.data[nodeid]
        for related_resource_item in related:
            search_request = HttpRequest()
            search_request.user = request.user
            search_request.GET["id"] = related_resource_item["resourceId"]
            result = json.loads(search_results(search_request).content)
            results.append(result["results"]["hits"]["hits"][0])

        return JSONResponse({"items": results})
