import json
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.translation import ugettext as _
from django.views.generic import View
from arches.app.models.tile import Tile
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.response import JSONResponse

logger = logging.getLogger(__name__)


class UpdateResourceListView(View):
    """
    Originally created to support add-things-step in new project workflow
    But it can be used to add/remove a related resource to/from a resource-instance-list nodegroup
    without creating/deleting a new tile

    The request body should look like this
    {
        relatedresourceid: related resourceid to be added or removed,
        nodegroupid : nodegroup_id where the rr_resource is added,
        nodeid : node_id where the rr_resource is added,
        transactionid: transaction_id if a part of workflow,
        data: [{
            resourceid: resourceid of resource to be edited,
            tileid: tileid of resource to be edited if available,
            action: 'add' or 'remove'
        }]
    }
    """

    def post(self, request):
        member_of_set_nodegroup_id = "63e49254-c444-11e9-afbe-a4d18cec433a"

        related_resource_id = request.POST.get("relatedresourceid")
        data = JSONDeserializer().deserialize(request.POST.get("data"))
        nodegroup_id = request.POST.get("nodegroupid", member_of_set_nodegroup_id)
        node_id = request.POST.get("node_id", member_of_set_nodegroup_id)
        transaction_id = request.POST.get("transactionid", None)

        try:
            with transaction.atomic():
                for datum in data:
                    action = datum["action"]
                    resource_id = datum["resourceid"] if "resourceid" in datum else None
                    tile_id = datum["tileid"] if "tileid" in datum else None

                    related_resource_template = {
                        "resourceId": "",
                        "ontologyProperty": "",
                        "resourceXresourceId": "",
                        "inverseOntologyProperty": "",
                    }

                    if tile_id is not None:
                        tile = Tile.objects.get(pk=tile_id)
                    else:
                        try:
                            tile = Tile.objects.get(resourceinstance=resource_id, nodegroup=nodegroup_id)
                        except ObjectDoesNotExist as e:
                            tile = Tile.get_blank_tile(nodeid=node_id, resourceid=resource_id)
                            tile.data[node_id] = []

                    list_of_rr_resources = [data["resourceId"] for data in tile.data[node_id]]

                    if related_resource_id not in list_of_rr_resources and action == "add":
                        related_resource_template["resourceId"] = related_resource_id
                        tile.data[node_id].append(related_resource_template)
                        tile.save(transaction_id=transaction_id)
                    elif related_resource_id in list_of_rr_resources and action == "remove":
                        rr_data = tile.data[node_id]
                        tile.data[node_id] = [rr for rr in rr_data if rr["resourceId"] != related_resource_id]
                        tile.save(transaction_id=transaction_id)

                return JSONResponse({"result": "success"})

        except Exception as e:
            logger.exception(e)
            response = {"result": "failed", "message": [_("Request Failed"), _("Unable to save")]}
            return JSONResponse(response, status=500)
