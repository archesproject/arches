from datetime import datetime
import json
import os
from django.db import connection
from arches.app.etl_modules.base_excel_exporter import BaseExcelExporter
from arches.app.etl_modules.decorators import load_data_async
from arches.app.models.card import Card
from arches.app.models.models import Node
from arches.app.models.system_settings import settings
from arches.app.etl_modules.save import get_resourceids_from_search_url
import arches.app.tasks as tasks
from arches.app.utils.db_utils import dictfetchall
from arches.management.commands.etl_template import create_tile_excel_workbook


class TileExcelExporter(BaseExcelExporter):
    def __init__(self, request=None, loadid=None):
        self.request = request if request else None
        self.userid = request.user.id if request else None
        self.moduleid = request.POST.get("module") if request else None
        self.filename = request.POST.get("filename") if request else None
        self.loadid = loadid if loadid else None

    def run_export_task(
        self, load_id, graph_id, graph_name, resource_ids, *args, **kwargs
    ):
        concept_export_value_type = (
            "id" if kwargs.get("export_concepts_as") == "uuids" else None
        )

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

            nodes = Node.objects.filter(graph_id=graph_id)
            node_lookup_by_id = self.get_node_lookup_by_id(nodes)
            tiles_to_export = {}
            files_to_download = []

            for resource_id in resource_ids:
                cursor.execute(
                    """SELECT * FROM tiles WHERE resourceinstanceid = (%s)""",
                    [resource_id],
                )
                tiles = dictfetchall(cursor)
                for tile in tiles:
                    tile_data = json.loads(tile["tiledata"])
                    for key, value in tile_data.items():
                        alias = node_lookup_by_id[key]["alias"]
                        datatype = node_lookup_by_id[key]["datatype"]
                        if datatype == "file-list":
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
                        else:
                            from arches.app.datatypes.datatypes import DataTypeFactory

                            self.datatype_factory = DataTypeFactory()
                            datatype_instance = self.datatype_factory.get_instance(
                                datatype
                            )
                            tile[alias] = (
                                datatype_instance.transform_export_values(
                                    value,
                                    concept_export_value_type=concept_export_value_type,
                                )
                                if value
                                else None
                            )
                    card_name = str(
                        Card.objects.get(nodegroup=tile["nodegroupid"]).name
                    )
                    tiles_to_export.setdefault(card_name, []).append(tile)

        wb = create_tile_excel_workbook(graph_id, tiles_to_export)

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
        export_concepts_as = request.POST.get("export_concepts_as")
        filename = request.POST.get("filename")
        search_url = request.POST.get("search_url", None)
        if search_url and not resource_ids:
            resource_ids = get_resourceids_from_search_url(
                search_url, self.request.user
            )

        export_task = tasks.export_tile_excel.apply_async(
            (
                self.userid,
                self.loadid,
                graph_id,
                graph_name,
                resource_ids,
                export_concepts_as,
                filename,
            ),
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET taskid = %s WHERE loadid = %s""",
                (export_task.task_id, self.loadid),
            )
