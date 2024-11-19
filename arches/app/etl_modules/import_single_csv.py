import csv
from datetime import datetime
import io
import json
import os
import uuid
import zipfile
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import connection
from django.db.models.functions import Lower
from django.http import HttpRequest
from django.utils.translation import gettext as _
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import ETLModule, GraphModel, Node, NodeGroup
from arches.app.models.system_settings import settings
import arches.app.tasks as tasks
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.file_validator import FileValidator
from arches.app.etl_modules.base_import_module import BaseImportModule
from arches.app.etl_modules.decorators import load_data_async
from arches.app.etl_modules.save import save_to_tiles


class ImportSingleCsv(BaseImportModule):
    def __init__(self, request=None, loadid=None, params=None):
        self.loadid = request.POST.get("load_id") if request else loadid
        self.userid = (
            request.user.id
            if request
            else settings.DEFAULT_RESOURCE_IMPORT_USER["userid"]
        )
        self.mode = "cli" if not request and params else "ui"
        try:
            self.user = User.objects.get(pk=self.userid)
        except User.DoesNotExist:
            raise User.DoesNotExist(
                _(
                    "The userid {} does not exist. Probably DEFAULT_RESOURCE_IMPORT_USER is not configured correctly in settings.py.".format(
                        self.userid
                    )
                )
            )
        if not request and params:
            request = HttpRequest()
            request.user = self.user
            request.method = "POST"
            for k, v in params.items():
                request.POST.__setitem__(k, v)
        self.request = request if request else None
        self.moduleid = request.POST.get("module") if request else None
        self.config = (
            ETLModule.objects.get(pk=self.moduleid).config if self.moduleid else {}
        )
        self.datatype_factory = DataTypeFactory()
        self.node_lookup = {}
        self.blank_tile_lookup = {}

    def get_graphs(self, request):
        graph_name_i18n = "name__" + settings.LANGUAGE_CODE
        graphs = (
            GraphModel.objects.all()
            .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(isresource=False)
            .exclude(is_active=False)
            .exclude(source_identifier__isnull=False)
            .order_by(graph_name_i18n)
        )
        return {"success": True, "data": graphs}

    def get_nodes(self, request):
        """
        Only returing nodes that belong to the top cards at the moment
        """

        def is_top_nodegroup(nodegroupid):
            return (
                NodeGroup.objects.get(nodegroupid=nodegroupid).parentnodegroup is None
            )

        graphid = request.POST.get("graphid")
        nodes = (
            Node.objects.filter(graph_id=graphid)
            .exclude(datatype__in=["semantic"])
            .order_by(Lower("name"))
        )
        filteredNodes = []
        for node in nodes:
            if is_top_nodegroup(node.nodegroup_id):
                filteredNodes.append(node)
        return {"success": True, "data": filteredNodes}

    def get_node_lookup(self, graphid):
        if graphid not in self.node_lookup.keys():
            self.node_lookup[graphid] = Node.objects.filter(graph_id=graphid)
        return self.node_lookup[graphid]

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
                written = self.write(self.request)
            except Exception as e:
                return return_with_error(
                    _("Unexpected error while processing file(s): {}").format(e)
                )
        else:
            return return_with_error(read["message"])

        if written["success"]:
            return {"success": True, "data": _("Successfully Imported")}
        else:
            return return_with_error(written["message"])

    def read(self, request=None, source=None):
        """
        Reads added csv file and returns all the rows
        If the loadid already exists also returns the load_details
        """

        if request:
            content = request.FILES.get("file")
        else:
            if source.split(".")[-1].lower() == "csv":
                file_type = "text/csv"
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

        temp_dir = os.path.join(settings.UPLOADED_FILES_DIR, "tmp", self.loadid)
        try:
            self.delete_from_default_storage(temp_dir)
        except FileNotFoundError:
            pass

        csv_file_name = None
        validator = FileValidator()
        if len(validator.validate_file_type(content, content.name.split(".")[-1])) > 0:
            pass
        elif content.content_type == "text/csv":
            csv_file_name = content.name
            csv_file_path = os.path.join(temp_dir, csv_file_name)
            default_storage.save(csv_file_path, content)
        elif content.name.split(".")[-1].lower() == "zip":
            with zipfile.ZipFile(content, "r") as zip_ref:
                files = zip_ref.infolist()
                for file in files:
                    if not file.filename.startswith("__MACOSX"):
                        default_storage.save(
                            os.path.join(temp_dir, file.filename),
                            File(zip_ref.open(file)),
                        )
                        if file.filename.endswith(".csv"):
                            csv_file_name = file.filename
            try:
                csv_file_path = os.path.join(temp_dir, csv_file_name)
            except TypeError:
                pass
        content.file.close()

        if csv_file_name is None:
            return {
                "status": 400,
                "success": False,
                "title": _("No csv file found"),
                "message": _("Upload a valid csv file"),
            }

        with default_storage.open(csv_file_path, mode="rb") as csvfile:
            text_wrapper = io.TextIOWrapper(csvfile, encoding="utf-8")
            reader = csv.reader(text_wrapper)
            data = {"csv": [line for line in reader], "csv_file": csv_file_name}
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT load_details FROM load_event WHERE loadid = %s""",
                    [self.loadid],
                )
                row = cursor.fetchall()
            if len(row) > 0:
                data["config"] = row[0][0]
        return {"success": True, "data": data}

    def validate(self, loadid):
        """
        Creates records in the load_staging table (validated before poulating the load_staging table with error message)
        Collects error messages if any and returns table of error messages
        """
        rows = self.get_validation_result(loadid)
        return {"success": True, "data": rows}

    def write(self, request):
        """
        Move the records from load_staging to tiles table using db function
        """
        graphid = request.POST.get("graphid")
        has_headers = request.POST.get("hasHeaders")
        fieldnames = request.POST.get("fieldnames")
        if type(fieldnames) != list:
            fieldnames = fieldnames.split(",")
        csv_mapping = request.POST.get("fieldMapping")
        if csv_mapping and type(csv_mapping) == str:
            csv_mapping = json.loads(csv_mapping)
        csv_file_name = request.POST.get("csvFileName")
        column_names = [fieldname for fieldname in fieldnames if fieldname != ""]
        id_label = "resourceid"

        error_message = None
        if len(column_names) == 0:
            error_message = _("No valid node is selected")
        if column_names.count(id_label) > 1:
            error_message = _("Only one column should be selected for id")
        if error_message:
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("failed", datetime.now(), self.loadid),
                )
            return {"success": False, "data": error_message}

        temp_dir = os.path.join(settings.UPLOADED_FILES_DIR, "tmp", self.loadid)
        csv_file_path = os.path.join(temp_dir, csv_file_name)
        csv_size = default_storage.size(csv_file_path)  # file size in byte
        use_celery_threshold = self.config.get("celeryByteSizeLimit", 500)

        if self.mode != "cli" and csv_size > use_celery_threshold:
            response = self.run_load_task_async(request, self.loadid)
        else:
            response = self.run_load_task(
                self.userid,
                self.loadid,
                graphid,
                has_headers,
                fieldnames,
                csv_mapping,
                csv_file_name,
                id_label,
            )

        return response

    def run_load_task(
        self,
        userid,
        loadid,
        graphid,
        has_headers,
        fieldnames,
        csv_mapping,
        csv_file_name,
        id_label,
    ):

        self.populate_staging_table(
            loadid,
            graphid,
            has_headers,
            fieldnames,
            csv_mapping,
            csv_file_name,
            id_label,
        )

        validation = self.validate(loadid)
        if len(validation["data"]) == 0:
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE load_event SET status = %s WHERE loadid = %s""",
                    ("validated", loadid),
                )
            self.loadid = loadid  # currently redundant, but be certain
            response = save_to_tiles(userid, loadid)
            with connection.cursor() as cursor:
                cursor.execute(
                    """CALL __arches_update_resource_x_resource_with_graphids();"""
                )
                cursor.execute("""SELECT __arches_refresh_spatial_views();""")
                refresh_successful = cursor.fetchone()[0]
            if not refresh_successful:
                raise Exception("Unable to refresh spatial views")
            return response
        else:
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("failed", datetime.now(), loadid),
                )
            return {"success": False, "data": "failed"}

    @load_data_async
    def run_load_task_async(self, request):
        graphid = request.POST.get("graphid")
        has_headers = request.POST.get("hasHeaders")
        fieldnames = request.POST.get("fieldnames").split(",")
        csv_mapping = request.POST.get("fieldMapping")
        if csv_mapping:
            csv_mapping = json.loads(csv_mapping)
        csv_file_name = request.POST.get("csvFileName")
        id_label = "resourceid"

        load_task = tasks.load_single_csv.apply_async(
            (
                self.userid,
                self.loadid,
                graphid,
                has_headers,
                fieldnames,
                csv_mapping,
                csv_file_name,
                id_label,
            ),
        )
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET taskid = %s WHERE loadid = %s""",
                (load_task.task_id, self.loadid),
            )

    def start(self, request):
        graphid = request.POST.get("graphid")
        csv_mapping = request.POST.get("fieldMapping")
        csv_file_name = request.POST.get("csvFileName")
        if type(csv_mapping) == str:
            csv_mapping = json.loads(csv_mapping)
        mapping_details = {
            "mapping": csv_mapping,
            "graph": graphid,
            "file_name": csv_file_name,
        }
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO load_event (loadid, complete, status, etl_module_id, load_details, load_start_time, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    self.loadid,
                    False,
                    "running",
                    self.moduleid,
                    json.dumps(mapping_details),
                    datetime.now(),
                    self.userid,
                ),
            )
        message = "load event created"
        return {"success": True, "data": message}

    def populate_staging_table(
        self,
        loadid,
        graphid,
        has_headers,
        fieldnames,
        csv_mapping,
        csv_file_name,
        id_label,
    ):
        temp_dir = os.path.join(settings.UPLOADED_FILES_DIR, "tmp", loadid)
        csv_file_path = os.path.join(temp_dir, csv_file_name)
        with default_storage.open(csv_file_path, mode="rb") as csvfile:
            text_wrapper = io.TextIOWrapper(csvfile, encoding="utf-8")
            reader = csv.reader(
                text_wrapper
            )  # if there is a duplicate field, DictReader will not work

            if has_headers:
                next(reader)

            with connection.cursor() as cursor:
                for row in reader:
                    if id_label in fieldnames:
                        id_index = fieldnames.index(id_label)
                        try:
                            resourceid = uuid.UUID(row[id_index])
                            legacyid = None
                        except (AttributeError, ValueError):
                            resourceid = uuid.uuid4()
                            legacyid = row[id_index]
                    else:
                        resourceid = uuid.uuid4()
                        legacyid = None

                    dict_by_nodegroup = {}

                    for i in range(len(fieldnames)):
                        if fieldnames[i] != "" and fieldnames[i] != id_label:
                            current_node = self.get_node_lookup(graphid).get(
                                alias=fieldnames[i]
                            )
                            nodegroupid = str(current_node.nodegroup_id)
                            node = str(current_node.nodeid)
                            datatype = (
                                self.node_lookup[graphid].get(nodeid=node).datatype
                            )
                            datatype_instance = self.datatype_factory.get_instance(
                                datatype
                            )
                            source_value = row[i]
                            config = current_node.config
                            config["nodeid"] = node
                            config["path"] = temp_dir

                            if source_value:
                                if datatype == "string":
                                    try:
                                        code = csv_mapping[i]["language"]["code"]
                                        direction = csv_mapping[i]["language"][
                                            "default_direction"
                                        ]
                                        transformed_value = {
                                            code: {
                                                "value": row[i],
                                                "direction": direction,
                                            }
                                        }
                                    except:
                                        transformed_value = source_value
                                    value = (
                                        datatype_instance.transform_value_for_tile(
                                            transformed_value, **config
                                        )
                                        if transformed_value
                                        else None
                                    )
                                    errors = datatype_instance.validate(
                                        value, nodeid=node
                                    )
                                else:
                                    value, errors = self.prepare_data_for_loading(
                                        datatype_instance, source_value, config
                                    )

                                valid = True if len(errors) == 0 else False
                                error_message = ""
                                for error in errors:
                                    error_message = (
                                        "{0}|{1}".format(
                                            error_message, error["message"]
                                        )
                                        if error_message != ""
                                        else error["message"]
                                    )
                                    cursor.execute(
                                        """
                                        INSERT INTO load_errors (type, value, source, error, message, datatype, loadid, nodeid)
                                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                                        (
                                            "node",
                                            source_value,
                                            csv_file_name,
                                            error["title"],
                                            error["message"],
                                            datatype,
                                            loadid,
                                            node,
                                        ),
                                    )

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
                        for key in tile_data:
                            tile_data[key] = None
                        for node in dict_by_nodegroup[nodegroup]:
                            for key in node:
                                if tile_data[key]:
                                    if tile_data[key]["datatype"] == "string":
                                        tile_data[key]["value"].update(
                                            node[key]["value"]
                                        )
                                        tile_data[key]["source"] += (
                                            " | " + node[key]["source"]
                                        )
                                        tile_data[key]["notes"] = " | ".join(
                                            [
                                                tile_data[key]["notes"],
                                                node[key]["notes"],
                                            ]
                                        )
                                        tile_data[key]["valid"] = (
                                            tile_data[key]["valid"]
                                            and node[key]["valid"]
                                        )
                                else:
                                    tile_data[key] = node[key]
                                if node[key]["valid"] is False:
                                    passes_validation = False

                        tileid = uuid.uuid4()
                        tile_value_json = JSONSerializer().serialize(tile_data)
                        node_depth = 0

                        cursor.execute(
                            """
                            INSERT INTO load_staging (
                                nodegroupid,
                                legacyid,
                                resourceid,
                                tileid,
                                value,
                                loadid,
                                nodegroup_depth,
                                source_description,
                                operation,
                                passes_validation,
                                sortorder
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (
                                nodegroup,
                                legacyid,
                                resourceid,
                                tileid,
                                tile_value_json,
                                loadid,
                                node_depth,
                                csv_file_name,
                                "insert",
                                passes_validation,
                                0,
                            ),
                        )

                cursor.execute(
                    """CALL __arches_check_tile_cardinality_violation_for_load(%s)""",
                    [loadid],
                )
                cursor.execute(
                    """
                    INSERT INTO load_errors (type, source, error, loadid, nodegroupid)
                    SELECT 'tile', source_description, error_message, loadid, nodegroupid
                    FROM load_staging
                    WHERE loadid = %s AND passes_validation = false AND error_message IS NOT null
                    """,
                    [loadid],
                )

        self.delete_from_default_storage(temp_dir)

        message = "staging table populated"
        return {"success": True, "data": message}

    def get_blank_tile_lookup(self, nodegroupid):
        if nodegroupid not in self.blank_tile_lookup.keys():
            self.blank_tile_lookup[nodegroupid] = {}
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT nodeid FROM nodes WHERE datatype <> 'semantic' AND nodegroupid = %s;""",
                    [nodegroupid],
                )
                for row in cursor.fetchall():
                    (nodeid,) = row
                    self.blank_tile_lookup[nodegroupid][str(nodeid)] = None
        return self.blank_tile_lookup[nodegroupid]
