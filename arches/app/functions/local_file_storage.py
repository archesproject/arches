from arches.app.models import models
from arches.app.functions.base import BaseFunction

class LocalFileStorageFunction(BaseFunction):

    def save(self, tile, request):
        # a function meant to handle this datatype during tile save
        try:
            tile_model = models.Tile.objects.get(pk=tile['tileid'])
        except models.Tile.DoesNotExist:
            tile_model = None

        nodegroup = models.NodeGroup.objects.get(pk=tile['nodegroup_id'])
        for node in nodegroup.node_set.all():
            if node.datatype == 'file-list':
                if tile_model is not None:
                    model_files = tile_model.data[str(node.pk)]
                    for model_file in model_files:
                        incoming_file = None
                        for file_json in tile['data'][str(node.pk)]:
                            if file_json["file_id"] == model_file["file_id"]:
                                incoming_file = file_json
                        if incoming_file == None:
                            deleted_file = models.File.objects.get(pk=model_file["file_id"])
                            deleted_file.delete()
                files = request.FILES.getlist('file-list_' + str(node.pk), [])
                for file_data in files:
                    file_model = models.File()
                    file_model.path = file_data
                    file_model.save()
                    for file_json in tile['data'][str(node.pk)]:
                        if file_json["name"] == file_data.name and file_json["url"] is None:
                            file_json["file_id"] = str(file_model.pk)
                            file_json["url"] = str(file_model.path.url)
                            file_json["status"] = 'uploaded'

        return tile
