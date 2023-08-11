import logging
import os
import uuid

from django.core.files.storage import default_storage
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.db import connection

from arches.app.models.models import Node
from arches.app.utils.decorators import user_created_transaction_match
from arches.app.utils.transaction import reverse_edit_log_entries
import arches.app.tasks as tasks
import arches.app.utils.task_management as task_management

logger = logging.getLogger(__name__)


class BaseImportModule:
    def __init__(self, loadid=None):
        self.loadid = loadid
        self.legacyid_lookup = {}

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
        logger.warn(response)
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
