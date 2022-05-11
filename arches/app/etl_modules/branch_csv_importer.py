from datetime import datetime
import json
import logging
import math
import os
import shutil
import uuid
import zipfile
from django.http import HttpResponse
from openpyxl import load_workbook
from django.db import connection
from django.db.utils import IntegrityError
from django.utils.translation import ugettext as _
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import Node
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.index_database import index_resources_by_transaction
from arches.management.commands.etl_template import create_workbook
from openpyxl.writer.excel import save_virtual_workbook

logger = logging.getLogger(__name__)


class BranchCsvImporter:
    def __init__(self, request=None):
        self.request = request
        self.userid = request.user.id
        self.moduleid = request.POST.get("module")
        self.datatype_factory = DataTypeFactory()
        self.legacyid_lookup = {}
        self.temp_path = ""

    def filesize_format(self, bytes):
        """Convert bytes to readable units"""
        bytes = int(bytes)
        if bytes == 0:
            return "0 kb"
        log = math.floor(math.log(bytes, 1024))
        return "{0:.2f} {1}".format(bytes / math.pow(1024, log), ["bytes", "kb", "mb", "gb"][int(log)])

    def get_graph_tree(self, graphid):
        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM __get_nodegroup_tree_by_graph(%s)""", (graphid,))
            rows = cursor.fetchall()
            node_lookup = {str(row[1]): {"depth": int(row[5])} for row in rows}
            nodes = Node.objects.filter(graph_id=graphid)
            for node in nodes:
                nodeid = str(node.nodeid)
                if nodeid in node_lookup:
                    node_lookup[nodeid]["alias"] = node.alias
                    node_lookup[nodeid]["datatype"] = node.datatype
                    node_lookup[nodeid]["config"] = node.config
            return node_lookup, nodes

    def get_parent_tileid(self, depth, tileid, previous_tile, nodegroup, nodegroup_tile_lookup):
        parenttileid = None
        if len(previous_tile.keys()) == 0:
            previous_tile["tileid"] = tileid
            previous_tile["depth"] = depth
            previous_tile["parenttile"] = None
            nodegroup_tile_lookup[nodegroup] = tileid

        if previous_tile["depth"] < depth:
            parenttileid = previous_tile["tileid"]
            nodegroup_tile_lookup[nodegroup] = parenttileid
            previous_tile["parenttile"] = parenttileid
        if previous_tile["depth"] > depth:
            if depth == 0:
                parenttileid = None
            else:
                parenttileid = nodegroup_tile_lookup[nodegroup]
        if previous_tile["depth"] == depth:
            parenttileid = previous_tile["parenttile"]

        previous_tile["tileid"] = tileid
        previous_tile["depth"] = depth
        return parenttileid

    def set_legacy_id(self, resourceid):
        try:
            uuid.UUID(resourceid)
            legacyid = None
        except (AttributeError, ValueError):
            legacyid = resourceid
            if legacyid not in self.legacyid_lookup:
                self.legacyid_lookup[legacyid] = uuid.uuid4()
            resourceid = self.legacyid_lookup[legacyid]
        return legacyid, resourceid

    def create_tile_value(self, cell_values, data_node_lookup, node_lookup, row_details):
        nodegroup_alias = cell_values[1].strip()
        node_value_keys = data_node_lookup[nodegroup_alias]
        tile_value = {}
        tile_valid = True
        for key in node_value_keys:
            try:
                nodeid = node_lookup[key]["nodeid"]
                node_details = node_lookup[key]
                datatype = node_details["datatype"]
                datatype_instance = self.datatype_factory.get_instance(datatype)
                source_value = row_details[key]
                config = node_details["config"]
                if datatype == "file-list":
                    config["path"] = self.temp_dir
                try:
                    config["nodeid"] = nodeid
                except TypeError:
                    config = {}
                value = datatype_instance.transform_value_for_tile(source_value, **config) if source_value is not None else None
                if datatype == "file-list":
                    validation_errors = datatype_instance.validate(value, nodeid=nodeid, path=self.temp_dir)
                else:
                    validation_errors = datatype_instance.validate(value, nodeid=nodeid)
                valid = True if len(validation_errors) == 0 else False
                if not valid:
                    tile_valid = False
                error_message = ""
                for error in validation_errors:
                    error_message = "{0}|{1}".format(error_message, error["message"]) if error_message != "" else error["message"]

                tile_value[nodeid] = {"value": value, "valid": valid, "source": source_value, "notes": error_message, "datatype": datatype}
            except KeyError as e:
                pass

        tile_value_json = JSONSerializer().serialize(tile_value)
        return tile_value_json, tile_valid

    def process_worksheet(self, worksheet, cursor, node_lookup, nodegroup_lookup):
        data_node_lookup = {}
        nodegroup_tile_lookup = {}
        previous_tile = {}
        row_count = 0
        for row in worksheet.rows:
            cell_values = [cell.value for cell in row]
            if len(cell_values) == 0:
                continue
            node_values = cell_values[2:]
            resourceid = cell_values[0]
            if str(resourceid).strip() in ("--", "resource_id"):
                nodegroup_alias = cell_values[1][0:-4].strip()
                data_node_lookup[nodegroup_alias] = node_values
            elif cell_values[1] is not None:
                try:
                    row_count += 1
                    nodegroup_alias = cell_values[1].strip()
                    row_details = dict(zip(data_node_lookup[nodegroup_alias], node_values))
                    row_details["nodegroup_id"] = node_lookup[nodegroup_alias]["nodeid"]
                    tileid = uuid.uuid4()
                    nodegroup_depth = nodegroup_lookup[row_details["nodegroup_id"]]["depth"]
                    parenttileid = None if "None" else row_details["parenttile_id"]
                    parenttileid = self.get_parent_tileid(
                        nodegroup_depth, str(tileid), previous_tile, nodegroup_alias, nodegroup_tile_lookup
                    )
                    legacyid, resourceid = self.set_legacy_id(resourceid)
                    tile_value_json, passes_validation = self.create_tile_value(cell_values, data_node_lookup, node_lookup, row_details)
                    cursor.execute(
                        """INSERT INTO load_staging (nodegroupid, legacyid, resourceid, tileid, parenttileid, value, loadid, nodegroup_depth, source_description, passes_validation) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (
                            row_details["nodegroup_id"],
                            legacyid,
                            resourceid,
                            tileid,
                            parenttileid,
                            tile_value_json,
                            self.loadid,
                            nodegroup_depth,
                            "worksheet:{0}, row:{1}".format(worksheet.title, row[0].row),  # source_description
                            passes_validation,
                        ),
                    )
                except KeyError:
                    pass
        return {"name": worksheet.title, "rows": row_count}

    def stage_excel_file(self, dir, summary):
        for (dirpath, dirnames, filenames) in os.walk(dir):
            for filename in filenames:
                if filename.endswith("xlsx"):
                    summary["files"][filename]["worksheets"] = []
                    workbook = load_workbook(filename=os.path.join(dirpath, filename))
                    try:
                        graphid = workbook.get_sheet_by_name("metadata")["B1"].value
                    except KeyError:
                        raise ValueError("A graphid is not available in the metadata worksheet")
                    nodegroup_lookup, nodes = self.get_graph_tree(graphid)
                    node_lookup = self.get_node_lookup(nodes)
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """INSERT INTO load_event (loadid, etl_module_id, load_details, complete, load_start_time, user_id) VALUES (%s, %s, %s, %s, %s, %s)""",
                            (self.loadid, self.moduleid, json.dumps(summary), False, datetime.now(), self.userid),
                        )
                        for worksheet in workbook.worksheets:
                            if worksheet.title.lower() != "metadata":
                                details = self.process_worksheet(worksheet, cursor, node_lookup, nodegroup_lookup)
                                summary["files"][filename]["worksheets"].append(details)

    def get_node_lookup(self, nodes):
        lookup = {}
        for node in nodes:
            lookup[node.alias] = {"nodeid": str(node.nodeid), "datatype": node.datatype, "config": node.config}
        return lookup

    def read(self, request):
        self.loadid = request.POST.get("load_id")
        content = request.FILES["file"]
        self.temp_dir = os.path.join(settings.APP_ROOT, "tmp", self.loadid)
        os.mkdir(self.temp_dir, 0o770)
        result = {"summary": {"name": content.name, "size": self.filesize_format(content.size), "files": {}}}
        with zipfile.ZipFile(content, "r") as zip_ref:
            files = zip_ref.infolist()
            for file in files:
                if not file.filename.startswith("__MACOSX"):
                    if not file.is_dir():
                        result["summary"]["files"][file.filename] = {"size": (self.filesize_format(file.file_size))}
                    zip_ref.extract(file, self.temp_dir)
        self.stage_excel_file(self.temp_dir, result["summary"])
        result["validation"] = self.validate(request)
        shutil.rmtree(self.temp_dir)
        return {"success": result["validation"]["success"], "data": result}

    def validate(self, request):
        """Validation is actually done - we're just getting the report here"""
        success = True
        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM __arches_load_staging_report_errors(%s)""", (self.loadid,))
            row = cursor.fetchall()
        return {"success": success, "data": row}

    def write(self, request):
        self.loadid = request.POST.get("load_id")
        try:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT * FROM __arches_staging_to_tile(%s)""", [self.loadid])
                row = cursor.fetchall()
        except IntegrityError as e:
            logger.error(e)
            return {
                "status": 400,
                "success": False,
                "title": _("Failed to complete load"),
                "message": _("Be sure any resources you are loading do not have resource ids that already exist in the system"),
            }

        index_resources_by_transaction(self.loadid, quiet=True, use_multiprocessing=True)
        if row[0][0]:
            return {"success": True, "data": "success"}
        else:
            return {"success": False, "data": "failed"}

    def download(self, request):
        format = request.POST.get("format")
        filename = request.POST.get("filename")
        if format == "xls":
            wb = create_workbook(request.POST.get("id"))
            response = HttpResponse(save_virtual_workbook(wb), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = "attachment"
            return {"success": True, "raw": response}
        else:
            return {"success": False, "data": "failed"}
