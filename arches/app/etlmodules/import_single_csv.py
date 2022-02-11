import csv
from datetime import datetime
import io
from importlib import import_module
import json
import logging
import uuid
from django.db import connection
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
            return NodeGroup.objects.get(nodegroupid=nodegroupid).parentnodegroup is None

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

    def drop_staging_db(self):
        """
        when import is done the database should be deleted
        """
        with connection.cursor() as cursor:
            cursor.execute('DROP TABLE etl_staging;')

    def validate(self, request):
        """
        Validate the csv file and return true / false
        User mapping is required
        Instantiate datatypes and validate the datatype?
        """
        print("validating")
        file = request.FILES.get("file")
        header = request.POST.get("header")
        graphid = request.POST.get("graphid")
        fieldnames = request.POST.get("fieldnames").split(",")
        csvfile = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(csvfile), fieldnames=fieldnames)
        if header:
            next(reader)

        column_names = [fieldname for fieldname in fieldnames if fieldname != '']
        if len(column_names) == 0:
            message = "No valid node is selected"
            return {"success": False, "message": message}  # what would be the right thing to return

        timestamp = int(datetime.now().timestamp())
        staging_table_name = 'etl_staging_{}'.format(timestamp)
        staging_table_name = 'etl_staging'

        with connection.cursor() as cursor:
            cursor.execute("CALL __arches_create_staging_db(%s);", [column_names])

        for row in reader:
            values = [row[column_name] for column_name in column_names]
            with connection.cursor() as cursor:
                cursor.execute("CALL __arches_populate_staging_db(%s, %s);", [column_names, values])

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM __arches_validate_staging_db(%s);", [graphid])
            result_table = cursor.fetchall()
            results = dict((row, message) for row, message in result_table)

        return {"results": results}

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
        column_names = [fieldname for fieldname in fieldnames if fieldname != '']
        if len(column_names):
            message = "No valid node is selected"
            return {"success": False, "message": message}  # what would be the right thing to return

        if header:
            next(reader)

        for row in reader:
            values = [row[column_name] for column_name in column_names]
            resource = Resource()
            resource.graph_id = graphid
            resource.save()
            dict_by_nodegroup = {}
            for key in values:
                current_node = Node.objects.filter(name=key).filter(graph_id=graphid)[0]
                nodegroupid = str(current_node.nodegroup_id)
                node = str(current_node.nodeid)
                if nodegroupid in dict_by_nodegroup:
                    dict_by_nodegroup[nodegroupid].append({node: row[key]})  # data structure here is weird thus line 105
                else:
                    dict_by_nodegroup[nodegroupid] = [{node: row[key]}]

            for nodegroup in dict_by_nodegroup:
                tile = Tile.get_blank_tile_from_nodegroup_id(nodegroup)
                tile.resourceinstance_id = resource.pk
                for node in dict_by_nodegroup[nodegroup]:
                    for key in node:
                        tile.data[key] = node[key]
                tile.save()

        message = "write succeeded"
        return {"success": True, "message": message}  # what would be the right thing to return
