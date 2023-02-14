from datetime import datetime
import json
import logging
import uuid
from django.db import connection
from django.db.models.functions import Lower
from django.utils.translation import ugettext as _
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.etl_modules.base_import_module import BaseImportModule
from arches.app.models.models import GraphModel, Node
from arches.app.models.system_settings import settings
import arches.app.tasks as tasks
from arches.app.utils.index_database import index_resources_by_transaction

logger = logging.getLogger(__name__)


class BaseDataEditor(BaseImportModule):
    def __init__(self, request=None, loadid=None):
        self.request = request if request else None
        self.userid = request.user.id if request else None
        self.loadid = request.POST.get("load_id") if request else loadid
        self.moduleid = request.POST.get("module") if request else None
        self.datatype_factory = DataTypeFactory()
        self.node_lookup = {}

    def get_graphs(self, request):
        graph_name_i18n = "name__" + settings.LANGUAGE_CODE
        graphs = (
            GraphModel.objects.all()
            .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(isresource=False)
            .exclude(publication_id__isnull=True)
            .order_by(graph_name_i18n)
        )
        return {"success": True, "data": graphs}

    def get_nodes(self, request):
        graphid = request.POST.get("graphid")
        nodes = Node.objects.filter(graph_id=graphid, datatype="string").order_by(Lower("name"))
        return {"success": True, "data": nodes}

    def get_node_lookup(self, graphid):
        if graphid not in self.node_lookup.keys():
            self.node_lookup[graphid] = Node.objects.filter(graph_id=graphid)
        return self.node_lookup[graphid]

    def create_load_event(self, cursor, load_details):
        result = {"success": False}
        load_details_json = json.dumps(load_details)
        try:
            cursor.execute(
                """INSERT INTO load_event (loadid, etl_module_id, load_details, complete, status, load_start_time, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (self.loadid, self.moduleid, load_details_json, False, "running", datetime.now(), self.userid),
            )
            result["success"] = True
        except Exception as e:
            logger.error(e)
            result["message"] = _("Unable to initialize load: {}").format(str(e))

        return result

    def stage_data(self, cursor, graph_id, node_id, resourceids):
        result = {"success": False}
        try:
            cursor.execute(
                """SELECT * FROM __arches_stage_data_for_bulk_edit(%s, %s, %s, %s, %s)""",
                (self.loadid, graph_id, node_id, self.moduleid, (resourceids)),
            )
            result["success"] = True
        except Exception as e:
            logger.error(e)
            result["message"] = _("Unable to stage data: {}").format(str(e))

        return result

    def edit_staged_data(self, cursor, graph_id, node_id, operation, language_code, old_text, new_text):
        result = {"success": False}
        try:
            cursor.execute(
                """SELECT * FROM __arches_edit_staged_data(%s, %s, %s, %s, %s, %s, %s)""",
                (self.loadid, graph_id, node_id, language_code, operation, old_text, new_text),
            )
            result["success"] = True
        except Exception as e:
            logger.error(e)
            result["message"] = _("Unable to edit staged data: {}").format(str(e))
        return result

    def log_event(self, cursor, status):
        cursor.execute(
            """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
            (status, datetime.now(), self.loadid),
        )

    def validate(self, request):
        return {"success": True, "data": {}}

    def preview(self, request):
        def get_first_five_values(graph_id, node_id, language_code):
            # if language_code is None:
            #     language_code = 'en'
            # graph_query = ''
            # if graph_id is not None:
            #     graph_query = "n.graphid = '{}'".format(graph_id)
            # else:

            # print(graph_id, node_id, language_code)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT t.tiledata -> %s -> %s ->> 'value' FROM tiles t, nodes n
                    WHERE t.nodegroupid = n.nodegroupid
                    AND n.graphid = %s AND n.nodeid = %s
                    LIMIT 5;""", [node_id, language_code, graph_id, node_id])
                row = [value[0] for value in cursor.fetchall()]
            return row

        graph_id = request.POST.get("graph_id", None)
        node_id = request.POST.get("node_id", None)
        operation = request.POST.get("operation", None)
        language_code = request.POST.get("language_code", None)
        old_text = request.POST.get("old_text", None)
        new_text = request.POST.get("new_text", None)
        resourceids = request.POST.get("resourceids", None)
        first_five_values = get_first_five_values(graph_id, node_id, language_code)
        return_list = []
        with connection.cursor() as cursor:
            for value in first_five_values:
                if operation == 'replace':
                    cursor.execute("""SELECT * FROM REPLACE(%s, %s, %s);""", [value, old_text, new_text])
                    transformed_value = cursor.fetchone()[0]
                elif operation == 'trim':
                    cursor.execute("""SELECT * FROM TRIM(%s);""", [value])
                    transformed_value = cursor.fetchone()[0]
                elif operation == 'capitalize':
                    cursor.execute("""SELECT * FROM INITCAP(%s);""", [value])
                    transformed_value = cursor.fetchone()[0]
                elif operation == 'upper':
                    cursor.execute("""SELECT * FROM UPPER(%s);""", [value])
                    transformed_value = cursor.fetchone()[0]
                elif operation == 'lower':
                    cursor.execute("""SELECT * FROM LOWER(%s);""", [value])
                    transformed_value = cursor.fetchone()[0]
                return_list.append([value, transformed_value])

        return {"success": True, "data": return_list}


    def write(self, request):
        graph_id = request.POST.get("graph_id", None)
        node_id = request.POST.get("node_id", None)
        node_name = request.POST.get("node_name", None)
        operation = request.POST.get("operation", None)
        language_code = request.POST.get("language_code", None)
        old_text = request.POST.get("old_text", None)
        new_text = request.POST.get("new_text", None)
        resourceids = request.POST.get("resourceids", None)
        use_celery_bulk_edit = True
        if operation == 'replace':
            operation_details = "{} -> {}".format(old_text, new_text)
        else:
            operation_details = 'N/A'
        load_details = { "graph": graph_id, "node": node_name, "operation": operation, "details": operation_details }

        if resourceids:
            resourceids = [uuid.UUID(id) for id in json.loads(resourceids)]

        with connection.cursor() as cursor:
            event_created = self.create_load_event(cursor, load_details)
            if event_created["success"]:
                if use_celery_bulk_edit:
                    response = self.load_data_async(request)
                else:
                    response = self.run_load_task(self.loadid, graph_id, node_id, operation, language_code, old_text, new_text, resourceids)
            else:
                self.log_event(cursor, "failed")
                return {"success": False, "data": event_created["message"]}

        return response

    def run_load_task_async(self, request):
        graph_id = request.POST.get("graph_id", None)
        node_id = request.POST.get("node_id", None)
        operation = request.POST.get("operation", None)
        language_code = request.POST.get("language_code", None)
        old_text = request.POST.get("old_text", None)
        new_text = request.POST.get("new_text", None)
        resourceids = request.POST.get("resourceids", None)
        tasks.edit_bulk_data.apply_async(
            (self.loadid, graph_id, node_id, operation, language_code, old_text, new_text, resourceids, self.userid),
        )

    def run_load_task(self, loadid, graph_id, node_id, operation, language_code, old_text, new_text, resourceids):
        with connection.cursor() as cursor:
            data_staged = self.stage_data(cursor, graph_id, node_id, resourceids)

            if data_staged["success"]:
                data_updated = self.edit_staged_data(cursor, graph_id, node_id, operation, language_code, old_text, new_text)
            else:
                self.log_event(cursor, "failed")
                return {"success": False, "data": data_staged["message"]}

        if data_updated["success"]:
            data_updated = self.save_to_tiles(loadid)
            return {"success": True, "data": "done"}
        else:
            return {"success": False, "data": data_updated["message"]}
