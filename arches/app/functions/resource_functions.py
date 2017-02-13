import uuid
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.datatypes.datatypes import DataTypeFactory

class PrimaryNameFunction(BaseFunction):
    def get(self, resource, config):
        return self.get_primary_name_from_nodes(resource, config)

    def get_primary_name_from_nodes(self, resource, config):
        for tile in models.TileModel.objects.filter(nodegroup_id=uuid.UUID(config['nodegroup_id']), sortorder=0).filter(resourceinstance_id=resource.resourceinstanceid):
            for node in models.Node.objects.filter(nodegroup_id=uuid.UUID(config['nodegroup_id'])):
                if str(node.nodeid) in tile.data:
                    value = tile.data[str(node.nodeid)]
                    if value:
                        datatype_factory = DataTypeFactory()
                        datatype = datatype_factory.get_instance(node.datatype)
                        display_value = datatype.get_display_value(tile, node)
                        if display_value is not None:
                            value = display_value
                        config['string_template'] = config['string_template'].replace('<%s>' % node.name, value)

        return config['string_template']
