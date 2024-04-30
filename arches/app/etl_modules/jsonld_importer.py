import os
import zipfile
from functools import lru_cache
from pathlib import Path

from django.core.files import File
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _

from arches.app.etl_modules.base_import_module import BaseImportModule, FileValidationError
from arches.app.etl_modules.decorators import load_data_async
from arches.app.models.models import GraphModel
from arches.app.utils.file_validator import FileValidator


@lru_cache(maxsize=1)
def graph_id_from_slug(slug):
    return GraphModel.objects.get(slug=slug).pk


class JSONLDImporter(BaseImportModule):
    def read(self, request):
        self.prepare_temp_dir(request)
        self.cumulative_json_files_size = 0
        content = request.FILES["file"]

        result = {"summary": {"name": content.name, "size": self.filesize_format(content.size), "files": {}}}
        validator = FileValidator()
        if validator.validate_file_type(content):
            return {
                "status": 400,
                "success": False,
                "title": _("Invalid Uploaded File"),
                "message": _("Upload a valid zip file"),
            }

        with zipfile.ZipFile(content, "r") as zip_ref:
            files = zip_ref.infolist()
            for file in files:
                if file.filename.split(".")[-1] != "json":
                    continue
                if file.filename.startswith("__MACOSX"):
                    continue
                if file.is_dir():
                    continue
                self.cumulative_json_files_size += file.file_size
                result["summary"]["files"][file.filename] = {"size": (self.filesize_format(file.file_size))}
                result["summary"]["cumulative_json_files_size"] = self.cumulative_json_files_size
                with zip_ref.open(file) as opened_file:
                    self.validate_uploaded_file(opened_file)
                    f = File(opened_file)
                    default_storage.save(os.path.join(self.temp_dir, file.filename), f)

        if not result["summary"]["files"]:
            title = _("Invalid Uploaded File")
            message = _("This file has missing information or invalid formatting. Make sure the file is complete and in the expected format.")
            return {"success": False, "data": {"title": title, "message": message}}

        return {"success": True, "data": result}

    def validate_uploaded_file(self, file):
        path = Path(file.name)
        try:
            graph_id_from_slug(path.parts[1])
        except GraphModel.ObjectDoesNotExist:
            raise FileValidationError(
                code=404,
                message=_('The model "{0}" does not exist.').format(path.parts[1])
            )

    def run_load_task(self, userid, files, summary, result, temp_dir, loadid):
        ...

    @load_data_async
    def run_load_task_async(self, request):
        ...
