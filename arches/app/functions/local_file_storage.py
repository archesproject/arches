from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.functions.base import BaseFunction
from arches.app.datatypes import datatypes

class LocalFileStorageFunction(BaseFunction):

    def save(self, tile, request):
        if request:
            for node in tile.nodegroup.node_set.all():
                datatype = datatypes.get_datatype_instance(node.datatype)
                datatype.manage_files(request, tile)
        return tile

    def delete(self, tile, request):
        print "in delete file"
