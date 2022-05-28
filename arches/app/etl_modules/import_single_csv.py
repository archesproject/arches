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
from arches.app.utils.index_database import index_resources_by_type
from arches.app.utils.index_database import index_resources_by_transaction

logger = logging.getLogger(__name__)


class ImportSingleCsv:
    def __init__(self, request=None):
        self.request = request
        self.userid = request.user.id
        self.loadid = request.POST.get("load_id")
        self.moduleid = request.POST.get("module")
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
        Reads added csv file and returns all the rows
        If the loadid already exsists also returns the load_details
        """

        file = request.FILES.get("file")
        csvfile = file.read().decode("utf-8")
        reader = csv.reader(io.StringIO(csvfile))
        data = {"csv": [line for line in reader]}
        with connection.cursor() as cursor:
            cursor.execute("""SELECT load_details FROM load_event WHERE loadid = %s""", [self.loadid])
            row = cursor.fetchall()
        if len(row) > 0:
            data["config"] = row[0][0]
        return {"success": True, "data": data}

    def validate(self, request):
        """
        Creates records in the load_staging table (validated before poulating the load_staging table with error message)
        Collects error messages if any and returns table of error messages
        """

        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM __arches_load_staging_report_errors(%s)""", [self.loadid])
            rows = cursor.fetchall()
        return {"success": True, "data": rows}

    def write(self, request):
        """
        Move the records from load_staging to tiles table using db function
        """

        fieldnames = request.POST.get("fieldnames").split(",")
        column_names = [fieldname for fieldname in fieldnames if fieldname != ""]
        if len(column_names) == 0:
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("failed", datetime.now(), self.loadid),
                )
            message = "No valid node is selected"
            return {"success": False, "data": message}

        self.populate_staging_table(request)

        validation = self.validate(request)
        if len(validation["data"]) != 0:
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("failed", datetime.now(), self.loadid),
                )
            return {"success": False, "data": "failed"}
        else:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT * FROM __arches_staging_to_tile(%s)""", [self.loadid])
                row = cursor.fetchall()
        if row[0][0]:
            index_resources_by_transaction(self.loadid, quiet=True, use_multiprocessing=True)
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE load_event SET status = %s WHERE loadid = %s""",
                    ("completed", self.loadid),
                )
            return {"success": True, "data": "success"}
        else:
            return {"success": False, "data": "failed"}

    def start(self, request):
        graphid = request.POST.get("graphid")
        csv_mapping = request.POST.get("fieldMapping")
        mapping_details = {"mapping": json.loads(csv_mapping), "graph": graphid}
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO load_event (loadid, complete, status, etl_module_id, load_details, load_start_time, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (self.loadid, False, "running", self.moduleid, json.dumps(mapping_details), datetime.now(), self.userid),
            )
        message = "load event created"
        return {"success": True, "data": message}

    def populate_staging_table(self, request):

        file = request.FILES.get("file")
        graphid = request.POST.get("graphid")
        has_headers = request.POST.get("hasHeaders")
        fieldnames = request.POST.get("fieldnames").split(",")
        csvfile = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(csvfile), fieldnames=fieldnames)
        if has_headers:
            next(reader)

        with connection.cursor() as cursor:
            for row in reader:
                if "id" in row:
                    try:
                        uuid.UUID(row["id"])
                        legacyid = None
                    except (AttributeError, ValueError):
                        legacyid = row["id"]
                        resourceid = uuid.uuid4()
                else:
                    resourceid = uuid.uuid4()
                    legacyid = None

                dict_by_nodegroup = {}

                for key in row:
                    if key != "" and key != "id":
                        current_node = self.get_node_lookup(graphid).get(alias=key)
                        nodegroupid = str(current_node.nodegroup_id)
                        node = str(current_node.nodeid)
                        datatype = self.node_lookup[graphid].get(nodeid=node).datatype
                        datatype_instance = self.datatype_factory.get_instance(datatype)
                        source_value = row[key]
                        value = datatype_instance.transform_value_for_tile(source_value) if source_value is not None else None
                        errors = datatype_instance.validate(value)
                        valid = True if len(errors) == 0 else False
                        error_message = ""
                        for error in errors:
                            error_message = "{0}|{1}".format(error_message, error["message"]) if error_message != "" else error["message"]

                        if nodegroupid in dict_by_nodegroup:
                            dict_by_nodegroup[nodegroupid].append(
                                {
                                    node: {
                                        "value": value,
                                        "valid": valid,
                                        "source": source_value,
                                        "notes": error_message,
                                        "datatype": datatype,
                                    }
                                }
                            )
                        else:
                            dict_by_nodegroup[nodegroupid] = [
                                {
                                    node: {
                                        "value": value,
                                        "valid": valid,
                                        "source": source_value,
                                        "notes": error_message,
                                        "datatype": datatype,
                                    }
                                }
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
                                nodegroupid, legacyid, resourceid, value, loadid, nodegroup_depth, source_description, passes_validation
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (nodegroup, legacyid, resourceid, tile_value_json, self.loadid, node_depth, file.name, passes_validation),
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
