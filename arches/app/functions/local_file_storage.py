from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.functions.base import BaseFunction
from arches.app.datatypes.datatypes import DataTypeFactory

class LocalFileStorageFunction(BaseFunction):

    def save(self, tile, request):
        if request:
            datatype_factory = DataTypeFactory()
            for node in tile.nodegroup.node_set.all():
                datatype = datatype_factory.get_instance(node.datatype)
                previously_saved_tile = Tile.objects.filter(pk=tile.tileid)
                datatype.manage_files(previously_saved_tile, tile, request, node)

        return tile

    def delete(self, tile, request):
        print "in delete file"
