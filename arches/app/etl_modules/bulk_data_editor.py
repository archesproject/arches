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
from arches.app.utils.index_database import index_resources_by_transaction

logger = logging.getLogger(__name__)

# details = {
#     "etlmoduleid": "6d0e7625-5792-4b83-b14b-82f603913706",
#     "name": "Bulk Data Editor",
#     "description": "Edit Existing Data in Arches",
#     "etl_type": "edit",
#     "component": "views/components/etl_modules/bulk-data-editor",
#     "componentname": "bulk-data-editor",
#     "modulename": "bulk_data_editor.py",
#     "classname": "BulkDataEditor",
#     "config": '{"bgColor": "#5B8899", "circleColor": "#AEC6CF", "show": true}',
#     "icon": "fa fa-upload",
#     "slug": "bulk-data-editor"
# }


class BulkDataEditor(BaseImportModule):
    def __init__(self, request=None):
        self.request = request if request else None
        self.userid = request.user.id if request else None
        self.loadid = request.POST.get("load_id") if request else None
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
        """
        Only returing nodes that belong to the top cards at the moment
        """

        graphid = request.POST.get("graphid")
        nodes = Node.objects.filter(graph_id=graphid, datatype="string").order_by(Lower("name"))
        return {"success": True, "data": nodes}

    def get_node_lookup(self, graphid):
        if graphid not in self.node_lookup.keys():
            self.node_lookup[graphid] = Node.objects.filter(graph_id=graphid)
        return self.node_lookup[graphid]

    def create_load_event(self, cursor, request):
        result = {"success": False}
        try:
            cursor.execute(
                """INSERT INTO load_event (loadid, etl_module_id, complete, status, load_start_time, user_id) VALUES (%s, %s, %s, %s, %s, %s)""",
                (self.loadid, self.moduleid, False, "running", datetime.now(), self.userid),
            )
            result["success"] = True
        except Exception as e:
            logger.error(e)
            result["message"] = _("Unable to initialize load: {}").format(str(e))

        return result

    def stage_data(self, cursor, request):
        graph_id = request.POST.get("graph_id")
        node_id = request.POST.get("node_id")
        resourceids = request.POST.get("resourceids")
        print(resourceids)
        if resourceids:
            resourceids = [uuid.UUID(id) for id in json.loads(resourceids)]
        print(resourceids)

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

    def edit_staged_data(self, cursor, request):
        graph_id = request.POST.get("graph_id", None)
        node_id = request.POST.get("node_id", None)
        operation = request.POST.get("operation", None)
        language_code = request.POST.get("language_code")
        old_text = request.POST.get("old_text", None)
        new_text = request.POST.get("new_text", None)

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

    def save_edits_to_tiles(self, cursor, request):
        result = {"success": False}
        try:
            cursor.execute("""SELECT * FROM __arches_save_tile_for_edit(%s)""", [self.loadid])
            result["success"] = True

        except Exception as e:
            logger.error(e)
            result["message"] = _("Unable to save the edits to tiles: {}").format(str(e))
        return result

    def log_event(self, cursor, status):
        cursor.execute(
            """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
            (status, datetime.now(), self.loadid),
        )

    def validate(self, request):
        return {"success": True, "data": {}}

    def write(self, request):
        with connection.cursor() as cursor:
            event_created = self.create_load_event(cursor, request)
            if event_created["success"]:
                data_staged = self.stage_data(cursor, request)
            else:
                self.log_event(cursor, "failed")
                return {"success": False, "data": event_created["message"]}

            if data_staged["success"]:
                data_updated = self.edit_staged_data(cursor, request)
            else:
                self.log_event(cursor, "failed")
                return {"success": False, "data": data_staged["message"]}

            if data_updated["success"]:
                data_updated = self.save_to_tiles(cursor, self.loadid)
                self.log_event(cursor, "completed")

                index_resources_by_transaction(self.loadid)
                cursor.execute(
                    """UPDATE load_event SET (complete, successful, status, indexed_time) = (%s, %s, %s, %s) WHERE loadid = %s""",
                    (True, True, "indexed", datetime.now(), self.loadid),
                )

                return {"success": True, "data": "done"}
            else:
                self.log_event(cursor, "failed")
                return {"success": False, "data": data_updated["message"]}
