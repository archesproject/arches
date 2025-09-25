from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from arches.app.models import models
from arches.app.models.tile import Tile as TileProxyModel
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase


@method_decorator(csrf_exempt, name="dispatch")
class Images(APIBase):
    # meant to handle uploading of full sized images from a mobile client
    def post(self, request):
        tileid = request.POST.get("tileid")
        fileid = request.POST.get("file_id")
        nodeid = request.POST.get("nodeid")
        file_name = request.POST.get("file_name", "temp.jpg")
        file_data = request.FILES.get("data")
        try:
            image_file, file_created = models.File.objects.get_or_create(pk=fileid)
            image_file.path.save(file_name, ContentFile(file_data.read()))

            tile = TileProxyModel.objects.get(pk=tileid)
            tile_data = tile.get_tile_data(request.user.pk)
            for image in tile_data[nodeid]:
                if image["file_id"] == fileid:
                    image["url"] = image_file.path.url
                    image["size"] = image_file.path.size
                    # I don't really want to run all the code TileProxyModel.save(),
                    # so I just call it's super class
                    super(TileProxyModel, tile).save()
                    tile.index()

            # to use base64 use the below code
            # import base64
            # with open("foo.jpg", "w+b") as f:
            #     f.write(base64.b64decode(request.POST.get('data')))

        except Exception as e:
            return JSONResponse(status=500)

        return JSONResponse()
