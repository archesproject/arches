from datetime import datetime
import json
import logging
from urllib.parse import urlsplit, parse_qs
import uuid
from django.db import connection
from django.http import HttpRequest
from django.utils.translation import ugettext as _
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.etl_modules.base_import_module import BaseImportModule
from arches.app.models.models import GraphModel, Node
from arches.app.models.system_settings import settings
import arches.app.tasks as tasks
from arches.app.views.search import search_results

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

    def stage_data(self, cursor, graph_id, node_id, resourceids, text_replacing, language_code, case_insensitive):
        result = {"success": False}
        try:
            cursor.execute(
                """SELECT * FROM __arches_stage_string_data_for_bulk_edit(%s, %s, %s, %s, %s, %s, %s, %s)""",
                (self.loadid, graph_id, node_id, self.moduleid, (resourceids), text_replacing, language_code, case_insensitive),
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
        request = HttpRequest()
        request.user = self.request.user
        request.method = "GET"
        request.GET["export"] = True
        params = parse_qs(urlsplit(search_url).query)
        for k, v in params.items():
            request.GET.__setitem__(k, v[0])
        response = search_results(request)
        results = json.loads(response.content)['results']['hits']['hits']
        return [result["_source"]["resourceinstanceid"] for result in results]

    def validate(self, request):
        return {"success": True, "data": {}}


class BulkStringEditor(BaseBulkEditor):
    def edit_staged_data(self, cursor, graph_id, node_id, operation, language_code, old_text, new_text):
        result = {"success": False}
        try:
            cursor.execute(
                """SELECT * FROM __arches_edit_staged_string_data(%s, %s, %s, %s, %s, %s, %s)""",
                (self.loadid, graph_id, node_id, language_code, operation, old_text, new_text),
            )
            result["success"] = True
        except Exception as e:
            logger.error(e)
            result["message"] = _("Unable to edit staged data: {}").format(str(e))
        return result

    def get_preview_data(self, graph_id, node_id, resourceids, language_code, old_text, case_insensitive):
        node_id_query = " AND nodeid = %(node_id)s" if node_id else ""
        graph_id_query = " AND graphid = %(graph_id)s" if graph_id else ""
        resourceids_query = " AND resourceinstanceid IN %(resourceids)s" if resourceids else ""
        like_operator = "ilike" if case_insensitive == "true" else "like"
        old_text_like = "%" + old_text + "%" if old_text else ""
        text_query = (
            " AND t.tiledata -> %(node_id)s -> %(language_code)s ->> 'value' " + like_operator + " %(old_text)s" if old_text else ""
        )
        if language_code is None:
            language_code = "en"

        request_parmas_dict = {
            "node_id": node_id,
            "language_code": language_code,
            "graph_id": graph_id,
            "resourceids": resourceids,
            "old_text": old_text_like,
        }

        sql_query = (
            """
            SELECT t.tiledata -> %(node_id)s -> %(language_code)s ->> 'value' FROM tiles t, nodes n
            WHERE t.nodegroupid = n.nodegroupid
        """
            + node_id_query
            + graph_id_query
            + resourceids_query
            + text_query
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
            + text_query
        )

        resource_count_query = (
            """
            SELECT count(DISTINCT t.resourceinstanceid) FROM tiles t, nodes n
            WHERE t.nodegroupid = n.nodegroupid
        """
            + node_id_query
            + graph_id_query
            + resourceids_query
            + text_query
        )

        with connection.cursor() as cursor:
            cursor.execute(sql_query, request_parmas_dict)
            row = [value[0] for value in cursor.fetchall()]

            cursor.execute(tile_count_query, request_parmas_dict)
            count = cursor.fetchall()
            (number_of_tiles,) = count[0]

            cursor.execute(resource_count_query, request_parmas_dict)
            count = cursor.fetchall()
            (number_of_resources,) = count[0]

        return row, number_of_tiles, number_of_resources

    def preview(self, request):
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

        if case_insensitive == "true" and operation == "replace":
            operation = "replace_i"
        if also_trim == "true":
            operation = operation + "_trim"

        first_five_values, number_of_tiles, number_of_resources = self.get_preview_data(
            graph_id, node_id, resourceids, language_code, old_text, case_insensitive
        )
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
            resourceids = tuple(resourceids)

        if case_insensitive == "true" and operation == "replace":
            operation = "replace_i"
        if also_trim == "true":
            operation = operation + "_trim"

        use_celery_bulk_edit = True
        operation_details = {
            "old_text": old_text,
            "new_text": new_text,
        }

        first_five_values, number_of_tiles, number_of_resources = self.get_preview_data(
            graph_id, node_id, resourceids, language_code, old_text, case_insensitive
        )

        load_details = {
            "graph": graph_id,
            "node": node_name,
            "operation": operation,
            "details": operation_details,
            "search_url": search_url,
            "language_code": language_code,
            "number_of_resources": number_of_resources,
            "number_of_tiles": number_of_tiles,
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
        case_insensitive = False
        if operation == "replace_i":
            case_insensitive = True

        with connection.cursor() as cursor:
            data_staged = self.stage_data(cursor, graph_id, node_id, resourceids, old_text, language_code, case_insensitive)

            if data_staged["success"]:
                data_updated = self.edit_staged_data(cursor, graph_id, node_id, operation, language_code, old_text, new_text)
            else:
                self.log_event(cursor, "failed")
                return {"success": False, "data": {"title": _("Error"), "message": data_staged["message"]}}

        if data_updated["success"]:
            data_updated = self.save_to_tiles(loadid)
            return {"success": True, "data": "done"}
        else:
            with connection.cursor() as cursor:
                self.log_event(cursor, "failed")
            return {"success": False, "data": {"title": _("Error"), "message": data_updated["message"]}}
