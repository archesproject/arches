from datetime import datetime
import json
import os
from django.db import connection
from arches.app.etl_modules.base_excel_exporter import BaseExcelExporter
from arches.app.etl_modules.decorators import load_data_async
from arches.app.models.models import Node
from arches.app.models.system_settings import settings
import arches.app.tasks as tasks
from arches.app.etl_modules.save import get_resourceids_from_search_url
from arches.app.utils.db_utils import dictfetchall
from arches.management.commands.etl_template import create_workbook

tile_tree_query = """
    WITH RECURSIVE tile_tree(tileid, parenttileid, tiledata, nodegroupid, depth) AS (
        SELECT
            t.tileid,
            t.parenttileid,
            t.tiledata,
            t.nodegroupid,
            0
        FROM
            tiles t
        WHERE tileid = (%s)
        UNION
            SELECT
                t.tileid,
                t.parenttileid,
                t.tiledata,
                t.nodegroupid,
                tt.depth + 1
            FROM
                tile_tree tt, tiles t
            WHERE
                t.parenttileid = tt.tileid
    )
    SEARCH DEPTH FIRST BY tileid SET ordercol
    SELECT * FROM tile_tree ORDER BY ordercol;
"""


class BranchExcelExporter(BaseExcelExporter):
    def __init__(self, request=None, loadid=None):
        self.request = request if request else None
        self.userid = request.user.id if request else None
        self.moduleid = request.POST.get("module") if request else None
        self.filename = request.POST.get("filename") if request else None
        self.loadid = loadid if loadid else None

    def run_export_task(
        self, load_id, graph_id, graph_name, resource_ids, *args, **kwargs
    ):
        if resource_ids is None:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT resourceinstanceid FROM resource_instances WHERE graphid = (%s)""",
                    [graph_id],
                )
                rows = cursor.fetchall()
                resource_ids = [row[0] for row in rows]

        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET load_details = %s WHERE  loadid = (%s)""",
                (
                    json.dumps(
                        {
                            "graph": graph_name,
                            "number_of_resources": len(resource_ids),
                        }
                    ),
                    load_id,
                ),
            )

            cursor.execute(
                """SELECT * FROM __get_nodegroup_tree_by_graph(%s)""", (graph_id,)
            )
            nodegroup_lookup = dictfetchall(cursor)

            nodes = Node.objects.filter(graph_id=graph_id)
            node_lookup_by_id = self.get_node_lookup_by_id(nodes)
            tiles_to_export = {}
            files_to_download = []

            for resource_id in resource_ids:
                cursor.execute(
                    """SELECT * FROM tiles WHERE parenttileid IS null AND resourceinstanceid = (%s)""",
                    [resource_id],
                )
                root_tiles = dictfetchall(cursor)
                for root_tile in root_tiles:
                    cursor.execute(tile_tree_query, [root_tile["tileid"]])
                    tile_tree = dictfetchall(cursor)
                    for tile in tile_tree:
                        root_nodegroup, nodegroup_alias = [
                            (ng["root_nodegroup"], ng["alias"])
                            for ng in nodegroup_lookup
                            if ng["nodegroupid"] == tile["nodegroupid"]
                        ][0]
                        root_alias = [
                            ng["alias"]
                            for ng in nodegroup_lookup
                            if ng["root_nodegroup"] == root_nodegroup
                        ][0]
                        tile["alias"] = nodegroup_alias
                        tile["resourceinstanceid"] = resource_id
                        tile_data = json.loads(tile["tiledata"])
                        for key, value in tile_data.items():
                            alias = node_lookup_by_id[key]["alias"]
                            if node_lookup_by_id[key]["datatype"] == "file-list":
                                file_names_to_export = []
                                if value is not None:
                                    for file in value:
                                        files_to_download.append(
                                            {
                                                "name": file["name"],
                                                "file_id": file["file_id"],
                                            }
                                        )
                                        file_names_to_export.append(file["name"])
                                    tile[alias] = ",".join(file_names_to_export)
                                else:
                                    tile[alias] = value
                            elif node_lookup_by_id[key]["datatype"] in [
                                "concept-list",
                                "domain-value-list",
                            ]:
                                if type(value) == list:
                                    value = ",".join(value)
                                tile[alias] = value
                            else:
                                try:
                                    value.keys()  # to check if it is a dictionary
                                    tile[alias] = json.dumps(value)
                                except AttributeError:
                                    tile[alias] = value
                        tiles_to_export.setdefault(root_alias, []).append(tile)

        wb = create_workbook(graph_id, tiles_to_export)

        user_generated_filename = self.filename or kwargs.get("filename")
        zip_file, download_files, skipped_files, files_not_found = (
            self.get_files_in_zip_file(
                files_to_download,
                graph_name,
                wb,
                user_generated_filename=user_generated_filename,
            )
        )

        zip_file_name = os.path.basename(zip_file.path.name)
        zip_file_url = settings.MEDIA_URL + zip_file.path.name

        load_details = {
            "graph": graph_name,
            "number_of_resources": len(resource_ids),
            "number_of_files": len(download_files),
            "skipped_files": skipped_files,
            "files_not_found": files_not_found,
            "zipfile": {
                "name": zip_file_name,
                "url": zip_file_url,
                "fileid": str(zip_file.fileid),
            },
        }

        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET (complete, status, load_details, load_end_time) = (%s, %s, %s, %s) WHERE  loadid = (%s)""",
                (True, "indexed", json.dumps(load_details), datetime.now(), load_id),
            )

        return {"success": True, "data": "success"}

    @load_data_async
    def run_load_task_async(self, request):
        self.loadid = request.POST.get("load_id")
        graph_id = request.POST.get("graph_id", None)
        graph_name = request.POST.get("graph_name", None)
        resource_ids = request.POST.get("resource_ids", None)
        filename = request.POST.get("filename")
        search_url = request.POST.get("search_url", None)
        if search_url and not resource_ids:
            resource_ids = get_resourceids_from_search_url(
                search_url, self.request.user
            )

        export_task = tasks.export_branch_excel.apply_async(
            (self.userid, self.loadid, graph_id, graph_name, resource_ids, filename),
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET taskid = %s WHERE loadid = %s""",
                (export_task.task_id, self.loadid),
            )
