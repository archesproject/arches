import logging
import uuid
import base64
from PIL import Image
from django.utils.translation import gettext as _
from django.views.generic import View
from django.shortcuts import redirect
from arches.app.models.models import File, SearchExportHistory, TempFile
from arches.app.models.system_settings import settings
from django.core.exceptions import PermissionDenied
from arches.app.utils.response import JSONResponse
from django.http import HttpResponse, HttpResponseNotFound
from mimetypes import MimeTypes

logger = logging.getLogger(__name__)


class FileView(View):
    def get(self, request, fileid=None):
        get_thumbnail = (
            False if request.GET.get("thumbnail", "false") == "false" else True
        )
        is_search_export_history = False
        try:
            file = File.objects.get(pk=fileid)
            path = file.path.url
        except File.DoesNotExist:
            file = SearchExportHistory.objects.get(pk=fileid)
            path = file.downloadfile.url
            is_search_export_history = True

        def get_file():
            if (
                not is_search_export_history
                and file.thumbnail_data is None
                and settings.GENERATE_THUMBNAILS_ON_DEMAND
            ):
                file.save()  # simply resaving the file will attempt to regenerate the thumbnail
            if get_thumbnail and file.thumbnail_data:
                return HttpResponse(file.thumbnail_data, content_type="image/png")
            else:
                return redirect(path)

        if settings.RESTRICT_MEDIA_ACCESS and not is_search_export_history:
            permission = request.user.has_perm("read_nodegroup", file.tile.nodegroup)
            permitted = permission is None or permission is True
            if permitted:
                return get_file()
            else:
                raise PermissionDenied()

        else:
            return get_file()


class TempFileView(View):
    def get(self, request, file_id):
        # file_id = request.GET.get("file_id")
        file = TempFile.objects.get(pk=file_id)
        try:
            with file.path.open("rb") as f:
                # sending response
                contents = f.read()
                file_mime = MimeTypes().guess_type(file.path.name)[0]
                response = HttpResponse(contents, content_type=file_mime)
                response["Content-Disposition"] = "attachment; filename={}".format(
                    file.path.name.split("/")[1]
                )

        except IOError:
            # handle file not exist case here
            response = HttpResponseNotFound("<h1>File not exist</h1>")

        return response

    def post(self, request):
        file_id = uuid.uuid4()
        file_name = request.POST.get("fileName", None)
        file = request.FILES.get("file", None)
        file.file_name = file_name
        file.name = file_name
        temp_file = TempFile.objects.create(fileid=file_id, path=file)
        temp_file.save()

        response_dict = {"file_id": file_id}

        return JSONResponse(response_dict)
