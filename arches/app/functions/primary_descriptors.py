import uuid
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.datatypes.datatypes import DataTypeFactory


class PrimaryDescriptorsFunction(BaseFunction):

    def get_primary_descriptor_from_nodes(self, resource, config):
        try:
            if 'nodegroup_id' in config and config['nodegroup_id'] != '' and config['nodegroup_id'] is not None:
                tiles = models.TileModel.objects.filter(
                        nodegroup_id=uuid.UUID(config['nodegroup_id']),
                        sortorder=0).filter(resourceinstance_id=resource.resourceinstanceid)
                if len(tiles) == 0:
                    tiles = models.TileModel.objects.filter(
                        nodegroup_id=uuid.UUID(config['nodegroup_id'])).filter(
                        resourceinstance_id=resource.resourceinstanceid)
                for tile in tiles:
                    for node in models.Node.objects.filter(nodegroup_id=uuid.UUID(config['nodegroup_id'])):
                        if len(list(tile.data.keys())) > 0:
                            data = tile.data
                        elif tile.provisionaledits is not None and len(list(tile.provisionaledits.keys())) == 1:
                            userid = list(tile.provisionaledits.keys())[0]
                            data = tile.provisionaledits[userid]['value']
                        if str(node.nodeid) in data:
                            datatype_factory = DataTypeFactory()
                            datatype = datatype_factory.get_instance(node.datatype)
                            value = datatype.get_display_value(tile, node)
                            config['string_template'] = config['string_template'].replace('<%s>' % node.name, value)
        except ValueError as e:
            print(e, 'invalid nodegroupid participating in descriptor function.')

        return config['string_template']
