from datetime import datetime
import json
import logging
from urllib.parse import urlsplit, parse_qs
import uuid
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import connection
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import GraphModel, Node, ETLModule, LoadStaging
from arches.app.models.system_settings import settings
from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    FiltersAgg,
    Match,
    Nested,
    NestedAgg,
    Query,
    Terms,
    Wildcard,
    Regex,
)
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineFactory
import arches.app.tasks as tasks
from arches.app.etl_modules.decorators import load_data_async
from arches.app.etl_modules.save import get_resourceids_from_search_url, save_to_tiles
from arches.app.utils.decorators import user_created_transaction_match
import arches.app.utils.task_management as task_management
from arches.app.utils.db_utils import dictfetchall
from arches.app.utils.transaction import reverse_edit_log_entries
from arches.app.views.search import search_results

logger = logging.getLogger(__name__)


class MissingRequiredInputError(Exception):
    pass


class BaseBulkEditor:
    def __init__(self, request=None, loadid=None):
        self.request = request if request else None
        self.userid = request.user.id if request else None
        self.loadid = request.POST.get("load_id") if request else loadid
        self.moduleid = request.POST.get("module") if request else None
        self.datatype_factory = DataTypeFactory()
        self.node_lookup = {}

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

    def get_graphs(self, request):
        graph_name_i18n = "name__" + settings.LANGUAGE_CODE
        graphs = (
            GraphModel.objects.all()
            .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(isresource=False)
            .exclude(source_identifier__isnull=False)
            .order_by(graph_name_i18n)
        )
        return {"success": True, "data": graphs}

    def get_nodes(self, request):
        graphid = request.POST.get("graphid")

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

    def get_nodegroups(self, request):
        graphid = request.POST.get("graphid")

        with connection.cursor() as cursor:
            cursor.execute(
                """
                WITH RECURSIVE card_tree(nodegroupid, parentnodegroupid, name) AS (
                    SELECT ng.nodegroupid, ng.parentnodegroupid, c.name ->> %s name
                    FROM node_groups ng, cards c
                    WHERE c.nodegroupid = ng.nodegroupid
                    AND c.graphid = %s
                    AND ng.parentnodegroupid IS null
                    AND c.visible = true
                UNION
                    SELECT ng.nodegroupid, ng.parentnodegroupid, (ct.name || ' > ' || (c.name ->> %s)) name
                    FROM node_groups ng, cards c, card_tree ct
                    WHERE ng.parentnodegroupid = ct.nodegroupid
                    AND c.nodegroupid = ng.nodegroupid
                    AND c.visible = true
                )
                SELECT nodegroupid, name FROM card_tree ORDER BY name
            """,
                [settings.LANGUAGE_CODE, graphid, settings.LANGUAGE_CODE],
            )
            nodegroups = dictfetchall(cursor)
        return {"success": True, "data": nodegroups}

    def create_load_event(self, cursor, load_details):
        result = {"success": False}
        load_details_json = json.dumps(load_details)
        try:
            load_description = "Preparing the load..."
            cursor.execute(
                """INSERT INTO load_event (loadid, etl_module_id, load_details, complete, status, load_description, load_start_time, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    self.loadid,
                    self.moduleid,
                    load_details_json,
                    False,
                    "running",
                    load_description,
                    datetime.now(),
                    self.userid,
                ),
            )
            result["success"] = True
        except Exception as e:
            logger.error(e)
            result["message"] = _("Unable to initialize load: {}").format(str(e))

        return result

    def stage_data(
        self,
        cursor,
        module_id,
        graph_id,
        node_id,
        resourceids,
        operation,
        pattern,
        new_text,
        language_code,
        case_insensitive,
    ):
        result = {"success": False}
        update_limit = ETLModule.objects.get(pk=module_id).config["updateLimit"]
        try:
            cursor.execute(
                """SELECT * FROM __arches_stage_string_data_for_bulk_edit(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    self.loadid,
                    graph_id,
                    node_id,
                    self.moduleid,
                    (resourceids),
                    operation,
                    pattern,
                    new_text,
                    language_code,
                    case_insensitive,
                    update_limit,
                ),
            )
            count_of_tiles_staged = LoadStaging.objects.filter(
                load_event=self.loadid
            ).count()
            self.log_event_details(
                cursor, f"done|{count_of_tiles_staged} tiles staged..."
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

    def log_event_details(self, cursor, details):
        cursor.execute(
            """UPDATE load_event SET load_description = concat(load_description, %s) WHERE loadid = %s""",
            (details, self.loadid),
        )

    def validate(self, request):
        raise NotImplementedError

    def validate_inputs(self, request):
        raise NotImplementedError


class BulkStringEditor(BaseBulkEditor):
    def validate(self, request):
        return {"success": True, "data": {}}

    def validate_inputs(self, request):
        operation = request.POST.get("operation", None)
        required_inputs = {
            "graph_id": _("Resource Model"),
            "node_id": _("Node"),
            "operation": _("Edit Operation"),
            "language_code": _("Language"),
        }
        if operation == "replace":
            required_inputs = required_inputs | {
                "old_text": _("Old Text"),
                "new_text": _("New Text"),
            }

        for required_input, display_value in required_inputs.items():
            if request.POST.get(required_input, None) is None:
                ret = _("Missing required value: {required_input}").format(
                    required_input=display_value
                )
                raise MissingRequiredInputError(ret)

    def edit_staged_data(
        self, cursor, graph_id, node_id, operation, language_code, pattern, new_text
    ):
        result = {"success": False}
        try:
            cursor.execute(
                """SELECT * FROM __arches_edit_staged_string_data(%s, %s, %s, %s, %s, %s, %s)""",
                (
                    self.loadid,
                    graph_id,
                    node_id,
                    language_code,
                    operation,
                    pattern,
                    new_text,
                ),
            )
            result["success"] = True
        except Exception as e:
            logger.error(e)
            result["message"] = _("Unable to edit staged data: {}").format(str(e))
        return result

    def get_preview_data(
        self,
        node_id,
        search_url,
        language_code,
        operation,
        old_text,
        case_insensitive,
        whole_word,
        preview_limit,
    ):
        request = HttpRequest()
        request.user = self.request.user
        request.method = "GET"
        request.GET["paging-filter"] = 1
        request.GET["tiles"] = True

        if search_url:
            validate = URLValidator()
            validate(search_url)
            params = parse_qs(urlsplit(search_url).query)
            for k, v in params.items():
                request.GET.__setitem__(k, v[0])

        search_url_query = search_results(request, returnDsl=True).dsl["query"]
        case_insensitive = True if case_insensitive == "true" else False

        if old_text:
            if whole_word != "true":
                search_query = Wildcard(
                    field=f"tiles.data.{node_id}.{language_code}.value.keyword",
                    query=f"*{old_text}*",
                    case_insensitive=case_insensitive,
                )
            else:
                search_query = Regex(
                    field=f"tiles.data.{node_id}.{language_code}.value.keyword",
                    query=f"(.* {old_text} .*)|({old_text} .*)|(.* {old_text})|({old_text})",
                    case_insensitive=case_insensitive,
                )

            search_bool_agg = Bool()
            search_bool_agg.must(search_query)

        else:
            if operation.startswith("upper"):
                regexp = "(.*[a-z].*)"
            elif operation.startswith("lower"):
                regexp = "(.*[A-Z].*)"
            elif operation.startswith("capitalize"):
                regexp = "([a-z].*)|([A-Z][a-zA-Z]*[A-Z].*)|((.+[ ]+)[a-z].*)|((.+[ ]+)[A-Z][a-zA-Z]*[A-Z].*)"
            elif operation.startswith("trim"):
                regexp = "[ \t].*|.*[ \t]"

            case_search_query = Regex(
                field=f"tiles.data.{node_id}.{language_code}.value.keyword",
                query=regexp,
                case_insensitive=case_insensitive,
            )

            search_query = Bool()
            search_query.must(case_search_query)
            search_bool_agg = Bool()
            search_bool_agg.must(case_search_query)

        string_search_nested = Nested(path="tiles", query=search_query)
        inner_hits_query = {
            "inner_hits": {
                "_source": False,
                "docvalue_fields": [
                    f"tiles.data.{node_id}.{language_code}.value.keyword"
                ],
            }
        }
        string_search_nested.dsl["nested"].update(inner_hits_query)

        search_bool_query = Bool()
        search_bool_query.must(string_search_nested)

        search_url_query["bool"]["must"].append(search_bool_query.dsl)

        search_filter_agg = FiltersAgg(name="string_search")
        search_filter_agg.add_filter(search_bool_agg)

        nested_agg = NestedAgg(path="tiles", name="tile_agg")
        nested_agg.add_aggregation(search_filter_agg)

        se = SearchEngineFactory().create()
        query = Query(se, limit=preview_limit)

        query.add_query(search_url_query)
        query.add_aggregation(nested_agg)

        results = query.search(index=RESOURCES_INDEX)
        values = []
        for hit in results["hits"]["hits"]:
            for tile in hit["inner_hits"]["tiles"]["hits"]["hits"]:
                values.append(
                    tile["fields"][
                        f"tiles.data.{node_id}.{language_code}.value.keyword"
                    ][0]
                )

        number_of_resources = results["hits"]["total"]["value"]
        number_of_tiles = results["aggregations"]["tile_agg"]["string_search"][
            "buckets"
        ][0]["doc_count"]

        return values[:preview_limit], number_of_tiles, number_of_resources

    def preview(self, request):
        graph_id = request.POST.get("graph_id", None)
        node_id = request.POST.get("node_id", None)
        operation = request.POST.get("operation", None)
        language_code = request.POST.get("language_code", None)
        old_text = request.POST.get("old_text", None)
        new_text = request.POST.get("new_text", None)
        resourceids = request.POST.get("resourceids", None)
        case_insensitive = request.POST.get("case_insensitive", "false")
        whole_word = request.POST.get("whole_word", "false")
        also_trim = request.POST.get("also_trim", "false")
        search_url = request.POST.get("search_url", None)

        preview_limit = ETLModule.objects.get(pk=self.moduleid).config.get(
            "previewLimit", 5
        )

        try:
            self.validate_inputs(request)
        except MissingRequiredInputError as e:
            return {
                "success": False,
                "data": {"title": _("Missing input error"), "message": str(e)},
            }

        if resourceids:
            resourceids = json.loads(resourceids)
        if search_url:
            try:
                resourceids = get_resourceids_from_search_url(
                    search_url, self.request.user
                )
            except ValidationError:
                return {
                    "success": False,
                    "data": {
                        "title": _("Invalid Search Url"),
                        "message": _("Please, enter a valid search url"),
                    },
                }
        if resourceids:
            resourceids = tuple(resourceids)

        pattern = old_text
        if operation == "replace":
            if case_insensitive == "true":
                operation = "replace_i"
            if whole_word == "true":
                pattern = "\\y{0}\\y".format(old_text)

        if also_trim == "true":
            operation = operation + "_trim"

        try:
            first_five_values, number_of_tiles, number_of_resources = (
                self.get_preview_data(
                    node_id,
                    search_url,
                    language_code,
                    operation,
                    old_text,
                    case_insensitive,
                    whole_word,
                    preview_limit,
                )
            )
        except TypeError:
            return {
                "success": False,
                "data": {
                    "title": _("Invalid Search Url"),
                    "message": _("Please, enter a valid search url"),
                },
            }

        return_list = []
        with connection.cursor() as cursor:
            for value in first_five_values:
                if operation == "replace":
                    cursor.execute(
                        """SELECT * FROM REGEXP_REPLACE(%s, %s, %s, 'g');""",
                        [value, pattern, new_text],
                    )
                elif operation == "replace_i":
                    cursor.execute(
                        """SELECT * FROM REGEXP_REPLACE(%s, %s, %s, 'ig');""",
                        [value, pattern, new_text],
                    )
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
            "data": {
                "value": return_list,
                "number_of_tiles": number_of_tiles,
                "number_of_resources": number_of_resources,
                "preview_limit": preview_limit,
            },
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
        whole_word = request.POST.get("whole_word", "false")
        also_trim = request.POST.get("also_trim", "false")
        search_url = request.POST.get("search_url", None)

        try:
            self.validate_inputs(request)
        except MissingRequiredInputError as e:
            return {
                "success": False,
                "data": {"title": _("Missing input error"), "message": str(e)},
            }

        pattern = old_text
        if operation == "replace":
            if case_insensitive == "true":
                operation = "replace_i"
            if whole_word == "true":
                pattern = "\\y{0}\\y".format(old_text)

        if also_trim == "true":
            operation = operation + "_trim"

        load_details = {
            "graph": graph_id,
            "node": node_name,
            "operation": operation,
            "details": {
                "old_text": old_text,
                "new_text": new_text,
            },
            "search_url": search_url,
            "language_code": language_code,
        }

        with connection.cursor() as cursor:
            event_created = self.create_load_event(cursor, load_details)
            if not event_created["success"]:
                self.log_event(cursor, "failed")
                return {"success": False, "data": event_created["message"]}

        use_celery_bulk_edit = True

        if use_celery_bulk_edit:
            response = self.run_load_task_async(request, self.loadid)
        else:
            if resourceids:
                resourceids = json.loads(resourceids)
            if search_url:
                with connection.cursor() as cursor:
                    self.log_event_details(
                        cursor, "done|Getting resources from search url..."
                    )
                resourceids = get_resourceids_from_search_url(
                    search_url, self.request.user
                )
            if resourceids:
                resourceids = tuple(resourceids)
            response = self.run_load_task(
                self.userid,
                self.loadid,
                self.moduleid,
                graph_id,
                node_id,
                operation,
                language_code,
                pattern,
                new_text,
                resourceids,
            )

        return response

    @load_data_async
    def run_load_task_async(self, request):
        graph_id = request.POST.get("graph_id", None)
        node_id = request.POST.get("node_id", None)
        operation = request.POST.get("operation", None)
        language_code = request.POST.get("language_code", None)
        old_text = request.POST.get("old_text", None)
        new_text = request.POST.get("new_text", None)
        resourceids = request.POST.get("resourceids", None)
        case_insensitive = request.POST.get("case_insensitive", "false")
        whole_word = request.POST.get("whole_word", "false")
        also_trim = request.POST.get("also_trim", "false")
        search_url = request.POST.get("search_url", None)

        if resourceids:
            resourceids = json.loads(resourceids)
        if search_url:
            with connection.cursor() as cursor:
                self.log_event_details(
                    cursor, "done|Getting resources from search url..."
                )
            resourceids = get_resourceids_from_search_url(search_url, self.request.user)

        pattern = old_text
        if operation == "replace":
            if case_insensitive == "true":
                operation = "replace_i"
            if whole_word == "true":
                pattern = "\\y{0}\\y".format(old_text)

        if also_trim == "true":
            operation = operation + "_trim"

        edit_task = tasks.edit_bulk_string_data.apply_async(
            (
                self.userid,
                self.loadid,
                self.moduleid,
                graph_id,
                node_id,
                operation,
                language_code,
                pattern,
                new_text,
                resourceids,
            ),
        )
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET taskid = %s WHERE loadid = %s""",
                (edit_task.task_id, self.loadid),
            )

    def run_load_task(
        self,
        userid,
        loadid,
        module_id,
        graph_id,
        node_id,
        operation,
        language_code,
        pattern,
        new_text,
        resourceids,
    ):
        if resourceids:
            resourceids = [uuid.UUID(id) for id in resourceids]
        case_insensitive = False
        if operation == "replace_i":
            case_insensitive = True

        with connection.cursor() as cursor:
            self.log_event_details(cursor, "done|Staging the data for edit...")
            data_staged = self.stage_data(
                cursor,
                module_id,
                graph_id,
                node_id,
                resourceids,
                operation,
                pattern,
                new_text,
                language_code,
                case_insensitive,
            )

            if data_staged["success"]:
                self.log_event_details(cursor, "done|Editing the data...")
                data_updated = self.edit_staged_data(
                    cursor,
                    graph_id,
                    node_id,
                    operation,
                    language_code,
                    pattern,
                    new_text,
                )
            else:
                self.log_event(cursor, "failed")
                return {
                    "success": False,
                    "data": {"title": _("Error"), "message": data_staged["message"]},
                }

            if data_updated["success"]:
                self.loadid = loadid  # currently redundant, but be certain
                save_to_tiles(userid, loadid)
                return {"success": True, "data": "done"}
            else:
                self.log_event(cursor, "failed")
                return {
                    "success": False,
                    "data": {"title": _("Error"), "message": data_updated["message"]},
                }
