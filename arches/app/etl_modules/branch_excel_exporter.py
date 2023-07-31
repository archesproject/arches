from datetime import datetime
from io import BytesIO
import json
import logging
import os
import zipfile
from openpyxl.writer.excel import save_virtual_workbook
from django.core.files import File as DjangoFile
from django.http import HttpResponse
from django.db import connection
from django.utils.translation import ugettext as _
from arches.app.etl_modules.branch_csv_importer import BranchCsvImporter
from arches.app.models.models import GraphModel, Node, File, TempFile
from arches.app.models.system_settings import settings
import arches.app.tasks as tasks
from arches.management.commands.etl_template import create_workbook

logger = logging.getLogger(__name__)

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

class BranchExcelExporter(BranchCsvImporter):
    def __init__(self, request=None, loadid=None):
        self.request = request if request else None
        self.userid = request.user.id if request else None
        self.moduleid = request.POST.get("module") if request else None
        self.loadid = loadid if loadid else None

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

    def get_node_lookup_by_id(self, nodes):
        lookup = {}
        for node in nodes:
            lookup[str(node.nodeid)] = {"alias": str(node.alias), "datatype": node.datatype, "config": node.config}
        return lookup

    def dictfetchall(self, cursor): 
        desc = cursor.description 
        return [
            dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall() 
        ]
    
    def get_files_in_zip_file(self, files, graph_name, wb):
        file_ids = [file["file_id"] for file in files]
        file_objects = list(File.objects.filter(pk__in=file_ids))
        for file in files:
            for file_object in file_objects:
                if str(file_object.fileid) == file["file_id"]:
                    file["file"] = file_object.path
        download_files = []
        skipped_files = []
        size_limit = 104857600  # 100MByte
        for file in files:
            if file["file"].size >= size_limit:
                skipped_files.append({
                    "name": file["name"],
                    "url": settings.MEDIA_URL + file['file'].name,
                    "fileid": file["file_id"]
                })
            else:
                download_files.append({"name": file["name"], "downloadfile": file["file"]})

        buffer = BytesIO()
        excel_file_name = "{}_export.xlsx".format(graph_name.replace(" ", "_"))
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip:
            for f in download_files:
                f["downloadfile"].seek(0)
                zip.writestr(f["name"], f["downloadfile"].read())
            zip.writestr(excel_file_name, save_virtual_workbook(wb))

        zip.close()
        buffer.flush()
        zip_stream = buffer.getvalue()
        buffer.close()
        f = BytesIO(zip_stream)

        now = datetime.now().isoformat()
        name = "{0}-{1}.zip".format(graph_name.replace(" ", "_"), now)

        download = DjangoFile(f)
        zip_file = TempFile()
        zip_file.source = "branch-excel-exporter"
        zip_file.path.save(name, download)

        return zip_file, download_files, skipped_files

    def export(self, request):
        self.loadid = request.POST.get("load_id")
        graph_id = request.POST.get("graph_id", None)
        graph_name = request.POST.get("graph_name", None)
        resource_ids = request.POST.get("resource_ids", None)
        use_celery = True

        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO load_event (loadid, complete, status, etl_module_id, load_start_time, user_id) VALUES (%s, %s, %s, %s, %s, %s)""",
                (self.loadid, False, "validated", self.moduleid, datetime.now(), self.userid),
            )

        if use_celery:
            response = self.load_data_async(request)
        else:
            response = self.run_export_task(self.loadid, graph_id, graph_name, resource_ids)

        return response

    def run_export_task(self, load_id, graph_id, graph_name, resource_ids):
        if resource_ids is None:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT resourceinstanceid FROM resource_instances WHERE graphid = (%s)""", [graph_id])
                rows = cursor.fetchall()
                resource_ids = [ row[0] for row in rows ]

        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM __get_nodegroup_tree_by_graph(%s)""", (graph_id,))
            nodegroup_lookup = self.dictfetchall(cursor)

            nodes = Node.objects.filter(graph_id=graph_id)
            node_lookup_by_id = self.get_node_lookup_by_id(nodes)
            tiles_to_export = {}
            files_to_download = []

            for resource_id in resource_ids:
                cursor.execute("""SELECT * FROM tiles WHERE parenttileid IS null AND resourceinstanceid = (%s)""", [resource_id])
                root_tiles = self.dictfetchall(cursor)
                for root_tile in root_tiles:
                    cursor.execute(tile_tree_query, [root_tile["tileid"]])
                    tile_tree = self.dictfetchall(cursor)
                    for tile in tile_tree:
                        root_nodegroup, nodegroup_alias = [
                            (ng["root_nodegroup"], ng["alias"]) for ng in nodegroup_lookup if ng["nodegroupid"] == tile["nodegroupid"]
                        ][0]
                        root_alias = [ng["alias"] for ng in nodegroup_lookup if ng["root_nodegroup"] == root_nodegroup][0]
                        tile["alias"] = nodegroup_alias
                        tile["resourceinstanceid"] = resource_id
                        tile_data = json.loads(tile['tiledata'])
                        for key, value in tile_data.items():
                            alias = node_lookup_by_id[key]["alias"]
                            if node_lookup_by_id[key]["datatype"] == "file-list":
                                file_names_to_export = []
                                for file in value:
                                    files_to_download.append({"name": file["name"], "file_id": file["file_id"]})
                                    file_names_to_export.append(file["name"])
                                tile[alias] = ",".join(file_names_to_export)
                            else:
                                try:
                                    value.keys() # to check if it is a dictionary
                                    tile[alias] = json.dumps(value)
                                except AttributeError:
                                    tile[alias] = value
                        tiles_to_export.setdefault(root_alias, []).append(tile)

        wb = create_workbook(graph_id, tiles_to_export)

        zip_file, download_files, skipped_files = self.get_files_in_zip_file(files_to_download, graph_name, wb)
        zip_file_name = os.path.basename(zip_file.path.name)
        zip_file_url = settings.MEDIA_URL + zip_file.path.name

        load_details = {
            "graph": graph_name,
            "number_of_resources": len(resource_ids),
            "number_of_files": len(download_files),
            "skipped_files": skipped_files,
            "zipfile": {
                "name": zip_file_name,
                "url": zip_file_url,
                "fileid": str(zip_file.fileid)
            }
        }

        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET (complete, status, load_details, load_end_time) = (%s, %s, %s, %s) WHERE  loadid = (%s)""",
                (True, "indexed", json.dumps(load_details), datetime.now(), load_id),
            )

        return { "success": True, "data": "success" }

    def run_load_task_async(self, request):
        self.loadid = request.POST.get("load_id")
        graph_id = request.POST.get("graph_id", None)
        graph_name = request.POST.get("graph_name", None)
        resource_ids = request.POST.get("resource_ids", None)

        export_task = tasks.export_branch_csv.apply_async(
            (self.userid, self.loadid, graph_id, graph_name, resource_ids),
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET taskid = %s WHERE loadid = %s""",
                (export_task.task_id, self.loadid),
            )

