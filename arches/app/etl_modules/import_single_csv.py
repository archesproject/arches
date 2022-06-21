import csv
from datetime import datetime
import json
import logging
import os
import uuid
import zipfile
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import connection
from django.db.models.functions import Lower
from django.db.utils import IntegrityError, ProgrammingError
from django.utils.translation import ugettext as _
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import GraphModel, Node, NodeGroup
from arches.app.models.system_settings import settings
import arches.app.tasks as tasks
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.file_validator import FileValidator
from arches.app.utils.index_database import index_resources_by_transaction
from arches.app.etl_modules.base_import_module import BaseImportModule
import arches.app.utils.task_management as task_management

logger = logging.getLogger(__name__)


class ImportSingleCsv(BaseImportModule):
    def __init__(self, request=None):
        self.request = request if request else None
        self.userid = request.user.id if request else None
        self.loadid = request.POST.get("load_id") if request else None
        self.moduleid = request.POST.get("module") if request else None
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

        content = request.FILES.get("file")
        temp_dir = os.path.join("uploadedfiles", "tmp", self.loadid)
        try:
            self.delete_from_default_storage(temp_dir)
        except (FileNotFoundError):
            pass

        csv_file_name = None
        validator = FileValidator()
        if len(validator.validate_file_type(content, content.name.split(".")[-1])) > 0:
            pass
        elif content.content_type == "text/csv":
            csv_file_name = content.name
            csv_file_path = os.path.join(temp_dir, csv_file_name)
            default_storage.save(csv_file_path, content)
        elif content.content_type == "application/zip":
            with zipfile.ZipFile(content, "r") as zip_ref:
                files = zip_ref.infolist()
                for file in files:
                    if not file.filename.startswith("__MACOSX"):
                        default_storage.save(os.path.join(temp_dir, file.filename), File(zip_ref.open(file)))
                        if file.filename.endswith(".csv"):
                            csv_file_name = file.filename
            csv_file_path = os.path.join(temp_dir, csv_file_name)

        if csv_file_name is None:
            return {
                "status": 400,
                "success": False,
                "title": _("No csv file found"),
                "message": _("Upload a valid csv file"),
            }

        with default_storage.open(csv_file_path, mode="r") as csvfile:
            reader = csv.reader(csvfile)
            data = {"csv": [line for line in reader], "csv_file": csv_file_name}
            with connection.cursor() as cursor:
                cursor.execute("""SELECT load_details FROM load_event WHERE loadid = %s""", [self.loadid])
                row = cursor.fetchall()
            if len(row) > 0:
                data["config"] = row[0][0]
        return {"success": True, "data": data}

    def validate(self):
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

        graphid = request.POST.get("graphid")
        has_headers = request.POST.get("hasHeaders")
        fieldnames = request.POST.get("fieldnames").split(",")
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

        temp_dir = os.path.join("uploadedfiles", "tmp", self.loadid)
        csv_file_path = os.path.join(temp_dir, csv_file_name)
        csv_size = default_storage.size(csv_file_path)  # file size in byte
        use_celery_threshold = 500  # 500 bytes

        if csv_size > use_celery_threshold:
            if task_management.check_if_celery_available():
                logger.info(_("Delegating load to Celery task"))
                tasks.load_single_csv.apply_async(
                    (self.loadid, graphid, has_headers, fieldnames, csv_file_name, id_label),
                )
                result = _("delegated_to_celery")
                return {"success": True, "data": result}
            else:
                err = _("Celery appears not to be running. You need to have celery running in order to import a large csv.")
                with connection.cursor() as cursor:
                    cursor.execute(
                        """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                        ("failed", datetime.now(), self.loadid),
                    )
                return {"success": False, "data": err}

        else:
            response = self.run_load_task(self.loadid, graphid, has_headers, fieldnames, csv_file_name, id_label)

        return response

    def run_load_task(self, loadid, graphid, has_headers, fieldnames, csv_file_name, id_label):

        self.populate_staging_table(loadid, graphid, has_headers, fieldnames, csv_file_name, id_label)

        validation = self.validate()
        if len(validation["data"]) != 0:
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("failed", datetime.now(), loadid),
                )
            return {"success": False, "data": "failed"}
        else:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT * FROM __arches_staging_to_tile(%s)""", [loadid])
                    row = cursor.fetchall()
            except (IntegrityError, ProgrammingError) as e:
                logger.error(e)
                with connection.cursor() as cursor:
                    cursor.execute(
                        """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                        ("failed", datetime.now(), loadid),
                    )
                return {
                    "status": 400,
                    "success": False,
                    "title": _("Failed to complete load"),
                    "message": _("Unable to insert record into staging table"),
                }

        if row[0][0]:
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE load_event SET (status, load_end_time) = (%s, %s) WHERE loadid = %s""",
                    ("completed", datetime.now(), loadid),
                )
            index_resources_by_transaction(loadid, quiet=True, use_multiprocessing=False)
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE load_event SET (status, indexed_time, complete, successful) = (%s, %s, %s, %s) WHERE loadid = %s""",
                    ("indexed", datetime.now(), True, True, loadid),
                )
            return {"success": True, "data": "success"}
        else:
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                    ("failed", datetime.now(), loadid),
                )
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

    def populate_staging_table(self, loadid, graphid, has_headers, fieldnames, csv_file_name, id_label):

        temp_dir = os.path.join("uploadedfiles", "tmp", loadid)
        csv_file_path = os.path.join(temp_dir, csv_file_name)

        with default_storage.open(csv_file_path, mode="r") as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)

            if has_headers:
                next(reader)

            with connection.cursor() as cursor:
                for row in reader:
                    if id_label in row:
                        try:
                            resourceid = uuid.UUID(row[id_label])
                            legacyid = None
                        except (AttributeError, ValueError):
                            resourceid = uuid.uuid4()
                            legacyid = row[id_label]
                    else:
                        resourceid = uuid.uuid4()
                        legacyid = None

                    dict_by_nodegroup = {}

                    for key in row:
                        if key != "" and key != id_label:
                            current_node = self.get_node_lookup(graphid).get(alias=key)
                            nodegroupid = str(current_node.nodegroup_id)
                            node = str(current_node.nodeid)
                            datatype = self.node_lookup[graphid].get(nodeid=node).datatype
                            datatype_instance = self.datatype_factory.get_instance(datatype)
                            source_value = row[key]
                            if datatype == "file-list":
                                config = current_node.config
                                config["path"] = temp_dir
                                value = (
                                    datatype_instance.transform_value_for_tile(source_value, **config) if source_value is not None else None
                                )
                                errors = datatype_instance.validate(value, nodeid=node, path=temp_dir)
                            else:
                                value = datatype_instance.transform_value_for_tile(source_value) if source_value is not None else None
                                errors = datatype_instance.validate(value)
                            valid = True if len(errors) == 0 else False
                            error_message = ""
                            for error in errors:
                                error_message = (
                                    "{0}|{1}".format(error_message, error["message"]) if error_message != "" else error["message"]
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
                        for node in dict_by_nodegroup[nodegroup]:
                            for key in node:
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
                                passes_validation
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (
                                nodegroup,
                                legacyid,
                                resourceid,
                                tileid,
                                tile_value_json,
                                loadid,
                                node_depth,
                                csv_file_name,
                                passes_validation,
                            ),
                        )

                cursor.execute("""CALL __arches_check_tile_cardinality_violation_for_load(%s)""", [loadid])

        self.delete_from_default_storage(temp_dir)

        message = "staging table populated"
        return {"success": True, "data": message}

    def delete_from_default_storage(self, directory):
        dirs, files = default_storage.listdir(directory)
        for dir in dirs:
            dir_path = os.path.join(directory, dir)
            self.delete_from_default_storage(dir_path)
        for file in files:
            file_path = os.path.join(directory, file)
            default_storage.delete(file_path)
        default_storage.delete(directory)

    def get_blank_tile_lookup(self, nodegroupid):
        if nodegroupid not in self.blank_tile_lookup.keys():
            self.blank_tile_lookup[nodegroupid] = {}
            with connection.cursor() as cursor:
                cursor.execute("""SELECT nodeid FROM nodes WHERE datatype <> 'semantic' AND nodegroupid = %s;""", [nodegroupid])
                for row in cursor.fetchall():
                    (nodeid,) = row
                    self.blank_tile_lookup[nodegroupid][str(nodeid)] = None
        return self.blank_tile_lookup[nodegroupid]
