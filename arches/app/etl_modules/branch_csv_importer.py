from datetime import datetime
import io
import json
import logging
import math
import os
import shutil
import uuid
import zipfile
import arches.app.tasks as tasks
from django.core.files import File
from django.http import HttpResponse
from openpyxl import load_workbook
from django.db import connection
from django.db.utils import IntegrityError, ProgrammingError
from django.utils.translation import ugettext as _
from django.core.files.storage import default_storage
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import Node
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.file_validator import FileValidator
from arches.app.utils.index_database import index_resources_by_transaction
from arches.management.commands.etl_template import create_workbook
from openpyxl.writer.excel import save_virtual_workbook
import arches.app.utils.task_management as task_management
from arches.app.etl_modules.base_import_module import BaseImportModule

logger = logging.getLogger(__name__)


class BranchCsvImporter(BaseImportModule):
    def __init__(self, request=None, loadid=None, temp_dir=None):
        self.request = request if request else None
        self.userid = request.user.id if request else None
        self.moduleid = request.POST.get("module") if request else None
        self.datatype_factory = DataTypeFactory()
        self.legacyid_lookup = {}
        self.temp_path = ""
        self.loadid = loadid if loadid else None
        self.temp_dir = temp_dir if temp_dir else None

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
        if depth == 0:
            previous_tile["tileid"] = tileid
            previous_tile["depth"] = depth
            return parenttileid
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
                    config["path"] = os.path.join("uploadedfiles", "tmp", self.loadid)
                    config["loadid"] = self.loadid
                try:
                    config["nodeid"] = nodeid
                except TypeError:
                    config = {}
                value = datatype_instance.transform_value_for_tile(source_value, **config) if source_value is not None else None
                if datatype == "file-list":
                    validation_errors = datatype_instance.validate(value, nodeid=nodeid, path=self.temp_dir)
                else:
                    validation_errors = datatype_instance.validate(value, nodeid=nodeid)
                validation_errors = [message for message in validation_errors if message["type"] != "WARNING"]
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
            resourceid = cell_values[0]
            if str(resourceid).strip() in ("--", "resource_id"):
                nodegroup_alias = cell_values[1][0:-4].strip()
                data_node_lookup[nodegroup_alias] = [val for val in cell_values[2:] if val]
            elif cell_values[1] is not None:
                node_values = cell_values[2:]
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

    def stage_excel_file(self, file, summary, cursor):
        if file.endswith("xlsx"):
            summary["files"][file]["worksheets"] = []
            workbook = load_workbook(filename=default_storage.open(os.path.join("uploadedfiles", "tmp", self.loadid, file)))
            try:
                graphid = workbook.get_sheet_by_name("metadata")["B1"].value
            except KeyError:
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("failed", datetime.now(), self.loadid),
                )
                raise ValueError("A graphid is not available in the metadata worksheet")
            nodegroup_lookup, nodes = self.get_graph_tree(graphid)
            node_lookup = self.get_node_lookup(nodes)
            for worksheet in workbook.worksheets:
                if worksheet.title.lower() != "metadata":
                    details = self.process_worksheet(worksheet, cursor, node_lookup, nodegroup_lookup)
                    summary["files"][file]["worksheets"].append(details)
            cursor.execute(
                """UPDATE load_event SET load_details = %s WHERE loadid = %s""",
                (json.dumps(summary), self.loadid),
            )

    def get_node_lookup(self, nodes):
        lookup = {}
        for node in nodes:
            lookup[node.alias] = {"nodeid": str(node.nodeid), "datatype": node.datatype, "config": node.config}
        return lookup

    def validate(self):
        success = True
        with connection.cursor() as cursor:
            error_message = _("Legacy id(s) already exist. Legacy ids must be unique")
            cursor.execute(
                """UPDATE load_event SET error_message = %s, status = 'failed' WHERE  loadid = %s::uuid
            AND EXISTS (SELECT legacyid FROM load_staging where loadid = %s::uuid and legacyid is not null INTERSECT SELECT legacyid from resource_instances);""",
                (error_message, self.loadid, self.loadid),
            )
            cursor.execute("""SELECT * FROM __arches_load_staging_report_errors(%s)""", (self.loadid,))
            row = cursor.fetchall()
        return {"success": success, "data": row}

    def complete_load(self, loadid, multiprocessing=True):
        self.loadid = loadid
        with connection.cursor() as cursor:
            try:
                cursor.execute("""SELECT * FROM __arches_staging_to_tile(%s)""", [self.loadid])
                row = cursor.fetchall()
            except (IntegrityError, ProgrammingError) as e:
                logger.error(e)
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("failed", datetime.now(), self.loadid),
                )
                return {
                    "status": 400,
                    "success": False,
                    "title": _("Failed to complete load"),
                    "message": _("Unable to insert record into staging table"),
                }
            if row[0][0]:
                cursor.execute(
                    """UPDATE load_event SET (status, load_end_time) = (%s, %s) WHERE loadid = %s""",
                    ("completed", datetime.now(), loadid),
                )
                index_resources_by_transaction(loadid, quiet=True, use_multiprocessing=False)
                cursor.execute(
                    """UPDATE load_event SET (status, indexed_time, complete, successful) = (%s, %s, %s, %s) WHERE loadid = %s""",
                    ("indexed", datetime.now(), True, True, loadid),
                )
                return {"success": True, "data": "success"}
            else:
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("failed", datetime.now(), self.loadid),
                )
                return {"success": False, "data": "failed"}

    def read(self, request):
        self.loadid = request.POST.get("load_id")
        self.cumulative_excel_files_size = 0
        content = request.FILES["file"]
        self.temp_dir = os.path.join("uploadedfiles", "tmp", self.loadid)
        try:
            self.delete_from_default_storage(self.temp_dir)
        except (FileNotFoundError):
            pass
        result = {"summary": {"name": content.name, "size": self.filesize_format(content.size), "files": {}}}
        validator = FileValidator()
        if len(validator.validate_file_type(content)) > 0:
            return {
                "status": 400,
                "success": False,
                "title": _("Invalid excel file/zip specified"),
                "message": _("Upload a valid excel file"),
            }
        if content.content_type == "application/zip":
            with zipfile.ZipFile(content, "r") as zip_ref:
                files = zip_ref.infolist()
                for file in files:
                    if file.filename.split(".")[-1] == "xlsx":
                        self.cumulative_excel_files_size += file.file_size
                    if not file.filename.startswith("__MACOSX"):
                        if not file.is_dir():
                            result["summary"]["files"][file.filename] = {"size": (self.filesize_format(file.file_size))}
                            result["summary"]["cumulative_excel_files_size"] = self.cumulative_excel_files_size
                        default_storage.save(os.path.join(self.temp_dir, file.filename), File(zip_ref.open(file)))
        return {"success": result, "data": result}

    def start(self, request):
        self.loadid = request.POST.get("load_id")
        self.temp_dir = os.path.join("uploadedfiles", "tmp", self.loadid)
        result = {"started": False, "message": ""}
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    """INSERT INTO load_event (loadid, etl_module_id, complete, status, load_start_time, user_id) VALUES (%s, %s, %s, %s, %s, %s)""",
                    (self.loadid, self.moduleid, False, "running", datetime.now(), self.userid),
                )
                result["started"] = True
            except Exception:
                result["message"] = _("Unable to initialize load")
        return {"success": result["started"], "data": result}

    def write(self, request):
        self.loadid = request.POST.get("load_id")
        self.temp_dir = os.path.join("uploadedfiles", "tmp", self.loadid)
        self.file_details = request.POST.get("load_details", None)
        result = {}
        if self.file_details:
            details = json.loads(self.file_details)
            files = details["result"]["summary"]["files"]
            summary = details["result"]["summary"]
            use_celery_file_size_threshold_in_MB = 0.1
            if summary["cumulative_excel_files_size"] / 1000000 > use_celery_file_size_threshold_in_MB:
                if task_management.check_if_celery_available():
                    logger.info(_("Delegating load to Celery task"))
                    tasks.load_branch_csv.apply_async(
                        (files, summary, result, self.temp_dir, self.loadid),
                    )
                    result = _("delegated_to_celery")
                    return {"success": True, "data": result}
                else:
                    err = _("Celery appears not to be running, you need to have celery running in order to immport large csv.")
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                            ("failed", datetime.now(), self.loadid),
                        )
                    return {"success": False, "data": err}
            else:
                response = self.run_load_task(files, summary, result, self.temp_dir, self.loadid)

            return response

    def run_load_task(self, files, summary, result, temp_dir, loadid):
        with connection.cursor() as cursor:
            for file in files.keys():
                self.stage_excel_file(file, summary, cursor)
            cursor.execute("""CALL __arches_check_tile_cardinality_violation_for_load(%s)""", [loadid])
            result["validation"] = self.validate()
            if len(result["validation"]["data"]) == 0:
                self.complete_load(loadid, multiprocessing=False)
            else:
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("failed", datetime.now(), loadid),
                )
        self.delete_from_default_storage(temp_dir)
        result["summary"] = summary
        return {"success": result["validation"]["success"], "data": result}

    def delete_from_default_storage(self, directory):
        dirs, files = default_storage.listdir(directory)
        for dir in dirs:
            dir_path = os.path.join(directory, dir)
            self.delete_from_default_storage(dir_path)
        for file in files:
            file_path = os.path.join(directory, file)
            default_storage.delete(file_path)
        default_storage.delete(directory)

    def download(self, request):
        format = request.POST.get("format")
        if format == "xls":
            wb = create_workbook(request.POST.get("id"))
            response = HttpResponse(save_virtual_workbook(wb), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = "attachment"
            return {"success": True, "raw": response}
        else:
            return {"success": False, "data": "failed"}
