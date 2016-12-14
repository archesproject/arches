from arches.app.models.tile import Tile
from arches.app.models import models
from arches.app.functions.base import BaseFunction

class LocalFileStorageFunction(BaseFunction):

    def save(self, tile, request):
        for node in tile.nodegroup.node_set.all():
            if node.datatype == 'file-list':
                previously_saved_tile = Tile.objects.filter(pk=tile.tileid)
                if previously_saved_tile.count() == 1:
                    for previously_saved_file in previously_saved_tile[0].data[str(node.pk)]:
                        previously_saved_file_has_been_removed = True
                        for incoming_file in tile.data[str(node.pk)]:
                            if previously_saved_file['file_id'] == incoming_file['file_id']:
                                previously_saved_file_has_been_removed = False
                        if previously_saved_file_has_been_removed:
                            deleted_file = models.File.objects.get(pk=previously_saved_file["file_id"])
                            deleted_file.delete()

                files = request.FILES.getlist('file-list_' + str(node.pk), [])
                for file_data in files:
                    file_model = models.File()
                    file_model.path = file_data
                    file_model.save()
                    for file_json in tile.data[str(node.pk)]:
                        if file_json["name"] == file_data.name and file_json["url"] is None:
                            file_json["file_id"] = str(file_model.pk)
                            file_json["url"] = str(file_model.path.url)
                            file_json["status"] = 'uploaded'

        return tile

    def delete(self, tile, request):
        print "in delete file"

