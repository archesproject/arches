from datetime import datetime
import json
import logging
from urllib.parse import urlsplit, parse_qs
import uuid
from django.db import connection
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import GraphModel, Node, ETLModule
from arches.app.models.system_settings import settings
from arches.app.search.elasticsearch_dsl_builder import Bool, Exists, FiltersAgg, Nested, NestedAgg, Query, Wildcard
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineFactory
import arches.app.tasks as tasks
from arches.app.etl_modules.base_data_editor import BaseBulkEditor
from arches.app.etl_modules.decorators import load_data_async
from arches.app.etl_modules.save import save_to_tiles
from arches.app.utils.decorators import user_created_transaction_match
import arches.app.utils.task_management as task_management
from arches.app.utils.transaction import reverse_edit_log_entries
from arches.app.views.search import search_results

logger = logging.getLogger(__name__)



class BulkDataDeletion(BaseBulkEditor):
    def write(self, request):
        graph_id = request.POST.get("graph_id", None)
        nodegroup_id = request.POST.get("nodegroup_id", None)
        nodegroup_name = request.POST.get("nodegroup_name", None)
        resourceids = request.POST.get("resourceids", None)
        search_url = request.POST.get("search_url", None)

        if resourceids:
            resourceids = json.loads(resourceids)
        if resourceids:
            resourceids = tuple(resourceids)
        if search_url:
            resourceids = self.get_resourceids_from_search_url(search_url)

        use_celery_bulk_edit = False

        load_details = {
            "graph": graph_id,
            "nodegroup": nodegroup_name,
            "search_url": search_url,
            # "number_of_resources": number_of_resources,
            # "number_of_tiles": number_of_tiles,
        }

        with connection.cursor() as cursor:
            event_created = self.create_load_event(cursor, load_details)
            if event_created["success"]:
                if use_celery_bulk_edit:
                    response = self.run_load_task_async(request, self.loadid)
                else:
                    response = self.run_load_task(self.userid, self.loadid, self.moduleid, graph_id, nodegroup_id, resourceids)
            else:
                self.log_event(cursor, "failed")
                return {"success": False, "data": event_created["message"]}

        return response

    @load_data_async
    def run_load_task_async(self, request):
        graph_id = request.POST.get("graph_id", None)
        nodegroup_id = request.POST.get("nodegroup_id", None)
        resourceids = request.POST.get("resourceids", None)
        search_url = request.POST.get("search_url", None)

        if resourceids:
            resourceids = json.loads(resourceids)
        if search_url:
            resourceids = self.get_resourceids_from_search_url(search_url)

        edit_task = tasks.edit_bulk_string_data.apply_async(
            (self.userid, self.loadid, self.moduleid, graph_id, nodegroup_id, resourceids),
        )
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET taskid = %s WHERE loadid = %s""",
                (edit_task.task_id, self.loadid),
            )

    def run_load_task(self, userid, loadid, module_id, graph_id, nodgroup_id, resourceids):
        if resourceids:
            resourceids = [uuid.UUID(id) for id in resourceids]

        with connection.cursor() as cursor:
            data_staged = self.stage_data(cursor, module_id, graph_id, nodegroup_id, resourceids)

            if data_staged["success"]:
                data_updated = self.edit_staged_data(cursor, graph_id, nodegroup_id)
            else:
                self.log_event(cursor, "failed")
                return {"success": False, "data": {"title": _("Error"), "message": data_staged["message"]}}

        if data_updated["success"]:
            self.loadid = loadid  # currently redundant, but be certain
            data_updated = save_to_tiles(userid, loadid, finalize_import=False)
            return {"success": True, "data": "done"}
        else:
            with connection.cursor() as cursor:
                self.log_event(cursor, "failed")
            return {"success": False, "data": {"title": _("Error"), "message": data_updated["message"]}}
