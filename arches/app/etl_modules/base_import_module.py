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
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.db import connection

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.etl_modules.decorators import load_data_async
from arches.app.etl_modules.save import save_to_tiles
from arches.app.models.models import ETLModule, Node
from arches.app.models.system_settings import settings
from arches.app.utils.decorators import user_created_transaction_match
from arches.app.utils.file_validator import FileValidator
from arches.app.utils.transaction import reverse_edit_log_entries
import arches.app.tasks as tasks
import arches.app.utils.task_management as task_management

logger = logging.getLogger(__name__)


class BaseImportModule:
    def __init__(
        self, loadid=None, request=None, userid=None, moduleid=None, fileid=None
    ):
        self.request = request
        self.userid = userid
        self.moduleid = moduleid
        self.fileid = fileid
        self.loadid = loadid
        self.legacyid_lookup = {}
        self.datatype_factory = DataTypeFactory()
        self.config = (
            ETLModule.objects.get(pk=self.moduleid).config if self.moduleid else {}
        )
        self.mode = "ui"
        if self.request:
            self.userid = request.user.id
            self.moduleid = request.POST.get("module")
            self.loadid = request.POST.get("load_id")
            if loadid is not None and self.loadid != loadid:
                raise ValueError("loadid from request does not match loadid argument")

    def filesize_format(self, bytes):
        """Convert bytes to readable units"""
        bytes = int(bytes)
        if bytes == 0:
            return "0 kb"
        log = math.floor(math.log(bytes, 1024))
        return "{0:.2f} {1}".format(
            bytes / math.pow(1024, log), ["bytes", "kb", "mb", "gb"][int(log)]
        )

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
            cursor.execute(
                """SELECT * FROM __arches_load_staging_report_errors(%s)""", [loadid]
            )
            rows = cursor.fetchall()
        return rows

    def prepare_data_for_loading(self, datatype_instance, source_value, config):
        try:
            value = (
                datatype_instance.transform_value_for_tile(source_value, **config)
                if source_value
                else None
            )
        except:
            value = source_value
        try:
            errors = []
            if value is not None:
                errors = datatype_instance.validate(value, **config)
        except:
            message = "Unexpected Error Occurred"
            title = "Invalid {} Format".format(datatype_instance.datatype_name)
            errors = [
                datatype_instance.create_error_message(value, "", "", message, title)
            ]

        return value, errors

    def get_graph_tree(self, graphid):
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM __get_nodegroup_tree_by_graph(%s)""", (graphid,)
            )
            rows = cursor.fetchall()
            node_lookup = {
                str(row[1]): {"depth": int(row[5]), "cardinality": row[7]}
                for row in rows
            }
            nodes = Node.objects.filter(graph_id=graphid).select_related("nodegroup")
            for node in nodes:
                nodeid = str(node.nodeid)
                if nodeid in node_lookup:
                    node_lookup[nodeid]["alias"] = node.alias
                    node_lookup[nodeid]["datatype"] = node.datatype
                    node_lookup[nodeid]["config"] = node.config
                elif not node.istopnode:
                    node_lookup[nodeid] = {
                        "depth": 0,  # ???
                        "cardinality": node.nodegroup.cardinality,
                        "alias": node.alias,
                        "datatype": node.datatype,
                        "config": node.config,
                    }
            return node_lookup, nodes

    def get_parent_tileid(
        self, depth, tileid, previous_tile, nodegroup, nodegroup_tile_lookup
    ):
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
            lookup[node.alias] = {
                "nodeid": str(node.nodeid),
                "datatype": node.datatype,
                "config": node.config,
            }
        return lookup

    def run_load_task(
        self, userid, files, summary, result, temp_dir, loadid, multiprocessing=False
    ):
        try:
            with connection.cursor() as cursor:
                self.stage_files(files, summary, cursor)
                self.check_tile_cardinality(cursor)
                result["validation"] = self.validate(loadid)
                if len(result["validation"]["data"]) == 0:
                    self.save_to_tiles(cursor, userid, loadid, multiprocessing)
                    cursor.execute(
                        """CALL __arches_update_resource_x_resource_with_graphids();"""
                    )
                    cursor.execute("""SELECT __arches_refresh_spatial_views();""")
                    refresh_successful = cursor.fetchone()[0]
                    if not refresh_successful:
                        raise Exception("Unable to refresh spatial views")
                else:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                            ("failed", datetime.now(), loadid),
                        )
        finally:
            self.delete_from_default_storage(temp_dir)
        result["summary"] = summary
        return {"success": result["validation"]["success"], "data": result}

    @load_data_async
    def run_load_task_async(self, request):
        raise NotImplementedError

    def prepare_temp_dir(self, request):
        self.temp_dir = os.path.join(settings.UPLOADED_FILES_DIR, "tmp", self.loadid)
        try:
            self.delete_from_default_storage(self.temp_dir)
        except FileNotFoundError:
            pass

    def validate_uploaded_file(self, file):
        pass

    def stage_files(self, files, summary, cursor):
        raise NotImplementedError

    def check_tile_cardinality(self, cursor):
        cursor.execute(
            """CALL __arches_check_tile_cardinality_violation_for_load(%s)""",
            [self.loadid],
        )
        cursor.execute(
            """
            INSERT INTO load_errors (type, source, error, loadid, nodegroupid)
            SELECT 'tile', source_description, error_message, loadid, nodegroupid
            FROM load_staging
            WHERE loadid = %s AND passes_validation = false AND error_message IS NOT null
            """,
            [self.loadid],
        )

    def save_to_tiles(self, cursor, userid, loadid, multiprocessing=False):
        return save_to_tiles(userid, loadid, multiprocessing)

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

    def read(self, request=None, source=None):
        self.prepare_temp_dir(request)
        self.cumulative_files_size = 0
        if request:
            content = request.FILES.get("file")
        else:
            if source.split(".")[-1].lower() == "xlsx":
                file_type = (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            elif source.split(".")[-1].lower() == "zip":
                file_type = "application/zip"
            file_stat = os.stat(source)
            file = open(source, "rb")
            content = InMemoryUploadedFile(
                file,
                "file",
                os.path.basename(source),
                file_type,
                file_stat.st_size,
                None,
            )

        result = {
            "summary": {
                "name": content.name,
                "size": self.filesize_format(content.size),
                "files": {},
            }
        }
        validator = FileValidator()
        extension = content.name.split(".")[-1] or None
        if len(validator.validate_file_type(content, extension=extension)) > 0:
            return {
                "status": 400,
                "success": False,
                "title": _("Invalid excel file/zip specified"),
                "message": _("Upload a valid .xlsx or .zip file"),
            }
        if content.name.split(".")[-1].lower() == "zip":
            with zipfile.ZipFile(content, "r") as zip_ref:
                files = zip_ref.infolist()
                for file in files:
                    if file.filename.split(".")[-1] == "xlsx":
                        self.cumulative_files_size += file.file_size
                    if not file.filename.startswith("__MACOSX"):
                        if not file.is_dir():
                            result["summary"]["files"][file.filename] = {
                                "size": (self.filesize_format(file.file_size))
                            }
                            result["summary"][
                                "cumulative_files_size"
                            ] = self.cumulative_files_size
                        default_storage.save(
                            os.path.join(self.temp_dir, file.filename),
                            File(zip_ref.open(file)),
                        )
        elif content.name.split(".")[-1] == "xlsx":
            self.cumulative_files_size += content.size
            result["summary"]["files"][content.name] = {
                "size": (self.filesize_format(content.size))
            }
            result["summary"]["cumulative_files_size"] = self.cumulative_files_size
            default_storage.save(
                os.path.join(self.temp_dir, content.name), File(content)
            )
        content.file.close()

        has_valid_excel_file = False
        for file in result["summary"]["files"]:
            if file.split(".")[-1] == "xlsx":
                try:
                    uploaded_file_path = os.path.join(self.temp_dir, file)
                    opened_file = default_storage.open(uploaded_file_path)
                    workbook = load_workbook(filename=opened_file, read_only=True)
                    self.validate_uploaded_file(workbook)
                    has_valid_excel_file = True
                except:
                    pass
                else:
                    opened_file.close()
        if not has_valid_excel_file:
            title = _("Invalid Uploaded File")
            message = _(
                "This file has missing information or invalid formatting. Make sure the file is complete and in the expected format."
            )
            return {"success": False, "data": {"title": title, "message": message}}

        return {"success": True, "data": result}

    def start(self, request):
        self.temp_dir = os.path.join(settings.UPLOADED_FILES_DIR, "tmp", self.loadid)
        result = {"started": False, "message": ""}
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    """INSERT INTO load_event (loadid, etl_module_id, complete, status, load_start_time, user_id) VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        self.loadid,
                        self.moduleid,
                        False,
                        "running",
                        datetime.now(),
                        self.userid,
                    ),
                )
                result["started"] = True
            except Exception:
                result["message"] = _("Unable to initialize load")
        return {"success": result["started"], "data": result}

    def write(self, request):
        self.temp_dir = os.path.join(settings.UPLOADED_FILES_DIR, "tmp", self.loadid)
        self.file_details = request.POST.get("load_details", None)
        multiprocessing = request.POST.get("multiprocessing", False)
        result = {}
        if self.file_details:
            details = json.loads(self.file_details)
            files = details["result"]["summary"]["files"]
            summary = details["result"]["summary"]
            use_celery_file_size_threshold = self.config.get(
                "celeryByteSizeLimit", 100000
            )

            if (
                self.mode != "cli"
                and summary["cumulative_files_size"] > use_celery_file_size_threshold
            ):
                response = self.run_load_task_async(request, self.loadid)
            else:
                response = self.run_load_task(
                    self.userid,
                    files,
                    summary,
                    result,
                    self.temp_dir,
                    self.loadid,
                    multiprocessing,
                )

            return response

    def cli(self, source):
        def return_with_error(error):
            return {
                "success": False,
                "data": {"title": _("Error"), "message": error},
            }

        read = {"success": False, "message": ""}
        written = {"success": False, "message": ""}

        initiated = self.start(self.request)

        if initiated["success"]:
            try:
                read = self.read(source=source)
            except Exception as e:
                return return_with_error(
                    _("Unexpected error while reading file(s): {}").format(e)
                )
        else:
            return return_with_error(initiated["message"])

        if read["success"]:
            try:
                self.request.POST.__setitem__(
                    "load_details", json.dumps({"result": read["data"]})
                )
                written = self.write(self.request)
            except Exception as e:
                return return_with_error(
                    _("Unexpected error while processing file(s): {}").format(e)
                )
        else:
            return return_with_error(read["data"]["message"])

        if written["success"]:
            return {"success": True, "data": "Successfully Imported"}
        else:
            return return_with_error(written["data"]["message"])


class FileValidationError(Exception):
    def __init__(self, message=_("Unable to read file"), code=400):
        self.title = _("Invalid Uploaded File")
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)
