from datetime import datetime
import json
import logging
import math
import os
import uuid
import zipfile
from openpyxl import load_workbook

from django.core.files import File
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.db import connection

from arches.app.etl_modules.save import save_to_tiles
from arches.app.models.models import Node
from arches.app.models.system_settings import settings
from arches.app.utils.decorators import user_created_transaction_match
from arches.app.utils.file_validator import FileValidator
from arches.app.utils.transaction import reverse_edit_log_entries
import arches.app.tasks as tasks
import arches.app.utils.task_management as task_management

logger = logging.getLogger(__name__)


class BaseImportModule:
    def __init__(self, loadid=None):
        self.moduleid = None
        self.fileid = None
        self.loadid = loadid
        self.legacyid_lookup = {}

    def filesize_format(self, bytes):
        """Convert bytes to readable units"""
        bytes = int(bytes)
        if bytes == 0:
            return "0 kb"
        log = math.floor(math.log(bytes, 1024))
        return "{0:.2f} {1}".format(bytes / math.pow(1024, log), ["bytes", "kb", "mb", "gb"][int(log)])

    def reverse_load(self, loadid):
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET status = %s WHERE loadid = %s""",
                ("reversing", loadid),
            )
            resources_changed_count = reverse_edit_log_entries(loadid)
            cursor.execute(
                """UPDATE load_event SET status = %s, load_details = load_details::jsonb || ('{"resources_removed":' || %s || '}')::jsonb WHERE loadid = %s""",
                ("unloaded", resources_changed_count, loadid),
            )

    @method_decorator(user_created_transaction_match, name="dispatch")
    def reverse(self, request, **kwargs):
        success = False
        response = {"success": success, "data": ""}
        loadid = self.loadid if self.loadid else request.POST.get("loadid")
        try:
            if task_management.check_if_celery_available():
                logger.info(_("Delegating load reversal to Celery task"))
                tasks.reverse_etl_load.apply_async([loadid])
            else:
                self.reverse_load(loadid)
            response["success"] = True
        except Exception as e:
            response["data"] = e
            logger.error(e)
        logger.warning(response)
        return response

    def delete_from_default_storage(self, directory):
        dirs, files = default_storage.listdir(directory)
        for dir in dirs:
            dir_path = os.path.join(directory, dir)
            self.delete_from_default_storage(dir_path)
        for file in files:
            file_path = os.path.join(directory, file)
            default_storage.delete(file_path)
        default_storage.delete(directory)

    def get_validation_result(self, loadid):
        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM __arches_load_staging_report_errors(%s)""", [loadid])
            rows = cursor.fetchall()
        return rows

    def prepare_data_for_loading(self, datatype_instance, source_value, config):
        try:
            value = datatype_instance.transform_value_for_tile(source_value, **config) if source_value else None
        except:
            value = source_value
        try:
            errors =[]
            if value is not None:
                errors = datatype_instance.validate(value, **config)
        except:
            message = "Unexpected Error Occurred"
            title = "Invalid {} Format".format(datatype_instance.datatype_name)
            errors = [datatype_instance.create_error_message(value, "", "", message, title)]

        return value, errors

    def get_graph_tree(self, graphid):
        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM __get_nodegroup_tree_by_graph(%s)""", (graphid,))
            rows = cursor.fetchall()
            node_lookup = {str(row[1]): {"depth": int(row[5]), "cardinality": row[7]} for row in rows}
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

    def get_node_lookup(self, nodes):
        lookup = {}
        for node in nodes:
            lookup[node.alias] = {"nodeid": str(node.nodeid), "datatype": node.datatype, "config": node.config}
        return lookup

    def run_load_task(self, userid, files, summary, result, temp_dir, loadid):
        with connection.cursor() as cursor:
            for file in files.keys():
                self.stage_excel_file(file, summary, cursor)
            cursor.execute("""CALL __arches_check_tile_cardinality_violation_for_load(%s)""", [loadid])
            cursor.execute(
                """
                INSERT INTO load_errors (type, source, error, loadid, nodegroupid)
                SELECT 'tile', source_description, error_message, loadid, nodegroupid
                FROM load_staging
                WHERE loadid = %s AND passes_validation = false AND error_message IS NOT null
                """,
                [loadid],
            )
            result["validation"] = self.validate(loadid)
            if len(result["validation"]["data"]) == 0:
                self.loadid = loadid  # currently redundant, but be certain
                save_to_tiles(userid, loadid)
                cursor.execute("""CALL __arches_update_resource_x_resource_with_graphids();""")
                cursor.execute("""SELECT __arches_refresh_spatial_views();""")
                refresh_successful = cursor.fetchone()[0]
                if not refresh_successful:
                    raise Exception('Unable to refresh spatial views')
            else:
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("failed", datetime.now(), loadid),
                )
        self.delete_from_default_storage(temp_dir)
        result["summary"] = summary
        return {"success": result["validation"]["success"], "data": result}

    def validate_uploaded_file(self, file, kwarg):
        pass

    ### Actions ###

    def validate(self, loadid):
        success = True
        with connection.cursor() as cursor:
            error_message = _("Legacy id(s) already exist. Legacy ids must be unique")
            cursor.execute(
                """UPDATE load_event SET error_message = %s, status = 'failed' WHERE  loadid = %s::uuid
            AND EXISTS (SELECT legacyid FROM load_staging where loadid = %s::uuid and legacyid is not null INTERSECT SELECT legacyid from resource_instances);""",
                (error_message, self.loadid, self.loadid),
            )
        row = self.get_validation_result(loadid)
        return {"success": success, "data": row}

    def read(self, request):
        self.loadid = request.POST.get("load_id")
        self.cumulative_excel_files_size = 0
        content = request.FILES["file"]
        self.temp_dir = os.path.join(settings.UPLOADED_FILES_DIR, "tmp", self.loadid)
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
        if content.name.split(".")[-1].lower() == "zip":
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
        elif content.name.split(".")[-1] == "xlsx":
            self.cumulative_excel_files_size += content.size
            result["summary"]["files"][content.name] = {"size": (self.filesize_format(content.size))}
            result["summary"]["cumulative_excel_files_size"] = self.cumulative_excel_files_size
            default_storage.save(os.path.join(self.temp_dir, content.name), File(content))

        has_valid_excel_file = False
        for file in result["summary"]["files"]:
            if file.split(".")[-1] == "xlsx":
                try:
                    uploaded_file_path = os.path.join(self.temp_dir, file)
                    workbook = load_workbook(filename=default_storage.open(uploaded_file_path))
                    self.validate_uploaded_file(workbook)
                    has_valid_excel_file = True
                except:
                    pass
        if not has_valid_excel_file:
            title = _("Invalid Uploaded File")
            message = _("This file has missing information or invalid formatting. Make sure the file is complete and in the expected format.")
            return {"success": False, "data": {"title": title, "message": message}}

        return {"success": True, "data": result}

    def start(self, request):
        self.loadid = request.POST.get("load_id")
        self.temp_dir = os.path.join(settings.UPLOADED_FILES_DIR, "tmp", self.loadid)
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
        self.temp_dir = os.path.join(settings.UPLOADED_FILES_DIR, "tmp", self.loadid)
        self.file_details = request.POST.get("load_details", None)
        result = {}
        if self.file_details:
            details = json.loads(self.file_details)
            files = details["result"]["summary"]["files"]
            summary = details["result"]["summary"]
            use_celery_file_size_threshold_in_MB = 0.1
            if summary["cumulative_excel_files_size"] / 1000000 > use_celery_file_size_threshold_in_MB:
                response = self.run_load_task_async(request, self.loadid)
            else:
                response = self.run_load_task(self.userid, files, summary, result, self.temp_dir, self.loadid)

            return response

class FileValidationError(Exception):
    def __init__(self, message=_("Unable to read file"), code=400):
        self.title = _("Invalid Uploaded File")
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)
