import csv
import io
from importlib import import_module
import json
import logging
import uuid
from django.db.models.functions import Lower
from arches.app.models.models import GraphModel, Node, NodeGroup, ResourceInstance
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse

logger = logging.getLogger(__name__)


class ImportSingleCsv:
    def __init__(self, request=None):
        self.request = request

    def get_graphs(self, request):
        print("getting graphs")
        graphs = (
            GraphModel.objects.all()
            .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(isresource=False)
            .exclude(isactive=False)
            .order_by(Lower("name"))
        )
        return graphs

    def get_nodes(self, request):
        """
        Only returing nodes that belong to the top cards at the moment
        """

        def is_top_nodegroup(nodegroupid):
            return NodeGroup.objects.get(nodegroupid=nodegroupid).parentnodegroup == None

        print("getting top nodes")
        graphid = request.POST.get("graphid")
        nodes = Node.objects.filter(graph_id=graphid).exclude(datatype__in=["semantic"]).order_by(Lower("name"))
        filteredNodes = []
        for node in nodes:
            if is_top_nodegroup(node.nodegroup_id):
                filteredNodes.append(node)
        return filteredNodes

    def read(self, request):
        """
        Reads added csv file and turn csv.reader or csv.DictReader object
        Reuiqres csv file and a flag indicating there is a header (can be handled in the front-end)
        Returns the reader object to display in a mapper && in a preview display
        """
        print("reading")
        file = request.FILES.get("file")
        csvfile = file.read().decode("utf-8")
        reader = csv.reader(io.StringIO(csvfile))  # returns iterator
        data = [line for line in reader]
        return data

    def validate(self, request):
        """
        Validate the csv file and return true / false
        User mapping is required
        Instantiate datatypes and validate the datatype?
        """
        print("validating")
        try:
            success = True
            message = "Everything looks good"
        except:
            success = False
            message = "There was an error"
        return JSONResponse({"success": False, "message": message})

    def write(self, request):
        """
        Runs the actual import
        Returns done
        Must be a transaction
        Will sys.exit() work for stop in the middle of importing?
        """
        print("writing")
        file = request.FILES.get("file")
        header = request.POST.get("header")
        graphid = request.POST.get("graphid")
        fieldnames = request.POST.get("fieldnames").split(",")
        csvfile = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(csvfile), fieldnames=fieldnames)
        if header:
            next(reader)

        # for debugging purpose if you have to store the data
        # data = [line for line in reader]
        # if header:
        #     data.pop(0)
        # for row in data:

        for row in reader:
            resource = Resource()
            resource.graph_id = graphid
            resource.save()
            dict_by_nodegroup = {}
            for key in row:
                nodegroupid = str(Node.objects.get(nodeid=key).nodegroup_id)
                if nodegroupid in dict_by_nodegroup:
                    dict_by_nodegroup[nodegroupid].append({key: row[key]})  # data structure here is weird thus line 105
                else:
                    dict_by_nodegroup[nodegroupid] = [{key: row[key]}]

            for nodegroup in dict_by_nodegroup:
                tile = Tile.get_blank_tile_from_nodegroup_id(nodegroup)
                tile.resourceinstance_id = resource.pk
                for node in dict_by_nodegroup[nodegroup]:
                    for key in node:
                        tile.data[key] = node[key]
                tile.save()

        return True  # what would be the right thing to return
