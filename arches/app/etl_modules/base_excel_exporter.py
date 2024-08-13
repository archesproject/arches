from datetime import datetime
from io import BytesIO
import json
import os
import zipfile
from tempfile import NamedTemporaryFile
from django.core.files import File as DjangoFile
from django.db import connection
from arches.app.etl_modules.save import get_resourceids_from_search_url
from arches.app.etl_modules.decorators import load_data_async
from arches.app.models.models import File, TempFile
from arches.app.models.system_settings import settings


class BaseExcelExporter:
    def __init__(self, request=None, loadid=None):
        self.request = request if request else None
        self.userid = request.user.id if request else None
        self.loadid = loadid if loadid else None

    def get_node_lookup_by_id(self, nodes):
        lookup = {}
        for node in nodes:
            lookup[str(node.nodeid)] = {
                "alias": str(node.alias),
                "datatype": node.datatype,
                "config": node.config,
            }
        return lookup

    def get_files_in_zip_file(
        self, files, graph_name, wb, user_generated_filename=None
    ):
        file_ids = [file["file_id"] for file in files]
        file_objects = list(File.objects.filter(pk__in=file_ids))
        for file in files:
            for file_object in file_objects:
                if str(file_object.fileid) == file["file_id"]:
                    file["file"] = file_object.path
        download_files = []
        skipped_files = []
        files_not_found = []
        size_limit = 104857600  # 100MByte
        for file in files:
            if not file["file"].storage.exists(file["file"].name):
                files_not_found.append(
                    {
                        "name": file["name"],
                        "url": settings.MEDIA_URL + file["file"].name,
                        "fileid": file["file_id"],
                    }
                )
            elif file["file"].size >= size_limit:
                skipped_files.append(
                    {
                        "name": file["name"],
                        "url": settings.MEDIA_URL + file["file"].name,
                        "fileid": file["file_id"],
                    }
                )
            else:
                download_files.append(
                    {"name": file["name"], "downloadfile": file["file"]}
                )

        buffer = BytesIO()
        excel_file_name = "{}_export.xlsx".format(graph_name.replace(" ", "_"))
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip:
            for f in download_files:
                f["downloadfile"].seek(0)
                zip.writestr(f["name"], f["downloadfile"].read())

            with NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_excel_file:
                wb.save(tmp_excel_file.name)
                with open(tmp_excel_file.name, "rb") as excel_file:
                    zip.writestr(excel_file_name, excel_file.read())

        os.unlink(tmp_excel_file.name)

        buffer.flush()
        zip_stream = buffer.getvalue()
        buffer.close()
        f = BytesIO(zip_stream)

        if user_generated_filename:
            name = "{user_generated_filename}.zip".format(
                user_generated_filename=user_generated_filename
            )
        else:
            name = "{0}-{1}.zip".format(
                graph_name.replace(" ", "_"), datetime.now().isoformat()
            )

        download = DjangoFile(f)
        zip_file = TempFile()

        zip_file.source = "branch-excel-exporter"
        zip_file.path.save(name, download)

        return zip_file, download_files, skipped_files, files_not_found

    def export(self, request):
        self.loadid = request.POST.get("load_id")
        graph_id = request.POST.get("graph_id", None)
        graph_name = request.POST.get("graph_name", None)
        resource_ids = request.POST.get("resource_ids", None)
        export_concepts_as = request.POST.get("export_concepts_as")
        search_url = request.POST.get("search_url", None)
        if search_url and not resource_ids:
            resource_ids = get_resourceids_from_search_url(
                search_url, self.request.user
            )
        use_celery = True

        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO load_event (loadid, complete, status, load_details, etl_module_id, load_start_time, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    self.loadid,
                    False,
                    "validated",
                    json.dumps({"graph": graph_name}),
                    self.moduleid,
                    datetime.now(),
                    self.userid,
                ),
            )

        if use_celery:
            response = self.run_load_task_async(request, self.loadid)
        else:
            response = self.run_export_task(
                self.loadid,
                graph_id,
                graph_name,
                resource_ids,
                export_concepts_as=export_concepts_as,
            )

        return response

    @load_data_async
    def run_load_task_async(self, request, load_id, *args, **kwargs):
        pass

    def run_export_task(
        self, load_id, graph_id, graph_name, resource_ids, *args, **kwargs
    ):
        pass
