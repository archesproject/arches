from datetime import datetime
import json
import logging
import requests
from urllib.parse import urlparse, urlunparse
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


class BaseBulkEditor(BaseImportModule):
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

        def dictfetchall(cursor):
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT n.*, c.name as card_name, w.label as widget_label
                FROM cards c, nodes n, cards_x_nodes_x_widgets w
                WHERE n.nodeid = w.nodeid
                AND w.cardid = c.cardid
                AND n.datatype = 'string'
                AND n.graphid = %s
                ORDER BY w.label;
            """,
                [graphid],
            )
            nodes = dictfetchall(cursor)
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

    def log_event(self, cursor, status):
        cursor.execute(
            """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
            (status, datetime.now(), self.loadid),
        )

    def get_resourceids_from_search_url(self, search_url):
        parsed_url = urlparse(search_url)
        search_result_url = urlunparse(parsed_url._replace(path="/search/resources"))
        response = requests.get(search_result_url + "&export=true")
        search_results = response.json()["results"]["hits"]["hits"]
        return [result["_source"]["resourceinstanceid"] for result in search_results]

    def validate(self, request):
        return {"success": True, "data": {}}


class BulkStringEditor(BaseBulkEditor):
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

    def preview(self, request):
        def get_first_five_values(graph_id, node_id, resourceids, language_code):
            node_id_query = ""
            graph_id_query = ""
            resourceids_query = ""
            if node_id:
                node_id_query = " AND nodeid = '{}'".format(node_id)
            if graph_id:
                graph_id_query = " AND graphid = '{}'".format(graph_id)
            if resourceids:
                resourceids_query = " AND resourceinstanceid IN {}".format(resourceids)
            if language_code is None:
                language_code = "en"

            sql_query = (
                """
                SELECT t.tiledata -> '{}' -> '{}' ->> 'value' FROM tiles t, nodes n
                WHERE t.nodegroupid = n.nodegroupid
            """.format(
                    node_id, language_code
                )
                + node_id_query
                + graph_id_query
                + resourceids_query
                + " LIMIT 5;"
            )

            tile_count_query = (
                """
                SELECT count(t.tileid) FROM tiles t, nodes n
                WHERE t.nodegroupid = n.nodegroupid
            """
                + node_id_query
                + graph_id_query
                + resourceids_query
            )

            resource_count_query = (
                """
                SELECT count(n.resourceinstanceid) FROM resource_instances n
                WHERE 0 = 0
            """
                + graph_id_query
                + resourceids_query
            )

            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                row = [value[0] for value in cursor.fetchall()]

                cursor.execute(tile_count_query)
                count = cursor.fetchall()
                (number_of_tiles,) = count[0]

                cursor.execute(resource_count_query)
                count = cursor.fetchall()
                (number_of_resources,) = count[0]

            return row, number_of_tiles, number_of_resources

        graph_id = request.POST.get("graph_id", None)
        node_id = request.POST.get("node_id", None)
        operation = request.POST.get("operation", None)
        language_code = request.POST.get("language_code", None)
        old_text = request.POST.get("old_text", None)
        new_text = request.POST.get("new_text", None)
        resourceids = request.POST.get("resourceids", None)
        case_insensitive = request.POST.get("case_insensitive", None)
        also_trim = request.POST.get("also_trim", "false")
        search_url = request.POST.get("search_url", None)

        if resourceids:
            resourceids = json.loads(resourceids)
        if search_url:
            resourceids = self.get_resourceids_from_search_url(search_url)
        if resourceids:
            resourceids = tuple(resourceids)
            if len(resourceids) == 1:
                resourceids = "('{}')".format(resourceids[0])
        if case_insensitive == "true" and operation == "replace":
            operation = "replace_i"
        if also_trim == "true":
            operation = operation + "_trim"

        first_five_values, number_of_tiles, number_of_resources = get_first_five_values(graph_id, node_id, resourceids, language_code)
        return_list = []
        with connection.cursor() as cursor:
            for value in first_five_values:
                if operation == "replace":
                    cursor.execute("""SELECT * FROM REPLACE(%s, %s, %s);""", [value, old_text, new_text])
                elif operation == "replace_i":
                    cursor.execute("""SELECT * FROM REGEXP_REPLACE(%s, %s, %s, 'i');""", [value, old_text, new_text])
                elif operation == "trim":
                    cursor.execute("""SELECT * FROM TRIM(%s);""", [value])
                elif operation == "capitalize":
                    cursor.execute("""SELECT * FROM INITCAP(%s);""", [value])
                elif operation == "capitalize_trim":
                    cursor.execute("""SELECT * FROM TRIM(INITCAP(%s));""", [value])
                elif operation == "upper":
                    cursor.execute("""SELECT * FROM UPPER(%s);""", [value])
                elif operation == "upper_trim":
                    cursor.execute("""SELECT * FROM TRIM(UPPER(%s));""", [value])
                elif operation == "lower":
                    cursor.execute("""SELECT * FROM LOWER(%s);""", [value])
                elif operation == "lower_trim":
                    cursor.execute("""SELECT * FROM TRIM(LOWER(%s));""", [value])
                transformed_value = cursor.fetchone()[0]
                return_list.append([value, transformed_value])

        return {
            "success": True,
            "data": {"value": return_list, "number_of_tiles": number_of_tiles, "number_of_resources": number_of_resources},
        }

    def write(self, request):
        graph_id = request.POST.get("graph_id", None)
        node_id = request.POST.get("node_id", None)
        node_name = request.POST.get("node_name", None)
        operation = request.POST.get("operation", None)
        language_code = request.POST.get("language_code", None)
        old_text = request.POST.get("old_text", None)
        new_text = request.POST.get("new_text", None)
        resourceids = request.POST.get("resourceids", None)
        case_insensitive = request.POST.get("case_insensitive", "false")
        also_trim = request.POST.get("also_trim", "false")
        search_url = request.POST.get("search_url", None)

        if resourceids:
            resourceids = json.loads(resourceids)
        if search_url:
            resourceids = self.get_resourceids_from_search_url(search_url)
        if resourceids:
            resourceids = [uuid.UUID(id) for id in resourceids]

        if case_insensitive == "true" and operation == "replace":
            operation = "replace_i"
        if also_trim == "true":
            operation = operation + "_trim"

        use_celery_bulk_edit = True
        operation_details = {
            "old_text": old_text,
            "new_text": new_text,
        }
        load_details = {
            "graph": graph_id,
            "node": node_name,
            "operation": operation,
            "details": operation_details,
            "search_url": search_url,
            "language_code": language_code,
        }

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
        case_insensitive = request.POST.get("case_insensitive", None)
        also_trim = request.POST.get("also_trim", "false")
        search_url = request.POST.get("search_url", None)

        if resourceids:
            resourceids = json.loads(resourceids)
        if search_url:
            resourceids = self.get_resourceids_from_search_url(search_url)

        if case_insensitive == "true" and operation == "replace":
            operation = "replace_i"
        if also_trim == "true":
            operation = operation + "_trim"

        edit_task = tasks.edit_bulk_string_data.apply_async(
            (self.loadid, graph_id, node_id, operation, language_code, old_text, new_text, resourceids, self.userid),
        )
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET taskid = %s WHERE loadid = %s""",
                (edit_task.task_id, self.loadid),
            )

    def run_load_task(self, loadid, graph_id, node_id, operation, language_code, old_text, new_text, resourceids):
        if resourceids:
            resourceids = [uuid.UUID(id) for id in resourceids]

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
