import csv
from datetime import datetime
import io
from importlib import import_module
import json
import logging
import uuid
from django.db import connection
from django.db.models.functions import Lower
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import GraphModel, Node, NodeGroup, ResourceInstance
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile
from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.index_database import index_resources_by_transaction

logger = logging.getLogger(__name__)


class ImportSingleCsv:
    def __init__(self, request=None):
        self.request = request
        self.userid = request.user.id
        self.loadid = request.POST.get("load_id")
        self.datatype_factory = DataTypeFactory()
        self.node_lookup = {}
        self.blank_tile_lookup = {}

    def get_graphs(self, request):
        graphs = (
            GraphModel.objects.all()
            .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(isresource=False)
            .exclude(isactive=False)
            .order_by(Lower("name"))
        )
        return {"success": True, "data": graphs}

    def get_nodes(self, request):
        """
        Only returing nodes that belong to the top cards at the moment
        """

        def is_top_nodegroup(nodegroupid):
            return NodeGroup.objects.get(nodegroupid=nodegroupid).parentnodegroup is None

        graphid = request.POST.get("graphid")
        nodes = Node.objects.filter(graph_id=graphid).exclude(datatype__in=["semantic"]).order_by(Lower("name"))
        filteredNodes = []
        for node in nodes:
            if is_top_nodegroup(node.nodegroup_id):
                filteredNodes.append(node)
        return {"success": True, "data": filteredNodes}

    def get_node_lookup(self, graphid):
        if graphid not in self.node_lookup.keys():
            self.node_lookup[graphid] = Node.objects.filter(graph_id=graphid)
        return self.node_lookup[graphid]

    def read(self, request):
        """
        Reads added csv file and turn csv.reader or csv.DictReader object
        Reuiqres csv file and a flag indicating there is a header (can be handled in the front-end)
        Returns the reader object to display in a mapper && in a preview display
        """

        file = request.FILES.get("file")
        csvfile = file.read().decode("utf-8")
        reader = csv.reader(io.StringIO(csvfile))  # returns iterator
        data = [line for line in reader]
        return {"success": True, "data": data}

    def delete_staging_db(self):
        """
        when import is done the database should be deleted
        """
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE etl_staging;")

    def validate(self, request):
        """
        Validate the csv file and return true / false
        User mapping is required
        Instantiate datatypes and validate the datatype?
        """

        fieldnames = request.POST.get("fieldnames").split(",")
        column_names = [fieldname for fieldname in fieldnames if fieldname != ""]
        if len(column_names) == 0:
            message = "No valid node is selected"
            return {"success": False, "error": message}

        self.populate_staging_table(request)
        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM __arches_load_staging_report_errors(%s)""", [self.loadid])
            rows = cursor.fetchall()
        return {"success": True, "data": rows}

    def write(self, request):
        graphid = request.POST.get("graphid")
        with connection.cursor() as cursor:
            cursor.execute("""CALL __arches_staging_to_tile(%s, %s)""", [self.loadid, graphid])
            cursor.execute("""SELECT complete, successful FROM load_event WHERE loadid = %s""", [self.loadid])
            row = cursor.fetchall()

        # index_resources_by_transaction(self.loadid, quiet=True, use_multiprocessing=True)
        result = {"complete": row[0][0], "successful": row[0][1]}
        if result["complete"] and result["successful"]:
            return {"success": True, "data": result}
        else:
            return {"success": False, "data": result}

    def clear_staging_table(self, loadid):
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM load_staging WHERE loadid = %s""", [self.loadid])
            cursor.execute("""DELETE FROM load_event WHERE loadid = %s""", [self.loadid])

    def populate_staging_table(self, request):
        """
        Runs the actual import
        Returns done
        Must be a transaction
        Will sys.exit() work for stop in the middle of importing?
        """

        file = request.FILES.get("file")
        header = request.POST.get("header")
        graphid = request.POST.get("graphid")
        fieldnames = request.POST.get("fieldnames").split(",")
        csvfile = file.read().decode("utf-8")

        reader = csv.DictReader(io.StringIO(csvfile), fieldnames=fieldnames)
        if header:
            next(reader)

        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO load_event (loadid, complete, user_id) VALUES (%s, %s, %s)""", (self.loadid, False, self.userid))

        for row in reader:
            resourceid = uuid.uuid4()
            dict_by_nodegroup = {}

            for key in row:
                current_node = self.get_node_lookup(graphid).get(alias=key)
                nodegroupid = str(current_node.nodegroup_id)
                node = str(current_node.nodeid)
                datatype = self.node_lookup[graphid].get(nodeid=node).datatype
                datatype_instance = self.datatype_factory.get_instance(datatype)
                source_value = row[key]
                error = datatype_instance.validate(source_value)
                valid = True if len(error) == 0 else False
                notes = None if valid else error[0]["message"]
                value = datatype_instance.transform_value_for_tile(source_value) if source_value is not None and valid else None

                if nodegroupid in dict_by_nodegroup:
                    dict_by_nodegroup[nodegroupid].append(
                        {node: {"value": value, "valid": valid, "source": source_value, "notes": notes, "datatype": datatype}}
                    )
                else:
                    dict_by_nodegroup[nodegroupid] = [
                        {node: {"value": value, "valid": valid, "source": source_value, "notes": notes, "datatype": datatype}}
                    ]

            for nodegroup in dict_by_nodegroup:
                tile_data = self.get_blank_tile_lookup(nodegroup)
                passes_validation = True
                for node in dict_by_nodegroup[nodegroup]:
                    for key in node:
                        tile_data[key] = node[key]
                        if node[key]["valid"] is False:
                            passes_validation = False

                tile_value_json = JSONSerializer().serialize(tile_data)
                node_depth = 0

                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO load_staging (
                            nodegroupid, resourceid, value, loadid, nodegroup_depth, source_description, passes_validation
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (nodegroup, resourceid, tile_value_json, self.loadid, node_depth, file.name, passes_validation),
                    )

        message = "staging table populated"
        return {"success": True, "data": message}

    def get_blank_tile_lookup(self, nodegroupid):
        if nodegroupid not in self.blank_tile_lookup.keys():
            self.blank_tile_lookup[nodegroupid] = {}
            with connection.cursor() as cursor:
                cursor.execute("""SELECT nodeid FROM nodes WHERE datatype <> 'semantic' AND nodegroupid = %s;""", [nodegroupid])
                for row in cursor.fetchall():
                    (nodeid,) = row
                    self.blank_tile_lookup[nodegroupid][str(nodeid)] = None
        return self.blank_tile_lookup[nodegroupid]
