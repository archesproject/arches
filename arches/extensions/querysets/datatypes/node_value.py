from arches.app.datatypes import datatypes
from arches.app.models import models


# arches_version==9.0.0: remove
class NodeValueDataType(datatypes.NodeValueDataType):
    def get_display_value(self, tile, node, **kwargs):
        """Backport of Arches 8.1 version that moves value_node query under if gate."""
        from arches_querysets.datatypes.datatypes import DataTypeFactory

        datatype_factory = DataTypeFactory()
        try:
            data = self.get_tile_data(tile)
            tileid = data[str(node.nodeid)]
            if tileid:
                value_node = models.Node.objects.get(nodeid=node.config["nodeid"])
                value_tile = models.TileModel.objects.get(tileid=tileid)
                datatype = datatype_factory.get_instance(value_node.datatype)
                return datatype.get_display_value(value_tile, value_node)
            return ""
        except:
            raise Exception(
                f'Node with name "{node.name}" is not configured correctly.'
            )
